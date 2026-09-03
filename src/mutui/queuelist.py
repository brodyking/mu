"""
 _   _
| | | | mutui
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from mu.api import Api
from mu.models import Track


class QueueList:
    def __init__(self, api: Api) -> None:
        self.api: Api = api  # Dict of all tracks
        self.queue: list[int] = []  # List of track Ids in the queue (full of ints)
        self.pos = 0  # Position in the queue

    def increment_current_track_playcount(self) -> Track:
        tid = self.queue[self.pos]
        return self.api.increment_playcount_tracks(f"id={tid}", amount=1)[tid]

    def queue_tracks_next(self, track_ids: list[int]) -> None:
        """Inserts tracks at the current position (right after pos)"""
        before = self.queue[: self.pos + 1]
        after = self.queue[self.pos + 1 :]
        self.queue = [*before, *track_ids, *after]

    def queue_tracks_last(self, track_ids: list[int]) -> None:
        """Adds tracks to the end of the queue"""
        self.queue = [*self.queue, *track_ids]

    def get_current_track(self) -> Track | None:
        """Returns the currently selected track"""
        if self.pos <= len(self.queue) - 1:
            tid: int = self.queue[self.pos]
            response = self.api.get_tracks(f"id={tid}")
            if tid in response:
                return response[tid]
        else:
            return None

    def start_queue(self, track_ids: list, start_pos: int = 0) -> Track | None:
        """Initializes the list of tracks, and returns the first one"""
        self.queue = [int(id) for id in track_ids]
        self.pos = start_pos

        return self.get_current_track()

    def get_queue_filepaths(self, offset=1) -> list[str]:
        tracks: list[Track] = self.get_queue(offset=offset)
        filepaths: list[str] = []
        for track in tracks:
            filepaths.append(track.filepath)
        return filepaths

    def get_queue(self, offset: int = 1) -> list[Track]:
        tids: list[int] = self.queue[self.pos + offset :]
        if not tids:
            return []
        tracks: dict[int, Track] = self.api.get_tracks_by_ids(tids)
        return [tracks[tid] for tid in tids if tid in tracks]

    def skip_track(self, offset: int = 1) -> Track | None:
        """
        Returns the next track and shifts the queue,
        or returns current track if none next.
        """

        if not self.queue:
            raise ValueError("The queue is empty.")
        new_pos = self.pos + offset
        if 0 <= new_pos < len(self.queue):
            self.pos = new_pos
            return self.get_current_track()
        return None  # off either end → caller can stop playback

    def remove_track(self, pos: int) -> Track | None:
        """
        Removes the track at specified pos, returns the track removed.
        """
        if pos > len(self.queue):
            return None
        tid = self.queue.pop(pos)
        response = self.api.get_tracks(f"id={tid}")
        if tid in response:
            return response[tid]
        return None
