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

from mu.database.playlist import Playlist
from muc.client.widgets.vimdatatable import VimDataTable


class PlaylistDataTable(Static):
    BINDINGS = [("/", "focus_search", "Search")]

    CSS = """
    VimDataTable {
        width: auto;
        height: auto;
    }
    """

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
        table = self.main_table
        search_term = search_term.lower()

        if not search_term:
            filtered_rows = self.full_rows
        else:
            prefixes = {
                "id": 0,
                "title": 1,
                "description": 2,
            }

            if ":" in search_term and search_term.split(":", 1)[0] in prefixes.keys():
                # Filter rows based on prefix provided
                filtered_rows = [
                    row
                    for row in self.full_rows
                    if search_term.split(":", 1)[1]
                    in str(row[prefixes.get(search_term.split(":", 1)[0])]).lower()
                ]
            else:
                # Filter rows based on Title (index 2) or Artist (index 3)
                filtered_rows = [
                    row
                    for row in self.full_rows
                    if search_term in str(row[0]).lower()
                    or search_term in str(row[1]).lower()
                ]

        table.clear()

        for i, row in enumerate(filtered_rows):
            table.add_row(*row, key=str(i))

    def on_mount(self) -> None:
        table = self.main_table

        # Add the maximum width to your column metadata definition
        columns = [
            ("id", "Id", 25),
            ("title", "Title", 15),
            ("description", "Description", 20),
        ]

        # Use the max_width argument in add_column
        for label, key, max_w in columns:
            table.add_column(label, key=key, width=max_w)

        self.full_rows = []
        for i, playlist in enumerate(self.playlists):
            row_tuple = (playlist.id, playlist.title, playlist.description)
            self.full_rows.append(row_tuple)
            table.add_row(*row_tuple, key=str(i))

        table.focus()
