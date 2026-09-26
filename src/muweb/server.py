"""
 _   _
| | | | muweb
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import os
import secrets
import subprocess
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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


class LoginBody(BaseModel):
    password: str


COOKIE_NAME = "muwebauth"
GATE_PAGE = WEB_DIR / "login.html"
PUBLIC_PATHS = {
    "/login.html",
    "/js/theme.js",
    "/css/styles.css",
    "/api/auth/login",
}

# Auth state lives on the app so the CLI can set it before uvicorn starts.
app.state.password = None
app.state.session_token = None


def configure_auth(password: str | None) -> None:
    """Enable auth with the given password, or disable it with None/empty."""
    if password:
        app.state.password = password
        # Random per-run token stored in the cookie instead of the password itself.
        app.state.session_token = secrets.token_urlsafe(32)
    else:
        app.state.password = None
        app.state.session_token = None


def auth_enabled() -> bool:
    return app.state.password is not None


@app.post("/api/auth/login")
def auth_login(body: LoginBody, response: Response) -> bool:
    if not auth_enabled():
        return True

    if not secrets.compare_digest(
        body.password.encode(), app.state.password.encode()
    ):
        response.status_code = 401
        return False

    response.set_cookie(
        COOKIE_NAME,
        app.state.session_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,  # 30 days
    )
    return True


@app.post("/api/auth/logout")
def auth_logout(response: Response) -> bool:
    response.delete_cookie(COOKIE_NAME, httponly=True, samesite="lax")
    return True


app.mount("/", StaticFiles(directory=WEB_DIR, html=True))


@app.middleware("http")
async def require_cookie(request: Request, call_next):
    if not auth_enabled() or request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    value = request.cookies.get(COOKIE_NAME, "")
    if not secrets.compare_digest(value.encode(), app.state.session_token.encode()):
        if request.url.path.startswith("/api/"):
            return JSONResponse({"detail": "unauthorized"}, status_code=401)
        return FileResponse(GATE_PAGE, status_code=401)

    return await call_next(request)


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    return FileResponse(INDEX_WEB_DIR)
