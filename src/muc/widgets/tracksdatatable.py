"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import random
from typing import Literal, override

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Input, Static

from mu.api import Api
from mu.models import Track
from muc.widgets.playlistsdatatable import PlaylistsDataTable
from muc.widgets.popups import BindsDataTablePopup, Popup
from muc.widgets.vimdatatable import VimDataTable


class SortTracksPopup(BindsDataTablePopup):
    BINDINGS = [
        ("A", "dismiss_msg('A')", "Artist"),
        ("a", "dismiss_msg('a')", "Album"),
        ("D", "dismiss_msg('D')", "Date"),
        ("d", "dismiss_msg('d')", "Date Added"),
        ("g", "dismiss_msg('g')", "Genre"),
        ("i", "dismiss_msg('i')", "Id"),
        ("p", "dismiss_msg('p')", "Plays"),
        ("s", "dismiss_msg('s')", "Shuffle"),
        ("t", "dismiss_msg('t')", "Title"),
        ("T", "dismiss_msg('T')", "Time"),
        ("r", "dismiss_msg('r')", "Reset"),
        ("esc", "dismiss_msg('esc')", "Cancel"),
    ]

    def __init__(self, *args, **kwargs) -> None:
        binds = {
            "A": "Sort by Artist",
            "a": "Sort by Album",
            "D": "Sort by Date",
            "d": "Sort by Date Added",
            "g": "Sort by Genre",
            "i": "Sort by Id",
            "p": "Sort by Plays",
            "s": "Sort by Shuffle",
            "t": "Sort by Title",
            "T": "Sort by Time",
            "r": "Reset",
            "esc": "Cancel",
        }
        super().__init__("Sort", binds, *args, **kwargs)


