from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable, Input, Static
from textual.containers import Vertical

from ms.database.database import Database
from ms.client.tracksdatatable import TracksDataTable, VimDataTable
from ms.client.nowplaying import NowPlaying

class Client(App):

    CSS = """
        NowPlaying {
            height: 3;      /* Reserves exactly 5 rows for your track info */
            dock: top;      /* Optional: keeps it pinned to the top */
            background: $boost;
        }

        TracksDataTable {
            height: 1fr;    /* Tells the table to take up the "fractional" remaining space */
        }

        Input {
            height:1;
            border: none;
            padding: 0;
        }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("/", "focus_search","Search")
    ]

    def __init__(self):
        super().__init__()
        self.db:Database = Database()
        self.tracks:dict = self.db.list_library(console_out=False)
        self.theme:str = "catppuccin-mocha"

        self.now_playing = NowPlaying()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield self.now_playing
            yield TracksDataTable(self.tracks)
            yield Footer()

    def action_focus_search(self) -> None:
        self.query_one("#search-bar").focus()

    def on_input_changed(self,event: Input.Changed) -> None:
        container = self.query_one(TracksDataTable)
        container.filter_table(event.value)

    def on_input_submitted(self,event:Input.Submitted) -> None:
        self.query_one("#main-table").focus()

    def on_data_table_row_selected(self,event: DataTable.RowSelected) -> None:
        row_key = event.row_key
        table = self.query_one("#main-table")
        row_data = table.get_row(row_key)
        self.app.notify(f"Track clicked: {row_data[0]}, {row_data[2]}")

        self.now_playing.set_track(row_data[2],row_data[3],row_data[4])


def start_client():
    app = Client()
    app.run()


if __name__ == "__main__":
    start_client()
