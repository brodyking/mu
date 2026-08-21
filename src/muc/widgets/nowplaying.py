from textual import events, on
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


class NowPlayingVolumeBar(ProgressBar):
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


class NowPlayingMetaData(Static):
    tid = Label()
    favorite = Label(id="now-playing-metadata-favorite")
    title = Label()
    artist = Label()
    album = Label()

    def compose(self):
        with Horizontal():
            yield self.tid
            yield self.favorite
            yield self.title
            yield self.artist
            yield self.album


class NowPlaying(Static):
    class TrackChanged(Message):
        def __init__(self) -> None:
            super().__init__()

    class FavoriteCurrentTrack(Message):
        def __init__(self, tid, *args, **kwargs) -> None:
            super().__init__()
            self.tid = tid

    def __init__(self, player: Player, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.player = player

        self._shown: object = object()

        self.track_metadata = NowPlayingMetaData()

        self.progressbar = NowPlayingProgressBar()
        self.volumebar = NowPlayingVolumeBar()

        self.progressbar_pos = Label()
        self.progressbar_duration = Label()

        self.voluembar_amount = Label()

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield self.track_metadata
            with Horizontal():
                with Horizontal(id="now-playing-progress"):
                    yield self.progressbar_pos
                    yield self.progressbar
                    yield self.progressbar_duration
                with Horizontal(id="now-playing-volume"):
                    yield self.volumebar
                    yield self.voluembar_amount

    def on_mount(self) -> None:
        self._timer = self.set_interval(0.25, self._tick)  # NOT in __init__

    @on(events.Click, "#now-playing-metadata-favorite")
    def favorite_clicked(self) -> None:
        track = self.player.cached_current_track
        if track is not None:
            self.post_message(self.FavoriteCurrentTrack(track.id))

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
            self.track_metadata.favorite.update(
                "[$error] 󰋑 [/]" if current.favorite else "[gray] ♥ [/]"
            )
            self.track_metadata.tid.update(
                f"[gray]#{str(current.id or '').rjust(4, '0')}[/]"
            )
            self.track_metadata.title.update(
                f"[$error] 󰈣 {(current.title or '')[:25]} [/]"
            )
            self.track_metadata.artist.update(
                f"[$primary] 󰠃 {(current.artist or '')[:20]} [/]"
            )
            self.track_metadata.album.update(
                f"[$accent] 󱍙 {(current.album or '')[:25]} [/]"
            )
            # Update queue table
            self.post_message(self.TrackChanged())
        elif not current:
            self.track_metadata.update("")
        self.progressbar.update(total=self.player.duration, progress=self.player.pos)
        self.progressbar_pos.update(self.format_secs(self.player.pos))
        self.progressbar_duration.update(str(current.time) if current else "?:??")

        volume = self.player.volume
        self.volumebar.update(total=1, progress=volume)
        self.voluembar_amount.update(str(int(volume * 100)) + "%")
