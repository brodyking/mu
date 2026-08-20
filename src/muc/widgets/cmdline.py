"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from textual import on
from textual.containers import Horizontal
from textual.screen import ModalScreen
from textual.widgets import Input, Label
import os


class CmdLine(ModalScreen[str]):
    BINDINGS = [("esc", "dismiss", "Close")]

    def __init__(self, *args, **kwargs) -> None:
        self.output = Label()
        self.search = Input(compact=True, select_on_focus=False)
        super().__init__(*args, **kwargs)

    def compose(self):
        with Horizontal():
            yield Label("> mu ")
            yield self.search

    def on_show(self) -> None:
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
