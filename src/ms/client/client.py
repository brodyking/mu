import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QWidget, QAbstractItemView, QHBoxLayout, QPushButton
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon

# Assuming these modules exist in your environment
from ms.database import Database
from ms.util import Util

import ms.client.resources_rc

class Client(QMainWindow):
    def __init__(self):
        super().__init__()

        Util.print("Starting client")

        # --- Window ---
        self.setWindowTitle("ms")
        self.resize(600, 400)

        # --- Audio Setup ---
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.7)

        # --- Set up the player ---
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        
        # --- Initialize control state ---
        self.is_playing = False

        # --- Database Setup ---
        db = Database()
        tracks = db.list_library(console_out=False)
        
        # --- UI Setup ---
        
        # 1. Table View
        self.tracks_table = self.gen_tracks_view(tracks)
        # Connect table click handler (double click for auto-play)
        self.tracks_table.cellDoubleClicked.connect(lambda: self.cell_clicked(self.tracks_table))

        # 2. Control Buttons Container (Horizontal Layout)
        control_layout = QHBoxLayout()
        
        self.toggle_playback_button = QPushButton("▶ Play")
        self.toggle_playback_button.clicked.connect(lambda: self.toggle_playback())

        control_layout.addWidget(self.toggle_playback_button)
        control_layout.addStretch(1) # Pushes buttons to the left

        # 3. Main Layout (Vertical Box)
        layout = QVBoxLayout()
        layout.addLayout(control_layout) # Add the control layout below the table
        layout.addWidget(self.tracks_table)
        
        # Container widget to hold the layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


    def gen_tracks_view(self,tracks: list) -> QTableWidget:
        # Table (unchanged)
        table = QTableWidget(len(tracks),4) 
        table.setHorizontalHeaderLabels(["Title", "Artist", "Album","File path"])
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) 
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) 
        table.verticalHeader().hide()

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

    # Plays song when double clicked (Kept for convenience)
    def cell_clicked(self,table):
        current_row = table.currentRow()

        filepath_col = table.item(current_row,3)
        if filepath_col is not None:
            filepath = filepath_col.text()
            self.load_track_source(filepath)
            # Play when double-clicked
            self.play_music()

    def load_track_source(self, filepath: str):
        """Loads the file path into the player source."""
        self.player.setSource(QUrl.fromLocalFile(filepath))

    def toggle_playback(self):
        if self.is_playing:
            self.pause_music();
        else:
            self.play_music();
        
    def play_music(self):
        """Called when the Play button is pressed."""
        if self.player.duration() == 0 and not self.player.error():
            # if nothing is loaded, prompt the user or do nothing
            Util.print("No track loaded. please select a song first.",ok=False)
            return
            
        if not self.player.isPlaying():
            self.player.play()
            self.is_playing = True
            self.toggle_playback_button.setText("⏸ Pause")

    def pause_music(self):
        """Called when the Pause button is pressed."""
        self.player.pause()
        self.is_playing = False
        self.toggle_playback_button.setText("▶ Play")


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

