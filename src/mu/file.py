"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import hashlib
import os
import re
import shutil
from pathlib import Path

from mutagen import MutagenError
from mutagen.mp3 import MP3

# ID3 frame -> metadata key
_TEXT_FRAMES = {
    "TIT2": "title",
    "TPE1": "artist",
    "TALB": "album",
    "TPE2": "albumartist",
    "TDRC": "date",
    "TCON": "genre",
}

_MAGIC = (
    (b"\xff\xd8\xff", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"GIF8", "gif"),
    (b"RIFF", "webp"),
)


def read_metadata(
    file_path: Path,
    albumart_path: Path | None,
) -> dict:
    """
    Reads tags, duration, and album art for an MP3.
    Art is deduplicated by content hash; the returned value is a
    bare filename relative to albumart_path.
    """
    try:
        audio = MP3(file_path)
        duration = format_duration(int(audio.info.length or 0))
        tags = audio.tags
    except MutagenError as exc:
        raise ValueError(f"cannot read {file_path.name}: {exc}") from exc

    meta: dict[str, str | int | None] = {
        key: _text(tags, frame) for frame, key in _TEXT_FRAMES.items()
    }
    meta.update(
        {
            "time": duration,
            "tracknumber": _leading_int(_text(tags, "TRCK")),
            "discnumber": _leading_int(_text(tags, "TPOS")),
            "filepath": str(file_path),
            "filename": file_path.name,
            "albumart": extract_album_art(tags, albumart_path)
            if albumart_path
            else None,
        }
    )
    return meta


def extract_album_art(tags, albumart_path: Path) -> str | None:
    """Saves embedded art as <sha256>.<ext>. Returns the filename, or None."""
    if tags is None:
        return None

    # Prefer the front cover (APIC type 3) when a file embeds several images.
    for frame in sorted(tags.getall("APIC"), key=lambda f: f.type != 3):
        data = frame.data
        if not data:
            continue
        name = f"{hashlib.sha256(data).hexdigest()}.{_sniff(data)}"
        path = albumart_path / name
        if not path.exists():
            _atomic_write(path, data)
        return name
    return None


def format_duration(seconds: int | None) -> str:
    """3:42 for display. Handles hour-long files."""
    seconds = int(seconds or 0)
    hours, rem = divmod(seconds, 3600)
    mins, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"


def _text(tags, frame_id: str) -> str | None:
    """First text value of an ID3 frame, or None."""
    frame = tags.get(frame_id) if tags else None
    if frame is None or not frame.text:
        return None
    return str(frame.text[0]).strip() or None


def _leading_int(value: str | None) -> int | None:
    """'3/12' -> 3, '07' -> 7, anything else -> None."""
    if value is None:
        return None
    head = value.split("/")[0].strip()
    return int(head) if head.isdigit() else None


def _sniff(data: bytes) -> str:
    """Extension from magic bytes — APIC mime fields lie constantly."""
    for magic, ext in _MAGIC:
        if data.startswith(magic):
            return ext
    return "bin"


def _atomic_write(path: Path, data: bytes) -> None:
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def _sanitize_tag(name: str | None, fallback: str) -> str:
    """Make a tag value safe as a folder name."""
    name = (name or "").strip()
    if not name:
        return fallback
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)  # illegal path chars
    name = name.rstrip(". ")  # trailing dot/space
    return name or fallback


def copy_file_to_source(src: Path, source_path: Path, albumart_path: Path) -> dict:
    """
    Reads metadata once, copies the file into source_path organised as
    artist/album/, and returns that metadata with filepath/filename
    pointing at the copy.
    """
    meta = read_metadata(src, albumart_path)  # the ONE read

    dest_dir = (
        source_path
        / _sanitize_tag(meta["artist"], "Unknown Artist")
        / _sanitize_tag(meta["album"], "Unknown Album")
    )
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name  # the FILE, not the dir

    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)

    meta["filepath"] = str(dest)
    meta["filename"] = dest.name
    return meta
