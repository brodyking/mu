"""
Tests for mutui.queuelist.QueueList.

The `api` and `tracks` fixtures live in tests/conftest.py.
"""

import pytest

from mutui.queuelist import QueueList


@pytest.fixture
def q(api, tracks):
    """A queue holding all five test tracks, positioned on the first one."""
    q = QueueList(api)
    q.start_queue(tracks)
    return q


# --- construction ------------------------------------------------------------


def test_new_queue_is_empty(api):
    q = QueueList(api)
    assert q.queue == []
    assert q.pos == 0


# --- start_queue -------------------------------------------------------------


def test_start_queue_returns_first_track(api, tracks):
    q = QueueList(api)
    track = q.start_queue(tracks)
    assert track.id == tracks[0]
    assert q.queue == tracks
    assert q.pos == 0


def test_start_queue_at_position(api, tracks):
    q = QueueList(api)
    track = q.start_queue(tracks, start_pos=2)
    assert track.id == tracks[2]
    assert q.pos == 2


def test_start_queue_converts_string_ids(api, tracks):
    q = QueueList(api)
    q.start_queue([str(t) for t in tracks])
    assert q.queue == tracks


def test_start_queue_replaces_existing_queue(q, tracks):
    q.pos = 3
    q.start_queue([tracks[4]])
    assert q.queue == [tracks[4]]
    assert q.pos == 0


def test_start_empty_queue_returns_none(api):
    q = QueueList(api)
    assert q.start_queue([]) is None


# --- get_current_track -------------------------------------------------------


def test_get_current_track(q, tracks):
    q.pos = 1
    assert q.get_current_track().id == tracks[1]


def test_get_current_track_past_end_is_none(q, tracks):
    q.pos = len(tracks)
    assert q.get_current_track() is None


def test_get_current_track_missing_from_library_is_none(api):
    q = QueueList(api)
    q.queue = [999]
    assert q.get_current_track() is None


# --- queue_tracks_next -------------------------------------------------------


def test_queue_tracks_next_inserts_after_current(api):
    q = QueueList(api)
    q.queue = [1, 2, 3]
    q.pos = 1
    q.queue_tracks_next([4])
    assert q.queue == [1, 2, 4, 3]


def test_queue_tracks_next_keeps_order_of_several(api):
    q = QueueList(api)
    q.queue = [1, 2, 3]
    q.queue_tracks_next([4, 5])
    assert q.queue == [1, 4, 5, 2, 3]


def test_queue_tracks_next_at_end_of_queue(api):
    q = QueueList(api)
    q.queue = [1, 2, 3]
    q.pos = 2
    q.queue_tracks_next([4])
    assert q.queue == [1, 2, 3, 4]


def test_queue_tracks_next_on_empty_queue(api):
    q = QueueList(api)
    q.queue_tracks_next([4])
    assert q.queue == [4]


def test_queue_tracks_next_does_not_change_current_track(api):
    q = QueueList(api)
    q.queue = [1, 2, 3]
    q.pos = 1
    q.queue_tracks_next([4])
    assert q.pos == 1
    assert q.queue[q.pos] == 2


# --- queue_tracks_last -------------------------------------------------------


def test_queue_tracks_last_appends(api):
    q = QueueList(api)
    q.queue = [1, 2, 3]
    q.queue_tracks_last([4, 5])
    assert q.queue == [1, 2, 3, 4, 5]


def test_queue_tracks_last_with_nothing_is_a_no_op(api):
    q = QueueList(api)
    q.queue = [1, 2, 3]
    q.queue_tracks_last([])
    assert q.queue == [1, 2, 3]


def test_queue_tracks_last_does_not_change_position(api):
    q = QueueList(api)
    q.queue = [1, 2, 3]
    q.pos = 1
    q.queue_tracks_last([4])
    assert q.pos == 1


# --- get_queue / get_queue_filepaths ----------------------------------------


def test_get_queue_returns_upcoming_tracks(q, tracks):
    q.pos = 2
    assert [t.id for t in q.get_queue()] == tracks[3:]


def test_get_queue_offset_zero_includes_current(q, tracks):
    q.pos = 2
    assert [t.id for t in q.get_queue(offset=0)] == tracks[2:]


def test_get_queue_at_last_track_is_empty(q, tracks):
    q.pos = len(tracks) - 1
    assert q.get_queue() == []


def test_get_queue_keeps_queue_order_not_database_order(q, tracks):
    q.queue = [tracks[0], tracks[4], tracks[2], tracks[1]]
    assert [t.id for t in q.get_queue()] == [tracks[4], tracks[2], tracks[1]]


def test_get_queue_keeps_duplicates(q, tracks):
    q.queue = [tracks[0], tracks[1], tracks[1]]
    assert [t.id for t in q.get_queue()] == [tracks[1], tracks[1]]


def test_get_queue_skips_ids_missing_from_library(q, tracks):
    q.queue = [tracks[0], 999, tracks[1]]
    assert [t.id for t in q.get_queue()] == [tracks[1]]


def test_get_queue_filepaths(q):
    q.pos = 3
    assert q.get_queue_filepaths() == ["/fake/song5.mp3"]


# --- skip_track --------------------------------------------------------------


@pytest.mark.parametrize(
    ("start", "offset", "expected_pos"),
    [
        (0, 1, 1),  # next
        (2, -1, 1),  # previous
        (0, 3, 3),  # jump forward several
        (4, -4, 0),  # jump back to the start
    ],
)
def test_skip_track_moves_position(q, tracks, start, offset, expected_pos):
    q.pos = start
    track = q.skip_track(offset)
    assert q.pos == expected_pos
    assert track.id == tracks[expected_pos]


@pytest.mark.parametrize(("start", "offset"), [(4, 1), (0, -1), (2, 10)])
def test_skip_track_off_either_end_returns_none_and_stays(q, start, offset):
    q.pos = start
    assert q.skip_track(offset) is None
    assert q.pos == start


def test_skip_track_on_empty_queue_raises(api):
    q = QueueList(api)
    with pytest.raises(ValueError, match="empty"):
        q.skip_track()


# --- remove_track ------------------------------------------------------------


def test_remove_track_returns_removed_track(q, tracks):
    removed = q.remove_track(2)
    assert removed.id == tracks[2]
    assert q.queue == [tracks[0], tracks[1], tracks[3], tracks[4]]


def test_remove_last_track(q, tracks):
    removed = q.remove_track(len(tracks) - 1)
    assert removed.id == tracks[-1]
    assert q.queue == tracks[:-1]


def test_remove_track_past_end_returns_none(q, tracks):
    assert q.remove_track(len(tracks) + 1) is None
    assert q.queue == tracks


def test_remove_track_one_past_end_returns_none(q, tracks):
    assert q.remove_track(len(tracks)) is None


def test_remove_track_before_current_keeps_current_track(q, tracks):
    q.pos = 3
    q.remove_track(1)
    assert q.get_current_track().id == tracks[3]


# --- increment_current_track_playcount --------------------------------------


def test_increment_playcount(q, api, tracks):
    q.pos = 1
    returned = q.increment_current_track_playcount()
    assert returned.plays == 1
    # Read it back from the database to prove it was actually saved.
    assert api.get_tracks(f"id={tracks[1]}")[tracks[1]].plays == 1
    # And only that track changed.
    assert api.get_tracks(f"id={tracks[0]}")[tracks[0]].plays == 0
