"""
 _   _
| | | | muweb
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from mu.api import Api as MuApi
from mu.models import Track

app = FastAPI()
api = MuApi()


WEB_DIR = Path(__file__).resolve().parent / "static"
INDEX_WEB_DIR = Path(__file__).resolve().parent / "static" / "index.html"


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
        t.get_dict()
        for t in api.get_tracks(q, order_by, descending, only_favorited).values()
    ]


@app.get("/api/tracks_by_ids")
def tracks_by_ids(id: list[int] = Query(None)):
    """Returns tracks by ids, more efficient than a regular mu list query."""
    return [t.get_dict() for t in api.get_tracks_by_ids(id).values()]


@app.get("/api/tracks/{track_id}/audio")
def track_audio(track_id: int):
    """Returns the audio file of the requested track"""

    def _track_or_404(track_id: int) -> Track:
        track = api.get_tracks_by_ids([track_id]).get(track_id)
        if track is None:
            raise HTTPException(404, "unknown track")
        return track

    track = _track_or_404(track_id)
    path = Path(track.filepath).resolve()
    root = api.db.source_path.resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise HTTPException(404, "file missing")

    return FileResponse(path, media_type="audio/mpeg")


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


app.mount("/", StaticFiles(directory=WEB_DIR, html=True))


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    return FileResponse(INDEX_WEB_DIR)
