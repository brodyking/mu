import subprocess


class Mpv:
    @staticmethod
    def play(tracks: list) -> None:
        """
        Plays a list of files in mpv
        """
        track_paths = []
        for track in tracks:
            track_paths.append(track.filepath)
        Interface.print(f"Starting mpv playback for {track_paths}")
        subprocess.run(["mpv"] + track_paths)


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


class Interface:
    @staticmethod
    def print(content: str, **kwargs):
        """
        Prints to the terminal
        - ok (bool): Shows checkmark or X. Defaults to True.
        - count (list): [current, total]. Defaults to empty.
        - track (list): The data pulled from the SQLite DB. Defaults to empty.
        """

        ok = kwargs.get("ok", True)  # Status. Shows check or x.
        count = kwargs.get(
            "count", []
        )  # Used to display progress in anticipation of another print.
        track = kwargs.get("track", None)
        album = kwargs.get("album", None)

        prefix = Color.green("[✓] ") if ok else Color.red("[✘] ")
        counter = (
            f"[{str(count[0]).rjust(len(str(count[1])), '0')}/{count[1]}] "
            if len(count) == 2
            else ""
        )
        favorited = (
            Color.red("❤ ")
            if track is not None and track.favorite
            else Color.light_gray("♥ ")
        )

        if track is not None:
            searchresult = (
                f"{Color.light_gray('#' + str(track.id).rjust(4, '0'))} "
                f"{favorited}{Color.red(Interface.fmt(f'{track.title}', 25))} | "
                f"{Interface.fmt(track.artist, 15)} | "
                f"{Interface.fmt(track.album, 15)} | "
                f"{Color.blue(track.filepath)}"
            )
        elif album is not None:
            searchresult = (
                f"{Color.red(Interface.fmt(album.title, 25))} | "
                f"{Interface.fmt(album.albumartist, 15)}"
            )
        else:
            searchresult = ""

        print(f"{prefix}{counter}{searchresult}{content}")

    @staticmethod
    def prompt_bool(content: str) -> bool:
        """Asks the user a question, returns the users chioce."""
        print(Color.yellow("[]"), end="")
        while True:
            response = input(f" {content} (y/n) ")
            if response == "y" or response == 1 or response == "yes":
                return True
            elif response == "n" or response == 0 or response == "no":
                return False

    @staticmethod
    def fmt(text, width):
        """Add spaces to string or add ... if too large"""
        text = str(text or "")
        if len(text) > width:
            return text[: width - 2] + ".."
        return text.ljust(width)

    @staticmethod
    def print_version(client_version: str, database_version: int) -> None:
       
        link_text = Color.blue("https://github.com/brodyking/mu")

        client_version_text = (
            Color.yellow("mu + muc: ") + Color.green(f"v{client_version}")
        )
        database_version_text = (
            Color.yellow("db schema: ") + Color.green(f"v{database_version}")
        )

        logo = (
            f" _   _ \n"
            f"| | | |\t{link_text}\n"
            f"| |_| |\t{client_version_text}\n"
            f"| ._,_|\t{database_version_text}\n"
            f"|_|\n"
            )

        lines = logo.split("\n")
        for line in lines:
            print(Color.red(line))

    @staticmethod
    def print_outdated_version(database_version: int, library_version: int) -> None:
        Interface.print("Library version is outdated or invalid.", ok=False)
        print(f"Database version:\t{database_version}")
        print(f"Library version:\t{library_version}")
