import json
from ms.database import Database
from pathlib import Path
import argparse

def main():
    db = Database()

    parser = argparse.ArgumentParser(prog="Based Music Server",description="This program manages your library of music",epilog="Created and maintained by Brody King. You can find this project at https://github.com/brodyking/ms")

    subparsers = parser.add_subparsers(dest="action", help="options for library", required=True)

    # Scan
    subparsers.add_parser("scan", help="imports all files in Source folder")

    # Reset
    reset_parser = subparsers.add_parser("reset", help="reset the internal database (keeps songs)")
    reset_parser.add_argument("-y","--skipconfirmation",help="skip confirmation and reset",action="store_true")
    
    # List
    list_parser = subparsers.add_parser("list", help="list all files in the library",description="List all your files, or just your favorites in your library.")
    list_parser.add_argument("-j","--json",action='store_true',help="output in json")
    list_parser.add_argument("-f","--favorited",action='store_true',help="list only your favorites")

    # Favorite
    favorite_parser = subparsers.add_parser("favorite", help="favorite or unfavorite a track")
    favorite_parser.add_argument("trackid",help="the id of the track you wish to favorite")

    # Importing
    import_parser = subparsers.add_parser("import", help="import individual files")
    import_parser.add_argument("filepath",help="path to the file being imported")

    # Searching
    search_parser = subparsers.add_parser("search", help="search the library")
    search_parser.add_argument("term",help="the name of the item(s) you are searching for")
    search_parser.add_argument("-j","--json",action='store_true',help="output in json")

    args = parser.parse_args()

    actions = {
        "scan": lambda: db.scan_source_folder(),
        "reset": lambda: db.reset_db(skip_confirmation=args.skipconfirmation),
        "favorite": lambda: db.favorite_track(args.trackid),
        "list": lambda: db.list_library(export_json=args.json,favorited=args.favorited),
        "import": lambda: db.import_media(args.filepath),
        "search": lambda: db.search(args.term,export_json=args.json)
    }

    if args.action in actions:
        actions[args.action]()
