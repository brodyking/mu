from datetime import date
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from mutagen import MutagenError
from pathlib import Path
import hashlib

class File:
    
    @staticmethod
    def read_metadata(filepath: Path,albumart_path:Path) -> dict:
        """
            Reads the metadata for the file and returns all the data as a dict.
            Album art is stored from extract_album_art(), and the key is set to the file path.
        """
        def get(tags, key):
            try:
                return tags[key][0]
            except (KeyError, IndexError):
                return None

        try:
            audio = MP3(str(filepath))
            length = audio.info.length if (audio and audio.info) else 0
            time_mins, time_secs = divmod(int(length), 60)

            tags = EasyID3(filepath)
        except MutagenError:
            tags = {}

        return {
            "title": get(tags, "title"),
            "artist": get(tags, "artist"),
            "album": get(tags, "album"),
            "time": f"{time_mins}:{time_secs:02d}",
            "dateadded": date.today(),
            "filepath": str(filepath),
            "filename": filepath.name,
            "albumartist": get(tags, "albumartist"),
            "tracknumber": get(tags, "tracknumber"),
            "discnumber": get(tags, "discnumber"),
            "date": get(tags, "date"),
            "genre": get(tags, "genre"),
            "albumart": File.extract_album_art(filepath,albumart_path),
        }

    @staticmethod
    def extract_album_art(filepath: Path, albumart_path: Path) -> str | None:
        """
        Extracts album art from a song file and saves it to albumart_path.
        Images are deduplicated by storing them as <sha256hash>.<ext>.
        Returns the path to the saved image, or None if no art is found.
        """
        try:
            tags = ID3(filepath)
        except Exception:
            return None

        for tag in tags.values():
            if isinstance(tag, APIC):
                art_hash = hashlib.sha256(tag.data).hexdigest() # type: ignore
                ext = "jpg" if tag.mime == "image/jpeg" else "png" # type: ignore
                art_path = albumart_path / f"{art_hash}.{ext}"

                if not art_path.exists():
                    art_path.write_bytes(tag.data) # type: ignore

                return str(art_path)

        return None
