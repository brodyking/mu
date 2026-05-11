from ms.database.track import Track

class Queue:
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

    def get_queue(self) -> list:
        """Returns the queue of tracks remaining in the queue"""
        output = []
        for id in self.queue[self.pos:]:
            output.append(self.tracks[id])
        return output

    def next_track(self) -> Track:
        """Returns the next track and shifts the queue, or returns current track if none next."""
        if self.pos+1 < len(self.queue):
            self.pos +=1
        return self.tracks[self.queue[self.pos]]

    def previous_track(self) -> Track:
        """Returns the next track and shifts the queue, or returns current track if none before."""
        if self.pos-1 > -1:
            self.pos -=1
        return self.tracks[self.queue[self.pos]]
