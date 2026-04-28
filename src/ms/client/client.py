import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QAbstractItemView
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon

from ms.database import Database
from ms.util import Util

import ms.client.resources_rc

class Client(QMainWindow):
    def __init__(self):
        super().__init__()

        Util.print("Starting client")

        # Window 
        self.setWindowTitle("ms")
        self.resize(600, 400)

        # Hardware output
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.7)

        # Set up the player
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        # Get all tracks
        db = Database()
        tracks = db.list_library(console_out=False)
        self.tracks_table = self.gen_tracks_view(tracks)
        self.tracks_table.cellDoubleClicked.connect(lambda: self.cell_clicked(self.tracks_table))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tracks_table)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)



    def gen_tracks_view(self,tracks: list) -> QTableWidget:
        # Table
        table = QTableWidget(len(tracks),4) # Row and Col setup
        table.setHorizontalHeaderLabels(["Title", "Artist", "Album","File path"]) # Headers
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Hide col number
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # Select whole row when clicked
        table.verticalHeader().hide() # Hide vertical headers

        # Add songs to table
        for row in range(len(tracks)):
            for col in range(4):
                if col == 0:
                    table.setItem(row,col,QTableWidgetItem(tracks[row].title))
                elif col == 1:
                    table.setItem(row,col,QTableWidgetItem(tracks[row].artist))
                elif col == 2:
                    table.setItem(row,col,QTableWidgetItem(tracks[row].album))
                else:
                    table.setItem(row,col,QTableWidgetItem(tracks[row].filepath))

        return table

    # Plays song when double clicked
    def cell_clicked(self,table):
        current_row = table.currentRow()

        filepath_col = table.item(current_row,3)
        if filepath_col is not None:
            filepath = filepath_col.text()
            self.player.setSource(QUrl.fromLocalFile(filepath))
            # 3. Play
            self.player.play()

def start_client():
    app = QApplication()
    app.setWindowIcon(QIcon(":/assets/logo1024.png"))
    app.setApplicationName("ms")
    app.setApplicationDisplayName("ms")
    window = Client()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    start_client()
