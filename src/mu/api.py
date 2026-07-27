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

    def list_library_tracks(self, only_favorited: bool = False) -> dict[int, Track]:
        """
        Returns a dict of tracks with the trackid as the key
        """
        sql = "SELECT * FROM tracks"
        if only_favorited:
            sql += " WHERE favorite = 1"
        sql += """
            ORDER BY artist COLLATE NOCASE,
                    album COLLATE NOCASE,
                    CAST(discnumber AS INTEGER),
                    CAST(tracknumber AS INTEGER)
        """
        return {t.id: t for t in (Track(row) for row in self.db.query(sql))}

    def list_library_albums(self) -> dict[str, Album]:
        """
        Returns every album mapped to their tracks.
        """

        rows = self.db.query("""
            SELECT * FROM tracks
            WHERE albumartist IS NOT NULL AND TRIM(albumartist) != ''
            ORDER BY albumartist COLLATE NOCASE,
                    album COLLATE NOCASE,
                    CAST(discnumber AS INTEGER),
                    CAST(tracknumber AS INTEGER)
        """)

        albums: dict[str, Album] = {}
        for row in rows:
            track = Track(row)
            album_name = track.album  # the grouping name for THIS track
            if album_name not in albums:
                albums[album_name] = Album(
                    title=track.album, albumartist=track.artist, tracks=[]
                )
            albums[album_name].tracks.append(track)
        return albums

    def list_library_artists(
        self, only_albumartists: bool = False
    ) -> dict[str, Artist]:
        """
        Returns every artist mapped to their tracks.
        Set only_albumartists to group by album artist instead of track artist.
        """
        column = "albumartist" if only_albumartists else "artist"

        rows = self.db.query(f"""
            SELECT * FROM tracks
            WHERE {column} IS NOT NULL AND TRIM({column}) != ''
            ORDER BY {column} COLLATE NOCASE,
                    album COLLATE NOCASE,
                    CAST(discnumber AS INTEGER),
                    CAST(tracknumber AS INTEGER)
        """)

        artists: dict[str, Artist] = {}
        for row in rows:
            track = Track(row)
            name = row[column]  # the grouping name for THIS track
            if name not in artists:
                artists[name] = Artist(name=name, tracks=[])
            artists[name].tracks.append(track)
        return artists

    def list_library_playlists(self) -> dict[int, Playlist]:
        playlists: dict[int, Playlist] = {}

        # Create playlists
        playlist_rows = self.db.query("SELECT * FROM playlists")
        for row in playlist_rows:
            playlists[row["id"]] = Playlist(
                id=row["id"],
                title=row["title"],
                description=row["description"],
            )

        # Get playlist tracks
        track_rows = self.db.query("""
            SELECT pt.playlist_id, t.*
            FROM playlist_tracks pt
            JOIN tracks t ON t.id = pt.track_id
            ORDER BY pt.playlist_id, pt.position
        """)
        for row in track_rows:
            playlist = playlists.get(row["playlist_id"])
            if playlist is not None:
                playlist.tracks.append(Track(row))
        return playlists

    def _build_search_sql(self, term: str, table: str) -> tuple[str, tuple]:
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
                    col, sep, value = filter.partition("=")  # try exact-match operator
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

        sql = f"SELECT * FROM {table} WHERE " + " OR ".join(groups)
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
                    with self.db.write() as con:  # lock held only here
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

        yield from flush()  # trailing partial batch
