"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from muc.client.widgets.tracksdatatable import TracksDataTable


class QueueDataTable(TracksDataTable):
    def __init__(self, *args, **kwargs):
        super().__init__(dict(), show_filter=False, *args, **kwargs)

    def update_queue(self, tracks):
        self.tracks = tracks
        self.full_rows = []
        self.main_table.clear()
        for i, track in enumerate(self.tracks):
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
            self.main_table.add_row(*row_tuple, key=str(i))
