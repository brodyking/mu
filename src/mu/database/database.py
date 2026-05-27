import sqlite3
import shutil
from pathlib import Path

from mu.database.file import File
from mu.database.track import Track
from mu.util import Interface

class Database:

    DATABASE_VERSION = 1

    def __init__(self,**kwargs):
        """
           Creates a new Database object.  
        """

        # Sets the file paths for db_path, source_path, and albumart_path
        self.db_path = Path(Path.home() / "Music" / "mu" / "mu.db") if "db_path" not in kwargs else Path(str(kwargs.get("db_path"))) 
        self.source_path = Path(Path.home() / "Music" / "mu" / "source") if "source_path" not in kwargs else Path(str(kwargs.get("source_path")))
        self.albumart_path = Path(Path.home() / "Music" / "mu" / "albumart") if "albumart_path" not in kwargs else Path(str(kwargs.get("albumart_path")))

        # Validates that the locations exist and have the necessary files.
        self.validate_library()

    def validate_library(self,database_folder=True,source_folder=True,albumart_folder=True):
        """
           By default, checks to ensure the database, source_folder, and albumart_folder exist.
           If they do not, they are created.
        """
        def check_db() -> None:
            """
                Checks if database file exists. If it dosen't, it creates it. 
            """

            # Creates blank table if file dosen't exist
            with sqlite3.connect(str(self.db_path)) as connection:

                current_version = connection.execute("PRAGMA user_version").fetchone()[0]
                
                if current_version != self.DATABASE_VERSION and current_version != 0:
                    Interface.print(f"Database version is outdated or invalid.\nDatabase file version:\t{current_version}\nClient version:\t\t{self.DATABASE_VERSION}\nTo fix this, downgrade to a previous version of mu or migrate manually.",ok=False)
                    exit()

                connection.execute('''
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
                ''')
                connection.execute(f"PRAGMA user_version = {self.DATABASE_VERSION}")
                connection.commit()
        
        if source_folder:
            self.source_path.mkdir(parents=True,exist_ok=True)
        if albumart_folder:
            self.albumart_path.mkdir(parents=True,exist_ok=True)                    
        if database_folder:
            check_db()

    def reset_db(self, skip_confirmation=False) -> None:
        """
           Deletes all tracks from database. Keeps files.
           skip_confirmation bypasses the prompt before deletion. 
        """
        if skip_confirmation or Interface.promptBool("Are you sure you want to erase the database file? This action cannot be undone."):
            with sqlite3.connect(str(self.db_path)) as connection:
                connection.execute("DELETE FROM tracks;")
                connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'tracks';")
                connection.commit();
            Interface.print('Database has been reset. Your files are still in ~/mu/source/. Type "mu scan" to rebuild.')

    def upsert_track(self,connection,metadata:dict) -> None:
        """
           Puts all song metadata along with album art and file location into the database.
           If the filepath already exists, then it just updates the metadata instead of reinserting.
        """
        existing = connection.execute(
            "SELECT id FROM tracks WHERE filepath = ?", (metadata["filepath"],)
        ).fetchone()

        if existing:
            connection.execute("""
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
            """, metadata)
        else:
            connection.execute("""
                INSERT INTO tracks (
                   title, artist, album, time, dateadded, tracknumber, albumartist, discnumber, genre, date, filepath, filename, albumart
                ) VALUES (
                   :title, :artist, :album, :time, :dateadded, :tracknumber, :albumartist, :discnumber, :genre, :date, :filepath, :filename, :albumart
                )
            """, metadata)

        connection.commit()

    def upsert_track_once(self,metadata:dict) -> None:
        with sqlite3.connect(str(self.db_path)) as connection:
            self.upsert_track(connection,metadata)

    def scan_folder(self,path) -> None:
        """
           Scans the path for music files.
           Each file is stored in the DB and has its album art hashed/saved. 
        """
        with sqlite3.connect(str(self.db_path)) as connection:
            mp3s = list(path.rglob("*.mp3"))

            for i, filepath in enumerate(mp3s,1):
                try:
                    metadata = File.read_metadata(filepath,self.albumart_path) # Gets dict of files metadata
                    self.upsert_track(connection,metadata) # Updates the track
                    Interface.print(f"{filepath.name}",count=[i,len(mp3s)])
                except Exception as e:
                    Interface.print(f"{filepath.name}\n{e}",count=[i,len(mp3s)],ok=False)

            connection.commit()

    def scan_source_folder(self):
        """
           Scans the mu/source/ folder for music files.
           Each file is stored in the DB and has its album art hashed/saved. 
        """
        self.scan_folder(self.source_path)

    def copy_file(self,path: Path) -> dict:
        """
           Copies the file, and returns the new metadata of the file. 
        """
        metadata = File.read_metadata(path,self.albumart_path)

        newpath = Path(self.source_path / metadata["artist"] / metadata["album"])
        newpath.mkdir(exist_ok=True,parents=True)
        shutil.copy(path,newpath)

        metadata["filepath"] = str(Path(newpath / metadata["filename"]))
    
        return metadata
         
    def import_media(self,path,console_out:bool=True) -> None:
        """Copies the file or files (if dir) to ~/mu/source, upserts metadata to the database."""
        path = Path(path).resolve()

        if (path.is_dir()):
            mp3s = list(path.rglob("*.mp3"))
        else:
            mp3s = [path]

        with sqlite3.connect(str(self.db_path)) as connection:
            for i, filepath in enumerate(mp3s,1):
                try:
                    metadata = self.copy_file(filepath)
                    self.upsert_track(connection,metadata)
                    if console_out: Interface.print(f"{filepath.name}",count=[i,len(mp3s)])
                except Exception as e:
                    Interface.print(f"{filepath.name}\n{e}",count=[i,len(mp3s)],ok=False)

            connection.commit()

    def search(self, term: str,console_out:bool=True) -> list:
        """
            Searches the database for tracks with prefix support. If no prefix is given, it will search by id.
            Returns a list of tracks.
        """

        # All col's in the database
        prefixes = [
            "id", "favorite","title", "artist", "album", "plays", "time", "dateadded", "tracknumber", "albumartist", "discnumber", "genre", "date", "filepath", "filename", "albumart"
        ]

        # Finds the target column if user is using a prefix.
        target_column = term.split(":",1)[0] if term.split(":",1)[0] in prefixes else None
        if target_column is None:
            Interface.print("The search query is missing a prefix. Please specify how you are searching by typing the prefix followed by a colon. Ex: title:,artist:",ok=False)
            raise ValueError("The search query is missing a prefix. Please specify how you are searching by typing the prefix followed by a colon. Ex: title:,artist:")
        with sqlite3.connect(str(self.db_path)) as connection:
            cursor = connection.cursor()

            if target_column:
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

            else:
                # Global search
                fmt = f"%{term}%"
                cursor.execute("""
                    SELECT * FROM tracks 
                    WHERE title LIKE ? OR artist LIKE ? OR albumartist LIKE ? OR album LIKE ?
                """, (fmt, fmt, fmt, fmt))

            results = cursor.fetchall()
            export = []
            for i, result in enumerate(results):
                if console_out: Interface.print("", track=Track(result), count=[i + 1, len(results)])
                export.append(Track(result))
            return export

    def increment_play_count(self, term:str,amount:int=1,console_out:bool=True) -> list:
        """Increment track(s) play counts by either 1 or a custom amount"""
        tracks: list[Track] = self.search(f"{term}",console_out=False)
        results = []
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            for track in tracks:
                cursor.execute("UPDATE tracks SET plays = ? WHERE id = ?",(track.plays + amount,track.id))
                cursor.execute("SELECT * FROM tracks WHERE id = ?",(track.id,))
                results.append(cursor.fetchone())
            connection.commit()
        if console_out:
            for result in results:
                if result is not None: Interface.print("",track=Track(result))
        return results

    def list_library(self,only_favorited: bool=False,console_out:bool=True) -> dict:
        """
            Returns all tracks in a dict, with the key being the songs ID.
        """
        with sqlite3.connect(str(self.db_path)) as connection:
            cursor = connection.cursor()
            if only_favorited:
                cursor.execute("SELECT * FROM tracks WHERE favorite = 1 ORDER BY artist")
            else:
                cursor.execute("SELECT * FROM tracks ORDER BY artist")
            results = cursor.fetchall()
        track_export = {}
        for i, result in enumerate(results):
            track = Track(result)
            track_export[track.id] = track
            if console_out: Interface.print("",track=track,count=[i+1,len(results)])
        return track_export

    def favorite(self,term: str,console_out:bool=True) -> list:
        """
          Lets a user favorite a track by title or id if search starts with id:  
        """

        tracks = self.search(term,console_out=False)
        results = []
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            for track in tracks:
                cursor.execute("UPDATE tracks SET favorite = 1 - favorite WHERE id = ?", (track.id,))
                cursor.execute("SELECT * FROM tracks WHERE id = ?", (track.id,))
                results.append(cursor.fetchone())
            connection.commit()
        if console_out:
            for i, result in enumerate(results):
                if result is not None: Interface.print("", track=Track(result), count=[i+1,len(results)])
        return results

