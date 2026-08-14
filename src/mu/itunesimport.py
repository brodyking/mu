"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import xml.etree.ElementTree as ET
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import unquote, urlparse

from mu.api import Api
from mu.file import copy_file_to_source
from mu.models import Playlist

# iTunes / Music generates these automatically; they are not user playlists.
_SYSTEM_PLAYLIST_NAMES = {
    "Library",
    "Downloaded",
    "Music",
    "Movies",
    "TV Shows",
    "Podcasts",
    "Audiobooks",
    "Books",
    "Genius",
    "Purchased",
    "Home Videos",
    "Voice Memos",
}


class ITunesImport:
    """
    Imports tracks and playlists from an iTunes / Music `Library.xml` into mu.

    Usage:
        for record in ITunesImport(api, "Library.xml").run():
            ...  # record is a progress dict; let the CLI print it

    Tracks are imported first (which populates the iTunes-id -> mu-id map),
    then playlists, so playlist membership can be resolved.

    Writes are batched: track upserts commit once per `batch_size`, and each
    playlist's membership is written in a single transaction — one fsync per
    batch/playlist instead of one per track.
    """

    def __init__(self, api: Api, filepath: Path | str) -> None:
        self.api = api
        self.filepath = Path(filepath)
        self.ids: dict[int, int] = {}  # iTunes "Track ID" -> mu track id

        root = ET.parse(self.filepath).getroot()
        # The library is a single top-level <dict>; parse it once and reuse.
        self.library: dict = self.parse_plist_dict(root[0])

    # ------------------------------------------------------------------ #
    # plist parsing
    # ------------------------------------------------------------------ #

    @staticmethod
    def parse_plist_dict(dict_element) -> dict:
        """Parse a plist <dict> element (alternating key/value children)."""
        result: dict = {}
        children = list(dict_element)
        for i in range(0, len(children) - 1, 2):
            key = children[i].text
            result[key] = ITunesImport.parse_plist_value(children[i + 1])
        return result

    @staticmethod
    def parse_plist_value(elem):
        """Parse a plist value element into the matching Python type."""
        tag = elem.tag
        if tag == "string":
            return elem.text
        if tag == "integer":
            return int(elem.text)
        if tag == "real":
            return float(elem.text)
        if tag == "true":
            return True
        if tag == "false":
            return False
        if tag == "date":
            return elem.text  # ISO-8601 string; stored as-is in dateadded (TEXT)
        if tag == "dict":
            return ITunesImport.parse_plist_dict(elem)
        if tag == "array":
            return [ITunesImport.parse_plist_value(child) for child in elem]
        return elem.text

    @staticmethod
    def plist_url_to_path(url: str) -> Path | None:
        """A file:// Location -> local Path. Non-file (remote) tracks -> None."""
        parsed = urlparse(url)
        if parsed.scheme != "file":
            return None
        return Path(unquote(parsed.path))

    # tracks

    def import_tracks(self, batch_size: int = 100) -> Iterator[dict]:
        """
        Copy + upsert every importable track, yielding one record each.

        File I/O (copy + metadata read) happens outside any transaction; the
        DB writes for a whole batch are committed together.
        """
        tracks: dict = self.library.get("Tracks", {})
        total = len(tracks)
        # each entry: (record, itunes_track, meta|None)
        batch: list[tuple[dict, dict, dict | None]] = []

        def flush() -> list[dict]:
            if not batch:
                return []
            try:
                with self.api.db.write() as conn:
                    for record, itr, meta in batch:
                        if meta is None:
                            continue  # file failed to read; stays a failure record
                        self._write_track(conn, record, itr, meta)
            except Exception as exc:
                for record, _, meta in batch:
                    if meta is not None:
                        record["ok"] = False
                        record["error"] = f"write failed: {exc}"
                        record["track"] = None
            records = [rec for rec, _, _ in batch]
            batch.clear()
            return records

        for count, itr in enumerate(tracks.values(), 1):
            record = self._blank_record("track", count, total, itr)
            meta: dict | None = None
            try:
                meta = self._read_track(itr)  # slow part, kept out of the txn
            except (ValueError, FileNotFoundError, OSError) as exc:
                record["ok"] = False
                record["error"] = str(exc)
            batch.append((record, itr, meta))
            if len(batch) >= batch_size:
                yield from flush()
        yield from flush()

    def _read_track(self, itunes_track: dict) -> dict:
        """Resolve the file, copy it into source, and return its metadata."""
        if itunes_track.get("Track ID") is None:
            raise ValueError("track has no Track ID")

        location = itunes_track.get("Location")
        if not location:
            raise ValueError("track has no file location")
        src = self.plist_url_to_path(location)
        if src is None:
            raise ValueError("track is not a local file")
        if not src.exists():
            raise FileNotFoundError(f"missing file: {src}")

        # One metadata read + copy into the source tree. Raises ValueError on a
        # non-MP3 or unreadable file (mu is MP3-only).
        return copy_file_to_source(
            src, self.api.db.source_path, self.api.db.albumart_path
        )

    def _write_track(self, conn, record: dict, itunes_track: dict, meta: dict) -> None:
        """Upsert one track and apply the iTunes-only fields, on `conn`."""
        track = self.api._upsert_track(conn, meta)

        dateadded = itunes_track.get("Date Added")
        plays = itunes_track.get("Play Count")
        loved = bool(itunes_track.get("Loved") or itunes_track.get("Favorited"))

        # dateadded, plays, and a *set* (not toggle) favorite are the three
        # iTunes fields the public Api can't express yet. COALESCE keeps existing
        # values when iTunes omits a field and makes re-imports idempotent.
        # Promote to an Api method (e.g. set_track_stats) to get this out of the
        # importer.
        conn.execute(
            """
            UPDATE tracks SET
                dateadded = COALESCE(?, dateadded),
                plays     = COALESCE(?, plays),
                favorite  = COALESCE(?, favorite)
            WHERE id = ?
            """,
            (dateadded, plays, 1 if loved else None, track.id),
        )

        # Reflect the applied fields on the returned object (no extra query).
        if dateadded is not None:
            track.dateadded = dateadded
        if plays is not None:
            track.plays = int(plays)
        if loved:
            track.favorite = True

        self.ids[itunes_track["Track ID"]] = track.id
        record["track"] = track

    # ------------------------------------------------------------------ #
    # playlists
    # ------------------------------------------------------------------ #

    def import_playlists(self) -> Iterator[dict]:
        """Recreate user playlists (order preserved), yielding one record each."""
        playlists = [p for p in self.library.get("Playlists", []) if self._wanted(p)]
        total = len(playlists)
        for count, itunes_pl in enumerate(playlists, 1):
            record = self._blank_record("playlist", count, total, itunes_pl)
            try:
                record["playlist"] = self._ingest_playlist(itunes_pl)
            except (ValueError, KeyError) as exc:
                record["ok"] = False
                record["error"] = str(exc)
            yield record

    @staticmethod
    def _wanted(itunes_pl: dict) -> bool:
        """Skip the master library, system playlists, and empty/folder ones."""
        if itunes_pl.get("Master") or "Distinguished Kind" in itunes_pl:
            return False
        if itunes_pl.get("Name") in _SYSTEM_PLAYLIST_NAMES:
            return False
        return bool(itunes_pl.get("Playlist Items"))

    def _ingest_playlist(self, itunes_pl: dict) -> Playlist:
        title = itunes_pl["Name"]
        description = itunes_pl.get("Description") or ""
        playlist = self.api.create_playlist(title, description)
        pid = playlist.id

        # Map iTunes item order -> mu ids, dropping tracks we didn't import
        # (non-MP3s, missing files, remote tracks).
        ordered_tids = [
            self.ids[item["Track ID"]]
            for item in itunes_pl.get("Playlist Items", [])
            if item.get("Track ID") in self.ids
        ]

        # Insert membership in ONE transaction, assigning positions in iTunes
        # order. This is the same logic append_playlists uses internally; calling
        # append_playlists once per track instead re-materialised the whole
        # playlist on every call (O(n^2)) and committed per track. Promote to an
        # Api.append_playlist_ordered(pid, tids) to get this out of the importer.
        with self.api.db.write() as conn:
            pos = conn.execute(
                "SELECT COALESCE(MAX(position), -1) + 1 FROM playlist_tracks "
                "WHERE playlist_id = ?",
                (pid,),
            ).fetchone()[0]
            for tid in ordered_tids:
                cur = conn.execute(
                    "INSERT INTO playlist_tracks (playlist_id, track_id, position) "
                    "VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
                    (pid, tid, pos),
                )
                if cur.rowcount:
                    pos += 1

        return self.api.get_playlists(f"id={pid}")[pid]

    # ------------------------------------------------------------------ #
    # driver
    # ------------------------------------------------------------------ #

    def run(self, batch_size: int = 100) -> Iterator[dict]:
        """Import tracks (builds the id map), then playlists."""
        yield from self.import_tracks(batch_size)
        yield from self.import_playlists()

    @staticmethod
    def _blank_record(kind: str, count: int, total: int, source: dict) -> dict:
        return {
            "kind": kind,
            "ok": True,
            "count": count,
            "total": total,
            "name": source.get("Name") or "(unknown)",
            "error": None,
            "track": None,
            "playlist": None,
        }
