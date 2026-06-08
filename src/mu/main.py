"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import argparse
from importlib.metadata import version

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
    """Prints all the artits in the database"""
    artists = db.list_library_artists(album_artist=album_artist)
    total = len(artists)
    for i, artist in enumerate(artists):
        Interface.print("", artist=artist[0], count=[i + 1, total])


def cmd_list_playlists(db: Database):
    playlists = db.list_playlists()
    for playlist in playlists:
        Interface.print("", playlist=playlist)


def cmd_playlist_create(db: Database, title: str, description: str):
    playlist = db.create_playlist(title, description=description)
    Interface.print("", playlist=playlist)


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
    """Builds the parser"""
    parser = argparse.ArgumentParser(
        prog="mu",
        description="your personal music library",
        epilog="""
            Created and maintained by Brody King.
            You can find this project at https://github.com/brodyking/mu
        """,
    )

    subparsers = parser.add_subparsers(
        dest="action", help="options for library", required=True
    )

    # Listing
    list_parser = subparsers.add_parser(
        "list",
        help="list different parts of your library",
        description="List different parts of your library",
    )

    list_subparsers = list_parser.add_subparsers(
        dest="list_type", required=True, help="what to list"
    )

    # Listing -> Tracks
    list_tracks_parser = list_subparsers.add_parser(
        "tracks",
        help="list all tracks in the library",
        description="""
        List all your tracks, just your favorite tracks,
        or albums in your library.
        """,
    )
    list_tracks_parser.add_argument(
        "-f", "--favorited", action="store_true", help="list only your favorite tracks"
    )
    list_tracks_parser.set_defaults(
        func=lambda args: cmd_list_tracks(db, only_favorited=args.favorited)
    )

    # Listing -> Albums
    list_subparsers.add_parser(
        "albums",
        help="list all albums in the library",
        description="List all albums in the library",
    ).set_defaults(func=lambda _: cmd_list_albums(db))

    # Listing -> Artists
    artists_parser = list_subparsers.add_parser(
        "artists",
        help="list all artists in the library",
        description="List all artists in the library",
    )
    artists_parser.add_argument(
        "-a", "--albums", action="store_true", help="list only album artists"
    )
    artists_parser.set_defaults(func=lambda args: cmd_list_artists(db, args.albums))

    # Listing -> Playlists
    list_subparsers.add_parser(
        "playlists",
        help="list all playlists in the library",
        description="List all playlists in the library",
    ).set_defaults(func=lambda _: cmd_list_playlists(db))

    # Playlists
    playlist_parser = subparsers.add_parser(
        "playlist",
        help="crud operations for playlists",
        description="Crud operations for playlists",
    )

    playlist_subparsers = playlist_parser.add_subparsers(
        dest="action", required=True, help="operation"
    )

    # Playlists -> Create
    create_playlist_parser = playlist_subparsers.add_parser(
        "create",
        help="create a new playlist",
        description="""
        Create a new playlist
        """,
    )
    create_playlist_parser.add_argument("title", help="title of playlist")
    create_playlist_parser.add_argument(
        "-d", "--description", help="description of the playlist"
    )
    create_playlist_parser.set_defaults(
        func=lambda args: cmd_playlist_create(db, args.title, args.description)
    )

    # Scan
    subparsers.add_parser(
        "scan",
        help="imports all files in Source folder",
        description="Imports all the files in the Source folder.",
    ).set_defaults(func=lambda _: cmd_scan(db))

    # Version
    subparsers.add_parser(
        "version", help="get current version", description="Get the current verson."
    ).set_defaults(func=lambda _: cmd_version(db))

    # Reset
    reset_parser = subparsers.add_parser(
        "reset",
        help="reset the internal database (keeps songs)",
        description="Reset's the internal database, keeps songs.",
    )
    reset_parser.add_argument(
        "-y",
        "--skipconfirmation",
        help="skip confirmation and reset",
        action="store_true",
    )
    reset_parser.set_defaults(
        func=lambda args: cmd_reset(db, skip_confirmation=args.skipconfirmation)
    )

    # Favorite
    favorite_parser = subparsers.add_parser(
        "favorite",
        help="favorite or unfavorite tack(s)",
        description="Favorite or unfavorite a track. Uses same prefixes as search.",
    )
    favorite_parser.add_argument(
        "term",
        help="the name of the track you wish to favorite (use id: to select by id)",
    )
    favorite_parser.set_defaults(func=lambda args: cmd_favorite(db, args.term))

    # Importing
    import_parser = subparsers.add_parser(
        "import",
        help="import individual files",
        description="""
            Import file(s) to Mu. Directories or individual files can be selected.
        """,
    )
    import_parser.add_argument("filepath", help="path to the file being imported")
    import_parser.set_defaults(func=lambda args: cmd_import(db, args.filepath))

    # Searching
    search_parser = subparsers.add_parser(
        "search",
        help="search the library",
        description="""Search your library.
            You can search with prefixes aswell.
            By typing id:, album:, title:, artist:, or albumartist: in front,
            you can narrow your search.
        """,
    )
    search_parser.add_argument(
        "term",
        help="""
            the name of the item(s) you are searching for.
            supports prefixes (id:,album:,etc)
        """,
    )
    search_parser.set_defaults(func=lambda args: cmd_search(db, args.term))

    return parser


def main():
    try:
        db = Database()
        args = build_parser(db).parse_args()
        args.func(args)
    except SchemaError as e:
        Interface.print_outdated_version(e.expected, e.found)


if __name__ == "__main__":
    main()
