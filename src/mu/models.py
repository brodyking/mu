"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""


class Track:
    def __init__(self, response: dict):
        """
        Creates a track object from SQLite response
        """
        self.id: int = response["id"]
        self.favorite: bool = bool(response["favorite"])
        self.title: str = response["title"]
        self.artist: str = response["artist"]
        self.album: str = response["album"]
        self.plays: int = response["plays"]
        self.time: str = response["time"]
        self.dateadded: str = response["dateadded"]
        self.tracknumber: int = response["tracknumber"]
        self.albumartist: str = response["albumartist"]
        self.discnumber: int = response["discnumber"]
        self.genre: str = response["genre"]
        self.date: str = response["date"]
        self.filepath: str = response["filepath"]
        self.filename: str = response["filename"]
        self.albumart: str = response["albumart"]

    def get_time_ms(self) -> int:
        minutes, seconds = map(int, self.time.split(":"))
        return (minutes * 60 * 1000) + (seconds * 1000)

    def get_dict(self) -> dict:
        return {
            "id": self.id,
            "favorite": self.favorite,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "plays": self.plays,
            "time": self.time,
            "dateadded": self.dateadded,
            "tracknumber": self.tracknumber,
            "albumartist": self.albumartist,
            "discnumber": self.discnumber,
            "genre": self.genre,
            "date": self.date,
            "filepath": self.filepath,
            "filename": self.filename,
            "albumart": self.albumart,
        }


class Album:
    def __init__(self, title: str, albumartist: str, tracks: list[Track]):
        """
        Creates a album object from SQLite response
        """
        self.title = title
        self.albumartist = albumartist
        self.tracks = tracks

    def get_dict(self) -> dict:
        return {
            "title": self.title,
            "albumartist": self.albumartist,
        }


class Playlist:
    def __init__(
        self,
        id: int,
        title: str,
        description: str = "",
        tracks: list[Track] | None = None,
    ):
        self.id = id
        self.title = title
        self.description = description if description is not None else ""
        self.tracks = tracks if tracks else []

    def get_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "tracks": self.tracks,
        }


class Artist:
    def __init__(self, name: str, tracks: list[Track]) -> None:
        self.name = name
        self.tracks = tracks

    def get_dict(self) -> dict:
        return {"name": self.name, "tracks": self.tracks}
