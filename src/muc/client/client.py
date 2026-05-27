# mu client source code
# (c) 2026 all rights reserved

# Textualize
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.coordinate import Coordinate
from textual.widgets import DataTable, Footer, TabbedContent, TabPane

from mu.database.database import Database
from mu.database.track import Track
from muc.client.queuelist import QueueList
from muc.client.widgets.albumsdatatable import AlbumsDataTable
from muc.client.widgets.artistsdatatable import ArtistsDataTable
from muc.client.widgets.nowplaying import NowPlaying
from muc.client.widgets.queuedatatable import QueueDataTable
from muc.client.widgets.tracksdatatable import TracksDataTable
from muc.player.player import Player


class Client(App):
    CSS = """
        TracksDataTable,QueueDataTable,AlbumsDataTable,ArtistsDataTable {
            height: 1fr; 
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
        ("a", "goto_tab(2)", "Albums"),
        ("A", "goto_tab(3)", "Artists"),
        ("Q", "quit", "Quit"),
        ("f", "favorite_track", "Favorite"),
        ("l", "skip_track(1)", "Next"),
        ("h", "skip_track(-1)", "Previous"),
        ("space", "pause_track", "Pause/Play"),
    ]

    def __init__(self):
        super().__init__()
        self.db: Database = Database()
        self.tracks: dict = self.db.list_library_tracks(console_out=False)
        self.albums: list = self.db.list_library_albums(console_out=False)
        self.artists: list = self.db.list_library_artists(console_out=False)
        self.queue_list = QueueList(self.tracks)
        self.theme = "catppuccin-mocha"

        self.now_playing = NowPlaying()
        self.queue_data_table = QueueDataTable(
            "queue-data-table-search", "queue-data-table-main-table"
        )
        self.tracks_data_table = TracksDataTable(
            self.tracks, "tracks-data-table-search", "tracks-data-table-main-table"
        )

        self.albums_data_table = AlbumsDataTable(
            self.albums, "album-data-table-search", "album-data-table-main-table"
        )

        self.artists_data_table = ArtistsDataTable(
            self.artists, "artist-data-table-search", "artist-data-table-main-table"
        )

        self.tabs = TabbedContent(id="tabs")
        self.tabs.can_focus_children = False

        self.player = Player(
            on_track_end=lambda event: self.track_finished_playing(),
            on_time_changed=lambda elapsed_ms: self.track_time_changed(elapsed_ms),
        )

    def compose(self) -> ComposeResult:
        with Vertical():
            yield self.now_playing
            with self.tabs:
                with TabPane("󰲸 Queue (q)", id="queue-tab"):
                    yield self.queue_data_table
                with TabPane("󰎇 Tracks (t)", id="tracks-tab"):
                    yield self.tracks_data_table
                with TabPane("󱍙 Albums (a)", id="albums-tab"):
                    yield self.albums_data_table
                with TabPane("󰠃 Artists (A)", id="artists-tab"):
                    yield self.artists_data_table
            yield Footer(compact=True, show_command_palette=False)

    def action_goto_tab(self, tabid: int) -> None:
        """Switches to a dedicated tab with h or l keys."""
        all_tabs = ["queue-tab", "tracks-tab", "albums-tab", "artists-tab"]
        try:
            self.tabs.active = all_tabs[tabid]

            if self.tabs.active == "tracks-tab":
                self.tracks_data_table.main_table.focus()
            elif self.tabs.active == "queue-tab":
                self.queue_data_table.main_table.focus()
            elif self.tabs.active == "albums-tab":
                self.albums_data_table.main_table.focus()
            elif self.tabs.active == "artists-tab":
                self.artists_data_table.main_table.focus()
        except ValueError:
            pass

    def play_track(self, track: Track, queue_ids: list) -> None:
        """Plays a given track."""
        self.now_playing.set_track(track)
        self.queue_list.start_queue(queue_ids)
        self.queue_data_table.update_queue(self.queue_list.get_queue())

        filepaths = []
        queue = self.queue_list.get_queue(offset=0)
        for track in queue:
            filepaths.append(track.filepath)

        self.player.set_queue(filepaths)
        self.player.start_playback()

    def action_pause_track(self) -> None:
        """Pauses the player"""
        self.player.toggle_playback()

    def action_skip_track(self, offset: int) -> None:
        """Skips to a song in the queue by an offest if the song exists"""
        if len(self.queue_list.queue) <= 0:
            return
        track = self.queue_list.skip_track(offset)
        if track:
            self.player.skip_by_offset(offset)
            self.update_now_playing()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Logic when a cell is clicked. Starts now playing and the queue."""

        # Select tab based on what is active
        if self.tabs.active == "tracks-tab":
            table = self.tracks_data_table.main_table
        elif self.tabs.active == "queue-tab":
            table = self.queue_data_table.main_table
        elif self.tabs.active == "albums-tab":
            table = self.albums_data_table.main_table
        elif self.tabs.active == "artists-tab":
            table = self.artists_data_table.main_table
        else:
            return

        start_index = event.cursor_row  # Get the starting row index from the event

        if self.tabs.active == "queue-tab" or self.tabs.active == "tracks-tab":
            row_count = table.row_count
            # Loop through the integer indices from the start to the end
            queue_ids = []
            for row_id in range(start_index, row_count):
                try:
                    cell_value = table.get_cell_at(Coordinate(row_id, 0))
                    queue_ids.append(str(cell_value))
                except Exception:
                    continue
            try:
                id = table.get_cell_at(Coordinate(event.cursor_row, 0))
                self.play_track(self.tracks[id], queue_ids)
            except Exception as e:
                self.app.notify(f"Error fetching cell data: {e}", severity="error")

        elif self.tabs.active == "albums-tab":
            album_title = table.get_cell_at(Coordinate(event.cursor_row, 0))
            self.tracks_data_table.search.value = f"album:{album_title}"
            self.tracks_data_table.main_table.focus()

        elif self.tabs.active == "artists-tab":
            artist = table.get_cell_at(Coordinate(event.cursor_row, 0))
            self.tracks_data_table.search.value = f"artist:{artist}"
            self.tracks_data_table.main_table.focus()

    def track_finished_playing(self) -> None:
        """This function is called when the track finishes from the player"""
        self.queue_list.skip_track()
        self.update_now_playing()

    def track_time_changed(self, current_ms: int) -> None:
        """Updates the current position of now playing"""
        self.now_playing.progress_bar.update_elapsed(current_ms)

    def update_now_playing(self) -> None:
        track = self.queue_list.get_current_track()
        if track:
            self.now_playing.set_track(track)
            self.queue_data_table.update_queue(self.queue_list.get_queue())

    def update_track_lists(self, tracks: dict) -> None:
        self.tracks = tracks
        self.queue_list.tracks = dict(self.tracks)
        self.tracks_data_table.tracks = dict(self.tracks)

    def action_favorite_track(self) -> None:
        """When f is pressed while browsing tracks"""
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
                track_id = table.main_table.get_cell_at(
                    Coordinate(table.main_table.cursor_row, 0)
                )

        else:
            # If track is favorited using the buttons on controls while playing
            if len(self.queue_list.queue) > 0:
                track_id = self.queue_list.get_current_track().id

        result = self.db.favorite(f"id:{track_id}")[0] if track_id else None

        if result:
            self.tracks[track_id] = result
            self.queue_list.tracks[track_id] = result

            if not table:
                self.now_playing.controls.set_favorite(result.favorite)

            self.tracks_data_table.set_track_favorite(track_id, result.favorite)
            self.queue_data_table.set_track_favorite(track_id, result.favorite)

