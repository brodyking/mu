"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Input, Static

from mu.api import Api
from mu.models import Album
from muc.widgets.vimdatatable import VimDataTable


class AlbumsDataTable(Static):
    class AlbumClicked(Message):
        def __init__(self, album: Album, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.album = album

    BINDINGS = [
        ("/", "focus_search", "Search"),
    ]

    def __init__(self, api: Api):
        super().__init__()

        self.api = api

        self.full_rows: list = []

        self.search = Input(placeholder="Filter albums (/)", compact=True, id="search")
        self.main_table = VimDataTable(cursor_type="row", id="tracks-main-table")

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield self.search
            yield self.main_table

    def action_focus_search(self) -> None:
        self.search.focus()

    @on(Input.Submitted)
    def input_submitted(self, event: Input.Submitted) -> None:
        self.populate(event.value)
        self.redraw_rows()
        self.main_table.focus()

    @on(VimDataTable.RowSelected)
    def album_clicked(self, event: VimDataTable.RowSelected) -> None:
        row = self.main_table.export_row_as_dict(event.cursor_row)
        response = list(self.api.get_albums(f"album={row['album']}").values())
        if len(response) > 0:
            album = response[0]
            self.post_message(self.AlbumClicked(album))
        else:
            self.notify("Album not found", severity="error")

    def redraw_rows(self) -> None:
        self.main_table.clear()
        for i, row in enumerate(self.full_rows):
            self.main_table.add_row(*row, key=str(i))

    def populate(
        self,
        albums_term: str | None = None,
    ) -> None:
        """
        Clears and repopulates the table with albums. Calls the database
        each time this is called. Also supports search queries with standard
        mu search syntax. If no prefix is given, it searches albumartist
        and album.
        """

        self.full_rows = []

        if albums_term and ":" not in albums_term and "=" not in albums_term:
            albums_term = f"albumartist:{albums_term}+album:{albums_term}"

        try:
            albums: dict[tuple, Album] = self.api.get_albums(
                albums_term,
            )
        except ValueError as e:
            self.app.notify(str(e), severity="error", timeout=0.25)
            return

        for aid in albums:
            album = albums[aid]
            row_tuple = (album.title, album.albumartist, str(len(album.tracks)))
            self.full_rows.append(row_tuple)

    def on_mount(self) -> None:
        table = self.main_table

        # Add the maximum width to your column metadata definition
        columns = [
            ("Album", "album", 15),
            ("Album Artist", "albumartist", 15),
            ("Tracks", "tracks", 10),
        ]

        # Use the max_width argument in add_column
        for label, key, max_w in columns:
            table.add_column(label, key=key, width=max_w)

    def on_show(self) -> None:
        self.populate(self.search.value)
        self.redraw_rows()
        self.main_table.focus()

    def on_hide(self) -> None:
        self.main_table.clear()
