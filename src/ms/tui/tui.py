from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable, Input, Static
from textual.containers import Vertical

from ms.database import Database
from ms.util import Util

# A separate class to wrap the table and other widgets (like search)
class VimDataTable(DataTable):
    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("h", "cursor_left", "Left"),
        ("l", "cursor_right", "Right"),
        ("g", "scroll_home", "Top"),
        ("G", "scroll_end", "Bottom")
    ]

class TracksDataTable(Static):
    
    def __init__(self, tracks: list):
        super().__init__()
        self.tracks = tracks
        self.full_rows = []

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search rows...", id="search-bar", classes="hidden")
        yield VimDataTable(cursor_type="row", id="main-table")

    def on_data_table_row_selected(self,event: DataTable.RowSelected) -> None:
        row_key = event.row_key
        table = self.query_one(VimDataTable)
        row_data = table.get_row(row_key)
        self.app.notify(f"Track clicked: {row_data[0]}, {row_data[2]}")

    def filter_table(self, search_term: str) -> None:
        table = self.query_one(VimDataTable)
        search_term = search_term.lower()

        if not search_term:
            filtered_rows = self.full_rows
        else:
            # Filter rows based on Title (index 2) or Artist (index 3)
            filtered_rows = [
                row for row in self.full_rows 
                if search_term in str(row[2]).lower() or search_term in str(row[3]).lower()
            ]

        table.clear()
        table.add_rows(filtered_rows)

    def on_mount(self) -> None:
        table = self.query_one(VimDataTable)
        table.add_columns(
            "Id",
            "",
            "Title",
            "Artist",
            "Album",
            "Plays",
            "Time",
            "Date Added",
            "Track Number",
            "Album Artist",
            "Disc Number",
            "Genre",
            "Date",
            "File Path",
            "File Name",
            "Album Art",
        )

        # Generating 50,000 rows of sample data
        # DataTable.add_rows is optimized for bulk inserts
        rows = []
        for trackid in self.tracks:
            track = self.tracks[trackid]

            favorite = "❤" if track.favorite else " "
            
            rows.append(
                (
                    track.id,
                    favorite,
                    Util.fmt(track.title,50),
                    Util.fmt(track.artist,30),
                    Util.fmt(track.album,50),
                    Util.fmt(track.plays,5),
                    Util.fmt(track.time,10),
                    Util.fmt(track.dateadded,20),
                    Util.fmt(track.tracknumber,10),
                    Util.fmt(track.albumartist,30),
                    Util.fmt(track.discnumber,10),
                    Util.fmt(track.genre,20),
                    Util.fmt(track.date,20),
                    track.filepath,
                    track.filename,
                    track.albumart
                )
            )
        self.full_rows = rows
        table.add_rows(rows)
        table.focus()

    # def on_input_changed(self, event: Input.Changed) -> None:
        # """Example: Simple search filtering (logic would go here)"""
        # search_value = event.value.lower()
        # Note: For 50k rows, you'd typically clear and re-add
        # or use a filtered view to maintain performance.


class Tui(App):

    CSS = """
        .hidden { display: none; }
    """

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
        ("/", "focus_search","Search")
    ]

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.tracks = self.db.list_library(console_out=False)
        self.theme = "textual-dark"

    def compose(self) -> ComposeResult:
        yield TracksDataTable(self.tracks)
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_focus_search(self) -> None:
        search_bar = self.query_one("#search-bar")
        search_bar.remove_class("hidden")
        search_bar.focus()

    def on_input_changed(self,event: Input.Changed) -> None:
        container = self.query_one(TracksDataTable)
        container.filter_table(event.value)

    def on_input_submitted(self,event:Input.Submitted) -> None:
        search_bar = self.query_one("#search-bar")
        search_bar.add_class("hidden")
        self.query_one("#main-table").focus()


def start_tui():
    app = Tui()
    app.run()


if __name__ == "__main__":
    start_tui()
