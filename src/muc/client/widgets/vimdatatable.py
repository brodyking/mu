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
from textual.screen import ModalScreen
from textual.widgets import DataTable


class InspectRow(ModalScreen[str]):
    DEFAULT_CSS = """
    InspectRow {
        /* Forces everything inside the modal screen to center perfectly */
        align: center middle;

        /* The alpha percentage allows the underlying app screen to show through */
        /*background: black 40%;*/
        background: transparent;
    }

    VimDataTable {
        width: 45;
        height: auto;
        border: heavy $primary;
        padding: 0 0;
        align: center middle;
        overflow:hidden;
    }

    """

    BINDINGS = [
        ("escape", "dismiss_msg('cancel')", "Close"),
    ]

    def __init__(self, row_dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.main_table = VimDataTable(cursor_type="row")
        self.row_dict = row_dict

    def compose(self) -> ComposeResult:
        yield self.main_table

    def on_mount(self) -> None:

        self.main_table.add_column("Key", key=0, width=9)
        self.main_table.add_column("Value", key=1, width=100)

        for label in self.row_dict.keys():
            self.main_table.add_row(label, self.row_dict[label])

    def action_dismiss_msg(self, message: str):
        self.dismiss(message)


# A separate class to wrap the table and other widgets (like search)
class VimDataTable(DataTable):
    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("tab", "inspect", "Inspect"),
    ]

    CSS = """
    VimDataTable {
        width: auto;
        padding: 0;
        margin: 0;
    }
    """

    def action_inspect(self):

        col_labels = []
        for col in self.columns:
            col_labels.append(col.value)

        row_dict = {}
        for i, col_label in enumerate(col_labels):
            row_dict[col_label] = self.get_cell_at(Coordinate(self.cursor_row, i))

        popup = InspectRow(row_dict)
        self.app.push_screen(popup)  # type:ignore
