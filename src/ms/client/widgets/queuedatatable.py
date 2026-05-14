from ms.client.widgets.tracksdatatable import TracksDataTable
from ms.util import Interface

class QueueDataTable(TracksDataTable):
    def __init__(self,*args,**kwargs):
        super().__init__(dict(),*args,**kwargs)

    def update_queue(self, tracks):
        self.tracks = tracks
        self.full_rows = []
        self.main_table.clear()
        for track in self.tracks:
            favorite = "❤" if track.favorite else " "
            
            row_tuple = (
                track.id,
                favorite,
                Interface.fmt(track.title, 50),
                Interface.fmt(track.artist, 30),
                Interface.fmt(track.album, 50),
                Interface.fmt(track.plays, 5),
                Interface.fmt(track.time, 10),
                Interface.fmt(track.dateadded, 20),
                Interface.fmt(track.tracknumber, 10),
                Interface.fmt(track.albumartist, 30),
                Interface.fmt(track.discnumber, 10),
                Interface.fmt(track.genre, 20),
                Interface.fmt(track.date, 20),
                track.filepath,
                track.filename,
                track.albumart,
            )
            self.full_rows.append(row_tuple)
            self.main_table.add_row(*row_tuple, key=str(track.id))

