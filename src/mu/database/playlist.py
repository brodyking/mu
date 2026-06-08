"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from mu.database.track import Track


class Playlist:
    def __init__(self, title: str, description: str = "", tracks: list[Track] = []):
        self.title = title
        self.description = description if description is not None else ""
        self.tracks = tracks
