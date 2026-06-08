"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import argparse
from importlib.metadata import version
from multiprocessing import Value

from mu.database.database import Database
from mu.database.schemaerror import SchemaError
from mu.util import Interface

VERSION = version("mu")


def cmd_scan(db: Database):
    """Scans the source folder"""
    for response in db.scan_source_folder():
        Interface.print(
            response["filename"],
            count=[response["count"] + 1, response["total"]],
            ok=response["ok"],
        )


def cmd_version(db: Database):
    """Prints the version of mu+muc+db"""
    Interface.print_version(VERSION, db.DATABASE_VERSION)


def cmd_reset(db: Database, skip_confirmation=False):
    """Asks for confirmation from the user, resets the DB"""
    if skip_confirmation or Interface.prompt_bool(
        "Are you sure you want to erase the database file? "
        "This action cannot be undone."
    ):
        db.reset_db()
        Interface.print(
            "Database has been reset. "
            'Your files are still in ~/mu/source/. Type "mu scan" to rebuild.'
        )


def cmd_list_tracks(db: Database, only_favorited: bool = False):
    """Prints all tracks in the database"""
    tracks = db.list_library_tracks(only_favorited=only_favorited)
    for track_id in tracks:
        Interface.print("", track=tracks[track_id])


def cmd_list_albums(db: Database):
    """Prints all albums in the database"""
    albums = db.list_library_albums()
    total = len(albums)
    for i, album in enumerate(albums):
        Interface.print("", album=album, count=[i + 1, total])


def cmd_list_artists(db: Database, album_artist: bool = False):
    """Prints all the artists in the database"""
    artists = db.list_library_artists(album_artist=album_artist)
    total = len(artists)
    for i, artist in enumerate(artists):
        Interface.print("", artist=artist[0], count=[i + 1, total])


def cmd_list_playlists(db: Database):
    """Prints all the playlists in the database"""
    playlists = db.list_playlists()
    for playlist in playlists:
        Interface.print("", playlist=playlist)


def cmd_playlist_create(db: Database, title: str, description: str):
    """Creates a playlist, prints it once created."""
    playlist = db.create_playlist(title, description=description)
    Interface.print("", playlist=playlist)


def cmd_playlist_list(db: Database, term: str):
    try:
        playlist = db.get_playlist(term)
        if playlist is not None:
            for i, track in enumerate(playlist.tracks):
                Interface.print("", track=track, count=[i + 1, len(playlist.tracks)])
        else:
            Interface.print("Playlist does not exist", ok=False)
    except ValueError:
        kw_missing_error = (
            "The search query is missing a prefix."
            "Please specify how you are searching by typing "
            "the prefix followed by a colon. Ex: title:gym,id:1"
        )
        Interface.print(kw_missing_error, ok=False)


def cmd_import(db: Database, path: str):
    """Imports all files from the specified directory"""
    for response in db.import_media(path):
        Interface.print(
            response["filename"],
            count=[response["count"] + 1, response["total"]],
            ok=response["ok"],
        )


def cmd_favorite(db: Database, term: str):
    """Favorite track(s)"""
    tracks = db.favorite(term)
    total = len(tracks)
    for i, track in enumerate(tracks):
        Interface.print("", track=track, count=[i + 1, total])


def cmd_search(db: Database, term: str):
    """Search the database"""
    try:
        tracks = db.search(term)
        total = len(tracks)
        for i, track in enumerate(tracks):
            Interface.print("", track=track, count=[i + 1, total])
    except ValueError:
        kw_missing_error = (
            "The search query is missing a prefix. "
            "Please specify how you are searching by typing "
            'the prefix followed by a colon. Ex: "artist:aphex twin"'
        )
        Interface.print(kw_missing_error, ok=False)


