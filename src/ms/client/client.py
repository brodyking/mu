import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QWidget, QAbstractItemView, QHBoxLayout, QPushButton, QLineEdit, QLabel, QSlider, QStackedLayout
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QPixmap

from ms.database import Database
from ms.util import Util
from ms.track import Track
from ms.client.clickable_slider import ClickableSlider

import ms.client.resources_rc

class Client(QMainWindow):
    def __init__(self):
        super().__init__()

        Util.print("Starting client")
        self.initApplication()
        self.initUI()

    def initApplication(self):

        # --- Window ---
        self.setWindowTitle("ms - based music server")
        self.resize(600, 400)
        self.setMinimumWidth(600) 

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
        

    def initUI(self):
        # --- Queue table ---
        queue_layout =QVBoxLayout()

        self.queue_table = self.gen_tracks_table(sorting=False)
        self.queue_table.cellDoubleClicked.connect(lambda: self.cell_clicked(self.queue_table))

        queue_layout.addWidget(self.queue_table)
        
        # --- Tracks table ---

        tracks_layout =QVBoxLayout()

        self.tracks_search_input = QLineEdit()
        self.tracks_search_input.setStyleSheet("QLineEdit { padding: 3px; }")
        self.tracks_search_input.setPlaceholderText("Search by Title, Artist, or Album...")
        self.tracks_search_input.textChanged.connect(self.filter_table)
        
        self.tracks_table = self.gen_tracks_table()
        self.tracks_table.cellDoubleClicked.connect(lambda: self.cell_clicked(self.tracks_table))

        self.populate_table(self.tracks_table,self.tracks)

        tracks_layout.addWidget(self.tracks_search_input)
        tracks_layout.addWidget(self.tracks_table)


        # --- Now Playing -- 

        # Album Art
        self.nowplaying_album_art = QLabel()
        self.nowplaying_album_art.setPixmap(QPixmap("").scaled(75,75,Qt.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))

        # Current track metadata
        nowplaying_track_metadata_layout = QVBoxLayout()

        self.nowplaying_track_label = QLabel(self,text="")
        self.nowplaying_artist_label = QLabel(self,text="")
        self.nowplaying_album_label = QLabel(self,text="")

        self.nowplaying_track_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.nowplaying_artist_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.nowplaying_album_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        nowplaying_track_metadata_layout.addWidget(self.nowplaying_track_label)
        nowplaying_track_metadata_layout.addWidget(self.nowplaying_artist_label)
        nowplaying_track_metadata_layout.addWidget(self.nowplaying_album_label)

        # Progress Bar
        self.nowplaying_progress_bar = ClickableSlider(Qt.Horizontal)

        self.player.durationChanged.connect(lambda max: self.nowplaying_progress_bar.setRange(0,max)) # Set max time
        self.player.positionChanged.connect(self.nowplaying_progress_bar.setValue) # Update handle position

        self.nowplaying_progress_bar.sliderMoved.connect(self.player.setPosition) # Jump to clicked time
        
        # Controls
        control_layout = QHBoxLayout()
        
        self.toggle_playback_button = QPushButton("▶")
        self.toggle_playback_button.clicked.connect(lambda: self.toggle_playback())

        self.play_next_button = QPushButton("▶▶")
        self.play_next_button.clicked.connect(lambda: self.play_next_in_queue())

        self.play_previous_button = QPushButton("◀◀")
        self.play_previous_button.clicked.connect(lambda: self.play_previous_in_queue())

        control_layout.addWidget(self.play_previous_button)
        control_layout.addWidget(self.toggle_playback_button)
        control_layout.addWidget(self.play_next_button)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Tab buttons
        tracks_button = QPushButton("Tracks")
        queue_button = QPushButton("Queue")

        # --- Layouts ---

        # Main Stacked Layout
        self.stacked = QStackedLayout()
        # Queue Page
        queue_page = QWidget()
        queue_page.setLayout(queue_layout)
        self.stacked.addWidget(queue_page)
        # Tracks Page
        tracks_page = QWidget()
        tracks_page.setLayout(tracks_layout)
        self.stacked.addWidget(tracks_page)
        # Set default to tracks
        self.stacked.setCurrentIndex(1)
        

        top_bar_top_layout = QHBoxLayout()
        top_bar_top_layout.addWidget(self.nowplaying_album_art)
        top_bar_top_layout.addLayout(nowplaying_track_metadata_layout)
        top_bar_top_layout.addStretch()
        top_bar_top_layout.addLayout(control_layout)

        top_bar_bottom_layout = QHBoxLayout()
        top_bar_bottom_layout.addWidget(queue_button)
        top_bar_bottom_layout.addWidget(tracks_button)
        queue_button.pressed.connect(lambda: self.stacked.setCurrentIndex(0))
        tracks_button.pressed.connect(lambda: self.stacked.setCurrentIndex(1))

        # Top bar
        top_bar_layout = QVBoxLayout()
        top_bar_layout.setSpacing(11)
        top_bar_layout.setContentsMargins(11,11,11,0)
        top_bar_layout.addLayout(top_bar_top_layout)
        top_bar_layout.addWidget(self.nowplaying_progress_bar)
        top_bar_layout.addLayout(top_bar_bottom_layout)
       
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addLayout(top_bar_layout) # Add the control layout below the table
        layout.addLayout(self.stacked) # Add the control layout below the table
        
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
        self.populate_table(self.tracks_table,self.tracks)
        
        Util.print(f"Search results found: {len(self.tracks)} tracks.")

    def populate_table_queue(self):
        queue_tracks = []
        for id in self.queue[self.queue_index:]:
            queue_tracks.append(self.db.search(f"id:{id}",console_out=False)[0])
        self.populate_table(self.queue_table,queue_tracks)
        
    def populate_table(self,table, tracks: list):
        """Helper function to populate the table with a given list of tracks."""
        # Clear existing content first
        table.setSortingEnabled(False)
        table.setRowCount(len(tracks))
        table.setColumnCount(15)


        # Repopulate using the existing logic from gen_tracks_view
        for row_index, track in enumerate(tracks):
            # Column 0: Title
            fav_icon = QTableWidgetItem(f"{'❤ ' if track.favorite else ''}")

            table.setItem(row_index, 0, QTableWidgetItem(str(track.id)))
            table.setItem(row_index, 1, fav_icon)
            table.setItem(row_index, 2, QTableWidgetItem(track.title))
            table.setItem(row_index, 3, QTableWidgetItem(track.artist))
            table.setItem(row_index, 4, QTableWidgetItem(track.album))
            table.setItem(row_index, 5, QTableWidgetItem(track.plays))
            table.setItem(row_index, 6, QTableWidgetItem(track.time))
            table.setItem(row_index, 7, QTableWidgetItem(track.dateadded))
            table.setItem(row_index, 8, QTableWidgetItem(track.tracknumber))
            table.setItem(row_index, 9, QTableWidgetItem(track.albumartist))
            table.setItem(row_index, 10, QTableWidgetItem(track.discnumber))
            table.setItem(row_index, 11, QTableWidgetItem(track.genre))
            table.setItem(row_index, 12, QTableWidgetItem(track.date))
            table.setItem(row_index, 13, QTableWidgetItem(track.filepath))
            table.setItem(row_index, 14, QTableWidgetItem(track.filename))
            table.setItem(row_index, 15, QTableWidgetItem(track.albumart))

        table.setSortingEnabled(True)

    def get_column_data(self,table_widget, col_index):
        column_list = []
        # rowCount() reflects the current state of the UI
        for row in range(table_widget.rowCount()):
            item = table_widget.item(row, col_index)
            if item is not None:
                column_list.append(item.text())
        return column_list

    def gen_tracks_table(self,sorting=True) -> QTableWidget:
        # Table
        table = QTableWidget(len(self.tracks),16) 
                    
        table.setHorizontalHeaderLabels(["Id", "Favorite", "Title","Artist","Album","Plays","Time","Date Added","Track Number", "Album Artist", "Disc Number", "Genre", "Date", "File Path", "File Name", "Album Art"])
        table.verticalHeader().hide()

        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) 
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) 

        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu)

        if sorting: table.setSortingEnabled(True)
        table.sortByColumn(1,Qt.SortOrder.AscendingOrder)
        table.setColumnWidth(0,60) # Id
        table.setColumnWidth(1,30) # Favorite
        table.setColumnWidth(2,200) # Title
        table.setColumnWidth(3,150) # Artist
        table.setColumnWidth(4,150) # Album
        table.setColumnWidth(5,60) # Plays
        table.setColumnWidth(6,100) # Time
        table.setColumnWidth(7,100) # Date Added
        table.setColumnWidth(8,60) # Track Number
        table.setColumnWidth(9,150) # Album Artist
        table.setColumnWidth(10,60) # Disc Number
        table.setColumnWidth(11,100) # Genre
        table.setColumnWidth(12,100) # Date
        table.setColumnWidth(13,150) # File Path
        table.setColumnWidth(14,100) # File Name
        table.setColumnWidth(15,150) # Album Art

        return table

    # Plays song when double clicked (Kept for convenience)
    def cell_clicked(self,table):
        current_row = table.currentRow()

        filepath_col = table.item(current_row,13)
        id_col = table.item(current_row,0)

        self.queue = self.get_column_data(table,0)
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
            self.toggle_playback_button.setText("⏸")


            Util.print("Playback started")

    def stop_playback(self):
        self.player.pause()
        self.is_playing = False
        self.toggle_playback_button.setText("▶")
        Util.print("Playback paused")

    def update_nowplaying(self):
        print(self.currentTrack)
        self.nowplaying_track_label.setText(Util.fmt(self.currentTrack.title,50))
        self.nowplaying_artist_label.setText(Util.fmt(self.currentTrack.artist,50))
        self.nowplaying_album_label.setText(Util.fmt(self.currentTrack.album,50))
        self.nowplaying_album_art.setPixmap(QPixmap(self.currentTrack.albumart).scaled(75,75,Qt.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))



    def player_status_change(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.update_nowplaying()
            self.populate_table_queue()

        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_next_in_queue()

    def play_next_in_queue(self):
        if self.queue_index + 1 < len(self.queue):
            self.queue_index += 1
            next_track_id = self.queue[self.queue_index]
            print(next_track_id)
            self.currentTrack = self.db.search(f"id:{next_track_id}",console_out=False)[0]
            self.load_track_source(self.currentTrack.filepath)
            self.start_playback()
        else:
            Util.print("End of queue reached.")

    def play_previous_in_queue(self):
        if self.queue_index - 1 >= 0:
            self.queue_index -= 1
            previous_track_id = self.queue[self.queue_index]
            self.currentTrack = self.db.search(f"id:{previous_track_id}",console_out=False)[0]
            self.load_track_source(self.currentTrack.filepath)
            self.start_playback()
        else:
            Util.print("End of queue reached.")

    def show_context_menu(self, position):
        from PySide6.QtWidgets import QMenu
        menu = QMenu()
        add_action = menu.addAction("Add to Queue")
    
        action = menu.exec(self.tracks_table.viewport().mapToGlobal(position))
        if action == add_action:
            current_row = self.tracks_table.currentRow()
            id = self.tracks_table.item(current_row,4).text()
            self.queue.insert(self.queue_index+1,id)

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
