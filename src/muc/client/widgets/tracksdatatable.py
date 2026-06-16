"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.coordinate import Coordinate
from textual.events import Click
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Static

from mu.track import Track
from muc.client.widgets.vimdatatable import VimDataTable


class SortPopup(ModalScreen[str]):
    DEFAULT_CSS = """
    SortPopup {
        /* Forces everything inside the modal screen to center perfectly */
        align: center middle;

        /* The alpha percentage allows the underlying app screen to show through */
        /*background: black 40%;*/
        background: transparent;
    }

    VimDataTable {
        /* CRITICAL: Explicit dimensions isolate the popup geometry */
        width: 50;
        height: auto;

        /* Internal formatting */
        border: heavy $primary;
        padding: 0 0;
        align: center middle;
        overflow:hidden;
    }

    """

    TABLE = [
        ("i", "Sort by Id"),
        ("t", "Sort by Title"),
        ("A", "Sort by Artist"),
        ("a", "Sort by Album"),
        ("p", "Sort by Plays"),
        ("d", "Sort by Date Added"),
        ("g", "Sort by Genre"),
        ("d", "Sort by Date"),
        ("esc", "Cancel"),
    ]

    BINDINGS = [
        ("enter", "option_selected", "Select Option"),
        ("escape", "cancel_popup", "Close"),
        ("i", "dismiss_msg('id')", "Id"),
        ("t", "dismiss_msg('title')", "Title"),
        ("A", "dismiss_msg('artist')", "Artist"),
        ("a", "dismiss_msg('album')", "Album"),
        ("p", "dismiss_msg('plays')", "Plays"),
        ("d", "dismiss_msg('dateadded')", "Dateadded"),
        ("g", "dismiss_msg('genre')", "Genre"),
        ("d", "dismiss_msg('date')", "Date"),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.sort_options_data_table = VimDataTable(cursor_type="row")

    def compose(self) -> ComposeResult:
        yield self.sort_options_data_table

    def on_mount(self) -> None:

        self.sort_options_data_table.add_column("Bind", key=0, width=4)
        self.sort_options_data_table.add_column("Sorting Options", key=1, width=100)

        for row in self.TABLE:
            self.sort_options_data_table.add_row(row[0], row[1])

    def action_dismiss_msg(self, message: str):
        self.dismiss(message)

    @on(DataTable.RowSelected)
    def action_option_selected(self, event: DataTable.RowSelected):
        row = event.cursor_row
        value = self.sort_options_data_table.get_cell_at(Coordinate(row, 1))
        print(value)
        if value and "Sort by" in value:
            self.dismiss(value[7:].lower())
        else:
            self.dismiss("cancel")

    def action_cancel_popup(self):
        self.dismiss("cancel")


class TracksDataTable(Static):
    BINDINGS = [("/", "focus_search", "Search"), ("comma", "open_sort", "Sort")]

    DEFAULT_CSS = """
    TracksDataTable {
        width: 1fr;
        height: 1fr;
    }
    TracksDataTable > Vertical > Horizontal {
        height: 1;
    }
    TracksDataTable > Vertical > Horizontal > Input {
        width: 1fr;
    }
    #sort-button {
        width: 4;
        max-width:4;
    }
    """

    def __init__(self, tracks: dict[int, Track], search_id: str, main_table_id: str):
        super().__init__()
        self.tracks = tracks
        self.full_rows: list = []

        self.search = Input(placeholder="Filter tracks (/)", id=search_id)
        self.main_table = VimDataTable(cursor_type="row", id=main_table_id)
        self.sort_button = Button("󰒼", compact=True, id="sort-button")
        self.sort_popup = SortPopup()

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield self.search
                yield self.sort_button
            yield self.main_table

    # 2. Listen for the click event on that specific button
    @on(Button.Pressed, "#sort-button")
    def action_open_sort(self) -> None:
        # 3. Trigger the popup event here
        self.app.push_screen(SortPopup(), self.handle_popup_result)

    def handle_popup_result(self, result: str | None) -> None:
        # 4. Handle whatever the user picked in the popup
        if result:
            self.notify(result)

    # Focuses search with "/" key
    def action_focus_search(self) -> None:
        self.search.focus()

    @on(Input.Changed)
    def input_changed(self, event: Input.Changed) -> None:
        self.filter_table(event.value)

    # When the input is submitted, focus the main table of tracks
    @on(Input.Submitted)
    def input_submitted(self) -> None:
        self.main_table.focus()

    def set_track_favorite(self, track_id, is_favorite) -> None:
        """
        Toggles a tracks favorite icon
        TODO: Make it not refresh all rows when updating
        """
        try:
            self.main_table.update_cell(
                str(track_id), "favorite", "❤" if is_favorite else " "
            )
            self.tracks[track_id].favorite = is_favorite
            self.generate_full_rows()
        except Exception:
            return

    def set_track_plays(self, track_id: int, amount: int) -> None:
        """
        Sets a tracks play count
        TODO: Make it not refresh all rows when updating
        """
        try:
            self.main_table.update_cell(str(track_id), "plays", str(amount))
            self.tracks[track_id].plays = amount
            self.generate_full_rows()
        except Exception:
            return

    def filter_table(self, search_term: str) -> None:
        """Filters a table with the same prefix/query support as the database"""
        table = self.main_table
        queries = search_term.split("+")
        prefixes = {
            "id": 0,
            "favorite": 1,
            "title": 2,
            "artist": 3,
            "album": 4,
            "plays": 5,
            "time": 6,
            "dateadded": 7,
            "tracknumber": 8,
            "albumartist": 9,
            "discnumber": 10,
            "genre": 11,
            "date": 12,
            "filepath": 13,
            "filename": 14,
            "albumart": 15,
        }

        if not search_term:
            filtered_rows = self.full_rows
        else:
            filtered_rows = []
            for query in queries:
                filters = query.split("&")
                # Start with all rows, then narrow down
                query_rows = set(map(tuple, self.full_rows))

                for filter in filters:
                    filter = filter.strip()
                    if ":" not in filter:
                        value = filter.lower()
                        query_rows &= {
                            tuple(row)
                            for row in self.full_rows
                            if value in str(row[2]).lower()
                            or value in str(row[3]).lower()
                            or value in str(row[4]).lower()
                        }
                    else:
                        prefix, sep, value = filter.partition(":")
                        prefix, value = prefix.strip(), value.strip().lower()
                        if sep and prefix in prefixes and value:
                            row_index = prefixes[prefix]
                            query_rows &= {
                                tuple(row)
                                for row in self.full_rows
                                if value in str(row[row_index]).lower()
                            }

                # Add rows matched by this query group (avoiding duplicates)
                for row in self.full_rows:
                    if tuple(row) in query_rows and row not in filtered_rows:
                        filtered_rows.append(row)
        table.clear()

        for row in filtered_rows:
            table.add_row(*row, key=str(row[0]))

    def generate_full_rows(self):
        self.full_rows = []
        for trackid in self.tracks:
            track = self.tracks[trackid]
            favorite = "❤" if track.favorite else " "

            row_tuple = (
                track.id,
                favorite,
                track.title,
                track.artist,
                track.album,
                track.plays,
                track.time,
                track.dateadded,
                track.tracknumber,
                track.albumartist,
                track.discnumber,
                track.genre,
                track.date,
                track.filepath,
                track.filename,
                track.albumart,
            )
            self.full_rows.append(row_tuple)

    def on_mount(self) -> None:
        table = self.main_table

        # Add the maximum width to your column metadata definition
        columns = [
            ("Id", "id", None),
            ("", "favorite", 2),
            ("Title", "title", 25),
            ("Artist", "artist", 15),
            ("Album", "album", 15),
            ("Plays", "plays", 5),
            ("Time", "time", 5),
            ("Date Added", "dateadded", 10),
            ("Track Number", "tracknumber", 5),
            ("Album Artist", "albumartist", 15),
            ("Disc Number", "discnumber", 3),
            ("Genre", "genre", 15),
            ("Date", "date", 15),
            ("File Path", "filepath", None),
            ("File Name", "filename", None),
            ("Album Art", "albumart", None),
        ]

        # Use the max_width argument in add_column
        for label, key, max_w in columns:
            table.add_column(label, key=key, width=max_w)

        self.generate_full_rows()

        for row_tuple in self.full_rows:
            table.add_row(*row_tuple, key=str(row_tuple[0]))

        table.focus()
