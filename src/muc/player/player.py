"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

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

        # Attach to the underlying MediaPlayer's event manager
        em = self.player.event_manager()  # type: ignore
        em.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_track_end)  # type: ignore
        em.event_attach(vlc.EventType.MediaPlayerTimeChanged, self._on_time_changed)  # type: ignore

    def _on_track_end(self, event):
        if self.on_track_end_callback:
            threading.Thread(
                target=self.on_track_end_callback,
                args=(event,),
                daemon=True,
            ).start()

    def _on_time_changed(self, event):
        if self.on_time_changed_callback:
            self.on_time_changed_callback(event.u.new_time)

    def stop_playback(self) -> None:
        """Stops playback"""
        self.player.stop()  # type:ignore

    def start_playback(self, filepath) -> None:
        """Starts playback"""
        self.stop_playback()
        media = self.instance.media_new(filepath)
        self.player.set_media(media)
        self.player.play()

    def toggle_playback(self) -> None:
        """Toggles playback"""
        self.player.pause()  # type: ignore

    def get_current_time(self) -> tuple[int, float]:
        """Returns a tuple of the current ms and the current percent of the track"""
        current_ms = self.player.get_time() if self.player.is_playing() else 0  # type: ignore
        current_percent = (
            self.player.get_position() if self.player.is_playing() else 0.0  # type:ignore
        )  # type: ignore
        return (current_ms, current_percent)

    def move_playhead_to_percentage(self, percentage: float):
        if self.player.is_playing():  # type: ignore
            self.player.set_position(percentage)  # type:ignore
