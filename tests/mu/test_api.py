"""
Tests for mu.api.Api: tracks, albums, artists and removing tracks.
Playlists are in test_playlists.py; importing files is in test_import.py.
"""

import pytest


def add_track(api, **fields):
    """Insert one track, filling anything not given with defaults."""
    n = len(api.get_tracks()) + 1
    meta = {
        "title": f"T{n}",
        "artist": "A",
        "album": "Al",
        "time": "1:00",
        "tracknumber": 1,
        "albumartist": "A",
        "discnumber": 1,
        "genre": None,
        "date": None,
        "filepath": f"/x/{n}.mp3",
        "filename": f"{n}.mp3",
        "albumart": None,
    }
    meta.update(fields)
    with api.db.write() as conn:
        return api._upsert_track(conn, meta)


# --- _upsert_track -----------------------------------------------------------


def test_new_track_defaults(api, tracks):
    t = api.get_tracks_by_ids([tracks[0]])[tracks[0]]
    assert t.plays == 0
    assert t.favorite is False


def test_upsert_same_filepath_updates_in_place(api, tracks):
    before = api.get_tracks_by_ids([tracks[0]])[tracks[0]]
    after = add_track(api, filepath=before.filepath, title="Renamed")
    assert after.id == before.id
    assert len(api.get_tracks()) == len(tracks)
    assert api.get_tracks_by_ids([before.id])[before.id].title == "Renamed"


def test_upsert_keeps_plays_and_favorite(api, tracks):
    tid = tracks[0]
    api.favorite_tracks(f"id={tid}")
    api.increment_playcount_tracks(f"id={tid}", 4)
    add_track(api, filepath="/fake/song1.mp3", title="Rescanned")
    t = api.get_tracks_by_ids([tid])[tid]
    assert (t.plays, t.favorite) == (4, True)


# --- get_tracks_by_ids -------------------------------------------------------


def test_get_tracks_by_ids(api, tracks):
    assert set(api.get_tracks_by_ids([tracks[1], tracks[3]])) == {tracks[1], tracks[3]}


def test_get_tracks_by_ids_ignores_missing_and_duplicates(api, tracks):
    assert list(api.get_tracks_by_ids([tracks[0], tracks[0], 999])) == [tracks[0]]


def test_get_tracks_by_ids_empty(api, tracks):
    assert api.get_tracks_by_ids([]) == {}


def test_get_tracks_by_ids_more_than_one_chunk(api, tracks):
    # 2000 ids is more than one IN (...) batch and more than SQLite's
    # default limit on parameters in older builds.
    wanted = list(range(1, 2001))
    assert set(api.get_tracks_by_ids(wanted)) == set(tracks)


# --- favorite_tracks ---------------------------------------------------------


def test_favorite_toggles(api, tracks):
    tid = tracks[2]
    assert api.favorite_tracks(f"id={tid}")[tid].favorite is True
    assert api.favorite_tracks(f"id={tid}")[tid].favorite is False


def test_favorite_toggles_each_track_independently(api, tracks):
    api.favorite_tracks(f"id={tracks[0]}")
    result = api.favorite_tracks(f"id={tracks[0]}, id={tracks[1]}")
    assert result[tracks[0]].favorite is False
    assert result[tracks[1]].favorite is True


def test_favorite_no_match(api, tracks):
    assert api.favorite_tracks("title=nothing") == {}


def test_favorite_bad_term_raises(api, tracks):
    with pytest.raises(ValueError):
        api.favorite_tracks("bogus:x")


# --- increment_playcount_tracks ---------------------------------------------


def test_increment_playcount_by_amount(api, tracks):
    api.increment_playcount_tracks(f"id={tracks[0]}", 2)
    result = api.increment_playcount_tracks(f"id={tracks[0]}", 3)
    assert result[tracks[0]].plays == 5


def test_increment_playcount_many(api, tracks):
    result = api.increment_playcount_tracks("artist:test", 1)
    assert set(result) == set(tracks)
    assert all(t.plays == 1 for t in result.values())


# --- get_albums --------------------------------------------------------------


def test_get_albums_groups_by_albumartist_and_title(api):
    add_track(api, album="X", albumartist="P", artist="feat. Q", tracknumber=2)
    add_track(api, album="X", albumartist="P", tracknumber=1)
    add_track(api, album="X", albumartist="R")  # same title, different artist
    albums = api.get_albums()
    assert set(albums) == {("P", "X"), ("R", "X")}
    assert [t.tracknumber for t in albums[("P", "X")].tracks] == [1, 2]


def test_get_albums_sorts_by_disc_then_track(api):
    add_track(api, discnumber=2, tracknumber=1, title="d2t1")
    add_track(api, discnumber=1, tracknumber=10, title="d1t10")
    add_track(api, discnumber=1, tracknumber=2, title="d1t2")
    album = api.get_albums()[("A", "Al")]
    assert [t.title for t in album.tracks] == ["d1t2", "d1t10", "d2t1"]


def test_get_albums_skips_tracks_without_album_or_albumartist(api):
    add_track(api, album=None)
    add_track(api, albumartist="")
    assert api.get_albums() == {}


def test_get_albums_with_term(api, tracks):
    add_track(api, album="Other", albumartist="Other")
    assert list(api.get_albums("album=Other")) == [("Other", "Other")]


# --- get_artists -------------------------------------------------------------


def test_get_artists_by_track_artist(api):
    add_track(api, artist="Solo", albumartist="Band")
    add_track(api, artist="Band", albumartist="Band")
    assert set(api.get_artists()) == {"Solo", "Band"}


def test_get_artists_by_albumartist(api):
    add_track(api, artist="Solo", albumartist="Band")
    add_track(api, artist="Band", albumartist="Band")
    artists = api.get_artists(only_albumartists=True)
    assert list(artists) == ["Band"]
    assert len(artists["Band"].tracks) == 2


def test_get_artists_skips_blank_names(api):
    add_track(api, artist=None)
    add_track(api, artist="   ")
    assert api.get_artists() == {}


def test_get_artists_sorted_case_insensitively(api):
    for name in ["beta", "Alpha", "Gamma"]:
        add_track(api, artist=name)
    assert list(api.get_artists()) == ["Alpha", "beta", "Gamma"]


# --- remove_tracks -----------------------------------------------------------


def test_remove_tracks(api, tracks):
    result = api.remove_tracks(f"id={tracks[0]}")
    assert result[tracks[0]][1] is True
    assert result[tracks[0]][0].title == "Song 1"
    assert tracks[0] not in api.get_tracks()


def test_remove_tracks_no_match(api, tracks):
    assert api.remove_tracks("title=nothing") == {}
    assert len(api.get_tracks()) == len(tracks)


def test_remove_tracks_also_removes_them_from_playlists(api, tracks):
    api.create_playlist("Mix")
    api.append_playlists("title=Mix", "artist:test")
    api.remove_tracks(f"id={tracks[1]}")
    playlist = api.get_playlists("title=Mix")
    (mix,) = playlist.values()
    assert [t.id for t in mix.tracks] == [tracks[0], *tracks[2:]]


def test_removed_track_ids_are_not_reused(api, tracks):
    api.remove_tracks(f"id={tracks[-1]}")
    assert add_track(api).id == tracks[-1] + 1
