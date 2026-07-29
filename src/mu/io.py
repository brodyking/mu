"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import typer

from mu.types import Album, Artist, Playlist, Track


class Color:
    # Standard Colors (Lower Intensity)
    @staticmethod
    def red(s):
        return f"\033[31m{s}\033[00m"

    @staticmethod
    def green(s):
        return f"\033[32m{s}\033[00m"

    @staticmethod
    def yellow(s):
        return f"\033[33m{s}\033[00m"

    @staticmethod
    def blue(s):
        return f"\033[34m{s}\033[00m"

    @staticmethod
    def purple(s):
        return f"\033[35m{s}\033[00m"

    @staticmethod
    def cyan(s):
        return f"\033[36m{s}\033[00m"

    # Bright/Light Colors (90-97 range)
    @staticmethod
    def light_gray(s):
        return f"\033[37m{s}\033[00m"

    @staticmethod
    def black(s):
        return f"\033[90m{s}\033[00m"  # Bright Black / Dark Gray

    @staticmethod
    def light_red(s):
        return f"\033[91m{s}\033[00m"

    @staticmethod
    def light_green(s):
        return f"\033[92m{s}\033[00m"

    @staticmethod
    def light_yellow(s):
        return f"\033[93m{s}\033[00m"

    @staticmethod
    def light_blue(s):
        return f"\033[94m{s}\033[00m"

    @staticmethod
    def pink(s):
        return f"\033[95m{s}\033[00m"

    @staticmethod
    def light_cyan(s):
        return f"\033[96m{s}\033[00m"

    @staticmethod
    def white(s):
        return f"\033[97m{s}\033[00m"


def mu_print(
    content: str,
    ok: bool = True,
    count: tuple[int, int] | None = None,
    url: str | None = None,
    track: Track | None = None,
    album: Album | None = None,
    playlist: Playlist | None = None,
    artist: Artist | None = None,
):
    """
    Prints to the terminal
    - ok (bool): Shows checkmark or X. Defaults to True.
    - count (list): [current, total]. Defaults to empty.
    - url (str): Prints out the URL in blue
    - track (Track): Prints track metadata
    - album (Album): Prints album metadata
    - playlist (Playlist): Prints playlist metadata
    - artist (str): Prints the artist names
    """

    prefix: str = Color.green("[✓] ") if ok else Color.red("[✘] ")
    counter: str = (
        f"[{str(count[0]).rjust(len(str(count[1])), '0')}/{count[1]}] "
        if count and len(count) == 2
        else ""
    )
    favorited: str = (
        Color.red("❤ ")
        if track is not None and track.favorite
        else Color.light_gray("♥ ")
    )
    link: str = f"{Color.blue(url)} " if url is not None else ""

    if track is not None:
        searchresult = (
            f"{Color.light_gray('#' + str(track.id or '').rjust(4, '0'))} "
            f"{favorited} "
            f"{Color.red('󰈣 ' + (track.title or '')[:25])} "
            f"{Color.blue('󰠃 ' + (track.artist or '')[:20])} "
            f"{Color.pink('󱍙 ' + (track.album) or '')[:25]} "
        )
    elif album is not None:
        searchresult = (
            f"{Color.pink('󱍙 ' + (album.title or '')[:25])} "
            f"{Color.blue('󰠃 ' + (album.albumartist or '')[:25])} "
            f"{Color.red('󰈣 ' + str(len(album.tracks)))}"
        )
    elif artist is not None:
        searchresult = (
            f"{Color.blue('󰠃 ' + (artist.name or '')[:25])} "
            f"{Color.red('󰈣 ' + str(len(artist.tracks)))}"
        )
    elif playlist is not None:
        searchresult = (
            f"{Color.light_gray('#' + str(playlist.id or '').rjust(4, '0'))} "
            f"{Color.green('󱝟 ' + (playlist.title or '')[:25])} "
            f"{(playlist.description or '')[:25]} "
            f"{Color.red('󰈣 ' + str(len(playlist.tracks)))}"
        )
    else:
        searchresult = ""

    typer.echo(f"{prefix}{content}{link}{counter}{searchresult}")


def mu_print_playlists(playlists: dict[int, Playlist]) -> None:
    total = len(playlists)
    if total == 0:
        mu_print("No results found", ok=False)
        return
    for i, pid in enumerate(playlists):
        mu_print("", playlist=playlists[pid], count=(i + 1, total))


def mu_print_tracks(tracks: dict[int, Track]) -> None:
    total: int = len(tracks)
    if total == 0:
        mu_print("No results found", ok=False)
        return
    for i, track_id in enumerate(tracks):
        mu_print("", track=tracks[track_id], count=(i + 1, total))


def mu_print_playlist_tracks(playlists: dict[int, Playlist]) -> None:
    tracks = []
    for pid in playlists:
        playlist = playlists[pid]
        tracks.extend(playlist.tracks)
    total = len(tracks)
    if total == 0:
        mu_print("No results found", ok=False)
        return
    for i, track in enumerate(tracks):
        mu_print("", track=track, count=(i + 1, total))


def mu_print_playlist_deletion(response: dict[int, bool]) -> None:
    for pid in response:
        if response[pid]:
            mu_print(f"Playlist (#{pid}) has been deleted")
        else:
            mu_print(f"Playlist (#{pid}) could not be deleted", ok=False)


def mu_print_albums(albums: dict[tuple, Album]) -> None:
    total = len(albums)
    if total == 0:
        mu_print("No results found", ok=False)
        return
    for i, album_name in enumerate(albums):
        mu_print("", album=albums[album_name], count=(i + 1, total))


def mu_print_artists(artists: dict[str, Artist]) -> None:
    total = len(artists)
    if total == 0:
        mu_print("No results found", ok=False)
        return
    for i, artist_name in enumerate(artists):
        mu_print("", artist=artists[artist_name], count=(i + 1, total))


def mu_print_version(client_version: str, database_schema: int) -> None:

    link_text = Color.blue("https://github.com/brodyking/mu")

    client_version_text = Color.yellow("mu + muc: ") + Color.green(f"v{client_version}")
    database_schema_text = Color.yellow("db schema: ") + Color.green(
        f"v{database_schema}"
    )

    logo = (
        f" _   _ \n"
        f"| | | |\t{link_text}\n"
        f"| |_| |\t{client_version_text}\n"
        f"| ._,_|\t{database_schema_text}\n"
        f"|_|\n"
    )

    lines = logo.split("\n")
    for line in lines:
        typer.echo(Color.red(line))


def mu_input_bool(content: str) -> bool:
    """Prompts a y/N question"""
    while True:
        response = typer.confirm(f"{Color.yellow('[]')} {content}")
        if response == "y" or response == 1 or response == "yes":
            return True
        elif response == "n" or response == 0 or response == "no":
            return False


def mu_input_str(content: str) -> bool:
    """Prompts with an str as the input"""
    while True:
        response = typer.prompt(f"{Color.yellow('[]')} {content}")
        return response
