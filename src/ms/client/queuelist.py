from ms.database.track import Track

class QueueList:
    def __init__(self,tracks:dict) -> None:
        self.tracks = tracks # Dict of all tracks
        self.queue = [] # List of track Ids in the queue (full of ints)
        self.pos = 0 # Position in the queue

    def get_current_track(self) -> Track:
        """Returns the currently selected track"""
        return self.tracks[self.queue[self.pos]]

    def start_queue(self,track_ids) -> Track:
        """Initializes the list of tracks, and returns the first one"""
        self.queue = [int(id) for id in track_ids]
        self.pos = 0

        return self.get_current_track()

    def get_queue(self,offset=1) -> list:
        """
        Returns the queue of tracks remaining in the queue.
        By default, it will return all tracks after the currently playing one.
        You can change this with offset.
        """
        output = []
        for id in self.queue[self.pos+offset:]:
            output.append(self.tracks[id])
        return output

    def skip_track(self,offset:int=1) -> Track:
        """Returns the next track and shifts the queue, or returns current track if none next."""
        
        if not self.queue:
            raise ValueError("The queue is empty.") # Or handle how you prefer

        # Use modulo to cleanly wrap around both positive and negative offset
        if self.pos + offset < len(self.queue) and self.pos + offset >= 0:
            self.pos = (self.pos + offset) % len(self.queue)
        
        return self.tracks[self.queue[self.pos]]
