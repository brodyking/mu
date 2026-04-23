import json
from smp_server.database import Database
from pathlib import Path
import argparse

def load_config():
    # Config path
    config_path = Path.home() / "Music" / "Scarlett" / "config.json"
    # Creates directory if it dosen't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    # Create file with defaults if it dosent exist
    if not config_path.exists():
        default_config = {"test key": "test value"}
        config = default_config or {}
        config_path.write_text(json.dumps(config, indent=2))
        return config
    with config_path.open() as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(prog="Scarlett Media Player Server",description="This program manages your library and can host a server for your SMP client.",epilog="Created and maintained by Brody King. You can find this project at https://github.com/brodyking/smp-server")

    subparsers = parser.add_subparsers(dest="action", help="options for library", required=True)

    scan_parser = subparsers.add_parser("scan", help="imports all files in Source folder")
    import_parser= subparsers.add_parser("import", help="import individual files")
    import_parser.add_argument("filepath",help="path to the file being imported")

    args = parser.parse_args()

    db = Database()

    if (args.action == "scan"):
        db.scan_source_folder()
    elif (args.action == "import"):
        db.import_media(args.filepath)
