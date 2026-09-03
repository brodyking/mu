from textual import on
from textual.containers import Horizontal
from textual.coordinate import Coordinate
from textual.widgets import Static

from mu.api import Api
from mutui.widgets.cmdline import CmdLine
from mutui.widgets.vimdatatable import VimDataTable


class OptionsDataTable(VimDataTable):
    ROWS = [
        ("Scan", "refresh metadata"),
        ("iTunes", "import an itunes library xml"),
        ("Playlist", "modify playlists"),
        ("Track", "modify tracks"),
        ("Theme", "change the theme"),
    ]
    COLUMNS = [
        ("Command", "command", 10),
        ("Description", "description", 18),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(cursor_type="row")

    def on_mount(self) -> None:
        for label, key, max_w in self.COLUMNS:
            self.add_column(label, key=key, width=max_w)
        for i, row in enumerate(self.ROWS):
            self.add_row(*row, key=str(i))


class PlaylistOptionsDataTable(VimDataTable):
    ROWS = [
        ("Append", "append track(s) into playlist(s)"),
        ("Create", "create a new playlist"),
        ("Delete", "delete a playlist"),
        ("Insert", "insert track(s) into playlist(s) at a specified position"),
        ("Remove", "remove track(s) from playlist(s)"),
    ]
    COLUMNS = [
        ("Command", "command", 10),
        ("Description", "description", 18),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(cursor_type="row")
        self.styles.display = "none"

    def on_mount(self) -> None:
        for label, key, max_w in self.COLUMNS:
            self.add_column(label, key=key, width=max_w)
        for i, row in enumerate(self.ROWS):
            self.add_row(*row, key=str(i))

    def run_command(self, command: str) -> None:
        match command:
            case "Append":
                self.app.push_screen(CmdLine("playlist append "))
            case "Create":
                self.app.push_screen(CmdLine("playlist create "))
            case "Delete":
                self.app.push_screen(CmdLine("playlist delete "))
            case "Insert":
                self.app.push_screen(CmdLine("playlist insert "))
            case "Remove":
                self.app.push_screen(CmdLine("playlist remove "))

    @on(OptionsDataTable.RowSelected)
    def option_selected(self, event: OptionsDataTable.RowSelected) -> None:
        command = self.get_cell_at(Coordinate(self.cursor_row, 0))
        self.run_command(command)


class TrackOptionsDataTable(VimDataTable):
    ROWS = [
        ("Favorite", "favorite track(s)"),
        ("Remove", "remove track(s)"),
        ("Import", "import media"),
    ]
    COLUMNS = [
        ("Command", "command", 10),
        ("Description", "description", 18),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(cursor_type="row")
        self.styles.display = "none"

    def on_mount(self) -> None:
        for label, key, max_w in self.COLUMNS:
            self.add_column(label, key=key, width=max_w)
        for i, row in enumerate(self.ROWS):
            self.add_row(*row, key=str(i))

    def run_command(self, command: str) -> None:
        match command:
            case "Favorite":
                self.app.push_screen(CmdLine("track favorite "))
            case "Remove":
                self.app.push_screen(CmdLine("track remove "))
            case "Import":
                self.app.push_screen(CmdLine("track import "))

    @on(OptionsDataTable.RowSelected)
    def option_selected(self, event: OptionsDataTable.RowSelected) -> None:
        command = self.get_cell_at(Coordinate(self.cursor_row, 0))
        self.run_command(command)


class ThemeOptionsDataTable(VimDataTable):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(cursor_type="row")
        self.styles.display = "none"

    def on_mount(self) -> None:
        self.add_column("Theme")
        themes = sorted(list(self.app.available_themes.keys()))
        for theme in themes:
            self.add_row(theme)

    @on(VimDataTable.RowSelected)
    def change_theme(self, event: VimDataTable.RowSelected) -> None:
        self.app.theme = self.get_cell_at(Coordinate(self.cursor_row, 0))


class OptionsSplit(Static):
    BINDINGS = [
        ("ctrl+h", "focus_left_table", "Focus Left"),
        ("ctrl+l", "focus_right_table", "Focus Right"),
    ]

    def __init__(self, api: Api, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.api = api
        self.options_data_table = OptionsDataTable()

        self.playlist_options_data_table = PlaylistOptionsDataTable()
        self.track_options_data_table = TrackOptionsDataTable()
        self.theme_options_data_table = ThemeOptionsDataTable()

    def compose(self):
        with Horizontal():
            yield self.options_data_table
            yield self.playlist_options_data_table
            yield self.track_options_data_table
            yield self.theme_options_data_table

    def on_show(self):
        self.options_data_table.focus()

    def action_focus_left_table(self):
        self.options_data_table.focus()

    def action_focus_right_table(self):
        """Focuses different tables. 0: Playlists, 1: Playlist Tracks"""
        if self.playlist_options_data_table.styles.display == "block":
            self.playlist_options_data_table.focus()
        elif self.track_options_data_table.styles.display == "block":
            self.track_options_data_table.focus()
        else:
            self.theme_options_data_table.focus()

    def run_command(self, command: str) -> None:
        match command:
            case "Scan":
                self.app.push_screen(CmdLine("scan ", auto_submit=True))
            case "iTunes":
                self.app.push_screen(CmdLine("itunes "))

    @on(OptionsDataTable.RowSelected)
    def option_selected(self, event: OptionsDataTable.RowSelected) -> None:
        table = self.options_data_table
        command = self.options_data_table.get_cell_at(Coordinate(table.cursor_row, 0))
        self.playlist_options_data_table.styles.display = "none"
        self.track_options_data_table.styles.display = "none"
        self.theme_options_data_table.styles.display = "none"
        match command:
            case "Playlist":
                table = self.playlist_options_data_table
            case "Track":
                table = self.track_options_data_table
            case "Theme":
                table = self.theme_options_data_table
            case _:
                self.run_command(command)

        if table:
            table.styles.display = "block"
            table.focus()
