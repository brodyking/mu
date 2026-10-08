"""
 _   _
| | | | muweb
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

from typing import Annotated, Optional

import typer
import uvicorn

from muweb.server import app, configure_auth

parser = typer.Typer(
    name="muweb",
    no_args_is_help=False,
    help="mu web api and client",
    epilog="created and maintained by brody king at https://github.com/brodyking/mu",
)


@parser.command()
def start(
    password: Annotated[
        Optional[str],
        typer.Option(
            "--password",
            "-p",
            envvar="MUWEB_PASSWORD",
            help="Require this password to access muweb. Omit to disable auth.",
        ),
    ] = None,
    ask_password: Annotated[
        bool,
        typer.Option(
            "--ask-password",
            help="Prompt for the password instead of passing it on the command line.",
        ),
    ] = False,
):
    """Start the muweb server."""
    if ask_password:
        password = typer.prompt("Password", hide_input=True, confirmation_prompt=True)

    configure_auth(password)
    uvicorn.run(app, host="0.0.0.0", port=8000)


def main():
    try:
        parser()
    except ValueError as e:
        print(str(e))


if __name__ == "__main__":
    main()
