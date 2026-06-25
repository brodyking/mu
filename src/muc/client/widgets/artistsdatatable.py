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

from muc.client.widgets.vimdatatable import VimDataTable


class ArtistsDataTable(Static):
    BINDINGS = [("/", "focus_search", "Search")]

    CSS = """
    ArtistsDataTable {
        width: auto;
        height: auto;
    }
    """

    def __init__(self, artists: list[str]):
        super().__init__()
        self.artists = artists
        self.full_rows: list = []

        self.search = Input(placeholder="Filter artists (/)", id="artists-search")
        self.main_table = VimDataTable(cursor_type="row", id="artists-main-table")

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
        prefixes = {
            "artist": 0,
        }

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
                            if value in str(row[0]).lower()
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

        for i, row in enumerate(filtered_rows):
            table.add_row(*row, key=str(i))

    def on_mount(self) -> None:
        table = self.main_table

        # Add the maximum width to your column metadata definition
        columns = [
            ("Artist", "artist", 25),
        ]

        # Use the max_width argument in add_column
        for label, key, max_w in columns:
            table.add_column(label, key=key, width=max_w)

        self.full_rows = []
        for i, artist in enumerate(self.artists):
            self.full_rows.append(artist)
            table.add_row(*artist, key=str(artist))

        table.focus()
