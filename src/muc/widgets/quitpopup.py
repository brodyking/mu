"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Label


class QuitPopup(ModalScreen[str]):
    BINDINGS = [("escape", "dismiss", "Close"), ("enter", "confirm", "Confirm")]

    class Confirm(Message):
        def __init__(self) -> None:
            super().__init__()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Are you sure you want to quit?")
            yield Label(
                "[$error]Yes (enter)[/] / [$success]Cancel (esc)[/]", expand=True
            )

    def action_confirm(self) -> None:
        self.post_message(self.Confirm())
        self.dismiss()
