class Album:
    def __init__(self, response):
        """
        Creates a album object from SQLite response
        TODO: Make this not selected from a tuple
        """
        self.title = response[0]
        self.albumartist = response[1]

    def get_dict(self) -> dict:
        return {
            "title": self.title,
            "albumartist": self.albumartist,
        }
