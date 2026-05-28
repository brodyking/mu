from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Label, ProgressBar, Static
from textual.message import Message
from textual.events import Click 

from mu.database.track import Track


class NowPlayingControls(Static):
    DEFAULT_CSS = """
        NowPlayingControls > Horizontal {
            height: 3;
            width: auto;
            align: right middle;
        }
        NowPlayingControls Button {
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

        NowPlayingControls Button > .button--label {
            height: 3;
            content-align: center middle;
            text-align: center;
        }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.favorite = Button(
            "",
            id="now-playing-controls-favorite",
            action="app.favorite_track(-1)",
            flat=True,
            classes="no-bg",
        )
        self.previous = Button(
            "⏮ ",
            id="now-playing-controls-previous",
            action="app.skip_track(-1)",
            flat=True,
        )
        self.toggle = Button(
            "⏸", id="now-playing-controls-toggle", action="app.pause_track()", flat=True
        )
        self.next = Button(
            "⏭ ", id="now-playing-controls-next", action="app.skip_track(1)", flat=True
        )

    def set_favorite(self, is_favorite: bool) -> None:
        self.favorite.label = "" if is_favorite else ""

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self.favorite
            yield self.previous
            yield self.toggle
            yield self.next


class NowPlayingProgressBar(ProgressBar):
    DEFAULT_CSS = """
        NowPlayingProgressBar Bar {
            width: 1fr;
            height:2;
        }
        NowPlayingProgressBar {
            height:2;
            padding:0;
            padding-left:2;
            padding-right:2;
        }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            total=0, show_percentage=False, show_eta=False, *args, **kwargs
        )

    class Clicked(Message):
        def __init__(self,percentage:float,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.percentage = percentage
        pass

    def on_click(self, event: Click) -> None:
        percentage = event.x / self.size.width
        self.post_message(self.Clicked(percentage))

    def set_track(self, track: Track):
        self.update(total=track.get_time_ms(), progress=0)

    def update_elapsed(self, elapsed_ms: int) -> None:
        self.update(progress=elapsed_ms)


class NowPlayingTrackInfo(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = Label("󰈣", id="now-playing-track-info-title")
        self.artist = Label("󰠃", id="now-playing-track-info-artist")
        self.album = Label("󱍙", id="now-playing-track-info-album")

    def set_info(self, title, artist, album):
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
        NowPlaying > Vertical {
            width: 100%;
            height: 5;
            padding: 1;
            padding-left: 2;
            padding-right: 2
        }
        NowPlayingTrackInfo {
            width: 1fr;
            height: auto;
        }
        NowPlayingControls { 
            width: auto;
            height:auto;
        }
        NowPlayingControls > Horizontal {
            align: right middle;
            width: auto;
        }
    """

    def __init__(self):
        super().__init__()
        self.track_info = NowPlayingTrackInfo(id="now-playing-track-info")
        self.controls = NowPlayingControls(id="now-playing-controls")
        self.progress_bar = NowPlayingProgressBar(id="now-playing-progress-bar")

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield self.track_info
                yield self.controls
        yield self.progress_bar

    def set_track(self, track: Track):
        self.track_info.set_info(
            f"󰈣  {track.title}", f"󰠃  {track.artist}", f"󱍙  {track.album}"
        )
        self.controls.set_favorite(track.favorite)
        self.progress_bar.set_track(track)

    def on_mount(self) -> None:
        pass
