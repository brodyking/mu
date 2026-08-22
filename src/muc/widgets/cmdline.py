"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import os

from textual import on
from textual.containers import Horizontal
from textual.coordinate import Coordinate
from textual.screen import ModalScreen
from textual.widgets import Input, Label

from muc.widgets.vimdatatable import VimDataTable


class CmdLineHintTable(VimDataTable):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.can_focus = False
        self.show_header = False

    def on_mount(self) -> None:
        self.add_column("Hint")


class CmdLine(ModalScreen[str]):
    BINDINGS = [
        ("esc", "dismiss", "Close"),
        ("up", "focus_hint_previous", "Previous hint"),
        ("ctrl+p", "focus_hint_previous", "Previous hint"),
        ("down", "focus_hint_next", "Next hint"),
        ("ctrl+n", "focus_hint_next", "Next hint"),
        ("tab", "accept_hint", "Accept hint"),
    ]

    COMMAND_TREE = {
        "scan": [],
        "version": [],
        "itunes": [],
        "list": ["tracks", "albums", "artists", "playlists", "playlist"],
        "playlist": ["append", "insert", "remove", "create", "delete"],
        "track": ["favorite", "remove", "import"],
    }

    def __init__(
        self, default_value: str = "", auto_submit: bool = False, *args, **kwargs
    ) -> None:
        self.search = Input(
            default_value,
            compact=True,
            select_on_focus=False,
        )
        self.prompt = Label("> mu")

        self.hint_table = CmdLineHintTable()
        self.in_subcommand = False
        self.auto_submit = auto_submit
        super().__init__(*args, **kwargs)

    def compose(self):
        yield self.hint_table
        with Horizontal():
            yield Label("> mu ")
            yield self.search

    def on_show(self) -> None:
        if self.auto_submit:
            self.on_submitted(Input.Submitted(self.search, self.search.value))
        self.update_hint_table(None)
        self.search.focus()

    @on(Input.Submitted)
    def on_submitted(self, event: Input.Submitted) -> None:
        with self.app.suspend():
            os.system("cls" if os.name == "nt" else "clear")
            os.system(f"mu {event.value}")
            input("Press Enter to return to muc")
        self.dismiss()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss()

    @on(Input.Changed)
    def update_hint_table(self, event: Input.Changed | None) -> None:
        self.hint_table.clear()

        if not event:
            hints = list(self.COMMAND_TREE.keys())
        else:
            command, _, subcommand = event.value.partition(" ")

            hints = []

            self.in_subcommand = command in self.COMMAND_TREE

            if self.in_subcommand:
                if not subcommand:
                    hints = self.COMMAND_TREE[command]
                else:
                    hints = (
                        hint
                        for hint in self.COMMAND_TREE[command]
                        if subcommand in hint
                    )
            else:
                if not command:
                    hints = list(self.COMMAND_TREE.keys())
                else:
                    hints = (
                        hint
                        for hint in self.COMMAND_TREE.keys()
                        if command == hint[: len(command)]
                    )

        for hint in hints:
            self.hint_table.add_row(hint)

    # @on(Input.Changed)
    # def update_hint_table(self, event: Input.Changed | None) -> None:
    #     self.hint_table.clear()
    #     for i, possible in enumerate(self.BASE_PARSER):
    #         if not event or (event.value.lower() == possible[: (len(event.value))]):
    #             self.hint_table.add_row(possible, key=str(i))

    def action_focus_hint_previous(self) -> None:
        self.hint_table.action_cursor_up()

    def action_focus_hint_next(self) -> None:
        self.hint_table.action_cursor_down()

    def action_accept_hint(self) -> None:
        try:
            hint = self.hint_table.get_cell_at(
                Coordinate(self.hint_table.cursor_row, 0)
            )
            if self.in_subcommand:
                self.search.value = f"{self.search.value.split(' ')[0]} {hint}"
            else:
                self.search.value = hint
            self.search.action_end()
        except Exception:
            ...
