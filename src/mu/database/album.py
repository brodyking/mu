class Album:
    def __init__(self, response:dict):
        """
        Creates a album object from SQLite response
        """
        self.title = response["album"]
        self.albumartist = response["albumartist"]

    def get_dict(self) -> dict:
        return {
            "title": self.title,
            "albumartist": self.albumartist,
        }
