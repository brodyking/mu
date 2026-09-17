"""
 _   _
| | | | muweb
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import subprocess
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from mu.api import Api as MuApi
from mu.models import Track

app = FastAPI(
    title="Muweb API",
    description="A custom FastAPI wrapper for the µ python library.",
    contact={"name": "Brody King", "url": "https://github.com/brodyking/mu"},
    docs_url="/api/",
)
api = MuApi()


WEB_DIR = Path(__file__).resolve().parent / "static"
INDEX_WEB_DIR = Path(__file__).resolve().parent / "static" / "index.html"


def track_json(t: Track) -> dict:
    d = t.get_dict()
    d.pop("filepath")
    d["audio_url"] = f"/api/tracks/{t.id}/audio"
    d["art_url"] = f"/api/tracks/{t.id}/art" if t.albumart else None
    return d


def track_or_404(track_id: int) -> Track:
    track = api.get_tracks_by_ids([track_id]).get(track_id)
    if track is None:
        raise HTTPException(404, "unknown track")
    return track


@app.get("/api/tracks")
def tracks(
    q: str | None = None,
    order_by: Literal[
        "artist",
        "album",
        "date",
        "dateadded",
        "id",
        "plays",
        "genre",
        "title",
        "time",
        "cancel",
        "shuffle",
        "reset",
    ]
    | None = None,
    descending: bool = False,
    only_favorited: bool = False,
):
    """Returns tracks from a mu search query"""
    return [
        track_json(t)
        for t in api.get_tracks(q, order_by, descending, only_favorited).values()
    ]


@app.get("/api/tracks_by_ids")
def tracks_by_ids(ids: list[int] = Query(None)):
    """Returns tracks by ids, more efficient than a regular mu list query."""
    return [track_json(t) for t in api.get_tracks_by_ids(ids).values()]


@app.get("/api/tracks/{track_id}/audio")
def track_audio(track_id: int, t: float = 0):
    track = track_or_404(track_id)
    path = Path(track.filepath).resolve()
    proc = subprocess.Popen(
        [
            "ffmpeg",
            "-ss",
            str(t),
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            "-f",
            "mp3",
            "-",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()

    if proc.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"ffmpeg failed: {stderr.decode(errors='replace')}",
        )

    return Response(content=stdout, media_type="audio/mpeg")


@app.get("/api/tracks/{track_id}/art")
def track_art(track_id: int):
    track = track_or_404(track_id)
    if not track.albumart:
        raise HTTPException(404, "no art")

    root = api.db.albumart_path.resolve()
    path = (root / track.albumart).resolve()
    if path.parent != root or not path.is_file():
        raise HTTPException(404, "art missing")

    return FileResponse(path)


@app.get("/api/albums")
def albums(q: str | None = None):
    """Returns albums from a mu search query"""
    return [a.get_dict() for a in api.get_albums(q).values()]


@app.get("/api/artists")
def artists(q: str | None = None):
    """Returns artists from a mu search query"""
    return [a.get_dict() for a in api.get_artists(q).values()]


@app.get("/api/playlists")
def playlists(q: str | None = None):
    """Returns playlists from a mu search query"""
    return [p.get_dict() for p in api.get_playlists(q).values()]


@app.put("/api/tracks/{track_id}/favorite")
def favorite(track_id: int):
    return [t.get_dict() for t in api.favorite_tracks(f"id={track_id}").values()]


app.mount("/", StaticFiles(directory=WEB_DIR, html=True))


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    return FileResponse(INDEX_WEB_DIR)
