"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.theme import Theme
from textual.widgets import TabbedContent, TabPane

from mu.api import Api
from muc.player import Player
from muc.widgets.albumsdatatable import AlbumsDataTable
from muc.widgets.artistsdatatable import ArtistsDataTable
from muc.widgets.footer import Footer
from muc.widgets.nowplaying import NowPlaying
from muc.widgets.optionssplit import OptionsSplit
from muc.widgets.playlistssplit import PlaylistsSplit, PlaylistTracksDataTable
from muc.widgets.queuedatatable import QueueDataTable
from muc.widgets.tracksdatatable import AddToPlaylistPopup, AddToPopup, TracksDataTable


class Client(App):
    CSS_PATH = "main.css"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = (
        ("q", "quit", "Quit"),
        # Cycling tabs
        ("H", "cycle_tab(-1)", "Previous Tab"),
        ("L", "cycle_tab(1)", "Next Tab"),
        # Goto specific tab
        ("Q", "goto_tab(0)", "Queue"),
        ("F", "goto_tab(1)", "Favorites"),
        ("T", "goto_tab(2)", "Tracks"),
        ("A", "goto_tab(3)", "Albums"),
        ("R", "goto_tab(4)", "Artists"),
        ("P", "goto_tab(5)", "Playlists"),
        ("O", "goto_tab(6)", "Options"),
        # Media keys
        ("h", "player_prev", "Previous"),
        ("l", "player_next", "Next"),
        ("space", "player_toggle", "Toggle Playback"),
    )  # type:ignore

    TAB_IDS = [
        "queue-tab",
        "favorites-tab",
        "tracks-tab",
        "albums-tab",
        "artists-tab",
        "playlists-tab",
        "options-tab",
    ]

    def __init__(self) -> None:
        super().__init__()
        self.api = Api()
        self.player = Player(self.api)

        self.register_theme(
            theme=Theme(
                name="tokyonight-moon",
                primary="#82AAFFFF",  # blue
                secondary="#394B70FF",  # blue7
                accent="#C099FFFF",  # magenta
                background="#222436FF",  # bg
                foreground="#C8D3F5FF",  # fg
                surface="#1E2030FF",  # bg_dark
                panel="#2F334DFF",  # bg_highlight
                success="#C3E88DFF",  # green
                warning="#FFC777FF",  # yellow
                error="#FF757FFF",  # red
                dark=True,
                variables={},
            )
        )

        self.theme = "tokyonight-moon"
        self.animation_level = "none"

        self.nowplaying = NowPlaying(self.player)
        self.nowplaying.border_title = "Now Playing"
        self.footer = Footer()
        self.tabs = TabbedContent(id="tabs", initial="tracks-tab")
        self.tabs.can_focus_children = False

        self.queue_data_table: QueueDataTable = QueueDataTable(self.api, self.player)
        self.tracks_data_table = TracksDataTable(self.api, self.player)
        self.favorite_tracks_data_table: TracksDataTable = TracksDataTable(
            self.api, self.player, only_favorites=True
        )
        self.albums_data_table: AlbumsDataTable = AlbumsDataTable(self.api)
        self.artists_data_table: ArtistsDataTable = ArtistsDataTable(self.api)

        self.playlists_split = PlaylistsSplit(self.api, self.player)

        self.options_split = OptionsSplit(self.api)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield self.nowplaying
            with Horizontal():
                with self.tabs:
                    with TabPane(title="󰲸 Queue (Q)", id="queue-tab"):
                        yield self.queue_data_table
                    with TabPane(title="󰋑 Favorites (F)", id="favorites-tab"):
                        yield self.favorite_tracks_data_table
                    with TabPane(title="󰎇 Tracks (T)", id="tracks-tab"):
                        yield self.tracks_data_table
                    with TabPane(title="󱍙 Albums (A)", id="albums-tab"):
                        yield self.albums_data_table
                    with TabPane(title="󰠃 Artists (R)", id="artists-tab"):
                        yield self.artists_data_table
                    with TabPane(title="󱝟 Playlists (P)", id="playlists-tab"):
                        yield self.playlists_split
                    with TabPane(title=" Options (O)", id="options-tab"):
                        yield self.options_split
            yield self.footer

    def action_goto_tab(self, tabid: int) -> None:
        """Switches to a dedicated tab."""
        try:
            tab_name = self.TAB_IDS[tabid]
            self.tabs.active = tab_name
        except (ValueError, IndexError):
            pass

    def action_cycle_tab(self, offset: int) -> None:
        """Moves to the tab left or right of the current one."""
        try:
            current_index = self.TAB_IDS.index(self.tabs.active)
        except ValueError:
            return
        new_index = (current_index + offset) % len(self.TAB_IDS)
        self.action_goto_tab(new_index)

    @on(NowPlaying.TrackChanged)
    def on_track_changed(self) -> None:
        """
        Called from the tick in nowplaying.
        Updates the queue table.
        """
        self.queue_data_table.populate()
        self.queue_data_table.redraw_rows()

    @on(AlbumsDataTable.AlbumClicked)
    def album_clicked(self, event: AlbumsDataTable.AlbumClicked) -> None:
        """
        Searches for an album's tracks in the tracks tab, then switches tab.
        Message sent from AlbumsDataTable
        """
        self.tracks_data_table.search.value = (
            f"album={event.album.title}&albumartist={event.album.albumartist}"
        )
        self.action_goto_tab(2)

    @on(ArtistsDataTable.ArtistClicked)
    def artist_clicked(self, event: ArtistsDataTable.ArtistClicked) -> None:
        """
        Searches for an album's tracks in the tracks tab, then switches tab.
        Message sent from AlbumsDataTable
        """
        self.albums_data_table.search.value = f"albumartist={event.artist.name}"
        self.action_goto_tab(3)

    @on(TracksDataTable.FavoriteTrack)
    def favorite_track(self, event: TracksDataTable.FavoriteTrack) -> None:
        """
        Toggles a tracks favorite icon
        """
        try:
            tid = event.tid
            self.api.favorite_tracks(f"id={tid}")[tid]
            self.player.recache_current_track()

        except Exception as e:
            self.app.notify(f"Couldn't favorite: {e}", severity="error", timeout=0.25)

    @on(AddToPopup.QueueTrack)
    def queue_track(self, event: AddToPopup.QueueTrack) -> None:
        if event.queue_next:
            self.player.queue.queue_tracks_next(
                [
                    event.tid,
                ]
            )
        else:
            self.player.queue.queue_tracks_last(
                [
                    event.tid,
                ]
            )
        if self.focused == self.queue_data_table.main_table:
            self.queue_data_table.on_show()

    @on(AddToPlaylistPopup.AppendTrackToPlaylist)
    def append_track_to_playlist(
        self, event: AddToPlaylistPopup.AppendTrackToPlaylist
    ) -> None:
        if event.tid and event.pid:
            response = self.api.append_playlists(f"id={event.pid}", f"id={event.tid}")
            if len(response) > 1:
                self.notify("Added track to playlist.", timeout=0.25)
            else:
                self.notify("Playlist not found", severity="error")

    @on(PlaylistTracksDataTable.RemoveTrackFromPlaylist)
    def remove_track_from_playlist(
        self, event: PlaylistTracksDataTable.RemoveTrackFromPlaylist
    ) -> None:
        response = self.api.remove_from_playlist(f"id={event.pid}", f"id={event.tid}")
        if len(response) < 1:
            self.notify("Playlist not found", severity="error")
            return
        self.notify("Removed track from playlist")
        if self.focused == self.playlists_split.tracks_data_table.main_table:
            self.playlists_split.tracks_data_table.playlist = self.api.get_playlists(
                f"id={event.pid}"
            )[event.pid]
            self.playlists_split.tracks_data_table.populate()
            self.playlists_split.tracks_data_table.redraw_rows()

    def action_player_next(self) -> None:
        """
        Skips to the next track
        """
        try:
            self.player.next()
        except ValueError as e:
            self.notify(str(e), severity="error", timeout=0.25)

    def action_player_prev(self) -> None:
        """
        Skips to the previous track if pos is under 3 seconds.
        If over, it restarts the track
        """
        if self.player.pos < 3:
            try:
                self.player.prev()
            except ValueError as e:
                self.notify(str(e), severity="error", timeout=0.25)
        else:
            self.player.seek(0)

    def action_player_toggle(self) -> None:
        """
        Toggles playback, used for pause/play.
        """
        self.player.toggle()
