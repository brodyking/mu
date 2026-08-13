"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from typing import Any

from textual.app import ComposeResult
from textual.coordinate import Coordinate
from textual.screen import ModalScreen
from textual.widgets import DataTable
from textual.widgets._data_table import CellDoesNotExist


# A separate class to wrap the table and other widgets (like search)
class VimDataTable(DataTable):
    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("J", "scroll_bottom", "Last"),
        ("K", "scroll_top", "First"),
        ("y", "yank_row", "Yank"),
        ("tab", "inspect", "Inspect"),
    ]

    def __init__(self, show_inspect: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_inspect = show_inspect

    def export_row_as_dict(self, row: int) -> dict[str, Any]:
        if row >= len(self.rows):
            return {}
        row_dict = {}
        col_labels = [col.value for col in self.columns]
        for i, col_label in enumerate(col_labels):
            row_dict[col_label] = self.get_cell_at(Coordinate(row, i))
        return row_dict

    def action_yank_row(self) -> None:
        try:
            row_index = self.cursor_row
            row = self.export_row_as_dict(row_index)
            self.app.copy_to_clipboard(repr(row))
            self.app.notify("Row copied to clipboard")
        except CellDoesNotExist:
            self.app.notify("No row is selected", severity="error")

    def action_inspect(self) -> None:

        if not self.show_inspect:
            return

        try:
            row_dict = self.export_row_as_dict(self.cursor_row)
            popup = InspectRowPopup(row_dict)
            self.app.push_screen(popup)  # type:ignore
        except CellDoesNotExist:
            self.notify(
                "No row is selected",
                severity="error",
            )


class InspectRowPopup(ModalScreen[str]):
    BINDINGS = [
        ("escape", "dismiss_msg('cancel')", "Close"),
    ]

    def __init__(self, row_dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.main_table = VimDataTable(show_inspect=False, cursor_type="row")
        self.row_dict = row_dict

    def compose(self) -> ComposeResult:
        yield self.main_table

    def on_mount(self) -> None:

        self.main_table.add_column("Key", key="key", width=9)
        self.main_table.add_column("Value", key="value", width=100)

        for label in self.row_dict.keys():
            self.main_table.add_row(label, self.row_dict[label], key=label)

    def action_dismiss_msg(self, message: str):
        self.dismiss(message)
