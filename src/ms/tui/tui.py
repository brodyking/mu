from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable, Input, Static
from textual.containers import Vertical

from ms.database import Database
from ms.util import Util

# A separate class to wrap the table and other widgets (like search)
class DataContainer(Static):
    def __init__(self, tracks: list):
        super().__init__()
        self.tracks = tracks

    def compose(self) -> ComposeResult:
        # yield Input(placeholder="Search rows...")
        yield DataTable(cursor_type="row", id="main-table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
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
        table.add_rows(rows)

    # def on_input_changed(self, event: Input.Changed) -> None:
        # """Example: Simple search filtering (logic would go here)"""
        # search_value = event.value.lower()
        # Note: For 50k rows, you'd typically clear and re-add
        # or use a filtered view to maintain performance.


class Tui(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("s", "sort_table", "Sort by Value"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.tracks = self.db.list_library(console_out=False)
        self.theme = "textual-dark"

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataContainer(self.tracks)
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_sort_table(self) -> None:
        """Sorts the table by the 4th column (Value)"""
        table = self.query_one(DataTable)
        # Textual handles the re-sorting internally without a full app redraw
        table.sort("Value", reverse=True)


def start_tui():
    app = Tui()
    app.run()


if __name__ == "__main__":
    start_tui()
