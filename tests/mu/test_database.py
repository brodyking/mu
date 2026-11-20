"""
Tests for mu.database.Database: setup, schema checks and transactions.
"""

import sqlite3

import pytest

from mu.database import Database


@pytest.fixture
def db(tmp_path):
    db = Database(tmp_path / "mu.db", tmp_path / "source", tmp_path / "art")
    yield db
    db.close()


def tables(db) -> set[str]:
    rows = db.query("SELECT name FROM sqlite_master WHERE type = 'table'")
    return {r["name"] for r in rows}


# --- setup -------------------------------------------------------------------


def test_creates_folders(tmp_path):
    with Database(
        tmp_path / "nested" / "mu.db", tmp_path / "src", tmp_path / "art"
    ) as db:
        assert db.db_path.exists()
        assert (tmp_path / "src").is_dir()
        assert (tmp_path / "art").is_dir()


def test_creates_tables(db):
    assert {"tracks", "playlists", "playlist_tracks"} <= tables(db)


def test_sets_schema_version(db):
    assert db.query("PRAGMA user_version")[0][0] == Database.SCHEMA


def test_foreign_keys_are_on(db):
    assert db.query("PRAGMA foreign_keys")[0][0] == 1


def test_reopening_keeps_data(tmp_path):
    paths = (tmp_path / "mu.db", tmp_path / "source", tmp_path / "art")
    with Database(*paths) as db:
        with db.write() as conn:
            conn.execute("INSERT INTO playlists (title) VALUES ('Kept')")
    with Database(*paths) as db:
        assert [r["title"] for r in db.query("SELECT title FROM playlists")] == ["Kept"]


def test_rejects_library_from_another_schema_version(tmp_path):
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.execute(f"PRAGMA user_version = {Database.SCHEMA + 1}")
    conn.close()
    with pytest.raises(ValueError, match="Library version"):
        Database(path, tmp_path / "source", tmp_path / "art")


def test_rows_are_accessible_by_column_name(db):
    with db.write() as conn:
        conn.execute("INSERT INTO playlists (title) VALUES ('Mix')")
    assert db.query("SELECT * FROM playlists")[0]["title"] == "Mix"


# --- write() -----------------------------------------------------------------


def test_write_commits(db):
    with db.write() as conn:
        conn.execute("INSERT INTO playlists (title) VALUES ('A')")
    assert len(db.query("SELECT * FROM playlists")) == 1


def test_write_rolls_back_on_error(db):
    with pytest.raises(RuntimeError):
        with db.write() as conn:
            conn.execute("INSERT INTO playlists (title) VALUES ('A')")
            raise RuntimeError("boom")
    assert db.query("SELECT * FROM playlists") == []
    assert not db.connection.in_transaction


def test_nested_write_joins_outer_transaction(db):
    with pytest.raises(RuntimeError):
        with db.write() as outer:
            outer.execute("INSERT INTO playlists (title) VALUES ('A')")
            with db.write() as inner:
                inner.execute("INSERT INTO playlists (title) VALUES ('B')")
            raise RuntimeError("boom")
    # The inner block must not have committed on its own.
    assert db.query("SELECT * FROM playlists") == []


def test_unique_playlist_title_is_enforced(db):
    with pytest.raises(sqlite3.IntegrityError):
        with db.write() as conn:
            conn.execute("INSERT INTO playlists (title) VALUES ('A')")
            conn.execute("INSERT INTO playlists (title) VALUES ('A')")
