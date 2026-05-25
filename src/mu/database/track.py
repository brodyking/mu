class Track:

    def __init__(self,response):
        """
            Creates a track object from SQLite response
            TODO: Make this not selected from a tuple
        """
        self.id=response[0]
        self.favorite=bool(response[1])
        self.title=response[2]
        self.artist=response[3]
        self.album=response[4]
        self.plays=response[5]
        self.time=response[6]
        self.dateadded=response[7]
        self.tracknumber=response[8]
        self.albumartist=response[9]
        self.discnumber=response[10]
        self.genre=response[11]
        self.date=response[12]
        self.filepath=response[13]
        self.filename=response[14]
        self.albumart=response[15]

    def get_time_ms(self) -> int:
        minutes, seconds = map(int, self.time.split(':'))
        return (minutes * 60 * 1000) + (seconds * 1000)

    def get_dict(self) -> dict:
        return {
            "id": self.id,
            "favorite": self.favorite,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "plays": self.plays,
            "time": self.time,
            "dateadded": self.dateadded,
            "tracknumber": self.tracknumber,
            "albumartist": self.albumartist,
            "discnumber": self.discnumber,
            "genre": self.genre,
            "date": self.date,
            "filepath": self.filepath,
            "filename": self.filename,
            "albumart": self.albumart
        }
