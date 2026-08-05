"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import random
from typing import Literal

from textual import on
from textual.app import ComposeResult
from textual.widgets import Static

from mu.api import Api
from mu.models import Track
from muc.player import Player
from muc.widgets.vimdatatable import VimDataTable


class QueueDataTable(Static):
    BINDINGS = [
        ("f", "favorite_track", "Favorite"),
    ]

    COL_INDEXES: dict[str, int] = {
        "id": 0,
        "favorite": 1,
        "title": 2,
        "artist": 3,
        "album": 4,
        "plays": 5,
        "time": 6,
        "dateadded": 7,
        "tracknumber": 8,
        "albumartist": 9,
        "discnumber": 10,
        "genre": 11,
        "date": 12,
        "filepath": 13,
        "filename": 14,
        "albumart": 15,
    }

    def __init__(self, api: Api, player: Player):
        super().__init__()

        self.api: Api = api
        self.player: Player = player
        self.full_rows: list = []

        self.main_table = VimDataTable(cursor_type="row", id="tracks-main-table")

    def compose(self) -> ComposeResult:
        yield self.main_table

    @on(VimDataTable.RowSelected)
    def start_queue(self, event: VimDataTable.RowSelected) -> None:
        tids = [row[0] for row in self.full_rows]
        self.player.play_now(tids, event.cursor_row)
        self.populate()
        self.redraw_rows()

    def action_favorite_track(self) -> None:
        """
        Toggles a tracks favorite icon
        TODO: Make it not refresh all rows when updating
        """
        try:
            row_index: int = self.main_table.cursor_row
            tid: int = int(self.main_table.export_row_as_dict(row_index)["id"])
            track: Track = self.api.favorite_tracks(f"id={tid}")[tid]
            self.main_table.update_cell(
                str(tid), "favorite", "❤" if track.favorite else " "
            )
            self.populate()
        except Exception as e:
            self.app.notify(f"Couldn't favorite: {e}", severity="error", timeout=0.25)

    def sort(
        self,
        method: Literal[
            "artist",
            "album",
            "date",
            "dateadded",
            "id",
            "plays",
            "genre",
            "title",
            "time",
            "cancel",
            "shuffle",
            "reset",
        ],
    ):
        """Callback for the sort popup."""
        if method in (None, "cancel"):
            return

        if method == "reset":
            self._sort_col, self._sort_desc = None, False
            self.populate()
            self.redraw_rows()
            return

        if method == "shuffle":
            random.shuffle(self.full_rows)  # session state, stays in memory
            self.redraw_rows()
            return

        # column sort: toggle direction only when re-selecting the same column
        self._sort_desc = not self._sort_desc if self._sort_col == method else False
        self._sort_col = method
        self.populate()  # re-queries the DB in the new order
        self.redraw_rows()

    def redraw_rows(self) -> None:
        self.main_table.clear()
        for row in self.full_rows:
            self.main_table.add_row(*row, key=str(row[0]))

    def populate(self) -> None:
        """
        Clears and repopulates the table with tracks in the current queue.
        Calls the database from the QueueList each time this is called."""

        self.full_rows = []

        try:
            tracks: list[Track] = self.player.queue.get_queue()
        except ValueError as e:
            self.app.notify(str(e), severity="error")
            return

        for track in tracks:
            favorite = "❤" if track.favorite else " "

            row_tuple = (
                track.id,
                favorite,
                track.title,
                track.artist,
                track.album,
                track.plays,
                track.time,
                track.dateadded,
                track.tracknumber,
                track.albumartist,
                track.discnumber,
                track.genre,
                track.date,
                track.filepath,
                track.filename,
                track.albumart,
            )
            self.full_rows.append(row_tuple)

    def on_mount(self) -> None:
        table = self.main_table

        # Add the maximum width to your column metadata definition
        columns = [
            ("Id", "id", None),
            ("", "favorite", 2),
            ("Title", "title", 25),
            ("Artist", "artist", 15),
            ("Album", "album", 15),
            ("Plays", "plays", 5),
            ("Time", "time", 5),
            ("Date Added", "dateadded", 10),
            ("Track Number", "tracknumber", 5),
            ("Album Artist", "albumartist", 15),
            ("Disc Number", "discnumber", 3),
            ("Genre", "genre", 15),
            ("Date", "date", 15),
            ("File Path", "filepath", None),
            ("File Name", "filename", None),
            ("Album Art", "albumart", None),
        ]

        # Use the max_width argument in add_column
        for label, key, max_w in columns:
            table.add_column(label, key=key, width=max_w)

    def on_show(self) -> None:
        self.populate()
        self.redraw_rows()
        self.main_table.focus()

    def on_hide(self) -> None:
        self.main_table.clear()
