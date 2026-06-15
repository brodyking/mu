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
        self.id = response["id"]
        self.favorite = bool(response["favorite"])
        self.title = response["title"]
        self.artist = response["artist"]
        self.album = response["album"]
        self.plays = response["plays"]
        self.time = response["time"]
        self.dateadded = response["dateadded"]
        self.tracknumber = response["tracknumber"]
        self.albumartist = response["albumartist"]
        self.discnumber = response["discnumber"]
        self.genre = response["genre"]
        self.date = response["date"]
        self.filepath = response["filepath"]
        self.filename = response["filename"]
        self.albumart = response["albumart"]

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
