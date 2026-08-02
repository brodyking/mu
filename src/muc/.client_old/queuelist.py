"""
 _   _
| | | | muc client
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

    def queue_tracks_next(self, track_ids: list[int]) -> list:
        """
        Inserts tracks at the current position (right after pos), removing
        any existing occurrences of those track_ids first. Returns the queue.
        """

        # Remove track_ids that already exist in the queue
        to_move = set(track_ids)
        before = self.queue[: self.pos + 1]
        after = self.queue[self.pos + 1 :]

        before = [t for t in before if t not in to_move]
        after = [t for t in after if t not in to_move]
        self.queue = [*before, *track_ids, *after]
        return self.queue

    def queue_tracks_last(self, track_ids: list[int]) -> list:
        """
        Adds tracks to the end of the queue, removing any existing
        occurrences of those track_ids first. Returns the queue.
        """
        existing = set(track_ids)
        self.queue = [t for t in self.queue if t not in existing] + track_ids
        return self.queue

    def get_current_track(self) -> Track | None:
        """Returns the currently selected track"""
        if self.pos <= len(self.queue) - 1:
            tid: int = self.queue[self.pos]
            return self.api.get_tracks(f"id={tid}")[tid]
        else:
            return None

    def start_queue(self, track_ids: list) -> Track | None:
        """Initializes the list of tracks, and returns the first one"""
        self.queue = [int(id) for id in track_ids]
        self.pos = 0

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
        term: str = "+".join(f"id={tid}" for tid in tids)
        tracks: dict[int, Track] = self.api.get_tracks(term)  # ONE query
        return [tracks[tid] for tid in tids if tid in tracks]  # preserve queue order

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
