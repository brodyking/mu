"""
Shared fixtures, available to every test file under tests/ without importing.
"""

import pytest

from mu.api import Api


@pytest.fixture
def api(tmp_path):
    """
    An Api backed by a brand-new, empty library inside a temporary folder.
    Nothing touches ~/Music/mu, and every test gets its own fresh copy.
    """
    api = Api(
        db_path=tmp_path / "mu.db",
        source_path=tmp_path / "source",
        albumart_path=tmp_path / "albumart",
    )
    yield api  # the test runs here
    api.db.close()  # cleanup runs afterward, even if the test failed


@pytest.fixture
def tracks(api):
    """
    Inserts five tracks into the library and returns their ids in order.
    A fresh database starts ids at 1, so this is [1, 2, 3, 4, 5], but tests
    use the returned list rather than assuming that.
    """
    ids = []
    with api.db.write() as conn:
        for n in range(1, 6):
            track = api._upsert_track(
                conn,
                {
                    "title": f"Song {n}",
                    "artist": "Test Artist",
                    "album": "Test Album",
                    "time": "3:00",
                    "tracknumber": n,
                    "albumartist": "Test Artist",
                    "discnumber": 1,
                    "genre": "Test",
                    "date": "2026",
                    "filepath": f"/fake/song{n}.mp3",
                    "filename": f"song{n}.mp3",
                    "albumart": None,
                },
            )
            ids.append(track.id)
    return ids
