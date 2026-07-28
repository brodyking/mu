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
from mu.util import Interface

VERSION: str = version("mu")

parser = typer.Typer(
    name="mu",
    no_args_is_help=True,
    help="your personal music library",
    epilog="maintained by brodyking at https://github.com/brodyking/mu",
)
list_parser = typer.Typer(no_args_is_help=True)
parser.add_typer(list_parser, name="list", help="list different parts of your library")
api = Api()


@parser.command("scan", help="refresh metadata")
def scan():
    """Scans the source folder"""
    global api
    for response in api.scan_source_folder():
        Interface.print(
            "",
            url=response["filename"],
            count=[response["count"] + 1, response["total"]],
            ok=response["ok"],
        )


@parser.command("version", help="get version")
def print_version():
    """Prints the version of mu+muc+db"""
    Interface.print_version(VERSION, api.db.SCHEMA)


@parser.command("import", help="import media")
def import_tracks(
    path: Annotated[str, typer.Argument(help="directory/location of track(s)")],
):
    """Imports all files from the specified directory"""
    for response in api.import_media(path):
        Interface.print(
            "",
            url=response["filename"],
            count=[response["count"] + 1, response["total"]],
            ok=response["ok"],
        )


@parser.command("favorite", help="favorite track(s)")
def favorite_tracks(term: Annotated[str, typer.Argument(help="search term")]):
    """Favorite track(s)"""
    try:
        tracks = api.favorite_tracks(term)
        total: int = len(tracks)
        for i, track_id in enumerate(tracks):
            Interface.print("", track=tracks[track_id], count=[i + 1, total])
    except ValueError as e:
        Interface.print(str(e), ok=False)


@parser.command("search")
def search_tracks(term: Annotated[str, typer.Argument(help="search term")]):
    """Search the database"""
    try:
        tracks = api.get_tracks(term)
        total = len(tracks)
        for i, track_id in enumerate(tracks):
            Interface.print("", track=tracks[track_id], count=[i + 1, total])
    except ValueError as e:
        Interface.print(str(e), ok=False)


@list_parser.command("tracks", help="list all tracks")
def list_tracks(
    only_favorited: Annotated[
        bool, typer.Option("--favorited", "-f", help="list only favorited")
    ] = False,
):
    """Prints all tracks in the database"""
    if only_favorited:
        tracks = api.get_tracks("favorite:1")
    else:
        tracks = api.get_tracks()
    total = len(tracks)
    for i, track_id in enumerate(tracks):
        Interface.print("", track=tracks[track_id], count=[i + 1, total])


@list_parser.command("albums", help="list all albums")
def list_albums():
    """Prints all albums in the database"""
    albums = api.get_albums()
    total = len(albums)
    for i, album_name in enumerate(albums):
        Interface.print("", album=albums[album_name], count=[i + 1, total])


@list_parser.command("artists", help="list all artists")
def list_artists(
    only_albumartists: Annotated[
        bool, typer.Option("--albumartists", "-a", help="list only album artists")
    ] = False,
):
    """Prints all the artists in the database"""
    artists = api.get_artists(only_albumartists=only_albumartists)
    total = len(artists)
    for i, artist_name in enumerate(artists):
        Interface.print("", artist=artists[artist_name], count=[i + 1, total])


@list_parser.command("playlists", help="list all playlists")
def list_playlists():
    """Prints all the playlists in the database"""
    playlists = api.get_playlists()
    for playlist_id in playlists:
        Interface.print("", playlist=playlists[playlist_id])


@list_parser.command("playlist", help="list a playlist's tracks")
def list_playlist(term: Annotated[str, typer.Argument(help="search term")]):
    try:
        playlists = api.get_playlists(term)
        for playlist_id in playlists:
            playlist = playlists[playlist_id]
            for i, track in enumerate(playlist.tracks):
                Interface.print("", track=track, count=[i + 1, len(playlist.tracks)])
    except ValueError as e:
        Interface.print(str(e), ok=False)


def main():
    global api
    try:
        api = Api()
        parser()
    except ValueError as e:
        Interface.print(str(e), ok=False)


if __name__ == "__main__":
    main()
