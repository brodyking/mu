"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Input, Static

from mu.api import Api
from mu.models import Artist
from muc.widgets.vimdatatable import VimDataTable


class ArtistsDataTable(Static):
    class ArtistClicked(Message):
        def __init__(self, artist: Artist, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.artist = artist

    BINDINGS = [
        ("/", "focus_search", "Search"),
    ]

    def __init__(self, api: Api):
        super().__init__()

        self.api = api

        self.full_rows: list = []

        self.search = Input(placeholder="Filter artists (/)", compact=True, id="search")
        self.main_table = VimDataTable(cursor_type="row", id="tracks-main-table")

    def compose(self) -> ComposeResult:
        with Vertical():
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
    def artist_clicked(self, event: VimDataTable.RowSelected) -> None:
        row = self.main_table.export_row_as_dict(event.cursor_row)
        response = list(self.api.get_artists(f'artist="{row["artist"]}"').values())
        if len(response) > 0:
            artist = response[0]
            self.post_message(self.ArtistClicked(artist))
        else:
            self.notify("Artist not found", severity="error")

    def redraw_rows(self) -> None:
        self.main_table.clear()
        for i, row in enumerate(self.full_rows):
            self.main_table.add_row(*row, key=str(i))

    def populate(
        self,
        artists_term: str | None = None,
    ) -> None:
        """
        Clears and repopulates the table with artsits. Calls the database
        each time this is called. Also supports search queries with standard
        mu search syntax. If no prefix is given, it searches artist and albumartist.
        """

        self.full_rows = []

        if artists_term and ":" not in artists_term and "=" not in artists_term:
            artists_term = f'albumartist:"{artists_term}",album:"{artists_term}"'

        try:
            artists: dict[str, Artist] = self.api.get_artists(
                artists_term, only_albumartists=True
            )
        except ValueError as e:
            self.app.notify(str(e), severity="error")
            return

        for artist_name in artists:
            artist = artists[artist_name]
            row_tuple = (artist.name, str(len(artist.tracks)))
            self.full_rows.append(row_tuple)

    def on_mount(self) -> None:
        table = self.main_table

        # Add the maximum width to your column metadata definition
        columns = [
            ("Artist", "artist", 15),
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
