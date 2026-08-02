"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.theme import Theme
from textual.widgets import Footer, TabbedContent, TabPane

from mu.api import Api
from muc.client.widgets.tracksdatatable import TracksDataTable


class Client(App):
    CSS_PATH = "main.css"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = (
        ("q", "quit", "Quit"),
        # Tabs
        ("H", "cycle_tab(-1)", "Previous Tab"),
        ("L", "cycle_tab(1)", "Next Tab"),
        ("T", "goto_tab(0)", "Tracks"),
        ("F", "goto_tab(1)", "Favorites"),
    )  # type:ignore

    def __init__(self) -> None:
        super().__init__()
        self.api = Api()

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

        self.tabs = TabbedContent(id="tabs")
        self.tracks_data_table = TracksDataTable(self.api)
        self.favorite_tracks_data_Table: TracksDataTable = TracksDataTable(
            self.api, only_favorites=True
        )

    def compose(self) -> ComposeResult:
        with Horizontal():
            with self.tabs:
                with TabPane(title="Tracks (T)", id="tracks-tab"):
                    yield self.tracks_data_table
                with TabPane(title="Favorites (F)", id="favorites-tab"):
                    yield self.favorite_tracks_data_Table
            yield Footer()

    def action_goto_tab(self, tabid: int) -> None:
        """Switches to a dedicated tab."""
        all_tabs: list[tuple] = [
            ("tracks-tab", self.tracks_data_table.main_table),
            ("favorites-tab", self.favorite_tracks_data_Table.main_table),
        ]
        try:
            tab_name, table = all_tabs[tabid]
            self.tabs.active = tab_name
            table.focus()
        except (ValueError, IndexError):
            pass

    def action_cycle_tab(self, offset: int) -> None:
        """Moves to the tab left or right of the current one."""
        tab_ids = [
            "tracks-tab",
            "favorites-tab",
        ]
        try:
            current_index = tab_ids.index(self.tabs.active)
        except ValueError:
            return
        new_index = (current_index + offset) % len(tab_ids)
        self.action_goto_tab(new_index)
