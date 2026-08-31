from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from mu.api import Api as MuApi

app = FastAPI()
api = MuApi()


WEB_DIR = Path(__file__).resolve().parent / "static"


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
    desc: bool = False,
):
    return [t.get_dict() for t in api.get_tracks(q, order_by, desc).values()]


@app.get("/api/tracks_by_ids")
def tracks_by_ids(id: list[int] = Query(None)):
    return [t.get_dict() for t in api.get_tracks_by_ids(id).values()]


@app.get("/api/albums")
def albums(q: str | None = None):
    return [a.get_dict() for a in api.get_albums(q).values()]


@app.get("/api/artists")
def artists(q: str | None = None):
    return [a.get_dict() for a in api.get_artists(q).values()]


@app.get("/api/playlists")
def playlists(q: str | None = None):
    return [p.get_dict() for p in api.get_playlists(q).values()]


app.mount("/", StaticFiles(directory=WEB_DIR, html=True))
