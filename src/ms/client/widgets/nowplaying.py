from ms.database.track import Track
from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import Horizontal, Vertical

class NowPlayingTrackInfo(Static):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.title = Label("",id="now-playing-track-info-title")
        self.artist= Label("",id="now-playing-track-info-artist")
        self.album= Label("",id="now-playing-track-info-album")

    def set_info(self,title,artist,album):
        self.title.update(title)
        self.artist.update(artist)
        self.album.update(album)
        
    def compose(self):
        with Vertical():
            yield self.title
            yield self.artist
            yield self.album

class NowPlaying(Static):
    
    def __init__(self):
        super().__init__()
        self.track_info = NowPlayingTrackInfo(id="now-playing-track-info")

    def compose(self) -> ComposeResult:
        yield self.track_info
                
    def set_track(self,title,artist,album):
        self.track_info.set_info(title,artist,album)
    
    def on_mount(self) -> None:
        pass
