"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from just_playback import Playback as _Playback  # aliased: its class is named Playback

from mu.api import Api
from mu.models import Track
from muc.queuelist import QueueList


class Player:
    """Owns the queue AND the audio device — the one object the UI drives."""

    def __init__(self, api: Api) -> None:
        self.queue = QueueList(api)
        self._audio = _Playback()
        self._loaded = False
        self.cached_current_track: Track | None = None

    def play_now(self, tids: list[int], start_pos: int = 0) -> None:
        self._play(self.queue.start_queue(tids, start_pos))

    def next(self) -> None:
        self._play(self.queue.skip_track(1))

    def prev(self) -> None:
        self._play(self.queue.skip_track(-1))

    def toggle(self) -> None:
        if not self._audio.active:
            return
        self._audio.pause() if self._audio.playing else self._audio.resume()

    def seek(self, seconds: float) -> None:
        self._audio.seek(seconds)

    def stop(self) -> None:
        self._audio.stop()
        self._loaded = False

    def tick(self) -> None:
        """
        Update playcount of current track and advance when the current track finishes.
        Called from a UI timer.
        """
        if self._loaded and not self._audio.active:
            self.queue.increment_current_track_playcount()
            self.next()

    def recache_current_track(self) -> None:
        self.cached_current_track = self.queue.get_current_track()

    def _play(self, track: Track | None) -> None:
        self.cached_current_track = track
        if track is None:
            self.stop()
            return
        self._audio.load_file(track.filepath)
        self._audio.play()
        self._loaded = True

    @property
    def pos(self) -> float:
        return self._audio.curr_pos

    @property
    def duration(self) -> float:
        return self._audio.duration
