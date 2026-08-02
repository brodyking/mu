from datetime import datetime
from importlib.metadata import version

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label


class MuFooter(Widget):
    DEFAULT_CSS = """
    MuFooter {
        height: 1;
        dock: bottom;
        background: $panel;
        color: $text;
        layout: horizontal;
    }
    MuFooter #version {
        width: auto;
        height: 1;
        padding: 0 1;
        background: $primary;
        color: $surface;
    }
    MuFooter #footer-left{
        width: 1fr;
        height: 1;
        padding: 0 1;
    }
    MuFooter #footer-right {
        dock: right;
        width: auto;
        height: 1;
        padding: 0 1;
        background: $primary;
        color: $surface;
    }
    """
    APP_NAME = "µ"
    APP_VERSION = version("mu")

    time: reactive[str] = reactive("")

    def on_mount(self) -> None:
        self._update_time()
        self.set_interval(1, self._update_time)

    def _update_time(self) -> None:
        self.time = datetime.now().strftime("%H:%M:%S")

    def watch_time(self, time: str) -> None:
        try:
            self.query_one("#footer-right", Label).update(self.time)
        except Exception:
            pass

    def _bindings_text(self) -> str:
        parts = []
        for key, active_binding in self.app.active_bindings.items():
            binding = active_binding.binding
            if binding.show:
                display_key = self.app.get_key_display(binding)
                parts.append(f"[b]{display_key}[/b] {binding.description}")
        return "  ".join(parts)

    def compose(self) -> ComposeResult:
        left = f"[b]{self.APP_NAME}[/b] v{self.APP_VERSION}"
        yield Label(left, id="version")
        yield Label(self._bindings_text(), id="footer-left")
        yield Label(self.time, id="footer-right")
