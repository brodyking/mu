
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
        ("f", "favorite_track" , "Favorite"),
        ("l", "skip_track(1)", "Next"),
        ("h", "skip_track(-1)", "Previous")
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
                with TabPane("󰲸 Queue (q)",id="queue-tab"):
                    yield self.queue_data_table
                with TabPane("󰎇 Tracks (t)",id="tracks-tab"):
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

    def play_track(self,track: Track,queue_ids: list) -> None:
        """Plays a given track."""
        self.now_playing.set_track(track)
        self.queue_list.start_queue(queue_ids)
        self.queue_data_table.update_queue(self.queue_list.get_queue())


    def action_skip_track(self,offset:int) -> None:
        """Skips to a song in the queue by an offest if the song exists"""
        if len(self.queue_list.queue) <= 0:
            return
        track = self.queue_list.skip_track(offset)
        if track:
            self.now_playing.set_track(track)
            self.queue_data_table.update_queue(self.queue_list.get_queue())


    # When a track is clicked
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Logic when a cell is clicked. Starts now playing and the queue."""

        # Select tab based on what is active
        if self.tabs.active == "tracks-tab":
            table = self.tracks_data_table.main_table
        else:
            table = self.queue_data_table.main_table    
        row_count = table.row_count # Get the total number of rows currently in the table
        start_index = event.cursor_row # Get the starting row index from the event
    
        # Loop through the integer indices from the start to the end
        queue_ids = []
        for row_id in range(start_index, row_count):
            try:
                cell_value = table.get_cell_at(Coordinate(row_id, 0))
                queue_ids.append(str(cell_value))
            except Exception:
                continue
 
        try:
            id = table.get_cell_at(Coordinate(event.cursor_row,0))
            print(id)
            self.play_track(
                self.tracks[id],
                queue_ids
            )
        except Exception as e:
            self.app.notify(f"Error fetching cell data: {e}", severity="error")

    def update_track_lists(self,tracks:dict) -> None:
        self.tracks = tracks
        self.queue_list.tracks = dict(self.tracks) 
        self.tracks_data_table.tracks = dict(self.tracks)

    # When f is pressed while browsing tracks
    def action_favorite_track(self) -> None:
        # Check if a table is focused
        track_id = None
        table = None
        result = None
        if self.focused == self.tracks_data_table.main_table:
            table = self.tracks_data_table
        elif self.focused == self.queue_data_table.main_table:
            table = self.queue_data_table
        elif len(self.queue_list.queue) > 0:
            track_id = self.queue_list.get_current_track().id

        # Favorite track
        if table:
            # If track favorited with f key while browsing
            if table.main_table.cursor_row is not None:
                track_id = table.main_table.get_cell_at(Coordinate(table.main_table.cursor_row,0))

        else:
            # If track is favorited using the buttons on controls while playing
            if len(self.queue_list.queue) > 0:
                track_id = self.queue_list.get_current_track().id
        
        result = self.db.favorite(f"id:{track_id}")[0] if track_id else None
        
        if result:
            print(result)
            new_track = Track(result)
            self.tracks[track_id] = new_track 
            self.queue_list.tracks[track_id] = new_track 

            if not table: self.now_playing.controls.set_favorite(new_track.favorite)

            self.tracks_data_table.set_track_favorite(track_id,new_track.favorite)
            self.queue_data_table.set_track_favorite(track_id,new_track.favorite)



def start_client():
    app = Client()
    app.run()


if __name__ == "__main__":
    start_client()
