from textual.app import ComposeResult
from textual.widgets import DataTable, Input, Static
from ms.util import Interface

# A separate class to wrap the table and other widgets (like search)
class VimDataTable(DataTable):
    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("h", "cursor_left", "Left"),
        ("l", "cursor_right", "Right"),
        ("g", "scroll_home", "Top"),
        ("G", "scroll_end", "Bottom")
    ]

class TracksDataTable(Static):
    
    def __init__(self, tracks: dict):
        super().__init__()
        self.tracks = tracks
        self.full_rows:list = []

        self.search = Input(placeholder="Filter tracks...", id="tracks-data-table-search")
        self.main_table = VimDataTable(cursor_type="row", id="tracks-data-table-table")

    def compose(self) -> ComposeResult:
        yield self.search
        yield self.main_table

    def filter_table(self, search_term: str) -> None:
        table = self.query_one(VimDataTable)
        search_term = search_term.lower()

        if not search_term:
            filtered_rows = self.full_rows
        else:
            # Filter rows based on Title (index 2) or Artist (index 3)
            filtered_rows = [
                row for row in self.full_rows 
                if search_term in str(row[2]).lower() or search_term in str(row[3]).lower()
            ]

        table.clear()
        table.add_rows(filtered_rows)

    def on_mount(self) -> None:
        table = self.query_one(VimDataTable)
        table.add_columns(
            "Id",
            "",
            "Title",
            "Artist",
            "Album",
            "Plays",
            "Time",
            "Date Added",
            "Track Number",
            "Album Artist",
            "Disc Number",
            "Genre",
            "Date",
            "File Path",
            "File Name",
            "Album Art",
        )

        rows = []
        for trackid in self.tracks:
            track = self.tracks[trackid]

            favorite = "❤" if track.favorite else " "
            
            rows.append(
                (
                    track.id,
                    favorite,
                    Interface.fmt(track.title,50),
                    Interface.fmt(track.artist,30),
                    Interface.fmt(track.album,50),
                    Interface.fmt(track.plays,5),
                    Interface.fmt(track.time,10),
                    Interface.fmt(track.dateadded,20),
                    Interface.fmt(track.tracknumber,10),
                    Interface.fmt(track.albumartist,30),
                    Interface.fmt(track.discnumber,10),
                    Interface.fmt(track.genre,20),
                    Interface.fmt(track.date,20),
                    track.filepath,
                    track.filename,
                    track.albumart
                )
            )
        self.full_rows = rows
        table.add_rows(rows)
        table.focus()
