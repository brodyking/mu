"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from mu.playlist import Playlist
from mu.track import Track
from muc.client.widgets.nowplaying import Horizontal
from muc.client.widgets.playlistsdatatable import PlaylistsDataTable
from muc.client.widgets.tracksdatatable import TracksDataTable
from textual import on
from textual.app import ComposeResult
from textual.coordinate import Coordinate
from textual.widgets import DataTable, Static


class PlaylistSplit(Static):
    DEFAULT_CSS = """
    PlaylistsDataTable {
        width: 30;
    }
    TracksDataTable {
        width: 1fr;
    }
    """

    BINDINGS = [
        ("ctrl+h", "focus_table(0)", "Focus Playlists"),
        ("ctrl+l", "focus_table(1)", "Focus Tracks"),
    ]

    def __init__(
        self, playlists: dict[int, Playlist], tracks: dict[int, Track], *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.playlists = playlists
        self.tracks = tracks
        self.playlists_data_table = PlaylistsDataTable(self.playlists)
        self.tracks_data_table = TracksDataTable(dict())

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self.playlists_data_table
            yield self.tracks_data_table

    def action_focus_table(self, table: int):
        """Focuses different tables. 0: Playlists, 1: Playlist Tracks"""
        if table == 0:
            self.playlists_data_table.main_table.focus()
        else:
            self.tracks_data_table.main_table.focus()

    @on(DataTable.RowSelected, "#playlists-main-table")
    def row_selected(self, event: DataTable.RowSelected) -> None:
        """
        Populates seperate table with tracks from the playlist
        Then changes focus
        """
        playlist_id = self.playlists_data_table.main_table.get_cell_at(
            Coordinate(event.cursor_row, 0)
        )
        playlist = self.playlists[playlist_id]
        tracks_sorted: dict = dict()
        for track in playlist.tracks:
            tracks_sorted[track.id] = self.tracks[track.id]
        self.tracks_data_table.tracks = tracks_sorted
        self.tracks_data_table.generate_full_rows()
        # TODO: Make this table refresh by generate,
        #       not working for some reason so im just filtering an empty string
        self.tracks_data_table.filter_table("")

        self.tracks_data_table.main_table.focus()
