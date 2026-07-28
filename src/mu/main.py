"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import argparse
from importlib.metadata import version

from mu.api import Api
from mu.util import Interface

VERSION = version("mu")


def cmd_scan():
    """Scans the source folder"""
    global api
    for response in api.scan_source_folder():
        Interface.print(
            "",
            url=response["filename"],
            count=[response["count"] + 1, response["total"]],
            ok=response["ok"],
        )


def cmd_version():
    """Prints the version of mu+muc+db"""
    Interface.print_version(VERSION, api.db.SCHEMA)


def cmd_list_tracks(only_favorited: bool = False):
    """Prints all tracks in the database"""
    if only_favorited:
        tracks = api.get_tracks("favorite:1")
    else:
        tracks = api.get_tracks()
    total = len(tracks)
    for i, track_id in enumerate(tracks):
        Interface.print("", track=tracks[track_id], count=[i + 1, total])


def cmd_list_albums():
    """Prints all albums in the database"""
    albums = api.get_albums()
    total = len(albums)
    for i, album_name in enumerate(albums):
        Interface.print("", album=albums[album_name], count=[i + 1, total])


def cmd_list_artists(only_albumartists: bool = False):
    """Prints all the artists in the database"""
    artists = api.get_artists(only_albumartists=only_albumartists)
    total = len(artists)
    for i, artist_name in enumerate(artists):
        Interface.print("", artist=artists[artist_name], count=[i + 1, total])


def cmd_list_playlists():
    """Prints all the playlists in the database"""
    playlists = api.get_playlists()
    for playlist_id in playlists:
        Interface.print("", playlist=playlists[playlist_id])


def cmd_list_playlist(term: str):
    try:
        playlists = api.get_playlists(term)
        for playlist_id in playlists:
            playlist = playlists[playlist_id]
            for i, track in enumerate(playlist.tracks):
                Interface.print("", track=track, count=[i + 1, len(playlist.tracks)])
    except ValueError as e:
        Interface.print(str(e), ok=False)


#
# def cmd_playlist_create(db: Database, title: str, description: str):
#     """Creates a playlist, prints it once created."""
#     playlist = db.create_playlist(title, description=description)
#     Interface.print("", playlist=playlist)
#
#
# def cmd_playlist_append(db: Database, playlist_term: str, tracks_term: str):
#     try:
#         playlist = db.append_playlist(playlist_term, tracks_term)
#         if playlist is not None:
#             for i, track in enumerate(playlist.tracks):
#                 Interface.print("", track=track, count=[i + 1, len(playlist.tracks)])
#     except ValueError as e:
#         Interface.print(str(e), ok=False)
#
#
# def cmd_playlist_remove(db: Database, playlist_term: str, tracks_term: str):
#     try:
#         playlist = db.remove_from_playlist(playlist_term, tracks_term)
#         if playlist is not None:
#             for i, track in enumerate(playlist.tracks):
#                 Interface.print("", track=track, count=[i + 1, len(playlist.tracks)])
#     except ValueError as e:
#         Interface.print(str(e), ok=False)
#
#
# def cmd_playlist_delete(db: Database, playlist_term: str):
#     try:
#         db.delete_playlist(playlist_term)
#         Interface.print("Playlist deleted")
#     except ValueError as e:
#         Interface.print(str(e), ok=False)
#
#
# def cmd_playlist_insert(
#     db: Database, playlist_term: str, tracks_term: str, position: int
# ):
#     try:
#         playlist = db.insert_into_playlist(playlist_term, tracks_term, int(position))
#         for i, track in enumerate(playlist.tracks):
#             Interface.print("", track=track, count=[i + 1, len(playlist.tracks)])
#     except ValueError as e:
#         Interface.print(str(e), ok=False)
#
#
def cmd_import(path: str):
    """Imports all files from the specified directory"""
    for response in api.import_media(path):
        Interface.print(
            "",
            url=response["filename"],
            count=[response["count"] + 1, response["total"]],
            ok=response["ok"],
        )


def cmd_favorite(term: str):
    """Favorite track(s)"""
    try:
        tracks: dict[int, Track] = api.favorite_tracks(term)
        total: int = len(tracks)
        for i, track_id in enumerate(tracks):
            Interface.print("", track=tracks[track_id], count=[i + 1, total])
    except ValueError as e:
        Interface.print(str(e), ok=False)


#
def cmd_search(term: str):
    """Search the database"""
    try:
        tracks = api.get_tracks(term)
        total = len(tracks)
        for i, track_id in enumerate(tracks):
            Interface.print("", track=tracks[track_id], count=[i + 1, total])
    except ValueError as e:
        Interface.print(str(e), ok=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mu",
        description="your personal music library",
        epilog="Created and maintained by Brody King. https://github.com/brodyking/mu",
    )
    subparsers = parser.add_subparsers(
        dest="action", help="options for library", required=True
    )

    _add_list_parser(subparsers)
    # _add_playlist_parser(db, subparsers)
    _add_scan_parser(subparsers)
    _add_version_parser(subparsers)
    # _add_reset_parser(db, subparsers)
    _add_favorite_parser(subparsers)
    _add_import_parser(subparsers)
    _add_search_parser(subparsers)

    return parser


