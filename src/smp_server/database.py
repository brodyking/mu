import sqlite3
from pathlib import Path
from smp_server.file import File

class Database:

    def __init__(self):
        self.check_db()
        self.check_source_folder()

    def __str__(self):
        return "hi"

    def check_source_folder(self):
        """
            Checks if the source music folder exists. If it dosen't, it creates it.
        """
        source_folder_path = Path.home() / "Music" / "Scarlett" / "Source"
        source_folder_path.mkdir(parents=True,exist_ok=True)

        albumart_folder_path = Path.home() / "Music" / "Scarlett" / "AlbumArt"
        albumart_folder_path.mkdir(parents=True,exist_ok=True)
            
    def check_db(self):
        """
           Checks if database file exists. If it dosen't, it creates it. 
        """
        db_path = Path.home() / "Music" / "Scarlett" / "Scarlett.db"
        db_path.parent.mkdir(parents=True, exist_ok=True) # Creates directory if it dosen't exist
        # Creates blank table if file dosen't exist
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute('''
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
        db_path = Path.home() / "Music" / "Scarlett" / "Scarlett.db"
        source_folder = Path.home() / "Music" / "Scarlett" / "Source"

        connection = sqlite3.connect(db_path)

        mp3s = list(source_folder.rglob("*.mp3"))

        for i, filepath in enumerate(mp3s,1):
            try:
                metadata = File.read_metadata(filepath)
                self.upsert_track(connection,metadata)
                print(f"[{i}/{len(mp3s)}] ✓ {filepath.name}")
            except Exception as e:
                print(f"[{i}/{len(mp3s)}] ✗ {filepath.name}: {e}")

        connection.commit()
        connection.close()
