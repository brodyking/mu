from textual import on
from textual.containers import Horizontal, Vertical
from textual.events import Click
from textual.message import Message
from textual.widgets import Label, ProgressBar, Static
from typer import progressbar

from muc.player import Player


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


class NowPlaying(Static):
    class TrackChanged(Message):
        def __init__(self) -> None:
            super().__init__()

    def __init__(self, player: Player, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.player = player

        self._shown: object = object()

        self.title_label = Label(classes="metadata-value")
        self.artist_label = Label(classes="metadata-value")
        self.album_label = Label(classes="metadata-value")

        self.progressbar = NowPlayingProgressBar()

    def compose(self):
        with Vertical():
            with Horizontal():
                yield Label(" 󰈣 ", classes="metadata-icon")
                yield self.title_label
                yield Label(" 󰠃 ", classes="metadata-icon")
                yield self.artist_label
                yield Label(" 󱍙 ", classes="metadata-icon")
                yield self.album_label
            yield self.progressbar

    def on_mount(self) -> None:
        self._timer = self.set_interval(0.25, self._tick)  # NOT in __init__

    def _tick(self) -> None:
        # Detects if track is finished, skips to next if its the case.
        self.player.tick()
        current = self.player.cached_current_track
        if current is not self._shown:
            self._shown = current
            # Update nowplaying
            self.title_label.update(current.title[:20] if current else "")
            self.artist_label.update(current.artist[:20] if current else "")
            self.album_label.update(current.album[:20] if current else "")
            # Update queue table
            self.post_message(self.TrackChanged())
        self.progressbar.update(total=self.player.duration, progress=self.player.pos)

    @on(NowPlayingProgressBar.Clicked)
    def progressbar_clicked(self, event: NowPlayingProgressBar.Clicked):
        self.player.seek(event.percentage * self.player.duration)
