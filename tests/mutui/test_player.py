"""
Tests for mutui.player.Player, with the real audio device swapped for a fake
so nothing is played and no sound hardware is needed.
"""

import pytest

import mutui.player
from mutui.player import Player


class FakePlayback:
    """Stands in for just_playback.Playback and records what it was asked."""

    def __init__(self):
        self.loaded: list[str] = []
        self.active = False  # a file is loaded and hasn't finished
        self.playing = False
        self.volume = 1.0
        self.curr_pos = 0.0
        self.duration = 180.0

    def load_file(self, path):
        self.loaded.append(path)

    def play(self):
        self.active = self.playing = True

    def pause(self):
        self.playing = False

    def resume(self):
        self.playing = True

    def stop(self):
        self.active = self.playing = False

    def seek(self, seconds):
        self.curr_pos = seconds

    def set_volume(self, volume):
        self.volume = volume

    def finish(self):
        """Pretend the current file has played to the end."""
        self.active = self.playing = False


@pytest.fixture
def player(api, monkeypatch):
    monkeypatch.setattr(mutui.player, "_Playback", FakePlayback)
    return Player(api)


@pytest.fixture
def audio(player) -> FakePlayback:
    return player._audio  # type: ignore[return-value]


def test_play_now_loads_and_plays(player, audio, tracks):
    player.play_now(tracks, start_pos=1)
    assert audio.loaded == ["/fake/song2.mp3"]
    assert audio.playing
    assert player.cached_current_track.id == tracks[1]


def test_next_and_prev(player, audio, tracks):
    player.play_now(tracks)
    player.next()
    player.next()
    player.prev()
    assert audio.loaded == [
        "/fake/song1.mp3",
        "/fake/song2.mp3",
        "/fake/song3.mp3",
        "/fake/song2.mp3",
    ]
    assert player.cached_current_track.id == tracks[1]


def test_next_past_the_end_stops(player, audio, tracks):
    player.play_now(tracks, start_pos=len(tracks) - 1)
    player.next()
    assert not audio.active
    assert player.cached_current_track is None


def test_play_now_with_nothing_stops(player, audio):
    player.play_now([])
    assert audio.loaded == []
    assert player.cached_current_track is None


def test_toggle_pauses_and_resumes(player, audio, tracks):
    player.play_now(tracks)
    player.toggle()
    assert not audio.playing
    player.toggle()
    assert audio.playing


def test_toggle_with_nothing_loaded_does_nothing(player, audio):
    player.toggle()
    assert not audio.playing


def test_seek_and_volume_pass_through(player, audio):
    player.seek(42)
    player.set_volume(0.3)
    assert player.pos == 42
    assert player.volume == 0.3
    assert player.duration == 180.0


def test_tick_while_playing_does_nothing(player, audio, api, tracks):
    player.play_now(tracks)
    player.tick()
    assert len(audio.loaded) == 1
    assert api.get_tracks_by_ids([tracks[0]])[tracks[0]].plays == 0


def test_tick_after_track_ends_counts_a_play_and_advances(player, audio, api, tracks):
    player.play_now(tracks)
    audio.finish()
    player.tick()
    assert api.get_tracks_by_ids([tracks[0]])[tracks[0]].plays == 1
    assert player.cached_current_track.id == tracks[1]
    assert audio.loaded[-1] == "/fake/song2.mp3"


def test_tick_after_last_track_ends_stops_once(player, audio, api, tracks):
    player.play_now([tracks[0]])
    audio.finish()
    player.tick()
    player.tick()  # already stopped: must not count the play again
    assert api.get_tracks_by_ids([tracks[0]])[tracks[0]].plays == 1
    assert player.cached_current_track is None


def test_tick_after_stop_does_not_count_a_play(player, audio, api, tracks):
    player.play_now(tracks)
    player.stop()
    player.tick()
    assert api.get_tracks_by_ids([tracks[0]])[tracks[0]].plays == 0


def test_recache_current_track_sees_database_changes(player, api, tracks):
    player.play_now(tracks)
    api.favorite_tracks(f"id={tracks[0]}")
    assert player.cached_current_track.favorite is False
    player.recache_current_track()
    assert player.cached_current_track.favorite is True