def build_parser(db: Database) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mu",
        description="your personal music library",
        epilog="Created and maintained by Brody King. https://github.com/brodyking/mu",
    )
    subparsers = parser.add_subparsers(
        dest="action", help="options for library", required=True
    )

    _add_list_parser(db, subparsers)
    _add_playlist_parser(db, subparsers)
    _add_scan_parser(db, subparsers)
    _add_version_parser(db, subparsers)
    _add_reset_parser(db, subparsers)
    _add_favorite_parser(db, subparsers)
    _add_import_parser(db, subparsers)
    _add_search_parser(db, subparsers)

    return parser


def _add_list_parser(db: Database, subparsers) -> None:
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
        func=lambda args: cmd_list_tracks(db, only_favorited=args.favorited)
    )

    # albums
    list_subparsers.add_parser(
        "albums", help="list all albums in the library"
    ).set_defaults(func=lambda _: cmd_list_albums(db))

    # artists
    artists = list_subparsers.add_parser(
        "artists", help="list all artists in the library"
    )
    artists.add_argument(
        "-a", "--albums", action="store_true", help="list only album artists"
    )
    artists.set_defaults(func=lambda args: cmd_list_artists(db, args.albums))

    # playlists
    list_subparsers.add_parser(
        "playlists", help="list all playlists in the library"
    ).set_defaults(func=lambda _: cmd_list_playlists(db))


def _add_playlist_parser(db: Database, subparsers) -> None:
    playlist_parser = subparsers.add_parser(
        "playlist",
        help="crud operations for playlists",
    )
    playlist_subparsers = playlist_parser.add_subparsers(
        dest="action", required=True, help="operation"
    )

    create = playlist_subparsers.add_parser("create", help="create a new playlist")
    create.add_argument("title", help="title of playlist")
    create.add_argument("-d", "--description", help="description of the playlist")
    create.set_defaults(
        func=lambda args: cmd_playlist_create(db, args.title, args.description)
    )

    list = playlist_subparsers.add_parser("list", help="list tracks in a playlist")
    list.add_argument(
        "term",
        help=(
            "the name of the playlist you are searching for."
            "supports prefixes (id:, title:)"
        ),
    )
    list.set_defaults(func=lambda args: cmd_playlist_list(db, args.term))


def _add_scan_parser(db: Database, subparsers) -> None:
    subparsers.add_parser(
        "scan", help="imports all files in Source folder"
    ).set_defaults(func=lambda _: cmd_scan(db))


def _add_version_parser(db: Database, subparsers) -> None:
    subparsers.add_parser("version", help="get current version").set_defaults(
        func=lambda _: cmd_version(db)
    )


def _add_reset_parser(db: Database, subparsers) -> None:
    reset = subparsers.add_parser(
        "reset", help="reset the internal database (keeps songs)"
    )
    reset.add_argument(
        "-y",
        "--skipconfirmation",
        action="store_true",
        help="skip confirmation and reset",
    )
    reset.set_defaults(
        func=lambda args: cmd_reset(db, skip_confirmation=args.skipconfirmation)
    )


def _add_favorite_parser(db: Database, subparsers) -> None:
    favorite = subparsers.add_parser("favorite", help="favorite or unfavorite track(s)")
    favorite.add_argument(
        "term",
        help="the name of the track you wish to favorite (use id: to select by id)",
    )
    favorite.set_defaults(func=lambda args: cmd_favorite(db, args.term))


def _add_import_parser(db: Database, subparsers) -> None:
    imp = subparsers.add_parser("import", help="import individual files")
    imp.add_argument("filepath", help="path to the file being imported")
    imp.set_defaults(func=lambda args: cmd_import(db, args.filepath))


def _add_search_parser(db: Database, subparsers) -> None:
    search = subparsers.add_parser("search", help="search the library")
    search.add_argument(
        "term",
        help="the name of the item(s) you are searching for. supports prefixes (id:, album:, etc)",
    )
    search.set_defaults(func=lambda args: cmd_search(db, args.term))


def main():
    try:
        db = Database()
        args = build_parser(db).parse_args()
        args.func(args)
    except SchemaError as e:
        Interface.print_outdated_version(e.expected, e.found)


if __name__ == "__main__":
    main()
