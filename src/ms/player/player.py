import vlc
import pathlib
import urllib.parse
from typing import Callable, Optional

class Player:

    def __init__(self, on_track_change: Optional[Callable] = None, on_track_end: Optional[Callable] = None):
        self.instance = vlc.Instance("--no-xlib")
        self.player = vlc.MediaListPlayer(self.instance)
        self.on_track_end = on_track_end

        # Attach to the underlying MediaPlayer's event manager
        em = self.player.get_media_player().event_manager() # type: ignore
        em.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_track_end) # type: ignore

    def _on_track_end(self, event):
        if self.on_track_end:
            self.on_track_end(event)

    def set_queue(self,filepaths: list[str]) -> None:
        """Creates the queue from a list of file paths"""
        self.player.stop() # type: ignore

        self.media_list = vlc.MediaList()
        for filepath in filepaths:
            filepath = pathlib.Path(filepath).as_uri()
            self.media_list.add_media(self.instance.media_new(str(filepath))) # type: ignore
        self.player.set_media_list(self.media_list) # type: ignore

    def start_playback(self) -> None:
        """Starts playback"""
        self.player.play() # type: ignore

    def toggle_playback(self) -> None:
        """Toggles playback"""
        self.player.pause() # type: ignore

    def skip_by_offset(self,offset_int):
        """Skips forward or backward by a given integer offset."""
        # 1. Get the underlying media list
        total_tracks = self.media_list.count() # type: ignore
        
        # 2. Find the index of the currently playing item
        current_media = self.player.get_media_player().get_media() # type:ignore
        if not current_media:
            print("No media is currently loaded.")
            return
            
        current_index = self.media_list.index_of_item(current_media) # type:ignore
        
        # 3. Calculate the new index
        new_index = current_index + offset_int
        
        # 4. Keep the index within playlist boundaries
        if 0 <= new_index < total_tracks:
            self.player.play_item_at_index(new_index) # type: ignore
        else:
            print(f"Index {new_index} is out of bounds (Playlist size: {total_tracks}).")

    def get_current_time(self) -> tuple[int,float]:
        """Returns a tuple of the current ms and the current percent of the track"""
        current_ms = self.player.get_time() if self.player.is_playing() else 0 #type: ignore
        current_percent = self.player.get_position() if self.player.is_playing() else 0.0 # type: ignore
        return (current_ms,current_percent)
