import sqlite3
from pathlib import Path
from ms.file import File
from ms.util import Util
import shutil
import json

class Database:

    def __init__(self,**kwargs):
        """
           Creates a new Database object.  
        """

        # Sets the file paths for db_path, source_path, and albumart_path
        self.db_path = Path.home() / "Music" / "ms" / "ms.db" if "db_path" not in kwargs else kwargs.get("db_path") 
        self.source_path = Path.home() / "Music" / "ms" / "source" if "source_folder_path" not in kwargs else kwargs.get("source_path") 
        self.albumart_path = Path.home() / "Music" / "ms" / "albumart" if "source_folder_path" not in kwargs else kwargs.get("albumart_path") 

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
            connection = sqlite3.connect(self.db_path)
            connection.execute('''
            CREATE TABLE IF NOT EXISTS "tracks" (
            	"id"	INTEGER NOT NULL UNIQUE,
            	"favorite" INT DEFAULT 0,
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

    def reset_db(self, skip_confirmation=False):
        if skip_confirmation or Util.PromptBool("Are you sure you want to erase the database file? This action cannot be undone."):
            connection = sqlite3.connect(self.db_path)
            connection.execute("DELETE FROM tracks;")
            connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'tracks';")
            connection.commit();
            connection.close();
            Util.Print('Database has been reset. Your files are still in ~/ms/source/. Type "ms scan" to rebuild.')

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

    def scan_folder(self,path) -> None:
        """
           Scans the path for music files.
           Each file is stored in the DB and has its album art hashed/saved. 
        """
        connection = sqlite3.connect(self.db_path)

        mp3s = list(path.rglob("*.mp3"))

        for i, filepath in enumerate(mp3s,1):
            try:
                metadata = File.read_metadata(filepath)
                self.upsert_track(connection,metadata)
                Util.Print(f"{filepath.name}",count=[i+1,len(mp3s)])
            except Exception as e:
                Util.Print(f"{filepath.name}\n{e}",count=[i+1,len(mp3s)],ok=False)

        connection.commit()
        connection.close()

    def scan_source_folder(self):
        """
           Scans the ms/source/ folder for music files.
           Each file is stored in the DB and has its album art hashed/saved. 
        """
        self.scan_folder(self.source_path)

    def copy_file(self,path: Path) -> dict:
        """
           Copies the file, and returns the new metadata of the file. 
        """
        metadata = File.read_metadata(path)
        
        newpath = Path(Path.home() / self.source_path / metadata["artist"] / metadata["album"] )
        newpath.mkdir(exist_ok=True,parents=True)
        shutil.copy(path,newpath)

        metadata["filepath"] = str(newpath / metadata["filename"])

        return metadata
         
    def import_media(self,path) -> None:
        """
            Copies the file or files (if dir) to ~/ms/source, upserts metadata to the database.
        """
        path = Path(path).resolve()

        if (path.is_dir()):
            mp3s = list(path.rglob("*.mp3"))
        else:
            mp3s = [path]

        connection = sqlite3.connect(self.db_path)
        for i, filepath in enumerate(mp3s,1):
            try:
                metadata = self.copy_file(filepath)
                self.upsert_track(connection,metadata)
                Util.Print(f"{filepath.name}",count=[i+1,len(mp3s)])
            except Exception as e:
                Util.Print(f"{filepath.name}\n{e}",count=[i+1,len(mp3s)],ok=False)

        connection.commit()
        connection.close()

    def search(self,term: str,export_json=False) -> None:
        """
            Searches the database for tracks.
        """

        formatted_search = f"%{term}%"

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM tracks
            WHERE title LIKE ?
            OR artist LIKE ?
            OR albumartist LIKE ?
            OR album LIKE ?
        """,(formatted_search,formatted_search,formatted_search,formatted_search))

        results = cursor.fetchall()

        if export_json:
            print(json.dumps(results))
        else:
            for i, result in enumerate(results):
                Util.Print("",track=result,count=[i+1,len(results)])

    def list_library(self,export_json: bool=False,favorited: bool=False) -> None:
        """
            Lists all of the tracks in the database, or just fav ones
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        if favorited:
            cursor.execute("SELECT * FROM tracks WHERE favorite = 1 ORDER BY artist")
        else:
            cursor.execute("SELECT * FROM tracks ORDER BY artist")
        results = cursor.fetchall()

        if export_json:
            print(json.dumps(results))
        else:
            for i, result in enumerate(results):
                Util.Print("",track=result,count=[i+1,len(results)])

    def favorite_track(self,term: str) -> None:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        if term.isdigit():
            # If it is an integer, it looks for the track id.
            cursor.execute("""
                UPDATE tracks
                SET favorite = 1 - favorite
                WHERE id=:id""",{'id': term})

            connection.commit()

            cursor.execute("""
                SELECT *  FROM tracks
                WHERE id = :id
                """,{'id': term})
        else:
            # If it is an integer, it looks for the track id.
            cursor.execute("""
                UPDATE tracks
                SET favorite = 1 - favorite
                WHERE title LIKE :title""",{'title': term})

            connection.commit()

            cursor.execute("""
                SELECT *  FROM tracks
                WHERE title LIKE :title
                """,{'title': term})
        result=cursor.fetchone()
        if result is None:
            Util.Print(f"{term} could not be found",ok=False)
        else:
            Util.Print("",track=result)
        connection.close()
