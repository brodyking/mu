"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from mu.track import Track

from muc.client.widgets.tracksdatatable import TracksDataTable


class FavoritesDataTable(TracksDataTable):
    def __init__(self, tracks: dict[int, Track], show_filter: bool = True):
        super().__init__(tracks, show_filter)

    def generate_full_rows(self):
        super().generate_full_rows()
        self.full_rows = [row for row in self.full_rows if row[1] == "❤"]

    def set_track_favorite(self, track_id, is_favorite) -> None:
        super().set_track_favorite(track_id, is_favorite)

        self.generate_full_rows()

        # Add or remove the row from the visible table
        if is_favorite:
            row = next((r for r in self.full_rows if r[0] == track_id), None)
            if row:
                try:
                    self.main_table.add_row(*row, key=str(row[0]))
                except Exception:
                    pass  # Row already exists
        else:
            try:
                self.main_table.remove_row(str(track_id))
            except Exception:
                pass  # Row didn't exist

        self.filter_table("")
