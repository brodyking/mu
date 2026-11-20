"""
Tests for playlist operations in mu.api.Api.
"""

import pytest


def track_ids(api, title="Mix") -> list[int]:
    (playlist,) = api.get_playlists(f"title={title}").values()
    return [t.id for t in playlist.tracks]


def positions(api, title="Mix") -> list[int]:
    rows = api.db.query(
        """
        SELECT position FROM playlist_tracks
        JOIN playlists ON playlists.id = playlist_id
        WHERE playlists.title = ? ORDER BY position
        """,
        (title,),
    )
    return [r["position"] for r in rows]


def ids_term(*ids) -> str:
    return ", ".join(f"id={i}" for i in ids)


@pytest.fixture
def mix(api):
    return api.create_playlist("Mix", "for testing")


# --- create / get ------------------------------------------------------------


def test_create_playlist(mix):
    assert mix.title == "Mix"
    assert mix.description == "for testing"
    assert mix.tracks == []


def test_create_existing_title_returns_existing(api, mix):
    again = api.create_playlist("Mix", "different description")
    assert again.id == mix.id
    assert again.description == "for testing"
    assert len(api.get_playlists()) == 1


def test_get_playlists_by_term(api, mix):
    api.create_playlist("Road Trip")
    assert [p.title for p in api.get_playlists("title:road").values()] == ["Road Trip"]


def test_get_playlists_empty_library(api):
    assert api.get_playlists() == {}


# --- append_playlists --------------------------------------------------------


def test_append_in_order(api, tracks, mix):
    api.append_playlists("title=Mix", ids_term(tracks[2], tracks[0]))
    api.append_playlists("title=Mix", ids_term(tracks[4]))
    # Within one append, tracks arrive in library order (get_tracks' order).
    assert track_ids(api) == [tracks[0], tracks[2], tracks[4]]
    assert positions(api) == [0, 1, 2]


def test_append_skips_tracks_already_present(api, tracks, mix):
    api.append_playlists("title=Mix", ids_term(tracks[0], tracks[1]))
    api.append_playlists("title=Mix", ids_term(tracks[1], tracks[2]))
    assert track_ids(api) == tracks[:3]
    assert positions(api) == [0, 1, 2]  # no gap left by the skipped one


def test_append_to_several_playlists(api, tracks, mix):
    api.create_playlist("Other")
    api.append_playlists("title=Mix, title=Other", ids_term(tracks[0]))
    assert track_ids(api, "Mix") == [tracks[0]]
    assert track_ids(api, "Other") == [tracks[0]]


def test_append_no_matching_tracks(api, tracks, mix):
    api.append_playlists("title=Mix", "title=nothing")
    assert track_ids(api) == []


# --- remove_from_playlist ----------------------------------------------------


def test_remove_from_playlist_renumbers(api, tracks, mix):
    api.append_playlists("title=Mix", "artist:test")
    api.remove_from_playlist("title=Mix", ids_term(tracks[1], tracks[3]))
    assert track_ids(api) == [tracks[0], tracks[2], tracks[4]]
    assert positions(api) == [0, 1, 2]


def test_remove_from_playlist_leaves_other_playlists_alone(api, tracks, mix):
    api.create_playlist("Other")
    api.append_playlists("title=Mix, title=Other", "artist:test")
    api.remove_from_playlist("title=Mix", ids_term(tracks[0]))
    assert track_ids(api, "Other") == tracks


def test_remove_from_playlist_track_not_in_it(api, tracks, mix):
    api.append_playlists("title=Mix", ids_term(tracks[0]))
    api.remove_from_playlist("title=Mix", ids_term(tracks[4]))
    assert track_ids(api) == [tracks[0]]


def test_remove_from_playlist_keeps_track_in_library(api, tracks, mix):
    api.append_playlists("title=Mix", ids_term(tracks[0]))
    api.remove_from_playlist("title=Mix", ids_term(tracks[0]))
    assert tracks[0] in api.get_tracks()


# --- insert_into_playlist ----------------------------------------------------


@pytest.fixture
def abc(api, tracks, mix):
    """Mix holds tracks 0, 1, 2; tracks 3 and 4 are free to insert."""
    api.append_playlists("title=Mix", ids_term(*tracks[:3]))
    return tracks


@pytest.mark.parametrize(
    ("position", "expected"),
    [
        (0, [3, 0, 1, 2]),
        (1, [0, 3, 1, 2]),
        (3, [0, 1, 2, 3]),
        (99, [0, 1, 2, 3]),  # clamped to the end
        (-5, [3, 0, 1, 2]),  # clamped to the start
    ],
)
def test_insert_at_position(api, abc, position, expected):
    api.insert_into_playlist("title=Mix", ids_term(abc[3]), position)
    assert track_ids(api) == [abc[i] for i in expected]
    assert positions(api) == [0, 1, 2, 3]


def test_insert_several_stay_together(api, abc):
    api.insert_into_playlist("title=Mix", ids_term(abc[3], abc[4]), 1)
    assert track_ids(api) == [abc[0], abc[3], abc[4], abc[1], abc[2]]


def test_insert_skips_tracks_already_present(api, abc):
    api.insert_into_playlist("title=Mix", ids_term(abc[0], abc[3]), 0)
    assert track_ids(api) == [abc[3], abc[0], abc[1], abc[2]]


def test_insert_into_empty_playlist(api, tracks, mix):
    api.insert_into_playlist("title=Mix", ids_term(tracks[0]), 5)
    assert track_ids(api) == [tracks[0]]


@pytest.mark.xfail(
    strict=True,
    reason="BUG: remove_tracks deletes playlist rows without renumbering, so "
    "the leftover gap makes insert_into_playlist land in the wrong place",
)
def test_insert_at_end_after_a_track_was_removed_from_library(api, abc):
    api.remove_tracks(ids_term(abc[1]))  # playlist is now [0, 2]
    api.insert_into_playlist("title=Mix", ids_term(abc[3]), 2)  # 2 = the end
    assert track_ids(api) == [abc[0], abc[2], abc[3]]


# --- delete_playlists --------------------------------------------------------


def test_delete_playlist(api, tracks, mix):
    api.append_playlists("title=Mix", "artist:test")
    result = api.delete_playlists("title=Mix")
    assert result[mix.id][1] is True
    assert result[mix.id][0].title == "Mix"
    assert api.get_playlists() == {}
    assert api.db.query("SELECT * FROM playlist_tracks") == []
    assert len(api.get_tracks()) == len(tracks)  # tracks survive


def test_delete_playlist_no_match(api, mix):
    assert api.delete_playlists("title=Nope") == {}
    assert len(api.get_playlists()) == 1


def test_deleted_title_can_be_reused(api, mix):
    api.delete_playlists("title=Mix")
    assert api.create_playlist("Mix").id != mix.id
