"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from importlib.metadata import version
from typing import Annotated

import typer

from mu.api import Api
from mu.io import (
    mu_print,
    mu_print_albums,
    mu_print_artists,
    mu_print_playlist_deletion,
    mu_print_playlist_tracks,
    mu_print_playlists,
    mu_print_tracks,
    mu_print_tracks_deletion,
    mu_print_version,
)
from mu.models import Playlist, Track

VERSION: str = version("mu")

parser = typer.Typer(
    name="mu",
    no_args_is_help=True,
    help="your personal music library",
    epilog="created and maintained by brody king at https://github.com/brodyking/mu",
)
list_parser = typer.Typer(no_args_is_help=True)
playlist_parser = typer.Typer(no_args_is_help=True)
track_parser = typer.Typer(no_args_is_help=True)
parser.add_typer(list_parser, name="ls", help="list different parts of your library")
parser.add_typer(playlist_parser, name="p", help="modify playlists")
parser.add_typer(track_parser, name="t", help="modify tracks")


@parser.command("s", help="refresh metadata")
def scan() -> None:
    """Scans the source folder"""
    for response in api.scan_source_folder():
        mu_print(
            "",
            url=response["filename"],
            count=(response["count"] + 1, response["total"]),
            ok=response["ok"],
        )


@parser.command("v", help="get version")
def print_version() -> None:
    """Prints the version of mu+muc+db"""
    mu_print_version(VERSION, api.db.SCHEMA)


@parser.command("i", help="import media")
def import_tracks(
    path: Annotated[str, typer.Argument(help="directory/location of track(s)")],
) -> None:
    """Imports all files from the specified directory"""
    for response in api.import_media(path):
        mu_print(
            "",
            url=response["filename"],
            count=(response["count"] + 1, response["total"]),
            ok=response["ok"],
        )


@track_parser.command("f", help="favorite track(s)")
def track_favorite(
    tracks_term: Annotated[str, typer.Argument(help="tracks search term")],
) -> None:
    """Favorite track(s)"""
    try:
        tracks: dict[int, Track] = api.favorite_tracks(tracks_term)
        mu_print_tracks(tracks)
    except ValueError as e:
        mu_print(str(e), ok=False)


@track_parser.command("rm", help="remove track(s)")
def track_remove(
    tracks_term: Annotated[str, typer.Argument(help="tracks search term")],
) -> None:
    response: dict[int, tuple[Track, bool]] = api.remove_tracks(tracks_term)
    mu_print_tracks_deletion(response)


@list_parser.command("t", help="list all tracks")
def list_tracks(
    tracks_term: Annotated[
        str | None, typer.Argument(help="tracks search term")
    ] = None,
    only_favorited: Annotated[
        bool, typer.Option("--favorited", "-f", help="list only favorited")
    ] = False,
) -> None:
    """Prints all tracks in the database"""
    if only_favorited:
        tracks_term = f"{tracks_term}&favorite:1" if tracks_term else "favorite:1"
    tracks: dict[int, Track] = api.get_tracks(tracks_term)
    mu_print_tracks(tracks)


@list_parser.command("al", help="list all albums")
def list_albums(
    tracks_term: Annotated[
        str | None, typer.Argument(help="tracks search term")
    ] = None,
) -> None:
    """Prints all albums in the database"""
    albums = api.get_albums(tracks_term)
    mu_print_albums(albums)


@list_parser.command("ar", help="list all artists")
def list_artists(
    tracks_term: Annotated[
        str | None, typer.Argument(help="tracks search term")
    ] = None,
    only_albumartists: Annotated[
        bool, typer.Option("--albumartists", "-a", help="list only album artists")
    ] = False,
) -> None:
    """Prints all the artists in the database"""
    artists = api.get_artists(tracks_term, only_albumartists=only_albumartists)
    mu_print_artists(artists)


@list_parser.command("p", help="list all playlists")
def list_playlists(
    playlists_term: Annotated[
        str | None, typer.Argument(help="playlists search term")
    ] = None,
) -> None:
    """Prints all the playlists in the database"""
    playlists = api.get_playlists(playlists_term)
    mu_print_playlists(playlists)


@list_parser.command("pt", help="list a playlist's tracks")
def list_playlist_tracks(
    playlists_term: Annotated[str, typer.Argument(help="playlists search term")],
) -> None:
    try:
        playlists: dict[int, Playlist] = api.get_playlists(playlists_term)
        mu_print_playlist_tracks(playlists)
    except ValueError as e:
        mu_print(str(e), ok=False)


@playlist_parser.command("a", help="append track(s) into playlist(s)")
def playlist_append(
    playlists_term: Annotated[str, typer.Argument(help="playlists search term")],
    tracks_term: Annotated[str, typer.Argument(help="tracks search term")],
) -> None:
    playlists = api.append_playlists(playlists_term, tracks_term)
    mu_print_playlists(playlists)


@playlist_parser.command("c", help="create a new playlist")
def playlist_create(
    title: Annotated[str, typer.Argument(help="name of playlist")],
    description: Annotated[str, typer.Argument(help="description of playlist")] = "",
) -> None:
    playlist = api.create_playlist(title, description)
    mu_print("", playlist=playlist)


@playlist_parser.command("d", help="delete a playlist")
def playlist_delete(
    playlists_term: Annotated[str, typer.Argument(help="playlist search term")],
) -> None:
    response: dict[int, tuple[Playlist, bool]] = api.delete_playlists(playlists_term)
    mu_print_playlist_deletion(response)


@playlist_parser.command(
    "i", help="insert track(s) into playlist(s) at a specified position"
)
def playlist_insert(
    playlists_term: Annotated[str, typer.Argument(help="playlist search term")],
    tracks_term: Annotated[str, typer.Argument(help="tracks search term")],
    position: Annotated[int, typer.Argument(help="position in playlist")],
) -> None:
    playlists = api.insert_into_playlist(playlists_term, tracks_term, position)
    mu_print_playlists(playlists)


@playlist_parser.command("rm", help="remove track(s) from playlist(s)")
def playlist_remove(
    playlists_term: Annotated[str, typer.Argument(help="playlist search term")],
    tracks_term: Annotated[str, typer.Argument(help="tracks search term")],
) -> None:
    playlists = api.remove_from_playlist(playlists_term, tracks_term)
    mu_print_playlists(playlists)


def main():
    global api
    try:
        api = Api()
        parser()
    except ValueError as e:
        mu_print(str(e), ok=False)


if __name__ == "__main__":
    main()
