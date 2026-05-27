import argparse
from importlib.metadata import version

from mu.client.client import start_client
from mu.database.database import Database
from mu.util import Interface, Mpv

VERSION = version("mu")


def main():
    db = Database()

    parser = argparse.ArgumentParser(
        prog="μ",
        description="your personal music library",
        epilog="""
            Created and maintained by Brody King.
            You can find this project at https://github.com/brodyking/mu
        """,
    )

    subparsers = parser.add_subparsers(
        dest="action", help="options for library", required=True
    )

    # Scan
    subparsers.add_parser(
        "scan",
        help="imports all files in Source folder",
        description="Imports all the files in the Source folder.",
    )

    # Client
    subparsers.add_parser(
        "client", help="start the tui client", description="Start the TUI client."
    )

    # Version
    subparsers.add_parser(
        "version", help="get current version", description="Get the current verson."
    )

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

    # Tracks
    tracks_parser = subparsers.add_parser(
        "tracks",
        help="list all tracks in the library",
        description="""
        List all your tracks, just your favorite tracks,
        or albums in your library.
        """
    )
    tracks_parser.add_argument(
        "-f", "--favorited", action="store_true", help="list only your favorite tracks"
    )

    # Albums
    subparsers.add_parser(
        "albums",
        help="list all albums in the library",
        description="List all albums in the library"
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

    # Importing
    import_parser = subparsers.add_parser(
        "import",
        help="import individual files",
        description="""
            Import file(s) to Mu. Directories or individual files can be selected.
        """,
    )
    import_parser.add_argument("filepath", help="path to the file being imported")

    # Searching
    search_parser = subparsers.add_parser(
        "search",
        help="search the library",
        description="""Search your library.
            You can search with prefixes aswell.
            By typing id:, album:, title:, artist:, or albumartist: in front,
            you can narrow your search.
        """
    )
    search_parser.add_argument(
        "term",
        help="""
            the name of the item(s) you are searching for.
            supports prefixes (id:,album:,etc)
        """,
    )

    # Playing
    play_parser = subparsers.add_parser(
        "play",
        help="play track(s) with mpv",
        description="Open track(s) with mpv. Finds tracks the same way as search.",
    )
    play_parser.add_argument(
        "term",
        help="""
            the name of the item(s) you are searching for.
            supports prefixes (id:,album:,etc.)
        """,
    )

    args = parser.parse_args()

    actions = {
        "scan": lambda: db.scan_source_folder(),
        "client": lambda: start_client(),
        "version": lambda: Interface.print_version(VERSION,db.DATABASE_VERSION),
        "reset": lambda: db.reset_db(skip_confirmation=args.skipconfirmation),
        "favorite": lambda: db.favorite(
            str(args.term),
        ),
        "tracks": lambda: db.list_library_tracks(
            only_favorited=args.favorited,
        ),
        "albums": lambda: db.list_library_albums(),
        "import": lambda: db.import_media(
            str(args.filepath),
        ),
        "search": lambda: db.search(
            str(args.term),
        ),
        "play": lambda: Mpv.play(db.search(str(args.term))),
    }

    if args.action in actions:
        actions[args.action]()


if __name__ == "__main__":
    main()
