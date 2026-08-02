"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import platform

from mu.track import Track
from PIL import Image as PILImage
from PIL import ImageOps
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Click
from textual.message import Message
from textual.widgets import Button, Label, ProgressBar, Static
from textual_image._terminal import get_cell_size
from textual_image.widget import Image

IS_UNIX = platform.system() in ("Darwin", "Linux")


class NowPlayingControls(Static):
    DEFAULT_CSS = """
        Button {
            width:3;
            padding:0;
            max-width: 3
        }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.favorite = Button(
            "",
            id="now-playing-controls-favorite",
            action="app.favorite_track()",
            compact=True,
            classes="no-bg",
        )
        self.previous = Button(
            "󰒫",
            id="now-playing-controls-previous",
            action="app.skip_track(-1)",
            compact=True,
        )
        self.toggle = Button(
            "󰏤",
            id="now-playing-controls-toggle",
            action="app.pause_track()",
            compact=True,
        )
        self.next = Button(
            "󰒬",
            id="now-playing-controls-next",
            action="app.skip_track(1)",
            compact=True,
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
    def __init__(self, *args, **kwargs):
        super().__init__(
            total=0, show_percentage=False, show_eta=False, *args, **kwargs
        )

    class Clicked(Message):
        def __init__(self, percentage: float, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.percentage = percentage

        pass

    @on(Click)
    def clicked(self, event: Click) -> None:
        percentage = event.x / self.size.width
        self.post_message(self.Clicked(percentage))

    def update_elapsed(self, elapsed_ms: int) -> None:
        self.update(progress=elapsed_ms)


class NowPlayingProgress(Static):
    DEFAULT_CSS = """
        NowPlayingProgress {
            height: 1;
            padding: 0;
            padding-top:0;
            background: $surface;
        }
        NowPlayingProgress > Horizontal {
            width: 1fr;
            height: 1;
        }
        NowPlayingProgress > Horizontal > Label {
            width: auto;
            height: 1;
            content-align: center middle;
            background: $primary;
            padding: 0 1;
            color: $background;
        }
        NowPlayingProgress > Horizontal > NowPlayingProgressBar {
            width: 1fr;
            height: 1;
            padding: 0 1;
        }
        NowPlayingProgress > Horizontal > NowPlayingProgressBar Bar {
            width: 100%;
            height: 1;
        }
        NowPlayingProgress > Horizontal > NowPlayingProgressBar Bar > .bar--bar {
            color: $primary;
            background: $panel;
        }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bar = NowPlayingProgressBar(id="now-playing-progress-bar")
        self.time_elapsed_ms = 0
        self.time_elapased_ms_label = Label("00:00")
        self.total_time_ms = 0
        self.total_time_ms_label = Label("00:00")

    @staticmethod
    def ms_to_min_sec(time_ms: int) -> str:
        seconds = time_ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def set_track(self, track: Track):
        self.total_time_ms = track.get_time_ms()
        self.total_time_ms_label.update(self.ms_to_min_sec(track.get_time_ms()))
        self.bar.update(total=self.total_time_ms, progress=0)

    def update_elapsed(self, elapsed_ms: int) -> None:
        self.time_elapased_ms = elapsed_ms
        self.time_elapased_ms_label.update(self.ms_to_min_sec(elapsed_ms))
        self.bar.update(progress=elapsed_ms)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self.time_elapased_ms_label
            yield self.bar
            yield self.total_time_ms_label


class NowPlayingTrackInfo(Static):
    DEFAULT_CSS = """

        Label {
            background: $surface
        }

        .icon {
            background: $primary;
            color: $background;
        }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = Label(" N/A ", id="now-playing-track-info-title")
        self.artist = Label(" N/A ", id="now-playing-track-info-artist")
        self.album = Label(" N/A ", id="now-playing-track-info-album")

    def set_track(self, track: Track) -> None:

        def format(text: str, length: int) -> str:
            return f" {text[: length - 3]} " if len(text) >= length else f" {text} "

        self.title.update(format(track.title, 30))
        self.artist.update(format(track.artist, 25))
        self.album.update(format(track.album, 25))

    def compose(self):
        with Vertical():
            with Horizontal():
                yield Label(" 󰈣 ", classes="icon")
                yield self.title
                yield Label(" 󰠃 ", classes="icon")
                yield self.artist
                yield Label(" 󱍙 ", classes="icon")
                yield self.album


class NowPlaying(Static):
    SHOW_ALBUM_ART = False

    DEFAULT_CSS = """
        Image {
            min-width: 4;
            min-height: 2;
            max-width: 4;
            max-height: 2;
            background: $panel;
        }


        NowPlaying > Horizontal {
            width: 100%;
            height: 2;
        }
        NowPlayingTrackInfo {
            width: 1fr;
            height: 1;
        }
        .transport {
            width: 1fr;
            height: 1;
        }
        .transport > NowPlayingProgress {
            width: 1fr;
        }
        .transport > NowPlayingControls {
            width: 12;
            height: 1;
        }
    """

    def __init__(self):
        super().__init__()
        self.cover_art = Image("")
        self.track_info = NowPlayingTrackInfo(id="now-playing-track-info")
        self.controls = NowPlayingControls(id="now-playing-controls")
        self.progress = NowPlayingProgress(id="now-playing-progress")

    def compose(self) -> ComposeResult:
        with Horizontal():
            if IS_UNIX and self.SHOW_ALBUM_ART:
                yield self.cover_art
            with Vertical():
                yield self.track_info
                with Horizontal(classes="transport"):
                    yield self.progress
                    yield self.controls

    @staticmethod
    def fit_image(path: str, max_cells_w: int, max_cells_h: int) -> PILImage.Image:
        cell = get_cell_size()
        img = PILImage.open(path)
        return ImageOps.fit(
            img,
            (max_cells_w * cell.width, max_cells_h * cell.height),
            PILImage.LANCZOS,
        )

    def set_track(self, track: Track):
        self.track_info.set_track(track)
        self.controls.set_favorite(track.favorite)
        self.progress.set_track(track)
        if IS_UNIX and self.cover_art:
            self.cover_art.image = self.fit_image(track.albumart, 4, 2)
