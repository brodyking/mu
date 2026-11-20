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


# MPEG-1 Layer III, 128 kbps, 44.1 kHz, no CRC, no padding: 417 bytes a frame,
# about 26 ms of (silent) audio. Enough for mutagen to read it as a real MP3.
_MP3_FRAME = b"\xff\xfb\x90\x64" + b"\x00" * 413
_FRAMES_PER_SECOND = 44100 / 1152

# A real 1x1 PNG, used as embedded album art.
PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082"
)


@pytest.fixture
def png_1px() -> bytes:
    """The bytes of a valid 1x1 PNG."""
    return PNG_1PX


@pytest.fixture
def make_mp3(tmp_path):
    """
    Returns a function that writes a small, valid MP3 with the ID3 tags you
    ask for and returns its path. Tags left as None are not written at all.

        path = make_mp3("a.mp3", title="Song", artist="Someone", seconds=2)
    """
    from mutagen.id3 import APIC, ID3, TALB, TCON, TDRC, TIT2, TPE1, TPE2, TPOS, TRCK

    frames = {
        "title": TIT2,
        "artist": TPE1,
        "album": TALB,
        "albumartist": TPE2,
        "date": TDRC,
        "genre": TCON,
        "tracknumber": TRCK,
        "discnumber": TPOS,
    }

    def make(
        name: str = "song.mp3",
        folder=None,
        seconds: float = 1,
        art: bytes | None = None,
        **tags,
    ):
        folder = folder if folder is not None else tmp_path / "incoming"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / name
        # Half a second of padding so mu's whole-second rounding lands on `seconds`.
        n_frames = round((seconds + 0.5) * _FRAMES_PER_SECOND)
        path.write_bytes(_MP3_FRAME * n_frames)

        id3 = ID3()
        for key, value in tags.items():
            if value is not None:
                id3.add(frames[key](encoding=3, text=str(value)))
        if art is not None:
            id3.add(APIC(encoding=3, mime="image/png", type=3, desc="", data=art))
        id3.save(path)
        return path

    return make
