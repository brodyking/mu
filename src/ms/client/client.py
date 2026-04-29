import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QWidget, QAbstractItemView, QHBoxLayout, QPushButton, QLineEdit
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
        self.setWindowTitle("ms - based music server")
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
        self.db = Database()
        self.tracks = self.db.list_library(console_out=False)
        
        # --- UI Setup ---

        # Tracks Table
        tracks_layout =QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Title, Artist, or Album...")
        self.search_input.textChanged.connect(self.filter_table) 
        
        self.tracks_table = self.gen_tracks_table()
        self.tracks_table.cellDoubleClicked.connect(lambda: self.cell_clicked(self.tracks_table))

        self.populate_table(self.tracks)

        tracks_layout.addWidget(self.search_input)
        tracks_layout.addWidget(self.tracks_table)
        
        # Controls
        control_layout = QHBoxLayout()
        
        self.toggle_playback_button = QPushButton("▶ Play")
        self.toggle_playback_button.clicked.connect(lambda: self.toggle_playback())

        control_layout.addWidget(self.toggle_playback_button)
        control_layout.addStretch(1) # Pushes buttons to the left
        
        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(control_layout) # Add the control layout below the table
        layout.addLayout(tracks_layout) # Add the control layout below the table
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def filter_table(self, query: str):
        """
        Filters the QTableWidget based on the input query.
        The table is cleared and repopulated with matching tracks.
        """
        query = query.lower().strip()
        
        # If the query is empty, display all tracks
        if not query:
            self.tracks_table.setRowCount(len(self.tracks))
            self.tracks_table.setColumnCount(4)
            self.populate_table(self.tracks)
            return

        # Find all matching tracks
        filtered_tracks = []
        for track in self.tracks:
            # Check if the query matches Title, Artist, or Album
            if (query in str(track.title).lower() or 
                query in track.artist.lower() or 
                query in track.album.lower()):
                filtered_tracks.append(track)
        
        # Repopulate the table with the filtered results
        self.tracks_table.setRowCount(len(filtered_tracks))
        self.tracks_table.setColumnCount(4)
        self.populate_table(filtered_tracks)
        
        Util.print(f"Search results found: {len(filtered_tracks)} tracks.")


    def populate_table(self, tracks: list):
        """Helper function to populate the table with a given list of tracks."""
        # Clear existing content first
        self.tracks_table.setSortingEnabled(False)
        self.tracks_table.setRowCount(len(tracks))
        self.tracks_table.setColumnCount(4)

        # Repopulate using the existing logic from gen_tracks_view
        for row_index, track in enumerate(tracks):
            # Column 0: Title
            title_item = QTableWidgetItem(f"{'❤ ' if track.favorite else ''}{track.title}")
            
            self.tracks_table.setItem(row_index, 0, title_item)
            
            # Column 1: Artist
            self.tracks_table.setItem(row_index, 1, QTableWidgetItem(track.artist))
            
            # Column 2: Album
            self.tracks_table.setItem(row_index, 2, QTableWidgetItem(track.album))
            
            # Column 3: File path
            self.tracks_table.setItem(row_index, 3, QTableWidgetItem(track.filepath))

        self.tracks_table.setSortingEnabled(True)


    def gen_tracks_table(self) -> QTableWidget:
        # Table
        table = QTableWidget(len(self.tracks),4) 
                    
        table.setHorizontalHeaderLabels(["Title", "Artist", "Album","File path"])
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) 
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) 
        table.verticalHeader().hide()

        table.setSortingEnabled(True)
        table.sortByColumn(1,Qt.SortOrder.AscendingOrder)
        table.setColumnWidth(0,200)
        table.setColumnWidth(1,150)
        table.setColumnWidth(2,150)
        table.setColumnWidth(3,150)

        return table

    # Plays song when double clicked (Kept for convenience)
    def cell_clicked(self,table):
        current_row = table.currentRow()

        filepath_col = table.item(current_row,3)
        if filepath_col is not None:
            filepath = filepath_col.text()
            self.load_track_source(filepath)
            # Play when double-clicked
            self.start_playback()

    def load_track_source(self, filepath: str):
        """Loads the file path into the player source."""
        self.player.setSource(QUrl.fromLocalFile(filepath))
        Util.print(f"Loaded {filepath}")

    def toggle_playback(self):
        if self.is_playing:
            self.stop_playback();
        else:
            self.start_playback();
        
    def start_playback(self):
        if self.player.duration() == 0 and not self.player.error():
            # if nothing is loaded, prompt the user or do nothing
            Util.print("No track loaded. please select a song first.",ok=False)
            return
            
        if not self.player.isPlaying():
            self.player.play()
            self.is_playing = True
            self.toggle_playback_button.setText("⏸ Pause")
            Util.print("Playback started")

    def stop_playback(self):
        self.player.pause()
        self.is_playing = False
        self.toggle_playback_button.setText("▶ Play")
        Util.print("Playback paused")

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

