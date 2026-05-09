from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable, Input, Static
from textual.containers import Vertical

from ms.database.database import Database
from ms.util import Util
from ms.client.tracksdatatable import TracksDataTable


class Client(App):

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
        self.theme = "catppuccin-mocha"

    def compose(self) -> ComposeResult:
        yield TracksDataTable(self.tracks)
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "catppuccin-mocha" if self.theme == "catppuccin-latte" else "catppuccin-latte"
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


def start_client():
    app = Client()
    app.run()


if __name__ == "__main__":
    start_client()
