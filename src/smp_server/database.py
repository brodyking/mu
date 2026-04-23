import sqlite3
from pathlib import Path
from smp_server.file import File

class Database:

    def __init__(self,**kwargs):
        """
           Creates a new Database object.  
        """

        # Sets the file paths for db_path, source_path, and albumart_path
        self.db_path = Path.home() / "Music" / "Scarlett" / "Scarlett.db" if "db_path" not in kwargs else kwargs.get("db_path") 
        self.source_path = Path.home() / "Music" / "Scarlett" / "Source" if "source_folder_path" not in kwargs else kwargs.get("source_path") 
        self.albumart_path = Path.home() / "Music" / "Scarlett" / "AlbumArt" if "source_folder_path" not in kwargs else kwargs.get("albumart_path") 

        # Validates that the locations exist and have the necessary files.
        self.validate_library()

    def validate_library(self,database_folder=True,source_folder=True,albumart_folder=True):
        """
           By default, checks to ensure the database, source_folder, and albumart_folder exist.
           If they do not, they are created.
        """
        def check_db():
            """
                Checks if database file exists. If it dosen't, it creates it. 
            """
            # Creates blank table if file dosen't exist
            connection = sqlite3.connect(self.db_path)
            connection.execute('''
            CREATE TABLE IF NOT EXISTS "tracks" (
            	"id"	INTEGER NOT NULL UNIQUE,
            	"title"	TEXT,
            	"tracknumber"	INTEGER,
            	"artist"	TEXT,
            	"albumartist"	TEXT,
            	"album"	TEXT,
            	"discnumber"	INTEGER,
            	"genre"	TEXT,
            	"date"	TEXT,
            	"filepath" TEXT,
            	"filename" TEXT,
            	"albumart" TEXT,
            	PRIMARY KEY("id" AUTOINCREMENT)
            )
            ''')
            connection.commit()
            connection.close()           
        
        if source_folder:
            self.source_path.mkdir(parents=True,exist_ok=True)
        if albumart_folder:
            self.albumart_path.mkdir(parents=True,exist_ok=True)                    
        if database_folder:
            check_db()

    def upsert_track(self,connection,metadata:dict):
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
                    filepath, filename, title, artist, album, albumartist, tracknumber, discnumber, date, genre, albumart
                ) VALUES (
                    :filepath, :filename, :title, :artist, :album, :albumartist, :tracknumber, :discnumber, :date, :genre, :albumart
                )
            """, metadata)

    def scan_source_folder(self):
        """
           Scans the Scarlett/Source/ folder for music files.
           Each file is stored in the DB and has its album art hashed/saved. 
        """
        connection = sqlite3.connect(self.db_path)

        mp3s = list(self.source_path.rglob("*.mp3"))

        for i, filepath in enumerate(mp3s,1):
            try:
                metadata = File.read_metadata(filepath)
                self.upsert_track(connection,metadata)
                print(f"[{i}/{len(mp3s)}] ✓ {filepath.name}")
            except Exception as e:
                print(f"[{i}/{len(mp3s)}] ✗ {filepath.name}: {e}")

        connection.commit()
        connection.close()
