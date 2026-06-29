"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from textual import on
from textual.app import ComposeResult
from textual.widgets import Input, Static

from mu.playlist import Playlist
from muc.client.widgets.vimdatatable import VimDataTable


class PlaylistsDataTable(Static):
    BINDINGS = [("/", "focus_search", "Search")]

    def __init__(self, playlists: dict[int, Playlist]):
        super().__init__()
        self.playlists = playlists
        self.full_rows: list = []

        self.search = Input(placeholder="Filter playlists (/)", id="playlists-search")
        self.main_table = VimDataTable(cursor_type="row", id="playlists-main-table")

    def compose(self) -> ComposeResult:
        yield self.search
        yield self.main_table

    # Focuses search with "/" key
    def action_focus_search(self) -> None:
        self.search.focus()

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.filter_table(event.value)
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
        for playlist_id in self.playlists:
            playlist = self.playlists[playlist_id]
            row_tuple = (playlist.id, playlist.title, playlist.description)
            self.full_rows.append(row_tuple)
            table.add_row(*row_tuple, key=str(playlist.id))

        table.focus()
