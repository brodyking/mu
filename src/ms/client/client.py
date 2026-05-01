import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QWidget, QAbstractItemView, QHBoxLayout, QPushButton, QLineEdit, QLabel
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QPixmap

from ms.database import Database
from ms.util import Util
from ms.track import Track

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

        # --- Set up the queue ---
        self.queue = []
        self.queue_index = -1

        # --- Set up current track ---
        self.currentTrack = None

        # --- Set up the player ---
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.player.mediaStatusChanged.connect(self.player_status_change)
        
        # --- Initialize control state ---
        self.is_playing = False

        # --- Database Setup ---
        self.db = Database()
        self.tracks = self.db.list_library(console_out=False)
        
        # --- UI Setup ---

        # Tracks Table
        tracks_layout =QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setStyleSheet("QLineEdit { padding: 5px; }")
        self.search_input.setPlaceholderText("Search by Title, Artist, or Album...")
        self.search_input.textChanged.connect(self.filter_table)
        
        self.tracks_table = self.gen_tracks_table()
        self.tracks_table.cellDoubleClicked.connect(lambda: self.cell_clicked(self.tracks_table))

        self.populate_table(self.tracks)

        tracks_layout.addWidget(self.search_input)
        tracks_layout.addWidget(self.tracks_table)

        # Album Art
        self.nowplaying_album_art = QLabel()
        self.nowplaying_album_art.setPixmap(QPixmap("").scaled(50,50,Qt.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))

        # Current track metadata
        nowplaying_layout = QVBoxLayout()

        self.nowplaying_track_label = QLabel(self,text="")
        self.nowplaying_artist_label = QLabel(self,text="")

        self.nowplaying_track_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.nowplaying_artist_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        nowplaying_layout.addWidget(self.nowplaying_track_label)
        nowplaying_layout.addWidget(self.nowplaying_artist_label)
        
        # Controls
        control_layout = QHBoxLayout()
        
        self.toggle_playback_button = QPushButton("▶ Play")
        self.toggle_playback_button.clicked.connect(lambda: self.toggle_playback())

        self.play_next_button = QPushButton("Next ▶▶")
        self.play_next_button.clicked.connect(lambda: self.play_next_in_queue())

        self.play_previous_button = QPushButton("◀◀ Previous")
        self.play_previous_button.clicked.connect(lambda: self.play_previous_in_queue())

        control_layout.addWidget(self.play_previous_button)
        control_layout.addWidget(self.toggle_playback_button)
        control_layout.addWidget(self.play_next_button)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Top bar
        top_bar_layout = QHBoxLayout()
        top_bar_layout.addWidget(self.nowplaying_album_art)
        top_bar_layout.addLayout(nowplaying_layout)
        top_bar_layout.addStretch()
        top_bar_layout.addLayout(control_layout)
        
        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(top_bar_layout) # Add the control layout below the table
        layout.addLayout(tracks_layout) # Add the control layout below the table
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def filter_table(self, query: str):
        """
        Filters the table based on the input query.
        The table is cleared and repopulated with matching tracks.
        """
        query = query.lower().strip()
        
        # If the query is empty, display all tracks
        if not query:
            self.tracks = self.db.list_library(console_out=False)
        else:
            self.tracks = self.db.search(query,console_out=False)
        
        # Repopulate the table with the filtered results
        self.tracks_table.setRowCount(len(self.tracks))
        self.tracks_table.setColumnCount(5)
        self.populate_table(self.tracks)
        
        Util.print(f"Search results found: {len(self.tracks)} tracks.")


    def populate_table(self, tracks: list):
        """Helper function to populate the table with a given list of tracks."""
        # Clear existing content first
        self.tracks_table.setSortingEnabled(False)
        self.tracks_table.setRowCount(len(tracks))
        self.tracks_table.setColumnCount(5)


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

            # Column 4: Id
            self.tracks_table.setItem(row_index, 4, QTableWidgetItem(str(track.id)))

        self.tracks_table.setSortingEnabled(True)


    def gen_tracks_table(self) -> QTableWidget:
        # Table
        table = QTableWidget(len(self.tracks),5) 
                    
        table.setHorizontalHeaderLabels(["Title", "Artist", "Album","File path","ID"])
        table.verticalHeader().hide()

        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) 
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) 

        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu)

        table.setSortingEnabled(True)
        table.sortByColumn(1,Qt.SortOrder.AscendingOrder)
        table.setColumnWidth(0,200)
        table.setColumnWidth(1,150)
        table.setColumnWidth(2,150)
        table.setColumnWidth(3,150)
        table.setColumnWidth(4,60)

        return table

    # Plays song when double clicked (Kept for convenience)
    def cell_clicked(self,table):
        current_row = table.currentRow()

        filepath_col = table.item(current_row,3)
        id_col = table.item(current_row,4)

        self.queue = self.tracks
        self.queue_index = current_row
        
        if filepath_col is not None and id_col is not None:
            filepath = filepath_col.text()
            id = id_col.text()
            self.load_track_source(filepath)
            self.currentTrack = self.db.search(f"id:{id}",console_out=False)[0]
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

    def update_nowplaying(self):
        Util.print(f"Now playing track: {self.currentTrack.title}")
        self.nowplaying_track_label.setText(Util.fmt(self.currentTrack.title,50))
        self.nowplaying_artist_label.setText(Util.fmt(self.currentTrack.artist,50))
        self.nowplaying_album_art.setPixmap(QPixmap(self.currentTrack.albumart).scaled(50,50,Qt.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))

    def player_status_change(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.update_nowplaying()
           
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_next_in_queue()

    def play_next_in_queue(self):
        if self.queue_index + 1 < len(self.queue):
            self.queue_index += 1
            next_track = self.queue[self.queue_index]
            self.currentTrack = next_track
            self.load_track_source(next_track.filepath)
            self.start_playback()
        else:
            Util.print("End of queue reached.")

    def play_previous_in_queue(self):
        if self.queue_index - 1 >= 0:
            self.queue_index -= 1
            previous_track = self.queue[self.queue_index]
            self.currentTrack = previous_track
            self.load_track_source(previous_track.filepath)
            self.start_playback()
        else:
            Util.print("Start of queue reached.")

    def show_context_menu(self, position):
        from PySide6.QtWidgets import QMenu
        menu = QMenu()
        add_action = menu.addAction("Add to Queue")
    
        action = menu.exec(self.tracks_table.viewport().mapToGlobal(position))
        if action == add_action:
            current_row = self.tracks_table.currentRow()
            id = self.tracks_table.item(current_row,4).text()
            track = self.db.search(f"id:{id}",console_out=False)[0]
            self.queue.insert(self.queue_index+1,track)

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
