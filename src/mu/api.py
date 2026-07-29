"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from collections.abc import Iterator
from pathlib import Path

from mu.database import Database
from mu.file import copy_file_to_source, read_metadata
from mu.types import Album, Artist, Playlist, Track


class Api:
    def __init__(
        self,
        db_path: Path | None = None,
        source_path: Path | None = None,
        albumart_path: Path | None = None,
    ):

        self.db = Database(db_path, source_path, albumart_path)

    def scan_source_folder(self, batch_size: int = 100) -> Iterator[dict]:
        """
        Rescans source_path and upserts every MP3 found.
        Yields one progress dict per file, after that file has been committed.
        """
        files = sorted(
            p
            for p in self.db.source_path.rglob("*")
            if p.is_file() and p.suffix.lower() == ".mp3"
        )
        yield from self._ingest(files, batch_size)

    def import_media(self, path, batch_size: int = 10) -> Iterator[dict]:
        """
        Copies media from the path into the source folder,
        then upserts to the database. Yields one progress dict per file
        """
        path = Path(path).resolve()

        if path.is_dir():
            files = sorted(
                p for p in path.rglob("*") if p.is_file() and p.suffix.lower() == ".mp3"
            )
        elif path.is_file() and path.suffix.lower() == ".mp3":
            files = [path]
        else:
            return  # not a dir, not an mp3 — nothing to do

        yield from self._ingest(files, batch_size, copy_to_source=True)

    def get_tracks(self, term: str | None = None) -> dict[int, Track]:
        """
        Returns a dict of tracks with the trackid as the key
        """
        ordering = """
            ORDER BY artist COLLATE NOCASE,
            album COLLATE NOCASE,
            CAST(discnumber AS INTEGER),
            CAST(tracknumber AS INTEGER)
        """
        select = "SELECT * FROM tracks "
        if term:
            where, values = self._build_sql(term, "tracks")
            rows = self.db.query(select + where + ordering, values)
        else:
            rows = self.db.query(select + ordering)
        return {t.id: t for t in (Track(row) for row in rows)}

    def get_albums(self, term: str | None = None) -> dict[tuple, Album]:
        """
        Returns every album mapped to its tracks.
        Optional `term` filters tracks using the same prefix syntax as list_tracks.
        """
        ordering = """
            ORDER BY albumartist COLLATE NOCASE,
                    album COLLATE NOCASE,
                    CAST(discnumber AS INTEGER),
                    CAST(tracknumber AS INTEGER)
        """
        select = "SELECT * FROM tracks"
        if term:
            where, values = self._build_sql(term, "tracks")
            rows = self.db.query(select + where + ordering, values)
        else:
            rows = self.db.query(select + ordering)

        albums: dict[tuple[str, str], Album] = {}
        for row in rows:
            track: Track = Track(row)
            if not track.album or not track.albumartist:
                continue
            key: tuple[str, str] = (track.albumartist, track.album)
            if key not in albums:
                albums[key] = Album(
                    title=track.album, albumartist=track.albumartist, tracks=[]
                )
            albums[key].tracks.append(track)
        return albums

    def get_artists(
        self, term: str | None = None, only_albumartists: bool = False
    ) -> dict[str, Artist]:
        """
        Returns every artist mapped to their tracks.
        Set only_albumartists to group by album artist instead of track artist.
        Term filters through tracks.
        """
        column = "albumartist" if only_albumartists else "artist"
        ordering = f"""
            ORDER BY {column} COLLATE NOCASE,
                album COLLATE NOCASE,
                CAST(discnumber AS INTEGER),
                CAST(tracknumber AS INTEGER)
        """
        select = "SELECT * FROM tracks"

        if term:
            where, values = self._build_sql(term, "tracks")
            rows = self.db.query(select + where + ordering, values)
        else:
            rows = self.db.query(select + ordering)

        artists: dict[str, Artist] = {}
        for row in rows:
            track = Track(row)
            name = row[column]  # the grouping name for THIS track
            if not name or not name.strip():
                continue
            if name not in artists:
                artists[name] = Artist(name=name, tracks=[])
            artists[name].tracks.append(track)
        return artists

    def get_playlists(self, term: str | None = None) -> dict[int, Playlist]:
        """
        Returns a dictionary with playlist id mapped to each playlist object.
        Term filters through tracks.
        """
        playlists: dict[int, Playlist] = {}
        ordering = " ORDER BY id, title COLLATE NOCASE"
        select = "SELECT * FROM playlists"
        # Create playlists
        if term:
            where, values = self._build_sql(term, "playlists")
            playlist_rows = self.db.query(select + where + ordering, values)
        else:
            playlist_rows = self.db.query(select + ordering)
        for row in playlist_rows:
            playlists[row["id"]] = Playlist(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                tracks=self._get_playlist_tracks(row["id"]),
            )

        return playlists

    def favorite_tracks(self, term: str) -> dict[int, Track]:
        """
        Toggles the favorite status of track(s), returns them
        as a dict with tracks mapped to their ids.
        Term filters through tracks.
        """
        match, values = self._build_sql(term, "tracks")
        with self.db.write() as conn:
            rows = conn.execute(
                "UPDATE tracks SET favorite = 1 - favorite " + match + " RETURNING *",
                values,
            ).fetchall()

        return {t.id: t for t in (Track(row) for row in rows)}

    def create_playlist(self, title: str, description: str = "") -> Playlist:
        """
        Creates a new playlist. If one is already found with the same name,
        it returns the playlists contents.
        """
        with self.db.write() as conn:
            playlist_row = conn.execute(
                """
                INSERT INTO playlists (title,description)
                VALUES (?,?)
                ON CONFLICT (title) DO NOTHING
                RETURNING *
                """,
                (title, description),
            ).fetchone()

            if playlist_row is None:
                playlist_row = conn.execute(
                    """
                    SELECT * FROM playlists
                    WHERE title = ?
                    """,
                    (title,),
                ).fetchone()

            playlist_id = playlist_row["id"]

        return self.get_playlists(f"id={playlist_id}")[playlist_id]

    def append_playlists(
        self, playlists_term: str, tracks_term: str
    ) -> dict[int, Playlist]:
        pids: list[int] = list(self.get_playlists(playlists_term).keys())
        tids: list[int] = list(self.get_tracks(tracks_term).keys())
        with self.db.write() as conn:
            for pid in pids:
                pos = conn.execute(
                    "SELECT COALESCE(MAX(position), -1) + 1 FROM playlist_tracks WHERE playlist_id = ?",
                    (pid,),
                ).fetchone()[0]
                for tid in tids:
                    cur = conn.execute(
                        """INSERT INTO playlist_tracks (playlist_id, track_id, position)
                        VALUES (?, ?, ?) ON CONFLICT DO NOTHING""",
                        (pid, tid, pos),
                    )
                    if cur.rowcount:
                        pos += 1
        return self.get_playlists(playlists_term)

    def playlist_remove(self, playlists_term, tracks_term) -> dict[int, Playlist]:
        pids = list(self.get_playlists(playlists_term).keys())
        tids = list(self.get_tracks(tracks_term).keys())
        if not tids:
            return self.get_playlists(playlists_term)

        placeholders = ",".join("?" * len(tids))
        with self.db.write() as conn:
            for pid in pids:
                cur = conn.execute(
                    f"DELETE FROM playlist_tracks "
                    f"WHERE playlist_id = ? AND track_id IN ({placeholders})",
                    (pid, *tids),
                )
                if cur.rowcount:  # only renumber if we removed something
                    conn.execute(
                        """
                        UPDATE playlist_tracks
                        SET position = (
                            SELECT COUNT(*) FROM playlist_tracks p2
                            WHERE p2.playlist_id = playlist_tracks.playlist_id
                            AND p2.position < playlist_tracks.position
                        )
                        WHERE playlist_id = ?
                        """,
                        (pid,),
                    )
        return self.get_playlists(playlists_term)

    def _get_playlist_tracks(self, playlist_id: int) -> list[Track]:
        """
        Returns a list of tracks in a playlist, in order.
        This is a supporting method to get get_playlist() method
        and should not be used alone.
        """
        rows = self.db.query(
            """
                SELECT tracks.*
                FROM tracks
                JOIN playlist_tracks ON tracks.id = playlist_tracks.track_id
                WHERE playlist_tracks.playlist_id = ?
                ORDER BY playlist_tracks.position
            """,
            (playlist_id,),
        )
        return [Track(row) for row in rows]

    def _build_sql(self, term: str, table: str) -> tuple[str, tuple]:
        """
        Converts mu search queries into SQL where statments.
        Returns a tuple of the SQL string and a tuple of values.
        """
        groups = []
        values = []

        if table not in self.db.SEARCHABLE:
            raise ValueError(f"Cannot search table {table!r}.")

        columns: set[str] = self.db.SEARCHABLE[table]

        for query in term.split("+"):
            conditions = []
            for filter in query.split("&"):
                col, sep, value = filter.partition(":")
                if not sep:
                    col, sep, value = filter.partition("=")
                if not sep:
                    raise ValueError(f"Filter {filter!r} needs ':' or '='.")

                col, value = col.strip(), value.strip()
                if col not in columns:
                    raise ValueError(f"Unknown or empty search field {col!r}.")
                if not value:
                    raise ValueError(f"Filter {filter!r} has no value.")
                if sep == ":":
                    conditions.append(f"{col} LIKE ? COLLATE NOCASE")
                    values.append(f"%{value}%")
                else:
                    conditions.append(f"{col} = ?")
                    values.append(value)
            groups.append("(" + " AND ".join(conditions) + ")")

        sql = " WHERE " + " OR ".join(groups)
        return sql, tuple(values)

    def _upsert_track(self, conn, metadata: dict) -> Track:
        """
        Inserts the track, or updates it in place if filepath already exists.
        Requires: "filepath" TEXT UNIQUE
        """
        row = conn.execute(
            """
            INSERT INTO tracks (
                title, artist, album, time, tracknumber, albumartist,
                discnumber, genre, date, filepath, filename, albumart
            ) VALUES (
                :title, :artist, :album, :time, :tracknumber, :albumartist,
                :discnumber, :genre, :date, :filepath, :filename, :albumart
            )
            ON CONFLICT(filepath) DO UPDATE SET
                title       = excluded.title,
                artist      = excluded.artist,
                album       = excluded.album,
                time        = excluded.time,
                tracknumber = excluded.tracknumber,
                albumartist = excluded.albumartist,
                discnumber  = excluded.discnumber,
                genre       = excluded.genre,
                date        = excluded.date,
                filename    = excluded.filename,
                albumart    = excluded.albumart
            RETURNING *
            """,
            metadata,
        ).fetchone()
        return Track(row)

    def _ingest(
        self, files: list[Path], batch_size: int, copy_to_source: bool = False
    ) -> Iterator[dict]:
        """Shared by scan_source_folder and import_media."""
        total = len(files)
        batch: list[tuple[dict, dict | None]] = []

        # Upserts metadata dict's from batch
        def flush() -> list[dict]:
            if not batch:
                return []
            metas: list[dict] = [m for _, m in batch if m is not None]
            if metas:
                try:
                    with self.db.write() as con:
                        for meta in metas:
                            self._upsert_track(con, meta)
                except Exception as exc:
                    for record, meta in batch:
                        if meta is not None:
                            record["ok"] = False
                            record["error"] = f"write failed: {exc}"
            records: list[dict] = [record for record, _ in batch]
            batch.clear()
            return records

        for count, path in enumerate(files, 1):
            record = {
                "ok": True,
                "count": count,
                "total": total,
                "filename": path.name,
                "error": None,
            }
            meta = None
            try:
                if copy_to_source:
                    meta = copy_file_to_source(
                        path, self.db.source_path, self.db.albumart_path
                    )
                else:
                    meta = read_metadata(path, self.db.albumart_path)
            except Exception as exc:
                record["ok"] = False
                record["error"] = f"read failed: {exc}"
            batch.append((record, meta))
            if len(batch) >= batch_size:
                yield from flush()

        yield from flush()
