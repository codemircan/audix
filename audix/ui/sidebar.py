from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QListWidget, QListWidgetItem, QMessageBox, QFrame, QProgressBar)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import os
import datetime

class Sidebar(QWidget):
    """
    Sidebar to list recordings and handle playback/deletion.
    """
    recording_selected = Signal(str)

    def __init__(self, storage_path, parent=None):
        super().__init__(parent)
        self.storage_path = storage_path
        self._setup_ui()
        self._setup_player()
        self.refresh_list()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Title
        self.title_label = QLabel("Recordings Library")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #E4E4E4;")
        self.layout.addWidget(self.title_label)

        # List of recordings
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #202020;
                border: 1px solid #333333;
                border-radius: 8px;
                color: #E4E4E4;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #2a2a2a;
            }
            QListWidget::item:selected {
                background-color: #333333;
                border-left: 3px solid #00D1FF;
            }
        """)
        self.layout.addWidget(self.list_widget)

        # Control Buttons
        self.btn_layout = QHBoxLayout()
        self.play_btn = QPushButton("Play")
        self.delete_btn = QPushButton("Delete")

        for btn in (self.play_btn, self.delete_btn):
            btn.setCursor(Qt.PointingHandCursor)

        self.play_btn.setObjectName("play-btn")
        self.delete_btn.setObjectName("delete-btn")

        self.btn_layout.addWidget(self.play_btn)
        self.btn_layout.addWidget(self.delete_btn)
        self.layout.addLayout(self.btn_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #333333;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #00D1FF;
            }
        """)
        self.layout.addWidget(self.progress_bar)

        # Connect signals
        self.play_btn.clicked.connect(self.play_selected)
        self.delete_btn.clicked.connect(self.delete_selected)

    def _setup_player(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.8)
        self.player.positionChanged.connect(self._update_progress)
        self.player.durationChanged.connect(self._update_duration)

    def _update_progress(self, position):
        self.progress_bar.setValue(position)

    def _update_duration(self, duration):
        self.progress_bar.setRange(0, duration)

    def refresh_list(self):
        self.list_widget.clear()
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)

        recordings = sorted(os.listdir(self.storage_path), reverse=True)
        for rec in recordings:
            if rec.endswith(('.mp3', '.wav')):
                item = QListWidgetItem(rec)
                self.list_widget.addItem(item)

    def get_selected_path(self):
        item = self.list_widget.currentItem()
        if item:
            return os.path.join(self.storage_path, item.text())
        return None

    def play_selected(self):
        path = self.get_selected_path()
        if path:
            self.player.setSource(QUrl.fromLocalFile(path))
            self.player.play()

    def stop_playback(self):
        self.player.stop()

    def delete_selected(self):
        path = self.get_selected_path()
        if path:
            msg = QMessageBox()
            msg.setWindowTitle("Delete Recording")
            msg.setText(f"Are you sure you want to delete {os.path.basename(path)}?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)

            if msg.exec() == QMessageBox.Yes:
                os.remove(path)
                self.refresh_list()
