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
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

from mu.api import Api
from mu.models import Playlist
from muc.widgets.vimdatatable import VimDataTable


class CreatePlaylistPopup(ModalScreen[str]):
    BINDINGS = [("escape", "dismiss", "Close"), ("enter", "create", "Create")]

    class CreatePlaylist(Message):
        def __init__(self, title: str, description: str, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.title = title
            self.description = description

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.vertical = Vertical()
        self.vertical.border_title = "Create Playlist"
        self.title_input = Input(placeholder="Title", compact=True, valid_empty=True)
        self.description_input = Input(placeholder="Description", compact=True)

        self.border_title = "Create Playlist"

    def compose(self):
        with self.vertical:
            yield self.title_input
            yield self.description_input

    @on(Input.Submitted)
    def action_create(self):
        self.post_message(
            self.CreatePlaylist(self.title_input.value, self.description_input.value)
        )
        self.dismiss()


class DeletePlaylistPopup(ModalScreen[str]):
    BINDINGS = [("escape", "dismiss", "Close"), ("enter", "confirm", "Confirm")]

    class DeletePlaylist(Message):
        def __init__(self, pid: int, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.pid = pid

    def __init__(self, pid: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pid = pid

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Are you sure you want to delete this playlist?")
            yield Label(
                "[$error]Yes (enter)[/] / [$success]Cancel (esc)[/]", expand=True
            )

    def action_confirm(self) -> None:
        self.post_message(self.DeletePlaylist(self.pid))
        self.dismiss()


class PlaylistsDataTable(Static):
    class PlaylistClicked(Message):
        def __init__(self, playlist: Playlist, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.playlist = playlist

    BINDINGS = [
        ("/", "focus_search", "Search"),
        ("d", "delete_playlist", "Delete"),
        ("a", "create_playlist", "Create"),
    ]

    def __init__(self, api: Api):
        super().__init__()

        self.api = api

        self.full_rows: list = []

        self.search = Input(placeholder="Filter playlists (/)", compact=True)
        self.main_table = VimDataTable(cursor_type="row")

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
    def playlist_clicked(self, event: VimDataTable.RowSelected) -> None:
        row = self.main_table.export_row_as_dict(event.cursor_row)
        response = list(self.api.get_playlists(f"id={row['id']}").values())
        if len(response) > 0:
            playlist = response[0]
            self.post_message(self.PlaylistClicked(playlist))
        else:
            self.notify("Playlist not found", severity="error")

    def action_delete_playlist(self) -> None:
        row_index: int = self.main_table.cursor_row
        pid: int = int(self.main_table.export_row_as_dict(row_index)["id"])
        self.app.push_screen(DeletePlaylistPopup(pid))

    def action_create_playlist(self) -> None:
        self.app.push_screen(CreatePlaylistPopup())

    def redraw_rows(self) -> None:
        self.main_table.clear()
        for i, row in enumerate(self.full_rows):
            self.main_table.add_row(*row, key=str(i))

    def populate(
        self,
        playlists_term: str | None = None,
    ) -> None:
        """
        Clears and repopulates the table with playlists. Calls the database
        each time this is called. Also supports search queries with standard
        mu search syntax. If no prefix is given, it searches title and description.
        """

        self.full_rows = []

        if playlists_term and ":" not in playlists_term and "=" not in playlists_term:
            playlists_term = f'title:"{playlists_term}",description:"{playlists_term}"'

        try:
            playlists: dict[int, Playlist] = self.api.get_playlists(playlists_term)
        except ValueError as e:
            self.app.notify(str(e), severity="error")
            return

        for pid in playlists:
            playlist = playlists[pid]
            row_tuple = (
                playlist.id,
                playlist.title,
                playlist.description,
                str(len(playlist.tracks)),
            )
            self.full_rows.append(row_tuple)

    def on_mount(self) -> None:
        table = self.main_table

        # Add the maximum width to your column metadata definition
        columns = [
            ("Id", "id", None),
            ("Title", "title", 20),
            ("Description", "description", 10),
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
