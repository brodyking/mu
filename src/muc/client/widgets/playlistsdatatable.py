"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from textual import on
from textual.app import ComposeResult
from textual.widgets import DataTable, Input, Static

from mu.database.playlist import Playlist
from mu.database.track import Track
from muc.client.widgets.nowplaying import Horizontal
from muc.client.widgets.tracksdatatable import TracksDataTable
from muc.client.widgets.vimdatatable import VimDataTable


class PlaylistPlaylistsDataTable(Static):
    BINDINGS = [("/", "focus_search", "Search")]

    def __init__(self, playlists: list, search_id: str, main_table_id: str):
        super().__init__()
        self.playlists = playlists
        self.full_rows: list = []

        self.search = Input(placeholder="Filter playlists (/)", id=search_id)
        self.main_table = VimDataTable(cursor_type="row", id=main_table_id)

    def compose(self) -> ComposeResult:
        yield self.search
        yield self.main_table

    # Focuses search with "/" key
    def action_focus_search(self) -> None:
        self.search.focus()

    # When search bar's input is changed
    @on(Input.Changed)
    def input_changed(self, event: Input.Changed) -> None:
        self.filter_table(event.value)

    # When the input is submitted, focus the main table of tracks
    def on_input_submitted(self) -> None:
        self.main_table.focus()

    def filter_table(self, search_term: str) -> None:
        """Filters a table with the same prefix/query support as the database"""
        table = self.main_table
        queries = search_term.split("+")
        prefixes = {"id": 0, "title": 1, "description": 2}

        if not search_term:
            filtered_rows = self.full_rows
        else:
            filtered_rows = []
            for query in queries:
                filters = query.split("&")
                # Start with all rows, then narrow down
                query_rows = set(map(tuple, self.full_rows))

                for filter in filters:
                    filter = filter.strip()
                    if ":" not in filter:
                        value = filter.lower()
                        query_rows &= {
                            tuple(row)
                            for row in self.full_rows
                            if value in str(row[1]).lower()
                        }
                    else:
                        prefix, sep, value = filter.partition(":")
                        prefix, value = prefix.strip(), value.strip().lower()
                        if sep and prefix in prefixes and value:
                            row_index = prefixes[prefix]
                            query_rows &= {
                                tuple(row)
                                for row in self.full_rows
                                if value in str(row[row_index]).lower()
                            }

                # Add rows matched by this query group (avoiding duplicates)
                for row in self.full_rows:
                    if tuple(row) in query_rows and row not in filtered_rows:
                        filtered_rows.append(row)
        table.clear()

        for row in filtered_rows:
            table.add_row(*row, key=str(row[0]))

    def on_mount(self) -> None:
        table = self.main_table

        # Add the maximum width to your column metadata definition
        columns = [
            ("id", "Id", 5),
            ("title", "Title", 15),
            ("description", "Description", 20),
        ]

        # Use the max_width argument in add_column
        for label, key, max_w in columns:
            table.add_column(label, key=key, width=max_w)

        self.full_rows = []
        for playlist in self.playlists:
            row_tuple = (playlist.id, playlist.title, playlist.description)
            self.full_rows.append(row_tuple)
            table.add_row(*row_tuple, key=str(playlist.id))

        table.focus()


class PlaylistDataTable(Static):
    DEFAULT_CSS = """
    PlaylistPlaylistsDataTable {
        width: 30;
    }
    TracksDataTable {
        width: 1fr;
    }
    """

    BINDINGS = [
        ("H", "focus_table(0)", "Focus Playlists"),
        ("L", "focus_table(1)", "Focus Tracks"),
    ]

    def __init__(self, playlists: list[Playlist], tracks: dict[Track], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlists = playlists
        self.tracks = tracks
        self.playlist_playlists_data_table = PlaylistPlaylistsDataTable(
            self.playlists,
            "playlist-playlists-data-table-search",
            "playlist-playlists-data-table-main-table",
        )
        self.playlist_tracks_data_table = TracksDataTable(
            dict(),
            "playlist-tracks-data-table-search",
            "playlist-tracks-data-table-main-table",
        )

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self.playlist_playlists_data_table
            yield self.playlist_tracks_data_table

    def action_focus_table(self, table: int):
        """Focuses different tables. 0: Playlists, 1: Playlist Tracks"""
        if table == 0:
            self.playlist_playlists_data_table.main_table.focus()
        else:
            self.playlist_tracks_data_table.main_table.focus()

    @on(DataTable.RowSelected, "#playlist-playlists-data-table-main-table")
    def row_selected(self, event: DataTable.RowSelected) -> None:
        """
        Populates seperate table with tracks from the playlist
        Then changes focus
        """
        row_pos = event.cursor_row
        playlist = self.playlists[row_pos]
        tracks_sorted: dict = dict()
        for track in playlist.tracks:
            tracks_sorted[track.id] = self.tracks[track.id]
        self.playlist_tracks_data_table.tracks = tracks_sorted
        self.playlist_tracks_data_table.generate_full_rows()
        # TODO: Make this table refresh by generate,
        #       not working for some reason so im just filtering an empty string
        self.playlist_tracks_data_table.filter_table("")

        self.playlist_tracks_data_table.main_table.focus()
