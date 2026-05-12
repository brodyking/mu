from textual.app import ComposeResult
from textual.widgets import DataTable, Input, Static
from ms.util import Interface

# A separate class to wrap the table and other widgets (like search)
class VimDataTable(DataTable):
    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
    ]

class TracksDataTable(Static):

    BINDINGS = [
        ("/", "focus_search","Search")
    ]
    
    def __init__(self, tracks: dict,search_id:str,main_table_id:str):
        super().__init__()
        self.tracks = tracks
        self.full_rows:list = []

        self.search = Input(placeholder="Filter tracks (/)", id=search_id)
        self.main_table = VimDataTable(cursor_type="row", id=main_table_id)

    def compose(self) -> ComposeResult:
        yield self.search
        yield self.main_table

    # Focuses search with "/" key
    def action_focus_search(self) -> None:
        self.search.focus()

    # When search bar's input is changed
    def on_input_changed(self,event: Input.Changed) -> None:
        self.filter_table(event.value)

    # When the input is submitted, focus the main table of tracks
    def on_input_submitted(self,event:Input.Submitted) -> None:
        self.main_table.focus()


    def filter_table(self, search_term: str) -> None:
        table = self.main_table
        search_term = search_term.lower()

        if not search_term:
            filtered_rows = self.full_rows
        else:

            prefixes = {
                "id": 0, "favorite":1,"title":2, "artist":3, "album":4, "plays":5, "time":6, "dateadded":7, "tracknumber":8, "albumartist":9, "discnumber":10, "genre":11, "date":12, "filepath":13, "filename":14, "albumart":15
            }

            if ":" in search_term and search_term.split(":",1)[0] in prefixes.keys():
                # Filter rows based on prefix provided
                filtered_rows = [
                    row for row in self.full_rows 
                    if search_term.split(":",1)[1] in str(row[prefixes.get(search_term.split(":",1)[0])]).lower()
                ]
            else:
                # Filter rows based on Title (index 2) or Artist (index 3)
                filtered_rows = [
                    row for row in self.full_rows 
                    if search_term in str(row[2]).lower() or search_term in str(row[3]).lower()
                ]

        table.clear()
        table.add_rows(filtered_rows)

    def on_mount(self) -> None:
        table = self.main_table
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

