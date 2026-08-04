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
from textual.widgets import Footer, TabbedContent, TabPane

from mu.api import Api
from muc.player import Player
from muc.widgets.queuedatatable import QueueDataTable
from muc.widgets.tracksdatatable import TracksDataTable
from muc.widgets.nowplaying import NowPlaying


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
        ("T", "goto_tab(1)", "Tracks"),
        ("F", "goto_tab(2)", "Favorites"),
        # Media keys
        ("h", "player_prev", "Previous"),
        ("l", "player_next", "Next"),
        ("space", "player_toggle", "Toggle Playback"),
    )  # type:ignore

    TAB_IDS = [
        "queue-tab",
        "tracks-tab",
        "favorites-tab",
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

        self.tabs = TabbedContent(id="tabs")

        self.queue_data_table: QueueDataTable = QueueDataTable(self.api, self.player)
        self.tracks_data_table = TracksDataTable(self.api, self.player)
        self.favorite_tracks_data_table: TracksDataTable = TracksDataTable(
            self.api, self.player, only_favorites=True
        )

    def compose(self) -> ComposeResult:
        with Vertical():
            yield self.nowplaying
            with Horizontal():
                with self.tabs:
                    with TabPane(title="Queue (Q)", id="queue-tab"):
                        yield self.queue_data_table
                    with TabPane(title="Tracks (T)", id="tracks-tab"):
                        yield self.tracks_data_table
                    with TabPane(title="Favorites (F)", id="favorites-tab"):
                        yield self.favorite_tracks_data_table
                yield Footer()

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

    def action_player_next(self) -> None:
        self.player.next()

    def action_player_prev(self) -> None:
        if self.player.pos < 3:
            self.player.prev()
        else:
            self.player.seek(0)

    def action_player_toggle(self) -> None:
        self.player.toggle()
