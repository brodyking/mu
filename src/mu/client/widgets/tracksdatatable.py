from textual.app import ComposeResult
from textual.widgets import DataTable, Input, Static
from mu.util import Interface


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


class TracksDataTable(Static):
    BINDINGS = [("/", "focus_search", "Search")]

    CSS = """
    TracksDataTable {
        width: auto;
        height: auto;
    }
    """

    def __init__(self, tracks: dict, search_id: str, main_table_id: str):
        super().__init__()
        self.tracks = tracks
        self.full_rows: list = []

        self.search = Input(placeholder="Filter tracks (/)", id=search_id)
        self.main_table = VimDataTable(cursor_type="row", id=main_table_id)

    def compose(self) -> ComposeResult:
        yield self.search
        yield self.main_table

    # Focuses search with "/" key
    def action_focus_search(self) -> None:
        self.search.focus()

    # When search bar's input is changed
    def on_input_changed(self, event: Input.Changed) -> None:
        self.filter_table(event.value)

    # When the input is submitted, focus the main table of tracks
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.main_table.focus()

    def set_track_favorite(self, track_id, is_favorite) -> None:
        try:
            self.main_table.update_cell(
                str(track_id), "favorite", "❤" if is_favorite else " "
            )
        except:
            return

    def filter_table(self, search_term: str) -> None:
        table = self.main_table
        search_term = search_term.lower()

        if not search_term:
            filtered_rows = self.full_rows
        else:
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

            if ":" in search_term and search_term.split(":", 1)[0] in prefixes.keys():
                # Filter rows based on prefix provided
                filtered_rows = [
                    row
                    for row in self.full_rows
                    if search_term.split(":", 1)[1]
                    in str(row[prefixes.get(search_term.split(":", 1)[0])]).lower()
                ]
            else:
                # Filter rows based on Title (index 2) or Artist (index 3)
                filtered_rows = [
                    row
                    for row in self.full_rows
                    if search_term in str(row[2]).lower()
                    or search_term in str(row[3]).lower()
                ]

        table.clear()

        for row in filtered_rows:
            table.add_row(*row, key=str(row[0]))

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
            table.add_row(*row_tuple, key=str(track.id))

        table.focus()
