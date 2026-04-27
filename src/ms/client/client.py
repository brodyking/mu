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

        # Table
        self.table = QTableWidget(len(tracks),4) # Row and Col setup
        self.table.setHorizontalHeaderLabels(["Title", "Artist", "Album","File path"]) # Headers
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Hide col number
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # Select whole row when clicked
        self.table.verticalHeader().hide() # Hide vertical headers

        # Add songs to table
        for row in range(len(tracks)):
            for col in range(4):
                if col == 0:
                    self.table.setItem(row,col,QTableWidgetItem(tracks[row].title))
                elif col == 1:
                    self.table.setItem(row,col,QTableWidgetItem(tracks[row].artist))
                elif col == 2:
                    self.table.setItem(row,col,QTableWidgetItem(tracks[row].album))
                else:
                    self.table.setItem(row,col,QTableWidgetItem(tracks[row].filepath))

        # Plays song when double clicked
        def on_cell_double_clicked():
            current_row = self.table.currentRow()

            filepath_col = self.table.item(current_row,3)
            if filepath_col is not None:
                filepath = filepath_col.text()
                self.player.setSource(QUrl.fromLocalFile(filepath))
                # 3. Play
                self.player.play()

        # Adds listener
        self.table.cellDoubleClicked.connect(on_cell_double_clicked)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        


def start_client():
    app = QApplication()
    app.setWindowIcon(QIcon(":/assets/logo1024.png"))
    app.setApplicationName("ms")
    app.setApplicationDisplayName("ms")
    window = Client()
    window.show()
    sys.exit(app.exec())
