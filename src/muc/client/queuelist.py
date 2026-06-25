"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from mu.track import Track


class QueueList:
    def __init__(self, tracks: dict) -> None:
        self.tracks = tracks  # Dict of all tracks
        self.queue: list[int] = []  # List of track Ids in the queue (full of ints)
        self.pos = 0  # Position in the queue

    def queue_tracks_next(self, track_ids: list[int]) -> list:
        """
        Inserts tracks at the current position (right after pos), removing
        any existing occurrences of those track_ids first. Returns the queue.
        """
        # Remove track_ids that already exist in the queue
        existing = set(track_ids)
        before = self.queue[: self.pos + 1]
        after = self.queue[self.pos + 1 :]

        before = [t for t in before if t not in existing]
        after = [t for t in after if t not in existing]

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
            return self.tracks[self.queue[self.pos]]
        else:
            return None

    def start_queue(self, track_ids: list) -> Track | None:
        """Initializes the list of tracks, and returns the first one"""
        self.queue = [int(id) for id in track_ids]
        self.pos = 0

        return self.get_current_track()

    def get_queue(self, offset=1) -> list:
        """
        Returns the queue of tracks remaining in the queue.
        By default, it will return all tracks after the currently playing one.
        You can change this with offset.
        """
        output = []
        for id in self.queue[self.pos + offset :]:
            output.append(self.tracks[id])
        return output

    def skip_track(self, offset: int = 1) -> Track | None:
        """
        Returns the next track and shifts the queue,
        or returns current track if none next.
        """

        if not self.queue:
            raise ValueError("The queue is empty.")  # Or handle how you prefer

        # Use modulo to cleanly wrap around both positive and negative offset
        if self.pos + offset < len(self.queue) and self.pos + offset >= 0:
            self.pos = (self.pos + offset) % len(self.queue)

        return self.get_current_track()
