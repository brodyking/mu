import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget 
from PySide6.QtCore import Qt

from ms.database import Database
from ms.util import Util

class Client(QMainWindow):
    def __init__(self):
        super().__init__()

        Util.print("Starting client")
        
        self.setWindowTitle("sm")
        self.resize(600, 400)

        db = Database()
        tracks = db.list_library()

        self.table = QTableWidget(len(tracks),3)
        self.table.setHorizontalHeaderLabels(["Title", "Artist", "Album"])

        for row in range(len(tracks)):
            for col in range(4):
                if col == 0:
                    self.table.setItem(row,col,QTableWidgetItem(tracks[row].title))
                elif col == 1:
                    self.table.setItem(row,col,QTableWidgetItem(tracks[row].artist))
                else:
                    self.table.setItem(row,col,QTableWidgetItem(tracks[row].album))

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        


def start_client():
    app = QApplication()
    window = Client()
    window.show()
    sys.exit(app.exec())
