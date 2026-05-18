from textual.app import ComposeResult
from textual.widgets import Static, Label, Button
from textual.containers import Horizontal, Vertical

from ms.database.track import Track

class Controls(Static):

    DEFAULT_CSS = """
    Controls > Horizontal {
        height: 3;
        width: auto;
        align: right middle;
    }
    Controls Button {
        border: none;
        height: 3;
        min-height: 3;
        max-width: 6; 
        min-width: 1;
        padding: 0 0;
        margin: 0 0 0 1;
        content-align: center middle;
        text-align: center;
    }

    .no-bg {
        min-width: 5;
        margin: 0 0 0 4;
        background: transparent!important;
        border: none!important;
    }

    Controls Button > .button--label {
        height: 3;
        content-align: center middle;
        text-align: center;
    }
    """

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.favorite = Button("",id="now-playing-controls-favorite",action="app.favorite_track(-1)",flat=True,classes="no-bg")
        self.previous = Button("⏮ ",id="now-playing-controls-previous",action="app.skip_track(-1)",flat=True)
        self.toggle = Button("⏸",id="now-playing-controls-toggle",action="app.pause_track()",flat=True,variant="primary")
        self.next= Button("⏭ ",id="now-playing-controls-next",action="app.skip_track(1)",flat=True)

    def set_favorite(self,is_favorite:bool) -> None:
        self.favorite.label = "" if is_favorite else ""
    
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self.favorite
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


    """


    def __init__(self):
        super().__init__()
        self.track_info = NowPlayingTrackInfo(id="now-playing-track-info")
        self.controls = Controls(id="now-playing-controls")

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self.track_info
            yield self.controls
                
    def set_track(self,track:Track):
        self.track_info.set_info(f"󰈣  {track.title}",f"󰠃  {track.artist}",f"󱍙  {track.album}")
        self.controls.set_favorite(track.favorite)
    def on_mount(self) -> None:
        pass