class AddToPlaylistPopup(Popup):
    class AppendTrackToPlaylist(Message):
        def __init__(self, tid: int, pid: int, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.tid = tid
            self.pid = pid

    def __init__(self, api: Api, tid: int, *args, **kwargs) -> None:
        super().__init__("Add to playlist", *args, **kwargs)
        self.api = api
        self.tid = tid

        self.main_table = PlaylistsDataTable(self.api)

    def compose(self) -> ComposeResult:
        with self.content:
            yield self.main_table

    @on(PlaylistsDataTable.PlaylistClicked)
    def playlist_selected(self, event: PlaylistsDataTable.PlaylistClicked) -> None:
        self.post_message(self.AppendTrackToPlaylist(self.tid, event.playlist.id))
        self.dismiss()


class TrackOptionsPopup(BindsDataTablePopup):
    BINDINGS = [
        ("l", "dismiss_msg('l')", "Queue Last"),
        ("n", "dismiss_msg('n')", "Queue Next"),
        ("p", "dismiss_msg('p')", "Add to Playlist"),
        ("esc", "dismiss_msg('esc')", "Cancel"),
    ]

    class QueueTrack(Message):
        def __init__(self, tid: int, queue_next: bool, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.tid = tid
            self.queue_next = queue_next

    def __init__(self, api: Api, tid: int, *args, **kwargs) -> None:

        binds = {
            "l": "Queue Last",
            "n": "Queue Next",
            "p": "Add to Playlist",
            "esc": "Cancel",
        }

        super().__init__("Track Options", binds, *args, **kwargs)
        self.main_table = VimDataTable(show_inspect=False, cursor_type="row")
        self.api = api
        self.tid = tid

    def compose(self) -> ComposeResult:
        with self.content:
            yield self.main_table

    @override
    def action_dismiss_msg(self, bind: str):
        match bind:
            case "l":
                self.post_message(self.QueueTrack(self.tid, False))
            case "n":
                self.post_message(self.QueueTrack(self.tid, True))
            case "p":
                self.dismiss()
                self.app.push_screen(AddToPlaylistPopup(self.api, self.tid))
                return
        super().action_dismiss_msg(bind)


class TracksDataTable(Static):
    class TrackClicked(Message):
        def __init__(self, tids: list[int], pos: int, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.tids = tids
            self.pos = pos

    class FavoriteTrack(Message):
        def __init__(self, tid: int, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.tid = tid

    BINDINGS = [
        ("/", "focus_search", "Search"),
        ("comma", "open_sort", "Sort"),
        (".", "open_options", "Options"),
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

    def __init__(
        self,
        api: Api,
        show_sort: bool = True,
        only_favorites: bool = False,
    ):
        super().__init__()

        self.api = api
        self.only_favorites = only_favorites

        self.full_rows: list = []
        self.show_sort = show_sort

        self._sort_col: (
            Literal[
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
            ]
            | None
        ) = None
        self._sort_desc: bool = False

        self.search = Input(placeholder="Filter tracks (/)", compact=True, id="search")
        self.main_table = VimDataTable(cursor_type="row", id="tracks-main-table")

    def compose(self) -> ComposeResult:
        with Vertical():
            yield self.search
            yield self.main_table

    def action_open_sort(self) -> None:
        if self.show_sort:
            self.app.push_screen(SortTracksPopup(), callback=self.sort)  # type:ignore

    def action_open_options(self) -> None:
        row_index = self.main_table.cursor_row
        row_dict = self.main_table.export_row_as_dict(row_index)
        tid = int(row_dict["id"]) if "id" in row_dict else None
        if tid:
            popup = TrackOptionsPopup(self.api, tid)
            self.app.push_screen(popup)  # type:ignore

    def action_focus_search(self) -> None:
        self.search.focus()

    @on(Input.Submitted)
    def input_submitted(self, event: Input.Submitted) -> None:
        self.populate(event.value)
        self.redraw_rows()
        self.main_table.focus()

    @on(VimDataTable.RowSelected)
    def start_queue(self, event: VimDataTable.RowSelected) -> None:
        tids = [row[0] for row in self.full_rows]
        self.post_message(self.TrackClicked(tids, event.cursor_row))

    def action_favorite_track(self) -> None:
        """
        Toggles a tracks favorite icon
        """
        try:
            row_index: int = self.main_table.cursor_row
            row: dict = self.main_table.export_row_as_dict(row_index)
            self.post_message(self.FavoriteTrack(int(row["id"])))
            self.main_table.update_cell(
                str(row_index), "favorite", " " if row["favorite"] == "󰋑" else "󰋑"
            )
            self.populate()
        except Exception as e:
            self.app.notify(
                f"Couldn't favorite: {e}",
                severity="error",
            )

    def sort(
        self,
        bind: Literal[
            "A",
            "a",
            "D",
            "d",
            "g",
            "i",
            "p",
            "s",
            "t",
            "T",
            "r",
            "esc",
        ],
    ):

        bind_to_method = {
            "A": "artist",
            "a": "album",
            "D": "date",
            "d": "dateadded",
            "i": "id",
            "p": "plays",
            "g": "genre",
            "t": "title",
            "T": "time",
            "r": "reset",
            "s": "shuffle",
            "esc": "cancel",
        }

        """Callback for the sort popup."""
        if bind in (None, "esc"):
            return

        method = bind_to_method[bind]

        if method == "reset":
            self._sort_col, self._sort_desc = None, False
            self.populate(self.search.value)
            self.redraw_rows()
            return

        if method == "shuffle":
            random.shuffle(self.full_rows)  # session state, stays in memory
            self.redraw_rows()
            return

        # column sort: toggle direction only when re-selecting the same column
        self._sort_desc = not self._sort_desc if self._sort_col == method else False
        self._sort_col = method  # type:ignore
        self.populate(self.search.value)  # re-queries the DB in the new order
        self.redraw_rows()

    def redraw_rows(self) -> None:
        self.main_table.clear()
        for i, row in enumerate(self.full_rows):
            self.main_table.add_row(*row, key=str(i))

    def populate(
        self,
        tracks_term: str | None = None,
    ) -> None:
        """
        Clears and repopulates the table with tracks. Calls the database
        each time this is called. Also supports search queries with standard
        mu search syntax. If no prefix is given, it searches artist, albumartist,
        album, and title
        """

        self.full_rows = []

        if tracks_term and ":" not in tracks_term and "=" not in tracks_term:
            tracks_term = (
                f'artist:"{tracks_term}",'
                f'albumartist:"{tracks_term}",'
                f'album:"{tracks_term}",'
                f'title:"{tracks_term}"'
            )

        try:
            tracks: dict[int, Track] = self.api.get_tracks(
                tracks_term,
                only_favorited=self.only_favorites,
                order_by=self._sort_col,
                descending=self._sort_desc,
            )
        except ValueError as e:
            self.app.notify(str(e), severity="error")
            return

        for tid in tracks:
            track = tracks[tid]
            favorite = "󰋑" if track.favorite else " "

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
        self.populate(self.search.value)
        self.redraw_rows()
        self.main_table.focus()

    def on_hide(self) -> None:
        self.main_table.clear()
