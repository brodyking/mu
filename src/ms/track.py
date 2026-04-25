class Track:

    def __init__(self,response):
        """
            Creates a track object from SQLite response
        """
        self.id=response[0]
        self.favorite=bool(response[1])
        self.title=response[2]
        self.tracknumber=response[3]
        self.artist=response[4]
        self.albumartist=response[5]
        self.album=response[6]
        self.discnumber=response[7]
        self.genre=response[8]
        self.date=response[9]
        self.filepath=response[10]
        self.filename=response[11]
        self.albumart=response[12]

    def get(self) -> dict:
        return {
            "id": self.id,
            "favorite": self.favorite,
            "title": self.title,
            "tracknumer": self.tracknumber,
            "artist": self.artist,
            "albumartist": self.albumartist,
            "album": self.album,
            "discnumber": self.discnumber,
            "genre": self.genre,
            "date": self.date,
            "filepath": self.filepath,
            "filename": self.filename,
            "albumart": self.albumart
        }
