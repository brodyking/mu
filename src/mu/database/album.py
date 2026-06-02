"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""


class Album:
    def __init__(self, response: dict):
        """
        Creates a album object from SQLite response
        """
        self.title = response["album"]
        self.albumartist = response["albumartist"]

    def get_dict(self) -> dict:
        return {
            "title": self.title,
            "albumartist": self.albumartist,
        }
