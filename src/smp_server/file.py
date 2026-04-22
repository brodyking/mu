from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen import MutagenError
from pathlib import Path
import hashlib


class File:
    @staticmethod
    def read_metadata(filepath: Path) -> dict:
        '''
            Reads the metadata for the file and returns all the data as a dict.
            Album art is stored from extract_album_art(), and the key is set to the file path.
        '''
        def get(tags, key):
            try:
                return tags[key][0]
            except (KeyError, IndexError):
                return None

        try:
            tags = EasyID3(filepath)
        except MutagenError:
            tags = {}

        return {
            "filepath": str(filepath),
            "filename": filepath.name,
            "title": get(tags, "title"),
            "artist": get(tags, "artist"),
            "album": get(tags, "album"),
            "albumartist": get(tags, "albumartist"),
            "tracknumber": get(tags, "tracknumber"),
            "discnumber": get(tags, "discnumber"),
            "date": get(tags, "date"),
            "genre": get(tags, "genre"),
            "albumart": File.extract_album_art(filepath),
        }

    @staticmethod
    def extract_album_art(filepath: Path) -> str | None:
        '''
        Extracts album art from a song file, and stores it in Scarlett/AlbumArt/.
        All images are hashed and stored with the hash as the filename.
        This prevents duplicates for same album covers.

        It then returns the file path
        
        '''
        try:
            tags = ID3(filepath)
        except Exception:
            return None

        for tag in tags.values():
            if isinstance(tag, APIC):
                art_hash = hashlib.md5(tag.data).hexdigest()
                ext = "jpg" if tag.mime == "image/jpeg" else "png"
                art_path = (
                    Path.home()
                    / "Music"
                    / "Scarlett"
                    / "AlbumArt"
                    / f"{art_hash}.{ext}"
                )

                if not art_path.exists():
                    art_path.write_bytes(tag.data)
                return str(art_path)

        return None
