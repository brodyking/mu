import argparse

from textual_serve.server import Server

from muc.client.client import Client


def start_client_tui():
    client = Client()
    client.run()

def start_client_web():
    server = Server("muc",title="muc")
    server.serve()

def main():

    parser = argparse.ArgumentParser(
        prog="mμc",
        description="a tui music player for mu",
        epilog="""
            Created and maintained by Brody King.
            You can find this project at https://github.com/brodyking/mu
        """,
    )

    parser.add_argument("action", nargs="?", choices=["web","tui"], default="tui")

    args = parser.parse_args()

    actions = {
        "web": start_client_web,
        "tui": start_client_tui
    }



    if args.action in actions:
        actions[args.action]()


if __name__ == "__main__":
    main()
