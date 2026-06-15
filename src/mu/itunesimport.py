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
from urllib.parse import unquote, urlparse

from mu.database import Database
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

    def parse_tracks(self, root) -> Iterator[tuple[dict, dict]]:
        """
        Yields a tuple of the plist track and the files metadata
        """
        top_dict = self.parse_plist_dict(root[0])
        tracks = top_dict.get("Tracks", {})

        for plist_id, plist_track in tracks.items():
            yield (plist_track, self.parse_track(plist_track))

    def upsert_tracks(self, connection) -> Iterator[Track]:
        for plist_track, metadata in self.parse_tracks(self.root):
            if "Date Added" in plist_track.keys():
                metadata["dateadded"] = plist_track["Date Added"]
            track = self.db.upsert_track(connection, metadata)
            if "Play Count" in plist_track.keys():
                track = self.db.increment_play_count(
                    f"id:{track.id}", plist_track["Play Count"], set=True
                )[0]
            self.ids[plist_track["Track ID"]] = track.id
            yield track

    def start(self) -> None:
        with sqlite3.connect(str(self.db.db_path)) as connection:
            for track in self.upsert_tracks(connection):
                Interface.print("iTunes Import >> Upsert ", track=track)