def _add_list_parser(subparsers) -> None:
    list_parser = subparsers.add_parser(
        "list", help="list different parts of your library"
    )
    list_subparsers = list_parser.add_subparsers(
        dest="list_type", required=True, help="what to list"
    )

    # tracks
    tracks = list_subparsers.add_parser("tracks", help="list all tracks in the library")
    tracks.add_argument(
        "-f", "--favorited", action="store_true", help="list only your favorite tracks"
    )
    tracks.set_defaults(
        func=lambda args: cmd_list_tracks(only_favorited=args.favorited)
    )

    # albums
    list_subparsers.add_parser(
        "albums", help="list all albums in the library"
    ).set_defaults(func=lambda _: cmd_list_albums())

    # artists
    artists = list_subparsers.add_parser(
        "artists", help="list all artists in the library"
    )

    artists.add_argument(
        "-a", "--albums", action="store_true", help="list only album artists"
    )
    artists.set_defaults(func=lambda args: cmd_list_artists(args.albums))

    # playlists
    list_subparsers.add_parser(
        "playlists", help="list all playlists in the library"
    ).set_defaults(func=lambda _: cmd_list_playlists())

    playlist = list_subparsers.add_parser(
        "playlist", help="list all tracks in a playlist"
    )
    playlist.add_argument(
        "term",
        help=(
            "the name of the playlist you are searching for.supports prefixes (id:, title:)"
        ),
    )
    playlist.set_defaults(func=lambda args: cmd_list_playlist(args.term))


#
# def _add_playlist_parser(db: Database, subparsers) -> None:
#     playlist_parser = subparsers.add_parser(
#         "playlist",
#         help="crud operations for playlists",
#     )
#     playlist_subparsers = playlist_parser.add_subparsers(
#         dest="action", required=True, help="operation"
#     )
#
#     create = playlist_subparsers.add_parser("create", help="create a new playlist")
#     create.add_argument("title", help="title of playlist")
#     create.add_argument("-d", "--description", help="description of the playlist")
#     create.set_defaults(
#         func=lambda args: cmd_playlist_create(db, args.title, args.description)
#     )
#
#     append = playlist_subparsers.add_parser(
#         "append", help="append track(s) to a playlist"
#     )
#     append.add_argument("playlist_term", help=("the search term for the playlist"))
#     append.add_argument(
#         "tracks_term", help=("the search term for the tracks being appended")
#     )
#     append.set_defaults(
#         func=lambda args: cmd_playlist_append(db, args.playlist_term, args.tracks_term)
#     )
#
#     remove = playlist_subparsers.add_parser(
#         "remove", help="remove track(s) from a playlist"
#     )
#     remove.add_argument("playlist_term", help=("the search term for the playlist"))
#     remove.add_argument(
#         "tracks_term", help=("the search term for the tracks being remove.d")
#     )
#     remove.set_defaults(
#         func=lambda args: cmd_playlist_remove(db, args.playlist_term, args.tracks_term)
#     )
#
#     delete = playlist_subparsers.add_parser("delete", help="delete a playlist")
#     delete.add_argument("playlist_term", help=("the search term for the playlist"))
#     delete.set_defaults(func=lambda args: cmd_playlist_delete(db, args.playlist_term))
#
#     insert = playlist_subparsers.add_parser(
#         "insert", help="insert track(s) to a playlist"
#     )
#     insert.add_argument("playlist_term", help=("the search term for the playlist"))
#     insert.add_argument(
#         "tracks_term", help=("the search term for the tracks being inserted")
#     )
#     insert.add_argument(
#         "position", help=("the position where the track(s) should be inserted")
#     )
#     insert.set_defaults(
#         func=lambda args: cmd_playlist_insert(
#             db, args.playlist_term, args.tracks_term, args.position
#         )
#     )
#
#
def _add_scan_parser(subparsers) -> None:
    subparsers.add_parser(
        "scan", help="imports all files in Source folder"
    ).set_defaults(func=lambda _: cmd_scan())


def _add_version_parser(subparsers) -> None:
    subparsers.add_parser("version", help="get current version").set_defaults(
        func=lambda _: cmd_version()
    )


#
#
# def _add_reset_parser(db: Database, subparsers) -> None:
#     reset = subparsers.add_parser(
#         "reset", help="reset the internal database (keeps songs)"
#     )
#     reset.add_argument(
#         "-y",
#         "--skipconfirmation",
#         action="store_true",
#         help="skip confirmation and reset",
#     )
#     reset.set_defaults(
#         func=lambda args: cmd_reset(db, skip_confirmation=args.skipconfirmation)
#     )
#
#
def _add_favorite_parser(subparsers) -> None:
    favorite = subparsers.add_parser("favorite", help="favorite or unfavorite track(s)")
    favorite.add_argument(
        "term",
        help="the name of the track you wish to favorite (use id: to select by id)",
    )
    favorite.set_defaults(func=lambda args: cmd_favorite(args.term))


def _add_import_parser(subparsers) -> None:
    imp = subparsers.add_parser("import", help="import individual files")
    imp.add_argument(
        "-i", "--itunes", help="import from a itunes xml export", action="store_true"
    )
    imp.add_argument("filepath", help="path to the file(s) being imported")
    imp.set_defaults(func=lambda args: cmd_import(args.filepath))


def _add_search_parser(subparsers) -> None:
    search = subparsers.add_parser("search", help="search the library")
    search.add_argument(
        "term",
        help=(
            "the name of the item(s) you are searching for.prefixes (id:, album:, etc)"
        ),
    )
    search.set_defaults(func=lambda args: cmd_search(args.term))


def main():
    global api
    try:
        api = Api()
        args = build_parser().parse_args()
        args.func(args)
    except ValueError as e:
        Interface.print(str(e), ok=False)


if __name__ == "__main__":
    main()
