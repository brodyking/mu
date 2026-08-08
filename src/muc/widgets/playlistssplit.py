"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from textual import on
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from mu.api import Api
from muc.player import Player
from muc.widgets.playlistsdatatable import PlaylistsDataTable
from muc.widgets.playlisttracksdatatable import PlaylistTracksDataTable


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
