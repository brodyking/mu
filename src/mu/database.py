"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path


class Database:
    SCHEMA = 2
    SEARCHABLE: dict[str, set[str]] = {
        "playlists": {"id", "title", "description"},
        "tracks": {
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
        },
    }
    NUMERIC_SORT_COLS = {"id", "favorite", "plays", "tracknumber", "discnumber"}

    DEFAULT_TRACK_ORDER = """
        ORDER BY artist COLLATE NOCASE,
                album COLLATE NOCASE,
                CAST(discnumber AS INTEGER),
                CAST(tracknumber AS INTEGER)
    """

    def __init__(
        self,
        db_path: Path | None = None,
        source_path: Path | None = None,
        albumart_path: Path | None = None,
    ) -> None:
        """
        Creates a new database connection. If paths are left as none,
        they are set to the default location at ~/Music/mu/
        """

        self.db_path = (
            Path(Path.home() / "Music" / "mu" / "mu.db") if db_path is None else db_path
        )
        self.source_path = (
            Path(Path.home() / "Music" / "mu" / "source")
            if source_path is None
            else source_path
        )
        self.albumart_path = (
            Path(Path.home() / "Music" / "mu" / "albumart")
            if albumart_path is None
            else albumart_path
        )

        self.source_path.mkdir(parents=True, exist_ok=True)
        self.albumart_path.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._lock = threading.RLock()

        self.connection = sqlite3.connect(
            str(self.db_path), check_same_thread=False, isolation_level=None
        )
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA busy_timeout = 5000")

        try:
            self._validate_database_version()  # Check's the libraries SCHEMA
            self._create_database()  # Creates the database if it dosen't exist
        except BaseException:
            self.connection.close()
            raise

    @contextmanager
    def write(self):
        """
        Yields a connection
        """
        with self._lock:
            if self.connection.in_transaction:
                yield self.connection
                return

            self.connection.execute("BEGIN")
            try:
                yield self.connection
            except BaseException:
                self.connection.execute("ROLLBACK")
                raise
            else:
                self.connection.execute("COMMIT")

    def query(self, sql: str, params: tuple = ()) -> list:
        """
        Queries the database, returns rows.
        """
        with self._lock:
            return self.connection.execute(sql, params).fetchall()

    def close(self) -> None:
        with self._lock:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _validate_database_version(self) -> None:
        """
        Compares the database schema and the sqlite3 version. Raises RunetimeError
        """

        library_version = self.query("PRAGMA user_version")[0][0]

        if library_version != self.SCHEMA and library_version != 0:
            raise ValueError(
                f"Library version {self.SCHEMA} required, found {library_version}"
            )

        if sqlite3.sqlite_version_info < (3, 35):
            raise RuntimeError(f"SQLite 3.35+ required, found {sqlite3.sqlite_version}")

    def _create_database(self) -> None:
        """
        Creates tables if they are not found, sets the pragma version.
        """

        with self.write() as conn:
            # Create tracks table
            conn.execute("""
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
                    "filepath" TEXT UNIQUE,
                    "filename" TEXT,
                    "albumart" TEXT,
                    PRIMARY KEY("id" AUTOINCREMENT))
            """)
            # Create playlists table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS "playlists" (
                    "id" INTEGER NOT NULL UNIQUE,
                    "title" TEXT NOT NULL UNIQUE,
                    "description" TEXT,
                    PRIMARY KEY("id" AUTOINCREMENT)
                )
            """)
            # Create playlist_tracks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS "playlist_tracks" (
                    "playlist_id" INTEGER NOT NULL REFERENCES playlists(id),
                    "track_id"    INTEGER NOT NULL REFERENCES tracks(id),
                    "position"    INTEGER NOT NULL,
                    "date_added"  TEXT DEFAULT (datetime('now')),
                    PRIMARY KEY (playlist_id, track_id)
                );
            """)
            # Set SCHEMA
            conn.execute(f"PRAGMA user_version = {self.SCHEMA}")
