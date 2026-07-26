"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from collections.abc import Iterator
import copy
from pathlib import Path

from mu.database import Database
from mu.file import read_metadata
from mu.file import read_metadata
from mu.types import Album, Artist, Track
import shutil


class Api:
    def __init__(
        self,
        db_path: Path | None = None,
        source_path: Path | None = None,
        albumart_path: Path | None = None,
    ):

        self.db = Database(db_path, source_path, albumart_path)

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

    def _copy_file_to_source(self, path: Path) -> Path:
        """
        Copies the file, and returns the new path of the file.
        """
        metadata = read_metadata(path, None)

        newpath = Path(self.db.source_path / metadata["artist"] / metadata["album"])
        newpath.mkdir(exist_ok=True, parents=True)
        shutil.copy(path, newpath)

        return newpath

    def import_media(self, path, batch_size: int = 10) -> Iterator[dict]:

        path = Path(path).resolve()
        files = (
            sorted(
                p for p in path.rglob("*") if p.is_file() and p.suffix.lower() == ".mp3"
            )
            if path.is_dir()
            else [path]
        )

        yield from self._ingest(files, batch_size, copy_to_source=True)

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
                    path = self._copy_file_to_source(path)
                meta = read_metadata(path, self.db.albumart_path)
            except Exception as exc:
                record["ok"] = False
                record["error"] = f"read failed: {exc}"
            batch.append((record, meta))
            if len(batch) >= batch_size:
                yield from flush()

        yield from flush()  # trailing partial batch

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
