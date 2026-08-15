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
from textual.containers import Vertical
from textual.coordinate import Coordinate
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import DataTable, Input, Static

from mu.api import Api
from mu.models import Track
from muc.player import Player
from muc.widgets.playlistsdatatable import PlaylistsDataTable
from muc.widgets.vimdatatable import VimDataTable


class SortTracksPopup(ModalScreen[str]):
    TABLE = [
        ("A", "Sort by Artist"),
        ("a", "Sort by Album"),
        ("D", "Sort by Date"),
        ("d", "Sort by Date Added"),
        ("g", "Sort by Genre"),
        ("i", "Sort by Id"),
        ("p", "Sort by Plays"),
        ("s", "Sort by Shuffle"),
        ("t", "Sort by Title"),
        ("T", "Sort by Time"),
        ("r", "Reset"),
        ("esc", "Cancel"),
    ]

    BINDINGS = [
        ("enter", "option_selected", "Select Option"),
        ("escape", "dismiss_msg('cancel')", "Close"),
        ("i", "dismiss_msg('id')", "Id"),
        ("T", "dismiss_msg('time')", "Time"),
        ("t", "dismiss_msg('title')", "Title"),
        ("A", "dismiss_msg('artist')", "Artist"),
        ("a", "dismiss_msg('album')", "Album"),
        ("p", "dismiss_msg('plays')", "Plays"),
        ("d", "dismiss_msg('dateadded')", "Dateadded"),
        ("g", "dismiss_msg('genre')", "Genre"),
        ("s", "dismiss_msg('shuffle')", "Shuffle"),
        ("D", "dismiss_msg('date')", "Date"),
        ("r", "dismiss_msg('reset')", "Reset"),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.main_table = VimDataTable(show_inspect=False, cursor_type="row")

    def compose(self) -> ComposeResult:
        yield self.main_table

    def on_mount(self) -> None:

        self.main_table.add_column("Bind", key="bind", width=4)
        self.main_table.add_column("Sorting Options", key="sorting-options", width=100)

        for row in self.TABLE:
            self.main_table.add_row(row[0], row[1])

    def action_dismiss_msg(self, message: str):
        self.dismiss(message)

    @on(DataTable.RowSelected)
    def action_option_selected(self, event: DataTable.RowSelected):
        row = event.cursor_row
        value = self.main_table.get_cell_at(Coordinate(row, 1))
        if value and "Sort by" in value:
            self.action_dismiss_msg(value[7:].lower().replace(" ", ""))
        else:
            self.action_dismiss_msg(value.lower())


class AddToPlaylistPopup(ModalScreen[str]):
    class AppendTrackToPlaylist(Message):
        def __init__(self, tid: int, pid: int, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.tid = tid
            self.pid = pid

    BINDINGS = [
        ("escape", "dismiss()", "Close"),
    ]

    def __init__(self, api: Api, tid: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.api = api
        self.tid = tid

        self.main_table = PlaylistsDataTable(self.api)

    def compose(self) -> ComposeResult:
        yield self.main_table

    @on(PlaylistsDataTable.PlaylistClicked)
    def playlist_selected(self, event: PlaylistsDataTable.PlaylistClicked) -> None:
        self.post_message(self.AppendTrackToPlaylist(self.tid, event.playlist.id))
        self.dismiss()


class AddToPopup(ModalScreen[str]):
    class QueueTrack(Message):
        def __init__(self, tid: int, queue_next: bool, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.tid = tid
            self.queue_next = queue_next

    TABLE = [
        ("l", "Queue Last"),
        ("n", "Queue Next"),
        ("p", "Add to Playlist"),
        ("esc", "Cancel"),
    ]

    BINDINGS = [
        ("enter", "option_selected", "Select Option"),
        ("escape", "dismiss()", "Close"),
        ("l", "queue_track(False)", "Queue Last"),
        ("n", "queue_track(True)", "Queue Next"),
        ("p", "add_track_to_playlist", "Add to Playlist"),
    ]

    def __init__(self, api: Api, tid: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.main_table = VimDataTable(show_inspect=False, cursor_type="row")
        self.api = api
        self.tid = tid

    def compose(self) -> ComposeResult:
        yield self.main_table

    def on_mount(self) -> None:

        self.main_table.add_column("Bind", key="bind", width=4)
        self.main_table.add_column("Add Options", key="add-options", width=100)

        for row in self.TABLE:
            self.main_table.add_row(row[0], row[1])

    @on(DataTable.RowSelected)
    def action_option_selected(self, event: DataTable.RowSelected):
        row = event.cursor_row
        value = self.main_table.get_cell_at(Coordinate(row, 1))
        match value:
            case "Queue Last":
                self.action_queue_track(False)
            case "Queue Next":
                self.action_queue_track(True)
            case "Add to Playlist":
                self.action_add_track_to_playlist()

    def action_queue_track(self, queue_next: bool) -> None:
        self.dismiss()
        self.post_message(self.QueueTrack(self.tid, queue_next))

    def action_add_track_to_playlist(self) -> None:
        self.dismiss()
        self.app.push_screen(AddToPlaylistPopup(self.api, self.tid))


class TracksDataTable(Static):
    class FavoriteTrack(Message):
        def __init__(self, tid: int, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.tid = tid

    BINDINGS = [
        ("/", "focus_search", "Search"),
        ("comma", "open_sort", "Sort"),
        (".", "open_addto", "Add to"),
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
        player: Player,
        show_filter: bool = True,
        only_favorites: bool = False,
    ):
        super().__init__()

        self.api = api
        self.player: Player = player
        self.only_favorites = only_favorites

        self.full_rows: list = []
        self.show_filter = show_filter

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
        if self.show_filter:
            self.app.push_screen(SortTracksPopup(), callback=self.sort)  # type:ignore

    def action_open_addto(self) -> None:
        row_index = self.main_table.cursor_row
        row_dict = self.main_table.export_row_as_dict(row_index)
        tid = int(row_dict["id"]) if "id" in row_dict else None
        if tid:
            popup = AddToPopup(self.api, tid)
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
        self.player.play_now(tids, event.cursor_row)

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
            self.populate(self.search.value)
            self.redraw_rows()
            return

        if method == "shuffle":
            random.shuffle(self.full_rows)  # session state, stays in memory
            self.redraw_rows()
            return

        # column sort: toggle direction only when re-selecting the same column
        self._sort_desc = not self._sort_desc if self._sort_col == method else False
        self._sort_col = method
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
                f"artist:{tracks_term},"
                f"albumartist:{tracks_term},"
                f"album:{tracks_term},"
                f"title:{tracks_term}"
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
