from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Click
from textual.message import Message
from textual.widgets import Label, ProgressBar, Static

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

        self.track_metadata = Label(classes="metadata-value")

        self.progressbar = NowPlayingProgressBar()

        self.progressbar_pos = Label()
        self.progressbar_duration = Label()

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield self.track_metadata
            with Horizontal():
                yield self.progressbar_pos
                yield self.progressbar
                yield self.progressbar_duration

    def on_mount(self) -> None:
        self._timer = self.set_interval(0.25, self._tick)  # NOT in __init__

    @staticmethod
    def format_secs(secs: float) -> str:
        if secs <= 0:
            return "?:??"
        mins, secs = divmod(int(secs), 60)
        return f"{mins}:{secs:02d}"

    def _tick(self) -> None:
        # Detects if track is finished, skips to next if its the case.
        self.player.tick()
        current = self.player.cached_current_track
        if current is not self._shown and current is not None:
            self._shown = current
            # Update nowplaying
            favorited: str = "[$error] 󰋑 [/]" if current.favorite else "[gray] ♥ [/]"
            self.track_metadata.update(
                f"[gray]#{str(current.id or '').rjust(4, '0')}[/]"
                f"{favorited}"
                f"[$error] 󰈣 {(current.title or '')[:25]} [/]"
                f"[$primary] 󰠃 {(current.artist or '')[:20]} [/]"
                f"[$accent] 󱍙 {(current.album or '')[:25]} [/]"
            )
            # Update queue table
            self.post_message(self.TrackChanged())
        elif not current:
            self.track_metadata.update("")
        self.progressbar.update(total=self.player.duration, progress=self.player.pos)
        self.progressbar_pos.update(self.format_secs(self.player.pos))
        self.progressbar_duration.update(str(current.time) if current else "?:??")

    @on(NowPlayingProgressBar.Clicked)
    def progressbar_clicked(self, event: NowPlayingProgressBar.Clicked):
        self.player.seek(event.percentage * self.player.duration)
