import vlc
import pathlib
import urllib.parse

class Player:

    def __init__(self):
        self.instance = vlc.Instance("--no-xlib",'--file-logging', '--logfile=vlc_log.txt', '--verbose=2')
        self.player = vlc.MediaListPlayer(self.instance)

    def set_queue(self,filepaths: list[str]) -> None:

        self.player.stop() # type: ignore

        self.media_list = vlc.MediaList()
        for filepath in filepaths:
            filepath = pathlib.Path(filepath).as_uri()
            self.media_list.add_media(self.instance.media_new(str(filepath))) # type: ignore
        self.player.set_media_list(self.media_list) # type: ignore

    def start_playback(self) -> None:
        self.player.play() # type: ignore

    def toggle_playback(self) -> None:
        self.player.pause() # type: ignore

    def skip_by_offset(self,offset_int):
        """
        Skips forward or backward by a given integer offset.
        Positive integers move forward; negative integers move backward.
        """
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

