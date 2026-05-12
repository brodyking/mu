
# ms client source code
# (c) 2026 all rights reserved

# Textualize
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable, Input, Static, TabbedContent, TabPane, Label
from textual.containers import Vertical
from textual.coordinate import Coordinate
# Database connection
from ms.database.database import Database

# Logic and Objects
from ms.client.queue import Queue

# Widgets
from ms.client.widgets.tracksdatatable import TracksDataTable, VimDataTable
from ms.client.widgets.nowplaying import NowPlaying

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
        ("q", "goto_tab(0)", "Queue"),
        ("t", "goto_tab(1)", "Tracks"),
        ("Q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.db:Database = Database()
        self.tracks:dict = self.db.list_library(console_out=False)
        self.theme:str = "catppuccin-mocha"

        self.now_playing = NowPlaying()
        self.tracks_data_table = TracksDataTable(self.tracks)
        self.queue = Queue(self.tracks)
        self.tabs = TabbedContent(id="tabs")
        self.tabs.can_focus_children = False

    def compose(self) -> ComposeResult:
        with Vertical():
            yield self.now_playing
            with self.tabs:
                with TabPane("Queue (q)",id="queue-tab"):
                    yield Label("This is the queue")
                with TabPane("Tracks (t)",id="tracks-tab"):
                    yield self.tracks_data_table
            yield Footer()

    # Switches tab with h or l
    def action_goto_tab(self, tabid: int) -> None:

        self.now_playing.focus()
        
        all_tabs = ["queue-tab", "tracks-tab"]
    
        try:
            self.tabs.active = all_tabs[tabid]

            if self.tabs.active == "tracks-tab":
                self.tracks_data_table.main_table.focus()
            elif self.tabs.active == "queue-tab":
                self.now_playing.focus()
            
        except ValueError:
            pass

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        print(self.tabs.focus)

    # When search bar's input is changed
    def on_input_changed(self,event: Input.Changed) -> None:
        self.tracks_data_table.filter_table(event.value)

    # When the input is submitted, focus the main table of tracks
    def on_input_submitted(self,event:Input.Submitted) -> None:
        self.tracks_data_table.main_table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = event.data_table
    
        row_count = table.row_count # Get the total number of rows currently in the table
        start_index = event.cursor_row # Get the starting row index from the event
    
        # Loop through the integer indices from the start to the end
        first_col_list = []
        for row_idx in range(start_index, row_count):
            try:
                cell_value = table.get_cell_at(Coordinate(row_idx, 0))
                first_col_list.append(str(cell_value))
            except Exception:
                continue

        # Handle Now Playing logic
        try:
            col2 = table.get_cell_at(Coordinate(start_index, 2))
            col3 = table.get_cell_at(Coordinate(start_index, 3))
            col4 = table.get_cell_at(Coordinate(start_index, 4))

            self.now_playing.set_track(col2, col3, col4)
            self.queue.start_queue(first_col_list)
            print(self.queue.queue)

            self.app.notify(f"Playing: {col2}")
        except Exception as e:
            self.app.notify(f"Error fetching cell data: {e}", severity="error")


def start_client():
    app = Client()
    app.run()


if __name__ == "__main__":
    start_client()
