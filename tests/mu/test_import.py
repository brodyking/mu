"""
Tests for Api.import_media and Api.scan_source_folder (both go through
Api._ingest). `make_mp3` comes from tests/conftest.py.
"""

from pathlib import Path


def run(gen) -> list[dict]:
    return list(gen)


def titles(api) -> list[str]:
    return sorted(t.title for t in api.get_tracks().values())


# --- import_media ------------------------------------------------------------


def test_import_single_file(api, make_mp3):
    src = make_mp3(title="One", artist="A", album="B")
    results = run(api.import_media(src))
    assert results == [
        {
            "ok": True,
            "count": 1,
            "total": 1,
            "filename": "song.mp3",
            "error": None,
            "skipped": False,
        }
    ]
    (track,) = api.get_tracks().values()
    assert track.title == "One"
    # The library points at the copy inside source_path, not the original.
    assert Path(track.filepath).is_relative_to(api.db.source_path)
    assert Path(track.filepath).exists()


def test_import_folder_recursively_and_only_mp3s(api, make_mp3, tmp_path):
    folder = tmp_path / "incoming"
    make_mp3("a.mp3", folder=folder, title="A")
    make_mp3("b.MP3", folder=folder / "deeper", title="B")
    (folder / "notes.txt").write_text("not music")
    results = run(api.import_media(folder))
    assert [r["count"] for r in results] == [1, 2]
    assert all(r["total"] == 2 for r in results)
    assert titles(api) == ["A", "B"]


def test_import_non_mp3_or_missing_path_does_nothing(api, tmp_path):
    txt = tmp_path / "x.txt"
    txt.write_text("hi")
    assert run(api.import_media(txt)) == []
    assert run(api.import_media(tmp_path / "missing")) == []


def test_import_skips_duplicates_already_in_library(api, make_mp3, tmp_path):
    run(
        api.import_media(
            make_mp3(folder=tmp_path / "1", title="Same", artist="A", album="B")
        )
    )
    again = make_mp3(
        "other-name.mp3", folder=tmp_path / "2", title=" same ", artist="a", album="b"
    )
    (result,) = run(api.import_media(again))
    assert result["skipped"] is True
    assert len(api.get_tracks()) == 1
    # A skipped file is never copied into the library.
    assert not list(api.db.source_path.rglob("other-name.mp3"))


def test_import_skips_duplicates_within_one_import(api, make_mp3, tmp_path):
    folder = tmp_path / "in"
    make_mp3("a.mp3", folder=folder, title="Same")
    make_mp3("b.mp3", folder=folder, title="Same")
    results = run(api.import_media(folder))
    assert [r["skipped"] for r in results] == [False, True]
    assert len(api.get_tracks()) == 1


def test_untitled_tracks_are_told_apart_by_filename(api, make_mp3, tmp_path):
    folder = tmp_path / "in"
    make_mp3("a.mp3", folder=folder)
    make_mp3("b.mp3", folder=folder)
    run(api.import_media(folder))
    assert len(api.get_tracks()) == 2


def test_import_reports_unreadable_files_and_keeps_going(api, make_mp3, tmp_path):
    folder = tmp_path / "in"
    (folder).mkdir()
    (folder / "a-broken.mp3").write_bytes(b"garbage")
    make_mp3("b-good.mp3", folder=folder, title="Good")
    broken, good = run(api.import_media(folder))
    assert broken["ok"] is False
    assert broken["error"].startswith("read failed")
    assert good["ok"] is True
    assert titles(api) == ["Good"]


def test_import_in_batches_saves_everything(api, make_mp3, tmp_path):
    folder = tmp_path / "in"
    for n in range(7):
        make_mp3(f"{n}.mp3", folder=folder, title=f"S{n}")
    results = run(api.import_media(folder, batch_size=3))
    assert [r["count"] for r in results] == list(range(1, 8))
    assert len(api.get_tracks()) == 7


def test_import_progress_is_yielded_after_commit(api, make_mp3, tmp_path):
    folder = tmp_path / "in"
    for n in range(4):
        make_mp3(f"{n}.mp3", folder=folder, title=f"S{n}")
    gen = api.import_media(folder, batch_size=2)
    next(gen)
    # The first batch of two is already in the database.
    assert len(api.get_tracks()) == 2


# --- scan_source_folder ------------------------------------------------------


def test_scan_picks_up_files_in_source(api, make_mp3):
    make_mp3("x.mp3", folder=api.db.source_path / "A" / "B", title="X")
    results = run(api.scan_source_folder())
    assert [r["ok"] for r in results] == [True]
    assert titles(api) == ["X"]


def test_rescan_updates_instead_of_duplicating(api, make_mp3):
    path = make_mp3("x.mp3", folder=api.db.source_path, title="Before")
    run(api.scan_source_folder())
    (tid,) = api.get_tracks()
    api.favorite_tracks(f"id={tid}")

    make_mp3("x.mp3", folder=api.db.source_path, title="After")  # retag in place
    (result,) = run(api.scan_source_folder())
    assert result["skipped"] is False
    track = api.get_tracks()[tid]
    assert track.title == "After"
    assert track.favorite is True
    assert track.filepath == str(path)


def test_scan_of_empty_source(api):
    assert run(api.scan_source_folder()) == []
