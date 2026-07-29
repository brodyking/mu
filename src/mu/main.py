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
from mu.io import mu_print, mu_print_version

VERSION: str = version("mu")

parser = typer.Typer(
    name="mu",
    no_args_is_help=True,
    help="your personal music library",
    epilog="maintained by brodyking at https://github.com/brodyking/mu",
)
list_parser = typer.Typer(no_args_is_help=True)
playlist_parser = typer.Typer(no_args_is_help=True)
parser.add_typer(list_parser, name="ls", help="list different parts of your library")
parser.add_typer(playlist_parser, name="p", help="modify playlists")


@parser.command("scan", help="refresh metadata")
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


@parser.command("f", help="favorite track(s)")
def favorite_tracks(term: Annotated[str, typer.Argument(help="search term")]) -> None:
    """Favorite track(s)"""
    try:
        tracks = api.favorite_tracks(term)
        total: int = len(tracks)
        for i, track_id in enumerate(tracks):
            mu_print("", track=tracks[track_id], count=(i + 1, total))
    except ValueError as e:
        mu_print(str(e), ok=False)


@list_parser.command("t", help="list all tracks")
def list_tracks(
    only_favorited: Annotated[
        bool, typer.Option("--favorited", "-f", help="list only favorited")
    ] = False,
) -> None:
    """Prints all tracks in the database"""
    if only_favorited:
        tracks = api.get_tracks("favorite:1")
    else:
        tracks = api.get_tracks()
    total = len(tracks)
    for i, track_id in enumerate(tracks):
        mu_print("", track=tracks[track_id], count=(i + 1, total))


@list_parser.command("al", help="list all albums")
def list_albums() -> None:
    """Prints all albums in the database"""
    albums = api.get_albums()
    total = len(albums)
    for i, album_name in enumerate(albums):
        mu_print("", album=albums[album_name], count=(i + 1, total))


@list_parser.command("ar", help="list all artists")
def list_artists(
    only_albumartists: Annotated[
        bool, typer.Option("--albumartists", "-a", help="list only album artists")
    ] = False,
) -> None:
    """Prints all the artists in the database"""
    artists = api.get_artists(only_albumartists=only_albumartists)
    total = len(artists)
    for i, artist_name in enumerate(artists):
        mu_print("", artist=artists[artist_name], count=(i + 1, total))


@list_parser.command("p", help="list all playlists")
def list_playlists() -> None:
    """Prints all the playlists in the database"""
    playlists = api.get_playlists()
    total = len(playlists)
    for i, pid in enumerate(playlists):
        mu_print("", playlist=playlists[pid], count=(i + 1, total))


@list_parser.command("pt", help="list a playlist's tracks")
def list_playlist(term: Annotated[str, typer.Argument(help="search term")]) -> None:
    try:
        playlists = api.get_playlists(term)
        for pid in playlists:
            playlist = playlists[pid]
            for i, track in enumerate(playlist.tracks):
                mu_print("", track=track, count=(i + 1, len(playlist.tracks)))
    except ValueError as e:
        mu_print(str(e), ok=False)


@playlist_parser.command("c", help="create a new playlist")
def playlist_create(
    title: Annotated[str, typer.Argument(help="name of playlist")],
    description: Annotated[str, typer.Argument(help="description of playlist")] = "",
) -> None:
    playlist = api.create_playlist(title, description)
    mu_print("", playlist=playlist)


@playlist_parser.command("a", help="append track(s) into playlist(s)")
def playlist_append(
    playlists_term: Annotated[str, typer.Argument(help="playlist search term")],
    tracks_term: Annotated[str, typer.Argument(help="tracks search term")],
) -> None:
    playlists = api.append_playlists(playlists_term, tracks_term)
    for i, pid in enumerate(playlists):
        mu_print("", playlist=playlists[pid], count=(i + 1, len(playlists)))


@playlist_parser.command("rm", help="unappend track(s) from playlist(s)")
def playlist_remove(
    playlists_term: Annotated[str, typer.Argument(help="playlist search term")],
    tracks_term: Annotated[str, typer.Argument(help="tracks search term")],
) -> None:
    playlists = api.playlist_remove(playlists_term, tracks_term)
    total = len(playlists)
    for i, pid in enumerate(playlists):
        mu_print("", playlist=playlists[pid], count=(i + 1, total))


def main():
    global api
    try:
        api = Api()
        parser()
    except ValueError as e:
        mu_print(str(e), ok=False)


if __name__ == "__main__":
    main()
