import argparse
from muc.client.client import Client
from textual_serve.server import Server

def start_client():
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

    parser.add_argument("action", nargs="?", choices=["web"], default=None)

    args = parser.parse_args()

    actions = {
        "web": start_client_web 
    }


    if args.action is None:
        client = Client()
        client.run()

    if args.action in actions:
        actions[args.action]()


if __name__ == "__main__":
    main()
