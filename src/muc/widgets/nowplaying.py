from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Label, Static

from muc.player import Player


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

    def compose(self):
        with Horizontal():
            yield Label(" 󰈣 ", classes="metadata-icon")
            yield self.title_label
            yield Label(" 󰠃 ", classes="metadata-icon")
            yield self.artist_label
            yield Label(" 󱍙 ", classes="metadata-icon")
            yield self.album_label

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

        # pct = self.player.pos / self.player.duration * 100
        # self.query_one("#progress", ProgressBar).update(progress=pct)
