"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from textual import on
from textual.app import ComposeResult
from textual.coordinate import Coordinate
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import DataTable

from mu.track import Track
from muc.client.widgets.vimdatatable import VimDataTable


class SortTracksPopup(ModalScreen[str]):
    DEFAULT_CSS = """
    SortTracksPopup {
        align: center middle;
        background: transparent;
    }

    VimDataTable {
        width: 35;
        height: auto;
        border: heavy $primary;
        padding: 0 0;
        align: center middle;
        overflow:hidden;
    }

    """

    TABLE = [
        ("A", "Sort by Artist"),
        ("a", "Sort by Album"),
        ("D", "Sort by Date"),
        ("d", "Sort by Date Added"),
        ("g", "Sort by Genre"),
        ("i", "Sort by Id"),
        ("p", "Sort by Plays"),
        ("s", "Sort by Shuffle"),
        ("t", "Sort by Title"),
        ("r", "Reset"),
        ("esc", "Cancel"),
    ]

    BINDINGS = [
        ("enter", "option_selected", "Select Option"),
        ("escape", "dismiss_msg('cancel')", "Close"),
        ("i", "dismiss_msg('id')", "Id"),
        ("t", "dismiss_msg('title')", "Title"),
        ("A", "dismiss_msg('artist')", "Artist"),
        ("a", "dismiss_msg('album')", "Album"),
        ("p", "dismiss_msg('plays')", "Plays"),
        ("d", "dismiss_msg('dateadded')", "Dateadded"),
        ("g", "dismiss_msg('genre')", "Genre"),
        ("s", "dismiss_msg('shuffle')", "Genre"),
        ("D", "dismiss_msg('date')", "Date"),
        ("r", "dismiss_msg('reset')", "Reset"),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.main_table = VimDataTable(show_inspect=False, cursor_type="row")

    def compose(self) -> ComposeResult:
        yield self.main_table

    def on_mount(self) -> None:

        self.main_table.add_column("Bind", key="bind", width=4)
        self.main_table.add_column("Sorting Options", key="sorting-options", width=100)

        for row in self.TABLE:
            self.main_table.add_row(row[0], row[1])

    def action_dismiss_msg(self, message: str):
        self.dismiss(message)

    @on(DataTable.RowSelected)
    def action_option_selected(self, event: DataTable.RowSelected):
        row = event.cursor_row
        value = self.main_table.get_cell_at(Coordinate(row, 1))
        if value and "Sort by" in value:
            self.action_dismiss_msg(value[7:].lower().replace(" ", ""))
        else:
            self.action_dismiss_msg(value.lower())


class AddToPopup(ModalScreen[str]):
    DEFAULT_CSS = """
    AddToPopup {
        align: center middle;
        background: transparent;
    }

    VimDataTable {
        width: 30;
        height: auto;
        border: heavy $primary;
        padding: 0 0;
        align: center middle;
        overflow:hidden;
    }

    """
    TABLE = [
        ("l", "Queue Last"),
        ("n", "Queue Next"),
        ("esc", "Cancel"),
    ]

    BINDINGS = [
        ("enter", "option_selected", "Select Option"),
        ("escape", "dismiss_msg('cancel')", "Close"),
        ("l", "dismiss_msg('last')", "Queue Last"),
        ("n", "dismiss_msg('next')", "Queue Next"),
    ]

    class AddToQueueLast(Message):
        def __init__(self, track: Track | None, *args, **kwargs):
            self.track = track
            super().__init__(*args, **kwargs)

    class AddToQueueNext(Message):
        def __init__(self, track: Track | None, *args, **kwargs):
            self.track = track
            super().__init__(*args, **kwargs)

    def __init__(self, row_dict, tracks, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.main_table = VimDataTable(show_inspect=False, cursor_type="row")

        self.track = tracks[row_dict["id"]] if row_dict else None

    def compose(self) -> ComposeResult:
        yield self.main_table

    def on_mount(self) -> None:

        self.main_table.add_column("Bind", key="bind", width=4)
        self.main_table.add_column("Sorting Options", key="sorting-options", width=100)

        for row in self.TABLE:
            self.main_table.add_row(row[0], row[1])

    @on(DataTable.RowSelected)
    def action_option_selected(self, event: DataTable.RowSelected):
        row = event.cursor_row
        value = self.main_table.get_cell_at(Coordinate(row, 1))
        match value:
            case "Queue Last":
                self.action_dismiss_msg("last")
            case "Queue Next":
                self.action_dismiss_msg("next")
            case _:
                self.action_dismiss_msg("Cancel")

    def action_dismiss_msg(self, message: str):
        match message:
            case "last":
                self.post_message(self.AddToQueueLast(self.track))
            case "next":
                self.post_message(self.AddToQueueNext(self.track))
        self.dismiss(message)
