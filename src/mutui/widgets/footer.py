from importlib.metadata import version

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label


class Footer(Widget):
    DEFAULT_CSS = """

    """
    APP_NAME = "µ"
    APP_VERSION = version("mu")

    time: reactive[str] = reactive("")

    def on_mount(self) -> None:
        self.set_interval(0.25, self._refresh_bindings)

    def _refresh_bindings(self) -> None:
        try:
            self.query_one("#footer-left", Label).update(self._bindings_text())
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
        left = "[b]mµ[/b]tui"
        yield Label(left, id="version")
        yield Label(self._bindings_text(), id="footer-left")
        yield Label(f"v{self.APP_VERSION}", id="footer-right")
