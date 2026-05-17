from textual.app import ComposeResult
from textual.widgets import Static, Label, Button
from textual.containers import Horizontal, Vertical

class Controls(Static):
    def __init__(self,*args,**kwargs):
        """
            Play: ▶
            Pause: ⏸ 
            ⏯ 
            ⏭ 
            ⏮ (U+23EE)
            """
        super().__init__(*args,**kwargs)
        self.previous = Button("⏮ ",id="now-playing-controls-previous",action="app.skip_track(1)")
        self.toggle = Button("⏸",id="now-playing-controls-toggle")
        self.next= Button("⏭",id="now-playing-controls-next",action="app.skip_track(1)")
    
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self.previous
            yield self.toggle
            yield self.next


class NowPlayingTrackInfo(Static):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.title = Label("󰈣",id="now-playing-track-info-title")
        self.artist= Label("󰠃",id="now-playing-track-info-artist")
        self.album= Label("󱍙",id="now-playing-track-info-album")

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
    
    DEFAULT_CSS = """
    NowPlaying > Horizontal {
        width: 100%;
        height: 5;
        padding: 1;
        padding-left: 2;
        padding-right: 2
    }

    #now-playing-track-info {
        width: 1fr;           /* Fills all leftover space, forcing controls to the right */
    }

    #now-playing-controls {
        width: auto;          /* Shrinks wrapper strictly to the width of the buttons */
    }

    #now-playing-controls > Horizontal {
        align: right middle;  /* Aligns the buttons tightly to the right side */
        width: auto;
    }

    #now-playing-controls Button {
        min-width: 4;         /* Keeps buttons small and compact */
        margin-left: 1;       /* Adds a little breathing room between buttons */
    }
    """

    def __init__(self):
        super().__init__()
        self.track_info = NowPlayingTrackInfo(id="now-playing-track-info")
        self.controls = Controls(id="now-playing-controls")

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self.track_info
            yield self.controls
                
    def set_track(self,title,artist,album):
        self.track_info.set_info(f"󰈣  {title}",f"󰠃  {artist}",f"󱍙  {album}")
    
    def on_mount(self) -> None:
        pass
