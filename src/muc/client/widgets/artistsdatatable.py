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

    def __init__(self, artists: list[str], search_id: str, main_table_id: str):
        super().__init__()
        self.artists = artists
        self.full_rows: list = []

        self.search = Input(placeholder="Filter artists (/)", id=search_id)
        self.main_table = VimDataTable(cursor_type="row", id=main_table_id)

    def compose(self) -> ComposeResult:
        yield self.search
        yield self.main_table

    # Focuses search with "/" key
    def action_focus_search(self) -> None:
        self.search.focus()

    # When search bar's input is changed
    def on_input_changed(self, event: Input.Changed) -> None:
        self.filter_table(event.value)

    # When the input is submitted, focus the main table of tracks
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.main_table.focus()

    def filter_table(self, search_term: str) -> None:
        table = self.main_table
        search_term = search_term.lower()

        if not search_term:
            filtered_rows = self.full_rows
        else:
            filtered_rows = [
                row for row in self.full_rows if search_term in str(row[0]).lower()
            ]

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
            table.add_row(*artist, key=str(i))

        table.focus()
