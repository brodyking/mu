"""
Tests for the plain data classes in mu.models.
"""

import pytest

from mu.models import Album, Artist, Playlist, Track


def row(**overrides) -> dict:
    """A complete tracks-table row, as Track() expects it."""
    base = {
        "id": 7,
        "favorite": 0,
        "title": "Title",
        "artist": "Artist",
        "album": "Album",
        "plays": 3,
        "time": "3:42",
        "dateadded": "2026-01-01T00:00:00Z",
        "tracknumber": 2,
        "albumartist": "Album Artist",
        "discnumber": 1,
        "genre": "Rock",
        "date": "2026",
        "filepath": "/music/a.mp3",
        "filename": "a.mp3",
        "albumart": "abc.png",
    }
    base.update(overrides)
    return base


# --- Track -------------------------------------------------------------------


def test_track_reads_every_column():
    t = Track(row())
    assert t.id == 7
    assert t.title == "Title"
    assert t.plays == 3
    assert t.filepath == "/music/a.mp3"


@pytest.mark.parametrize(("stored", "expected"), [(0, False), (1, True)])
def test_track_favorite_is_a_bool(stored, expected):
    assert Track(row(favorite=stored)).favorite is expected


def test_track_missing_column_raises():
    data = row()
    del data["title"]
    with pytest.raises(KeyError):
        Track(data)


def test_track_get_dict_round_trips():
    data = row(favorite=1)
    d = Track(data).get_dict()
    assert d == {**data, "favorite": True}


@pytest.mark.parametrize(
    ("time", "ms"),
    [("0:00", 0), ("0:01", 1000), ("3:42", 222_000), ("10:05", 605_000)],
)
def test_track_get_time_ms(time, ms):
    assert Track(row(time=time)).get_time_ms() == ms


@pytest.mark.xfail(
    strict=True,
    reason="BUG: format_duration writes 'h:mm:ss' for long files, "
    "but get_time_ms only understands 'm:ss'",
)
def test_track_get_time_ms_hour_long():
    assert Track(row(time="1:02:03")).get_time_ms() == 3_723_000


# --- Album / Playlist / Artist ----------------------------------------------


def test_album_get_dict_includes_tracks():
    t = Track(row())
    d = Album("Album", "Album Artist", [t]).get_dict()
    assert d["title"] == "Album"
    assert d["albumartist"] == "Album Artist"
    assert d["tracks"] == [t.get_dict()]


def test_playlist_defaults():
    p = Playlist(1, "Mix")
    assert p.description == ""
    assert p.tracks == []


def test_playlist_none_description_becomes_empty_string():
    # SQLite hands back NULL as None for playlists made without a description.
    assert Playlist(1, "Mix", description=None).description == ""  # type: ignore[arg-type]


def test_playlists_do_not_share_a_default_track_list():
    a, b = Playlist(1, "A"), Playlist(2, "B")
    a.tracks.append(Track(row()))
    assert b.tracks == []


def test_playlist_get_dict():
    t = Track(row())
    d = Playlist(4, "Mix", "desc", [t]).get_dict()
    assert d == {
        "id": 4,
        "title": "Mix",
        "description": "desc",
        "tracks": [t.get_dict()],
    }


def test_artist_get_dict():
    t = Track(row())
    assert Artist("Someone", [t]).get_dict() == {
        "name": "Someone",
        "tracks": [t.get_dict()],
    }
