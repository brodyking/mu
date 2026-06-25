"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from typing import Literal

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Static

from mu.track import Track
from muc.client.widgets.popups import AddToPopup, SortTracksPopup
from muc.client.widgets.vimdatatable import VimDataTable


class TracksDataTable(Static):
    BINDINGS = [
        ("/", "focus_search", "Search"),
        ("comma", "open_sort", "Sort"),
        (".", "open_addto", "Add to"),
    ]

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
        #sort-button, #addto-button {
            width: 8;
            max-width: 8;
        }
    """

    PREFIXES = {
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

    def __init__(
        self,
        tracks: dict[int, Track],
        show_filter: bool = True,
    ):
        super().__init__()
        self.tracks = tracks
        self.full_rows: list = []
        self.show_filter = show_filter

        self.search = Input(placeholder="Filter tracks (/)", id="search")
        self.main_table = VimDataTable(cursor_type="row", id="tracks-main-table")
        self.sort_button = Button("󰒼 Sort", compact=True, id="tracks-sort-button")
        self.addto_button = Button(" Add to", compact=True, id="addto-button")

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield self.search
                if self.show_filter:
                    yield self.sort_button
                yield self.addto_button
            yield self.main_table

    @on(Button.Pressed, "#sort-button")
    def action_open_sort(self) -> None:
        if self.show_filter:
            self.app.push_screen(SortTracksPopup(), callback=self.sort)  # type:ignore

    @on(Button.Pressed, "#addto-button")
    def action_open_addto(self) -> None:
        row_dict = self.main_table.export_cell_as_dict(self.main_table.cursor_row)
        if row_dict:
            popup = AddToPopup(row_dict, self.tracks)
            self.app.push_screen(popup)  # type:ignore

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
                        if sep and prefix in self.PREFIXES and value:
                            row_index = self.PREFIXES[prefix]
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
            table.add_row(*row, key=row[0])

    def sort(
        self,
        method: Literal[
            "artist",
            "album",
            "date",
            "dateadded",
            "id",
            "plays",
            "genre",
            "title",
            "cancel",
            "shuffle",
            "reset",
        ],
    ):
        """This is the callback function for the sort popup"""
        if method in (None, "cancel"):
            return

        if method == "reset":
            if method == "reset":
                self._last_sort = None
                self._sort_reverse = False
                self.generate_full_rows()
        elif method == "shuffle":
            import random

            random.shuffle(self.full_rows)
        else:
            numeric_cols = {"id", "plays", "tracknumber", "discnumber"}

            col_index = self.PREFIXES[method]
            reverse = getattr(self, "_sort_reverse", False)

            if getattr(self, "_last_sort", None) == method:
                reverse = not reverse
            else:
                reverse = False

            self._last_sort = method
            self._sort_reverse = reverse

            def sort_key(row):
                val = row[col_index]
                if val is None:
                    return (1, 0 if method in numeric_cols else "")
                if method in numeric_cols:
                    try:
                        return (0, int(val))
                    except (ValueError, TypeError):
                        return (1, 0)
                return (0, str(val).lower())

            self.full_rows.sort(key=sort_key, reverse=reverse)

        search_term = self.search.value
        if search_term:
            self.filter_table(search_term)
        else:
            self.main_table.clear()
            for row in self.full_rows:
                self.main_table.add_row(*row, key=str(row[0]))

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
