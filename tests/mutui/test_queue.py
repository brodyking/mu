from mu.api import Api
from mu.models import Track
from mutui.queuelist import QueueList


def test_append_queue():
    q = QueueList(Api())
    q.queue = [1, 2, 3]
    q.queue_tracks_last([4, 5])
    assert q.queue[len(q.queue) - 1] == 5
