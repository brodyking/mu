"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import sqlite3
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from pathlib import Path
from posix import stat
from urllib.parse import unquote, urlparse

from mu.database import Database
from mu.playlist import Playlist
from mu.track import Track
from mu.util import Interface


class ITunesImport:
    def __init__(self, db: Database, filepath: Path | str):
        self.db, self.filepath = db, filepath
        self.ids = dict()  # iTunes track id -> mu track id
        self.tree = ET.parse(self.filepath)
        self.root = self.tree.getroot()

    @staticmethod
    def parse_plist_dict(dict_element):
        """Parse a plist <dict> element into a Python dict."""
        result = {}
        children = list(dict_element)
        for i in range(0, len(children) - 1, 2):
            key = children[i].text
            value_elem = children[i + 1]
            result[key] = ITunesImport.parse_plist_value(value_elem)
        return result

    @staticmethod
    def parse_plist_value(elem):
        """Parse a plist value element into a Python type."""
        tag = elem.tag
        if tag == "string":
            return elem.text
        elif tag == "integer":
            return int(elem.text)
        elif tag == "real":
            return float(elem.text)
        elif tag == "true":
            return True
        elif tag == "false":
            return False
        elif tag == "date":
            return elem.text  # keep as string, or parse with datetime if needed
        elif tag == "dict":
            return ITunesImport.parse_plist_dict(elem)
        elif tag == "array":
            return [ITunesImport.parse_plist_value(child) for child in elem]
        else:
            return elem.text

    @staticmethod
    def plist_url_to_path(url):
        parsed = urlparse(url)
        return Path(unquote(parsed.path))

    def parse_track(self, plist_track) -> dict:
        path = ITunesImport.plist_url_to_path(plist_track["Location"])
        metadata = self.db.copy_file(path)
        return metadata

    def parse_tracks(self) -> Iterator[tuple[dict, dict]]:
        """
        Yields a tuple of the plist track and the files metadata
        """
        top_dict = self.parse_plist_dict(self.root[0])
        tracks = top_dict.get("Tracks", {})

        for plist_id, plist_track in tracks.items():
            yield (plist_track, self.parse_track(plist_track))

    def parse_playlists(self) -> Iterator[dict]:
        """
        Yields a dict of the plist playlist
        """
        top_dict = self.parse_plist_dict(self.root[0])
        playlists = top_dict.get("Playlists", {})
        for playlist in playlists:
            mu_ids = []
            if "Playlist Items" in playlist.keys():
                for plist_track in playlist["Playlist Items"]:
                    plist_id = plist_track["Track ID"]
                    mu_ids.append(self.ids[plist_id])
            yield {
                "title": playlist["Name"],
                "description": playlist["Description"],
                "tracks": mu_ids,
            }

    def upsert_tracks(self, connection) -> Iterator[Track]:
        for plist_track, metadata in self.parse_tracks():
            keys = plist_track.keys()
            if "Date Added" in keys:
                metadata["dateadded"] = plist_track["Date Added"]
            track = self.db.upsert_track(connection, metadata)
            if "Play Count" in keys:
                track = self.db.increment_play_count(
                    f"id:{track.id}", plist_track["Play Count"], set=True
                )[0]
            if "Favorited" in keys or "Loved" in keys:
                track = self.db.favorite(f"id:{track.id}")[0]
            self.ids[plist_track["Track ID"]] = track.id
            yield track

    def upsert_playlists(self, connection) -> Iterator[Playlist]:
        for playlist in self.parse_playlists():
            mu_playlist = self.db.create_playlist(
                playlist["title"], description=playlist["description"]
            )
            if mu_playlist:
                statement = ""
                for mu_track_id in playlist["tracks"]:
                    statement += f"id:{mu_track_id}+"
                if statement:
                    self.db.append_playlist(f"id:{mu_playlist.id}", statement[:-1])
                yield self.db.get_playlist(f"id:{mu_playlist.id}")

    def start(self) -> None:
        with sqlite3.connect(str(self.db.db_path)) as connection:
            for track in self.upsert_tracks(connection):
                Interface.print("iTunes Import >> Upsert Track ", track=track)
            for playlist in self.upsert_playlists(connection):
                Interface.print("iTunes Import >> Upsert Playlist", playlist=playlist)
