from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.coordinate import Coordinate
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Label

from muc.widgets.vimdatatable import VimDataTable


class Popup(ModalScreen[str]):
    """
    Base popup class. All widgets being
    composed should be placed inside of
    self.content
    """

    BINDINGS = [("escape", "dismiss", "Close")]

    def __init__(self, title: str = "", subtitle: str = "", *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        self.content: Vertical = Vertical()
        self.content.border_title = title
        self.content.border_subtitle = subtitle

    def compose(self) -> ComposeResult:
        with self.content:
            yield Label("test")


class ConfirmPopup(Popup):
    class Submitted(Message):
        def __init__(self, response: bool) -> None:
            super().__init__()
            self.response = response

    BINDINGS = [("enter", "submit", "Submit")]

    def __init__(self, prompt: str, title: str = "Confirm", subtitle: str = ""):
        super().__init__(title, subtitle)

        self.prompt: Label = Label(prompt)
        self.response: bool = False

    def compose(self) -> ComposeResult:
        with self.content:
            yield self.prompt
            yield Label(
                "[$error]Yes (enter)[/] / [$success]Cancel (esc)[/]", expand=True
            )

    async def action_submit(self, message: Message | None = None, *args, **kwargs):
        self.post_message(self.Submitted(True) if not message else message)
        await super().action_dismiss(*args, **kwargs)

    async def action_dismiss(self, message: Message | None = None, *args, **kwargs):
        self.post_message(self.Submitted(False) if not message else message)
        await super().action_dismiss(*args, **kwargs)


class BindsDataTablePopup(Popup):
    class Selected(Message):
        def __init__(self, bind: str, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

    def __init__(
        self,
        title: str,
        binds: dict[str, str],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(title, *args, **kwargs)
        self.main_table = VimDataTable(show_inspect=False, cursor_type="row")
        self.binds = binds

    def compose(self) -> ComposeResult:
        with self.content:
            yield self.main_table

    def on_mount(self) -> None:

        self.main_table.add_column("Bind", key="bind", width=4)
        self.main_table.add_column("Option", key="sorting-options", width=100)

        for bind in self.binds:
            self.main_table.add_row(bind, self.binds[bind])

        print(self.BINDINGS)

    def action_dismiss_msg(self, bind: str):
        self.post_message(self.Selected(bind))
        self.dismiss(bind)

    @on(VimDataTable.RowSelected)
    def action_option_selected(self, event: VimDataTable.RowSelected):
        row = event.cursor_row
        value = self.main_table.get_cell_at(Coordinate(row, 0))
        self.action_dismiss_msg(value)


class QuitPopup(ConfirmPopup):
    class Submitted(ConfirmPopup.Submitted): ...

    def __init__(self, *args, **kwargs):
        super().__init__("Are you sure you want to quit?", title="Quit?")
