
# ms client source code
# (c) 2026 all rights reserved

# Textualize
from textual.app import App, ComposeResult
from textual.widgets import Footer, DataTable, TabbedContent, TabPane 
from textual.containers import Vertical
from textual.coordinate import Coordinate
# Database connection
from ms.client.widgets import queuedatatable
from ms.database.database import Database
from ms.database.track import Track

# Logic and Objects
from ms.client.queuelist import QueueList

# Widgets
from ms.client.widgets.tracksdatatable import TracksDataTable
from ms.client.widgets.queuedatatable import QueueDataTable
from ms.client.widgets.nowplaying import NowPlaying

class Client(App):

    CSS = """
        NowPlaying {
            height: 4;      /* Reserves exactly 5 rows for your track info */
            margin: 1;
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
        ("f", "favorite" , "Favorite")
    ]

    def __init__(self):
        super().__init__()
        self.db:Database = Database()
        self.tracks:dict = self.db.list_library(console_out=False)
        self.theme = "catppuccin-mocha"

        self.now_playing = NowPlaying()
        self.tracks_data_table = TracksDataTable(self.tracks,"tracks-data-table-search","tracks-data-table-main-table")
        self.queue_list = QueueList(self.tracks)
        self.queue_data_table = QueueDataTable("queue-data-table-search","queue-data-table-main-table")
        self.tabs = TabbedContent(id="tabs")
        self.tabs.can_focus_children = False

    def compose(self) -> ComposeResult:
        with Vertical():
            yield self.now_playing
            with self.tabs:
                with TabPane("Queue (q)",id="queue-tab"):
                    yield self.queue_data_table
                with TabPane("Tracks (t)",id="tracks-tab"):
                    yield self.tracks_data_table
            yield Footer()

    # Switches tab with h or l
    def action_goto_tab(self, tabid: int) -> None:
        all_tabs = ["queue-tab", "tracks-tab"]
        try:
            self.tabs.active = all_tabs[tabid]

            if self.tabs.active == "tracks-tab":
                self.tracks_data_table.main_table.focus()
            elif self.tabs.active == "queue-tab":
                self.queue_data_table.main_table.focus()
        except ValueError:
            pass

    # When a track is clicked
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if self.tabs.active == "tracks-tab":
            table = self.tracks_data_table.main_table
        else:
            table = self.queue_data_table.main_table    
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
            self.queue_list.start_queue(first_col_list)
            self.queue_data_table.update_queue(self.queue_list.get_queue())

            self.app.notify(f"Playing: {col2}")
        except Exception as e:
            self.app.notify(f"Error fetching cell data: {e}", severity="error")

    def update_track_lists(self,tracks:dict) -> None:
        self.tracks = tracks
        self.queue_list.tracks = dict(self.tracks) 
        self.tracks_data_table.tracks = dict(self.tracks)

    # When f is pressed while browsing tracks
    def action_favorite(self) -> None:

        # Check if a table is focused
        if self.focused == self.tracks_data_table.main_table:
            table = self.tracks_data_table
        elif self.focused == self.queue_data_table.main_table:
            table = self.queue_data_table
        else:
            table = None 
        
        # Favorite track
        if table:
            if table.main_table.cursor_row is not None:
                row_data = table.main_table.get_row_at(table.main_table.cursor_row) 

                result = self.db.favorite(f"id:{row_data[0]}")[0]
                track_id = row_data[0]
                is_favorite = result[1]

                self.tracks[track_id] = Track(result)
                self.queue_list.tracks[track_id] = Track(result)
                self.tracks_data_table.tracks = Track(result)

                self.tracks_data_table.set_track_favorite(track_id,is_favorite)
                self.queue_data_table.set_track_favorite(track_id,is_favorite)

def start_client():
    app = Client()
    app.run()


if __name__ == "__main__":
    start_client()
