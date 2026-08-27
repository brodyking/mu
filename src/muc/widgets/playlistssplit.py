"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Label, Static

from mu.api import Api
from mu.models import Playlist, Track
from muc.player import Player
from muc.widgets.playlistsdatatable import PlaylistsDataTable
from muc.widgets.popups import ConfirmPopup
from muc.widgets.tracksdatatable import TrackOptionsPopup
from muc.widgets.vimdatatable import VimDataTable


class RemoveTrackFromPlaylistPopup(ConfirmPopup):
    class Submitted(ConfirmPopup.Submitted):
        def __init__(
            self, response: bool, tid: int = 0, pid: int = 0, *args, **kwargs
        ) -> None:
            super().__init__(response, *args, **kwargs)
            self.tid = tid
            self.pid = pid

    def __init__(self, tid: int, pid: int, *args, **kwargs) -> None:
        super().__init__(
            "Are you sure you want to remove this track?",
            title="Remove track?",
            subtitle="This cannot be undone!",
            *args,
            **kwargs,
        )
        self.tid = tid
        self.pid = pid

    async def action_submit(self, *args, **kwargs) -> None:
        await super().action_dismiss(message=self.Submitted(True, self.tid, self.pid))


class PlaylistTracksDataTable(Static):
    BINDINGS = [
        (".", "open_addto", "Add to"),
        ("f", "favorite_track", "Favorite"),
        ("d", "remove_track", "Remove"),
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
        playlist: Playlist | None,
    ):
        super().__init__()
        self.api = api
        self.player: Player = player
        self.playlist = playlist

        self.full_rows: list = []

        self.playlist_metadata = Label()
        self.main_table = VimDataTable(cursor_type="row", id="tracks-main-table")

    def compose(self) -> ComposeResult:
        with Vertical():
            yield self.playlist_metadata
            yield self.main_table

    def action_open_addto(self) -> None:
        row_index = self.main_table.cursor_row
        row_dict = self.main_table.export_row_as_dict(row_index)
        tid = int(row_dict["id"])
        if tid:
            popup = TrackOptionsPopup(self.api, tid)
            self.app.push_screen(popup)  # type:ignore

    @on(VimDataTable.RowSelected)
    def start_queue(self, event: VimDataTable.RowSelected) -> None:
        tids = [row[0] for row in self.full_rows]
        self.player.play_now(tids, event.cursor_row)

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
                str(row_index), "favorite", "󰋑" if track.favorite else " "
            )
            self.populate()
        except Exception as e:
            self.app.notify(f"Couldn't favorite: {e}", severity="error")

    def action_remove_track(self) -> None:
        try:
            row_index: int = self.main_table.cursor_row
            tid: int = int(self.main_table.export_row_as_dict(row_index)["id"])
            if self.playlist:
                self.app.push_screen(
                    RemoveTrackFromPlaylistPopup(tid, self.playlist.id)
                )
            else:
                self.app.notify("No playlist selected", severity="error")
        except Exception as e:
            self.app.notify(f"Couldn't favorite: {e}", severity="error")

    def redraw_rows(self) -> None:
        self.main_table.clear()
        for i, row in enumerate(self.full_rows):
            self.main_table.add_row(*row, key=str(i))

    def redraw_metadata(self) -> None:
        if self.playlist:
            self.playlist_metadata.update(
                f"[grey] #{self.playlist.id}[/]"
                f"[$success] 󱝟 {self.playlist.title}[/]"
                f" {self.playlist.description}"
                f"[$error] 󰈣 {len(self.playlist.tracks)}[/$error]"
            )

    def populate(
        self,
    ) -> None:
        """
        Clears and repopulates the table with tracks from the current playlist."""

        if not self.playlist:
            return

        self.full_rows = []

        for track in self.playlist.tracks:
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
        self.populate()
        self.redraw_rows()
        self.redraw_metadata()
        self.main_table.focus()

    def on_hide(self) -> None:
        self.main_table.clear()


class PlaylistsSplit(Static):
    BINDINGS = [
        ("ctrl+h", "focus_table(0)", "Focus Playlists"),
        ("ctrl+l", "focus_table(1)", "Focus Tracks"),
    ]

    def __init__(self, api: Api, player: Player, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        self.player = player
        self.api = api

        self.playlists_data_table = PlaylistsDataTable(self.api)
        self.tracks_data_table = PlaylistTracksDataTable(self.api, self.player, None)

    @on(PlaylistsDataTable.PlaylistClicked)
    def playlist_clicked(self, event: PlaylistsDataTable.PlaylistClicked):
        self.tracks_data_table.playlist = event.playlist
        self.tracks_data_table.populate()
        self.tracks_data_table.redraw_rows()
        self.tracks_data_table.redraw_metadata()
        self.tracks_data_table.main_table.focus()

    def action_focus_table(self, table: int):
        """Focuses different tables. 0: Playlists, 1: Playlist Tracks"""
        if table == 0:
            self.playlists_data_table.main_table.focus()
        else:
            self.tracks_data_table.main_table.focus()

    def compose(self):
        with Horizontal():
            yield self.playlists_data_table
            yield self.tracks_data_table
