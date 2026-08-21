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
from textual.screen import ModalScreen
from textual.suggester import SuggestFromList
from textual.widgets import Input, Label


class CmdLine(ModalScreen[str]):
    BINDINGS = [("esc", "dismiss", "Close")]

    POSSIBLE_COMMANDS = [
        "scan",
        "version",
        "itunes",
        "list",
        "list tracks",
        "list albums",
        "list artists",
        "list playlists",
        "list playlist",
        "playlist",
        "playlist append",
        "playlist create",
        "playlist delete",
        "playlist insert",
        "playlist remove",
        "track",
        "track favorite",
        "track remove",
        "track import",
    ]

    def __init__(
        self, default_value: str = "", auto_submit: bool = False, *args, **kwargs
    ) -> None:
        self.search = Input(
            default_value,
            compact=True,
            select_on_focus=False,
            suggester=SuggestFromList(self.POSSIBLE_COMMANDS, case_sensitive=False),
        )
        self.auto_submit = auto_submit
        super().__init__(*args, **kwargs)

    def compose(self):
        with Horizontal():
            yield Label("> mu ")
            yield self.search

    def on_show(self) -> None:
        if self.auto_submit:
            self.on_submitted(Input.Submitted(self.search, self.search.value))
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
