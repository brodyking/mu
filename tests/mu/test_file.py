"""
Tests for mu.file: reading tags, saving album art and copying into the library.
`make_mp3` and png_1px come from tests/conftest.py.
"""

import hashlib

import pytest

from mu.file import (
    _leading_int,
    _sanitize_tag,
    _sniff,
    copy_file_to_source,
    format_duration,
    read_metadata,
)

# --- small helpers -----------------------------------------------------------


@pytest.mark.parametrize(
    ("seconds", "text"),
    [
        (0, "0:00"),
        (None, "0:00"),
        (5, "0:05"),
        (65, "1:05"),
        (599, "9:59"),
        (3600, "1:00:00"),
        (3725, "1:02:05"),
    ],
)
def test_format_duration(seconds, text):
    assert format_duration(seconds) == text


@pytest.mark.parametrize(
    ("value", "number"),
    [
        ("3", 3),
        ("07", 7),
        ("3/12", 3),
        (" 4 / 9 ", 4),
        ("", None),
        ("A1", None),
        (None, None),
    ],
)
def test_leading_int(value, number):
    assert _leading_int(value) == number


@pytest.mark.parametrize(
    ("data", "ext"),
    [
        (b"\xff\xd8\xff\xe0rest", "jpg"),
        (b"\x89PNG\r\n\x1a\n....", "png"),
        (b"GIF89a...", "gif"),
        (b"RIFF....WEBP", "webp"),
        (b"something else", "bin"),
        (b"", "bin"),
    ],
)
def test_sniff(data, ext):
    assert _sniff(data) == ext


@pytest.mark.parametrize(
    ("name", "safe"),
    [
        ("Radiohead", "Radiohead"),
        ("AC/DC", "AC_DC"),
        ('What? "Yes" <no>', "What_ _Yes_ _no_"),
        ("Trailing dots...", "Trailing dots"),
        ("  padded  ", "padded"),
        ("", "Fallback"),
        (None, "Fallback"),
        ("...", "Fallback"),
    ],
)
def test_sanitize_tag(name, safe):
    assert _sanitize_tag(name, "Fallback") == safe


# --- read_metadata -----------------------------------------------------------


def test_read_metadata_tags(make_mp3, tmp_path):
    path = make_mp3(
        title="Song",
        artist="Artist",
        album="Album",
        albumartist="AA",
        date="2001",
        genre="Jazz",
        tracknumber="3/12",
        discnumber="2/2",
    )
    meta = read_metadata(path, None)
    assert meta == {
        "title": "Song",
        "artist": "Artist",
        "album": "Album",
        "albumartist": "AA",
        "date": "2001",
        "genre": "Jazz",
        "time": "0:01",
        "tracknumber": 3,
        "discnumber": 2,
        "filepath": str(path),
        "filename": "song.mp3",
        "albumart": None,
    }


def test_read_metadata_missing_tags_are_none(make_mp3):
    meta = read_metadata(make_mp3(), None)
    for key in ("title", "artist", "album", "albumartist", "tracknumber"):
        assert meta[key] is None


def test_read_metadata_blank_tag_is_none(make_mp3):
    assert read_metadata(make_mp3(title="   "), None)["title"] is None


def test_read_metadata_duration(make_mp3):
    assert read_metadata(make_mp3(seconds=65), None)["time"] == "1:05"


def test_read_metadata_not_an_mp3(tmp_path):
    bad = tmp_path / "bad.mp3"
    bad.write_bytes(b"this is not audio")
    with pytest.raises(ValueError, match="cannot read bad.mp3"):
        read_metadata(bad, None)


# --- album art ---------------------------------------------------------------


def test_album_art_is_saved_by_content_hash(make_mp3, tmp_path, png_1px):
    art_dir = tmp_path / "art"
    art_dir.mkdir()
    meta = read_metadata(make_mp3(art=png_1px), art_dir)
    expected = f"{hashlib.sha256(png_1px).hexdigest()}.png"
    assert meta["albumart"] == expected
    assert (art_dir / expected).read_bytes() == png_1px


def test_album_art_is_shared_between_tracks(make_mp3, tmp_path, png_1px):
    art_dir = tmp_path / "art"
    art_dir.mkdir()
    a = read_metadata(make_mp3("a.mp3", art=png_1px), art_dir)
    b = read_metadata(make_mp3("b.mp3", art=png_1px), art_dir)
    assert a["albumart"] == b["albumart"]
    assert len(list(art_dir.iterdir())) == 1  # no leftover temp files either


def test_no_album_art(make_mp3, tmp_path):
    art_dir = tmp_path / "art"
    art_dir.mkdir()
    assert read_metadata(make_mp3(), art_dir)["albumart"] is None
    assert list(art_dir.iterdir()) == []


# --- copy_file_to_source -----------------------------------------------------


def test_copy_organises_by_artist_and_album(make_mp3, tmp_path):
    src = make_mp3(artist="AC/DC", album="Back in Black")
    meta = copy_file_to_source(src, tmp_path / "lib", tmp_path / "art")
    dest = tmp_path / "lib" / "AC_DC" / "Back in Black" / "song.mp3"
    assert dest.read_bytes() == src.read_bytes()
    assert meta["filepath"] == str(dest)
    assert meta["filename"] == "song.mp3"
    assert src.exists()  # copied, not moved


def test_copy_without_tags_uses_unknown_folders(make_mp3, tmp_path):
    src = make_mp3()
    meta = copy_file_to_source(src, tmp_path / "lib", tmp_path / "art")
    assert meta["filepath"] == str(
        tmp_path / "lib" / "Unknown Artist" / "Unknown Album" / "song.mp3"
    )


def test_copy_never_overwrites(make_mp3, tmp_path):
    lib = tmp_path / "lib"
    first = copy_file_to_source(
        make_mp3(folder=tmp_path / "a", artist="X"), lib, tmp_path
    )
    second = copy_file_to_source(
        make_mp3(folder=tmp_path / "b", artist="X"), lib, tmp_path
    )
    third = copy_file_to_source(
        make_mp3(folder=tmp_path / "c", artist="X"), lib, tmp_path
    )
    assert [m["filename"] for m in (first, second, third)] == [
        "song.mp3",
        "song (1).mp3",
        "song (2).mp3",
    ]


def test_copy_file_already_in_place_is_left_alone(make_mp3, tmp_path):
    lib = tmp_path / "lib"
    src = make_mp3(folder=lib / "X" / "Y", artist="X", album="Y")
    meta = copy_file_to_source(src, lib, tmp_path)
    assert meta["filepath"] == str(src)
    assert list((lib / "X" / "Y").iterdir()) == [src]


def test_copy_does_not_change_callers_meta(make_mp3, tmp_path):
    src = make_mp3(artist="X")
    meta = read_metadata(src, None)
    copy_file_to_source(src, tmp_path / "lib", tmp_path, meta=meta)
    assert meta["filepath"] == str(src)
