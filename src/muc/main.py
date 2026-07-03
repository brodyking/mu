"""
 _   _
| | | | muc client
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import argparse

from muc.client.client import Client


def start_client_tui():
    client = Client()
    client.run()


def main():

    parser = argparse.ArgumentParser(
        prog="mμc",
        description="a tui music player for mu",
        epilog="""
            Created and maintained by Brody King.
            You can find this project at https://github.com/brodyking/mu
        """,
    )

    parser.add_argument("action", nargs="?", choices=["tui"], default="tui")

    args = parser.parse_args()

    actions = {"tui": start_client_tui}

    if args.action in actions:
        actions[args.action]()


if __name__ == "__main__":
    main()
