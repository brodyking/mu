import json
from ms.database import Database
from pathlib import Path
import argparse
from ms.util import Util
from ms.client.client import Client, start_client

VERSION = "0.0.2"

def main():
    db = Database()

    parser = argparse.ArgumentParser(prog="Based Music Server",description="This program manages your library of music",epilog="Created and maintained by Brody King. You can find this project at https://github.com/brodyking/ms")

    subparsers = parser.add_subparsers(dest="action", help="options for library", required=True)

    # Scan
    subparsers.add_parser("scan", help="imports all files in Source folder", description="Imports all the files in the Source folder.")

    # Client
    subparsers.add_parser("client", help="start the gui client", description="Start the GUI client.")

    # Version
    subparsers.add_parser("version", help="get current version", description="Get the current verson.")

    # Reset
    reset_parser = subparsers.add_parser("reset", help="reset the internal database (keeps songs)",description="Reset's the internal database, keeps songs.")
    reset_parser.add_argument("-y","--skipconfirmation",help="skip confirmation and reset",action="store_true")
    
    # List
    list_parser = subparsers.add_parser("list", help="list all files in the library",description="List all your files, or just your favorites in your library.")
    list_parser.add_argument("-j","--json",action='store_true',help="output in json")
    list_parser.add_argument("-f","--favorited",action='store_true',help="list only your favorites")

    # Favorite
    favorite_parser = subparsers.add_parser("favorite", help="favorite or unfavorite a track",description="Favorite or unfavorite a track.")
    favorite_parser.add_argument("trackid",help="the name of the track you wish to favorite (use id: to select by id)")

    # Importing
    import_parser = subparsers.add_parser("import", help="import individual files",description="Import file(s) to ms. Directories or individual files can be selected.")
    import_parser.add_argument("filepath",help="path to the file being imported")

    # Searching
    search_parser = subparsers.add_parser("search", help="search the library",description="Search your library. You can search with prefixes aswell. By typing id:, album:, title:, artist:, or albumartist: in front, you can narrow your search.")
    search_parser.add_argument("term",help="the name of the item(s) you are searching for. supports prefixes (id:,album:,etc.)")
    search_parser.add_argument("-j","--json",action='store_true',help="output in json")
    search_parser.add_argument("-p","--path",action='store_true',help="return the filepath(s)")

    # Playing
    play_parser = subparsers.add_parser("play", help="play track(s) with mpv",description="Open track(s) with mpv. Finds tracks the same way as search.")
    play_parser.add_argument("term",help="the name of the item(s) you are searching for. supports prefixes (id:,album:,etc.)")

    args = parser.parse_args()

    actions = {
        "scan": lambda: db.scan_source_folder(),
        "client": lambda: start_client(),
        "version": lambda: Util.print(f"Current version: {VERSION}"),
        "reset": lambda: db.reset_db(
            skip_confirmation=args.skipconfirmation
        ),
        "favorite": lambda: db.favorite_track(
            args.trackid,
        ),
        "list": lambda: db.list_library(
            export_json=args.json,
            only_favorited=args.favorited,
        ),
        "import": lambda: db.import_media(
            args.filepath,
        ),
        "search": lambda: db.search(
            args.term,
            export_json=args.json,
            export_path=args.path,
        ),
        "play": lambda: Util.mpv(db.search(args.term,export_path=True))
    }

    if args.action in actions:
        actions[args.action]()

if __name__ == "__main__":
    main()
