"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.coordinate import Coordinate
from textual.widgets import DataTable, TabbedContent, TabPane

from mu.database import Database
from mu.track import Track
from muc.client.queuelist import QueueList
from muc.client.widgets.albumsdatatable import AlbumsDataTable
from muc.client.widgets.artistsdatatable import ArtistsDataTable
from muc.client.widgets.favoritesdatatable import FavoritesDataTable
from muc.client.widgets.mufooter import MuFooter
from muc.client.widgets.nowplaying import NowPlaying, NowPlayingProgressBar
from muc.client.widgets.playlistsdatatable import PlaylistDataTable
from muc.client.widgets.queuedatatable import QueueDataTable
from muc.client.widgets.tracksdatatable import TracksDataTable
from muc.player.player import Player


class Client(App):
    CSS = """
        Vertical {
            height: 100%;
        }
        NowPlaying {
            height: 7;
        }
        TabbedContent {
            height: 1fr;
        }
        TracksDataTable,
        QueueDataTable,
        AlbumsDataTable,
        ArtistsDataTable,
        PlaylistPlaylistsDataTable {
            height: 1fr;
            max_height: 1fr;
            overflow-y: auto;
        }
        PlaylistPlaylistsDataTable,PlaylistDataTable {
            scrollbar-size: 0 0;
            scrollbar-visibility: hidden;
        }
        Input {
            height:1;
            border: none;
            padding: 0;
        }
        Tabs {
            border: none;
            height:1;
            background: $panel;
        }
        Tab.-active {
            background: $primary;
            color: $text
        }
        Tabs > Underline {
            display: none;
        }
        /* Make the underline bar invisible */
        Underline > .underline--bar {
            color: transparent;
            background: transparent;
        }

        /* Also hide it when the Tabs widget is focused */
        Tabs:focus .underline--bar {
            background: transparent;
        }    """

    BINDINGS = [
        ("q", "goto_tab(0)", "Queue"),
        ("F", "goto_tab(1)", "Favorites"),
        ("t", "goto_tab(2)", "Tracks"),
        ("a", "goto_tab(3)", "Albums"),
        ("A", "goto_tab(4)", "Artists"),
        ("p", "goto_tab(5)", "Playlists"),
        ("Q", "quit", "Quit"),
        ("f", "favorite_track", "Favorite"),
        ("l", "skip_track(1)", "Next"),
        ("h", "skip_track(-1)", "Previous"),
        ("space", "pause_track", "Pause/Play"),
    ]

    def __init__(self):
        super().__init__()
        self.db: Database = Database()
        self.tracks: dict = self.db.list_library_tracks()
        self.albums: list = self.db.list_library_albums()
        self.artists: list = self.db.list_library_artists(album_artist=True)
        self.playlists: list = self.db.list_playlists()
        self.queue_list = QueueList(self.tracks)

        self.theme = "catppuccin-mocha"
        self.animation_level = "none"

        self.now_playing = NowPlaying()
        self.queue_data_table = QueueDataTable(
            "queue-data-table-search", "queue-data-table-main-table"
        )

        self.favorites_data_table = FavoritesDataTable(
            self.tracks,
            "favorites-data-table-search",
            "favorites-data-table-main-table",
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

        self.playlists_data_table = PlaylistDataTable(self.playlists, self.tracks)

        self.tabs = TabbedContent(id="tabs")
        self.tabs.can_focus_children = False

        self.player = Player(
            on_track_end=lambda _: self.track_finished_playing(),
            on_time_changed=lambda elapsed_ms: self.track_time_changed(elapsed_ms),
        )

    def compose(self) -> ComposeResult:
        with Vertical():
            yield self.now_playing
            with self.tabs:
                with TabPane("󰲸 Queue (q)", id="queue-tab"):
                    yield self.queue_data_table
                with TabPane("❤ Favorites (F)", id="favorites-tab"):
                    yield self.favorites_data_table
                with TabPane("󰎇 Tracks (t)", id="tracks-tab"):
                    yield self.tracks_data_table
                with TabPane("󱍙 Albums (a)", id="albums-tab"):
                    yield self.albums_data_table
                with TabPane("󰠃 Artists (A)", id="artists-tab"):
                    yield self.artists_data_table
                with TabPane("󱝟 Playlists (p)", id="playlists-tab"):
                    yield self.playlists_data_table
        yield MuFooter()

    def on_mount(self) -> None:
        """Focuses playlists playlist list upon starting"""
        self.playlists_data_table.playlist_playlists_data_table.main_table.focus()

    def action_goto_tab(self, tabid: int) -> None:
        """Switches to a dedicated tab."""
        all_tabs = [
            ("queue-tab", self.queue_data_table.main_table),
            ("favorites-tab", self.favorites_data_table.main_table),
            ("tracks-tab", self.tracks_data_table.main_table),
            ("albums-tab", self.albums_data_table.main_table),
            ("artists-tab", self.artists_data_table.main_table),
            (
                "playlists-tab",
                self.playlists_data_table.playlist_playlists_data_table.main_table,
            ),
        ]
        try:
            tab_id, table = all_tabs[tabid]
            self.tabs.active = tab_id
            table.focus()
        except (ValueError, IndexError):
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
        try:
            track = self.queue_list.skip_track(offset)
            if track:
                self.player.skip_by_offset(offset)
                self.update_now_playing()
        except ValueError as e:
            self.notify(str(e), severity="warning")

    @on(
        DataTable.RowSelected,
        """
        #queue-data-table-main-table,
        #favorites-data-table-main-table,
        #queue-data-table-main-table,
        #tracks-data-table-main-table,
        #playlist-tracks-data-table-main-table
        """,
    )
    def tracks_row_selected(self, event: DataTable.RowSelected) -> None:
        """Logic when a cell is clicked. Starts now playing and the queue."""

        tab_to_table = {
            "tracks-tab": self.tracks_data_table.main_table,
            "favorites-tab": self.favorites_data_table.main_table,
            "queue-tab": self.queue_data_table.main_table,
            "playlists-tab": self.playlists_data_table.playlist_tracks_data_table.main_table,
        }
        table = tab_to_table.get(self.tabs.active)
        if table is None:
            return

        start_index = event.cursor_row
        queue_ids = []
        for row_id in range(start_index, table.row_count):
            try:
                queue_ids.append(str(table.get_cell_at(Coordinate(row_id, 0))))
            except Exception:
                continue

        try:
            track_id = table.get_cell_at(Coordinate(start_index, 0))
            self.play_track(self.tracks[track_id], queue_ids)
        except Exception as e:
            self.notify(f"Error fetching cell data: {e}", severity="error")

    @on(DataTable.RowSelected, "#album-data-table-main-table")
    def albums_row_selected(self, event: DataTable.RowSelected):
        """If a album is selected"""
        table = self.albums_data_table.main_table
        album_title = table.get_cell_at(Coordinate(event.cursor_row, 0))
        album_artist = table.get_cell_at(Coordinate(event.cursor_row, 1))
        self.tracks_data_table.search.value = (
            f"album:{album_title}&albumartist:{album_artist}"
        )
        self.tracks_data_table.main_table.focus()

    @on(DataTable.RowSelected, "#artist-data-table-main-table")
    def artist_row_selected(self, event: DataTable.RowSelected):
        """If a artist is selected"""
        table = self.artists_data_table.main_table
        artist = table.get_cell_at(Coordinate(event.cursor_row, 0))
        self.albums_data_table.search.value = f"albumartist:{artist}"
        self.albums_data_table.main_table.focus()

    @on(NowPlayingProgressBar.Clicked)
    def now_playing_progress_bar_clicked(
        self, event: NowPlayingProgressBar.Clicked
    ) -> None:
        """
        Moves the playhead to the new percentage.
        UI updates happen when the player sends an event when
        the tracks position changes.
        """
        self.player.move_playhead_to_percentage(event.percentage)

    @on(events.Click, "#now-playing-track-info-artist")
    def search_currently_playing_artist(self) -> None:
        """
        Shows all albums by the currently playing artist.
        """
        current_track = self.queue_list.get_current_track()
        if current_track is not None:
            artist = current_track.artist
            self.albums_data_table.search.value = f"albumartist:{artist}"
            self.albums_data_table.main_table.focus()

    @on(events.Click, "#now-playing-track-info-album")
    def search_currently_playing_album(self) -> None:
        """
        Shows all tracks from the currently playing album.
        """
        current_track = self.queue_list.get_current_track()
        if current_track is not None:
            album = current_track.album
            self.tracks_data_table.search.value = f"album:{album}"
            self.tracks_data_table.main_table.focus()

    def track_finished_playing(self) -> None:
        """This function is called when the track finishes from the player"""
        current_track = self.queue_list.get_current_track()
        if current_track:
            current_track = self.db.increment_play_count(f"id:{current_track.id}")[0]
            self.tracks_data_table.set_track_plays(
                current_track.id, current_track.plays
            )
            self.queue_data_table.set_track_plays(current_track.id, current_track.plays)
            self.favorites_data_table.set_track_plays(
                current_track.id, current_track.plays
            )

        self.queue_list.skip_track()
        self.update_now_playing()

    def track_time_changed(self, current_ms: int) -> None:
        """Updates the current position of now playing"""
        self.now_playing.progress.update_elapsed(current_ms)

    def update_now_playing(self) -> None:
        """Updates the now playing widget with the current track"""
        track = self.queue_list.get_current_track()
        if track:
            self.now_playing.set_track(track)
            self.queue_data_table.update_queue(self.queue_list.get_queue())

    def action_favorite_track(self) -> None:
        """
        Favorites a track. If table is selected, then the track
        is picked from the currently selected row. Else, it is
        selected from the currently playing track.
        """
        # Check if a table is focused
        track_id = None
        table = None
        result = None
        if self.focused == self.tracks_data_table.main_table:
            table = self.tracks_data_table
        elif self.focused == self.queue_data_table.main_table:
            table = self.queue_data_table
        elif self.focused == self.favorites_data_table.main_table:
            table = self.favorites_data_table
        elif (
            self.focused
            == self.playlists_data_table.playlist_tracks_data_table.main_table
        ):
            table = self.playlists_data_table.playlist_tracks_data_table
        elif len(self.queue_list.queue) > 0:
            track = self.queue_list.get_current_track()
            if track:
                track_id = track.id

        # Favorite track
        if table:
            # If track favorited with f key while browsing
            if (
                table.main_table.cursor_row is not None
                and table.main_table.row_count > 0
            ):
                track_id = table.main_table.get_cell_at(
                    Coordinate(table.main_table.cursor_row, 0)
                )
        else:
            # If track is favorited using the buttons on controls while playing
            current_track = self.queue_list.get_current_track()
            if current_track is Track:
                track_id = current_track.id

        result = self.db.favorite(f"id:{track_id}")[0] if track_id else None

        if result:
            self.tracks[track_id] = result

            if not table:
                self.now_playing.controls.set_favorite(result.favorite)

            self.tracks_data_table.set_track_favorite(track_id, result.favorite)
            self.queue_data_table.set_track_favorite(track_id, result.favorite)
            self.favorites_data_table.set_track_favorite(track_id, result.favorite)
            self.playlists_data_table.playlist_tracks_data_table.set_track_favorite(
                track_id, result.favorite
            )
