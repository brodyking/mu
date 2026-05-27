from textual.widgets import DataTable


# A separate class to wrap the table and other widgets (like search)
class VimDataTable(DataTable):
    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
    ]

    CSS = """
    VimDataTable {
        width: auto;
        padding: 0;
        margin: 0;
    }
    """
