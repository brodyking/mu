"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import shutil
import sqlite3
from collections.abc import Iterator
from pathlib import Path

from mu.database.album import Album
from mu.database.file import File
from mu.database.playlist import Playlist
from mu.database.schemaerror import SchemaError
from mu.database.track import Track


class Database:
    DATABASE_VERSION = 2

    def __init__(self, **kwargs):
        """
        Creates a new Database object.
        """

        # Sets the file paths for db_path, source_path, and albumart_path
        self.db_path = (
            Path(Path.home() / "Music" / "mu" / "mu.db")
            if "db_path" not in kwargs
            else Path(str(kwargs.get("db_path")))
        )
        self.source_path = (
            Path(Path.home() / "Music" / "mu" / "source")
            if "source_path" not in kwargs
            else Path(str(kwargs.get("source_path")))
        )
        self.albumart_path = (
            Path(Path.home() / "Music" / "mu" / "albumart")
            if "albumart_path" not in kwargs
            else Path(str(kwargs.get("albumart_path")))
        )

        # Validates that the locations exist and have the necessary files.
        self.validate_library()

    def validate_library(
        self, database_folder=True, source_folder=True, albumart_folder=True
    ):
        """
        By default, checks to ensure the database, source_folder,
        and albumart_folder exist.
        If they do not, they are created.
        """

        def check_db() -> None:
            """
            Checks if database file exists. If it dosen't, it creates it.
            """

            # Creates blank table if file dosen't exist
            with sqlite3.connect(str(self.db_path)) as connection:
                current_version = connection.execute("PRAGMA user_version").fetchone()[
                    0
                ]

                if current_version != self.DATABASE_VERSION and current_version != 0:
                    raise SchemaError(self.DATABASE_VERSION, current_version)

                # Creates tracks table
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS "tracks" (
                        "id"	INTEGER NOT NULL UNIQUE,
                        "favorite" INT DEFAULT 0,
                        "title"	TEXT,
                        "artist"	TEXT,
                        "album"	TEXT,
                        "plays" INT DEFAULT 0,
                        "time" TEXT,
                        "dateadded" TEXT,
                        "tracknumber"	INTEGER,
                        "albumartist"	TEXT,
                        "discnumber"	INTEGER,
                        "genre"	TEXT,
                        "date"	TEXT,
                        "filepath" TEXT,
                        "filename" TEXT,
                        "albumart" TEXT,
                        PRIMARY KEY("id" AUTOINCREMENT)
                    )
                """)
                # Creates playlists table
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS "playlists" (
                        "id" INTEGER NOT NULL UNIQUE,
                        "title" TEXT NOT NULL UNIQUE,
                        "description" TEXT,
                        PRIMARY KEY("id" AUTOINCREMENT)
                    )
                """)
                # Creates playlist_tracks table
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS "playlist_tracks" (
                        "playlist_id" INTEGER NOT NULL REFERENCES playlists(id),
                        "track_id"    INTEGER NOT NULL REFERENCES tracks(id),
                        "position"    INTEGER NOT NULL,
                        "date_added"  TEXT DEFAULT (datetime('now')),
                        PRIMARY KEY (playlist_id, track_id)
                    );
                """)
                connection.execute(f"PRAGMA user_version = {self.DATABASE_VERSION}")
                connection.commit()

        if source_folder:
            self.source_path.mkdir(parents=True, exist_ok=True)
        if albumart_folder:
            self.albumart_path.mkdir(parents=True, exist_ok=True)
        if database_folder:
            check_db()

    def reset_db(self) -> None:
        """
        Deletes all tracks and playlists from database. Keeps files.
        """
        with sqlite3.connect(str(self.db_path)) as connection:
            connection.execute("DELETE FROM tracks;")
            connection.execute("DELETE FROM playlists;")
            connection.execute("DELETE FROM playlist_tracks;")
            connection.execute("UPDATE sqlite_sequence SET seq = 0;")
            connection.commit()

    def upsert_track(self, connection, metadata: dict) -> None:
        """
        Puts all song metadata along with album art and file location
        into the database.
        If the filepath already exists, then it just updates
        the metadata instead of reinserting.
        """
        existing = connection.execute(
            "SELECT id FROM tracks WHERE filepath = ?", (metadata["filepath"],)
        ).fetchone()

        if existing:
            connection.execute(
                """
                UPDATE tracks SET
                    filename    = :filename,
                    title       = :title,
                    artist      = :artist,
                    album       = :album,
                    time        = :time,
                    albumartist = :albumartist,
                    tracknumber = :tracknumber,
                    discnumber  = :discnumber,
                    date        = :date,
                    genre       = :genre,
                    albumart   = :albumart
                WHERE filepath = :filepath
            """,
                metadata,
            )
        else:
            connection.execute(
                """
                INSERT INTO tracks (
                   title, artist, album, time, dateadded,
                   tracknumber, albumartist, discnumber, genre,
                   date, filepath, filename, albumart
                ) VALUES (
                   :title, :artist, :album, :time, :dateadded,
                   :tracknumber, :albumartist, :discnumber, :genre,
                   :date, :filepath, :filename, :albumart
                )
            """,
                metadata,
            )

        connection.commit()

    def upsert_track_once(self, metadata: dict) -> None:
        with sqlite3.connect(str(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            self.upsert_track(connection, metadata)

    def scan_source_folder(self) -> Iterator[dict]:
        """
        Scans the path for music files.
        Each file is stored in the DB and has its album art hashed/saved.
        Yields a dict with current pos, total, and track filename
        """
        path = self.source_path
        with sqlite3.connect(str(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            mp3s = list(path.rglob("*.mp3"))
            total = len(mp3s)
            for i, filepath in enumerate(mp3s, 1):
                out = {
                    "ok": True,
                    "count": i,
                    "total": total,
                    "filename": filepath.name,
                }
                try:
                    metadata = File.read_metadata(
                        filepath, self.albumart_path
                    )  # Gets dict of files metadata
                    self.upsert_track(connection, metadata)  # Updates the track
                    yield out
                except Exception:
                    out["ok"] = False
                    yield out

            connection.commit()

    def copy_file(self, path: Path) -> dict:
        """
        Copies the file, and returns the new metadata of the file.
        """
        metadata = File.read_metadata(path, self.albumart_path)

        newpath = Path(self.source_path / metadata["artist"] / metadata["album"])
        newpath.mkdir(exist_ok=True, parents=True)
        shutil.copy(path, newpath)

        metadata["filepath"] = str(Path(newpath / metadata["filename"]))

        return metadata

    def import_media(self, path) -> Iterator[dict]:
        """
        Copies the file or files (if dir) to ~/mu/source,
        upserts metadata to the database.
        Yields a dict with the current pos, total, and track filename
        """
        path = Path(path).resolve()

        if path.is_dir():
            mp3s = list(path.rglob("*.mp3"))
        else:
            mp3s = [path]

        if not mp3s:
            return

        with sqlite3.connect(str(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            total = len(mp3s)
            for i, filepath in enumerate(mp3s, 1):
                out = {
                    "ok": True,
                    "count": i,
                    "total": total,
                    "filename": filepath.name,
                }
                try:
                    metadata = self.copy_file(filepath)
                    self.upsert_track(connection, metadata)
                    yield out
                except Exception as e:
                    print(e)
                    out["ok"] = False
                    yield out

    def search(self, term: str) -> list:
        """
        Searches the database for tracks with prefix support.
        If no prefix is given, it will search by id.
        Returns a list of tracks.
        """

        # All col's in the database
        prefixes = [
            "id",
            "favorite",
            "title",
            "artist",
            "album",
            "plays",
            "time",
            "dateadded",
            "tracknumber",
            "albumartist",
            "discnumber",
            "genre",
            "date",
            "filepath",
            "filename",
            "albumart",
        ]

        # Finds the target column if user is using a prefix.
        target_column = (
            term.split(":", 1)[0] if term.split(":", 1)[0] in prefixes else None
        )
        if target_column is None:
            raise ValueError(
                "The search query is missing a prefix. "
                "Please specify how you are searching by typing "
                'the prefix followed by a colon. Ex: "artist:aphex twin"'
            )
        with sqlite3.connect(str(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()

            # Specific Search
            value = term.split(":", 1)[1]

            if target_column == "id":
                # IDs usually need to be exact
                query = "SELECT * FROM tracks WHERE id = ?"
                cursor.execute(query, (value,))
            else:
                # Text searches use LIKE and wildcards
                # We wrap the value in % so it finds partial matches
                query = f"SELECT * FROM tracks WHERE {target_column} LIKE ?"
                cursor.execute(query, (f"%{value}%",))

            results = cursor.fetchall()
            export = []
            for i, result in enumerate(results):
                export.append(Track(result))
            return export

    def increment_play_count(self, term: str, amount: int = 1) -> list[Track]:
        """Increment track(s) play counts by either 1 or a custom amount"""
        tracks: list[Track] = self.search(f"{term}")
        results = []
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            for track in tracks:
                cursor.execute(
                    "UPDATE tracks SET plays = ? WHERE id = ?",
                    (track.plays + amount, track.id),
                )
                cursor.execute("SELECT * FROM tracks WHERE id = ?", (track.id,))
                results.append(Track(cursor.fetchone()))
            connection.commit()
        return results

    def list_library_tracks(self, only_favorited: bool = False) -> dict:
        """
        Returns all tracks in a dict, with the key being the songs ID.
        """
        with sqlite3.connect(str(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            if only_favorited:
                cursor.execute("""
                    SELECT * FROM tracks
                    WHERE favorite = 1
                    ORDER BY artist,
                    album,
                    CAST(discnumber AS INTEGER),
                    CAST(tracknumber AS INTEGER)
                """)
            else:
                cursor.execute("""
                    SELECT * FROM tracks
                    ORDER BY artist,
                    album,
                    CAST(discnumber AS INTEGER),
                    CAST(tracknumber AS INTEGER)
                """)
            results = cursor.fetchall()
        track_export = {}
        for i, result in enumerate(results):
            track = Track(result)
            track_export[track.id] = track
        return track_export

    def list_library_albums(self) -> list[Album]:
        """
        Returns a list of albums
        """
        with sqlite3.connect(str(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            response = connection.execute("""
            SELECT album, albumartist
            FROM tracks
            GROUP BY album, albumartist
            ORDER BY albumartist COLLATE NOCASE ASC, album COLLATE NOCASE ASC
            """).fetchall()

        albums = []
        for album in response:
            albums.append(Album(album))

        return albums

    def list_library_artists(self, album_artist=False) -> list[str]:
        """Returns a list of artists. Album artist supported with the arg above."""
        with sqlite3.connect(str(self.db_path)) as connection:
            col = "albumartist" if album_artist else "artist"
            response = connection.execute(f"""
            SELECT {col}
            FROM tracks
            GROUP BY {col}
            ORDER BY {col} COLLATE NOCASE ASC
            """).fetchall()

        artists = []
        for artist in response:
            artists.append(artist[0])

        return response

    def list_playlists(self) -> list[Playlist]:
        with sqlite3.connect(str(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            response = connection.execute("SELECT * FROM playlists").fetchall()
            output = []
            for playlist in response:
                output.append(self.get_playlist(playlist["id"]))
            return output

    def favorite(self, term: str) -> list[Track]:
        """
        Lets a user favorite a track by title or id if search starts with id:
        """

        tracks = self.search(term)
        results = []
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            for track in tracks:
                cursor.execute(
                    "UPDATE tracks SET favorite = 1 - favorite WHERE id = ?",
                    (track.id,),
                )
                cursor.execute("SELECT * FROM tracks WHERE id = ?", (track.id,))
                results.append(Track(cursor.fetchone()))
            connection.commit()
        return results

    def get_playlist(
        self, id: int | None = None, title: str | None = None
    ) -> Playlist | None:
        """Returns a playlist object from a playlist id"""
        with sqlite3.connect(str(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            if id is not None:
                response = connection.execute(
                    "SELECT * FROM playlists WHERE id=?", (id,)
                ).fetchone()
            elif title is not None:
                response = connection.execute(
                    "SELECT * FROM playlists WHERE title=?", (title,)
                ).fetchone()
            else:
                response = None

            if response:
                playlist = Playlist(
                    response["title"],
                    description=response["description"],
                    tracks=self.get_playlist_tracks(response["id"]),
                )
                return playlist
            else:
                return None

    def get_playlist_tracks(self, playlist_id: int) -> list[Track]:
        """Returns a list of tracks in a playlist, in order"""
        with sqlite3.connect(str(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT tracks.*
                FROM tracks
                JOIN playlist_tracks ON tracks.id = playlist_tracks.track_id
                WHERE playlist_tracks.playlist_id = ?
                ORDER BY playlist_tracks.position
            """,
                (playlist_id,),
            )
            return [Track(row) for row in cursor.fetchall()]

    def create_playlist(self, title: str, description: str = "") -> Playlist | None:
        """Creates a playlist, returns the playlist"""
        with sqlite3.connect(str(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row

            # Checks if playlist already exists, if not creates it.
            existing = connection.execute(
                "SELECT * FROM playlists WHERE title=?", (title,)
            ).fetchone()
            if not existing:
                connection.execute(
                    """
                INSERT INTO playlists
                (title,description)
                VALUES (:title,:description)
                """,
                    (
                        title,
                        description,
                    ),
                )
                connection.commit()

            # Fetches the playlist from DB, and returns it
            response = connection.execute(
                "SELECT * FROM playlists WHERE title=?", (title,)
            ).fetchone()

            return self.get_playlist(id=response["id"])
