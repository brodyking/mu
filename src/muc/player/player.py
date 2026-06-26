"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import queue
import threading
from collections.abc import Callable

import vlc


class Player:
    def __init__(
        self,
        on_time_changed_callback: Callable | None = None,
        on_track_end_callback: Callable | None = None,
    ):
        self.instance = vlc.Instance("--no-xlib")
        self.player = vlc.MediaPlayer(self.instance)

        self.on_track_end_callback = on_track_end_callback
        self.on_time_changed_callback = on_time_changed_callback

        em = self.player.event_manager()  # type: ignore
        em.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_track_end)  # type: ignore
        em.event_attach(vlc.EventType.MediaPlayerTimeChanged, self._on_time_changed)  # type: ignore

        self._commands: queue.Queue = queue.Queue()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def _on_track_end(self, event):
        if self.on_track_end_callback:
            threading.Thread(
                target=self.on_track_end_callback, args=(event,), daemon=True
            ).start()

    def _on_time_changed(self, event):
        if self.on_time_changed_callback:
            self.on_time_changed_callback(event.u.new_time)

    def _run(self):
        while True:
            cmd, arg = self._commands.get()
            try:
                if cmd == "play":
                    arg = self._collapse_plays(arg)  # spam → newest track wins
                    media = self.instance.media_new(arg)
                    self.player.set_media(media)
                    self.player.play()
                elif cmd == "stop":
                    self.player.stop()
                elif cmd == "pause":
                    self.player.pause()
                elif cmd == "seek":
                    if self.player.is_playing():
                        self.player.set_position(arg)
            except Exception:
                pass

    def _collapse_plays(self, arg):
        """Drain a run of consecutive queued plays, keeping only the last."""
        while True:
            try:
                if self._commands.queue[0][0] != "play":  # peek (single consumer)
                    break
                _, arg = self._commands.get_nowait()
            except IndexError:
                break
        return arg

    def start_playback(self, filepath) -> None:
        self._commands.put(("play", filepath))

    def stop_playback(self) -> None:
        self._commands.put(("stop", None))

    def toggle_playback(self) -> None:
        self._commands.put(("pause", None))

    def move_playhead_to_percentage(self, percentage: float) -> None:
        self._commands.put(("seek", percentage))
