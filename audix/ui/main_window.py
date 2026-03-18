from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QStatusBar, QFrame,
                             QGroupBox, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QPalette, QColor
import os
import datetime
import numpy as np

from audix.audio_engine import AudioWorker
from audix.encoder import save_recording
from audix.utils import get_audio_devices
from audix.ui.visualizer import WaveformVisualizer
from audix.ui.sidebar import Sidebar

class Toast(QLabel):
    """
    A simple toast notification that fades in and out.
    """
    def __init__(self, message, parent=None):
        super().__init__(message, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            background-color: rgba(50, 50, 50, 230);
            color: #E4E4E4;
            border-radius: 20px;
            padding: 10px 20px;
            font-size: 14px;
            border: 1px solid #444444;
        """)
        self.setFixedSize(300, 40)
        self.setVisible(False)

        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)

    def show_toast(self):
        # Position at bottom center of parent
        if self.parent():
            parent_rect = self.parent().rect()
            self.move((parent_rect.width() - self.width()) // 2,
                      parent_rect.height() - self.height() - 60)

        self.setVisible(True)
        self.setWindowOpacity(0.0)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

        QTimer.singleShot(2500, self.fade_out)

    def fade_out(self):
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(lambda: self.setVisible(False))
        self.animation.start()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audix Voice Recorder")
        self.setMinimumSize(900, 600)

        self.storage_path = os.path.expanduser("~/Music/Audix")
        os.makedirs(self.storage_path, exist_ok=True)

        self.audio_worker = None
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self._setup_ui()
        self._load_style()
        self.refresh_devices()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Left Panel (Main Controls) ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(30, 30, 30, 30)
        left_layout.setSpacing(20)

        # Device Selection
        device_layout = QVBoxLayout()
        device_label = QLabel("Recording Input Device")
        device_label.setStyleSheet("font-weight: bold; color: #888888; font-size: 12px;")
        self.device_combo = QComboBox()
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_combo)
        left_layout.addLayout(device_layout)

        # Visualizer
        self.visualizer = WaveformVisualizer()
        self.visualizer.setMinimumHeight(150)
        left_layout.addWidget(self.visualizer)

        # Timer
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setObjectName("timer-label")
        self.timer_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.timer_label)

        # Record Toggle Button
        self.record_btn = QPushButton("●  RECORD")
        self.record_btn.setObjectName("record-btn")
        self.record_btn.setCheckable(True)
        self.record_btn.setCursor(Qt.PointingHandCursor)
        self.record_btn.clicked.connect(self.toggle_recording)
        left_layout.addWidget(self.record_btn)

        # Format & Bitrate Settings
        settings_group = QGroupBox("Export Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #333333; border-radius: 8px; margin-top: 15px; padding-top: 15px; color: #888888; }")
        settings_layout = QVBoxLayout(settings_group)

        # Format Selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_group = QButtonGroup(self)
        self.rb_mp3 = QRadioButton("MP3")
        self.rb_wav = QRadioButton("WAV")
        self.rb_mp3.setChecked(True)
        self.format_group.addButton(self.rb_mp3)
        self.format_group.addButton(self.rb_wav)
        format_layout.addWidget(self.rb_mp3)
        format_layout.addWidget(self.rb_wav)
        format_layout.addStretch()
        settings_layout.addLayout(format_layout)

        # Bitrate Selection
        bitrate_layout = QHBoxLayout()
        bitrate_layout.addWidget(QLabel("Bitrate:"))
        self.bitrate_group = QButtonGroup(self)
        self.rb_192 = QRadioButton("192 kbps")
        self.rb_320 = QRadioButton("320 kbps")
        self.rb_320.setChecked(True)
        self.bitrate_group.addButton(self.rb_192)
        self.bitrate_group.addButton(self.rb_320)
        bitrate_layout.addWidget(self.rb_192)
        bitrate_layout.addWidget(self.rb_320)
        bitrate_layout.addStretch()
        settings_layout.addLayout(bitrate_layout)

        left_layout.addWidget(settings_group)
        left_layout.addStretch()

        main_layout.addWidget(left_panel, 7) # Main area takes more space

        # --- Sidebar (Library) ---
        self.sidebar = Sidebar(self.storage_path)
        main_layout.addWidget(self.sidebar, 3)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _load_style(self):
        style_path = os.path.join(os.path.dirname(__file__), "style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())

    def refresh_devices(self):
        self.device_combo.clear()
        self.devices = get_audio_devices()
        for dev in self.devices:
            self.device_combo.addItem(dev['display_name'], dev['id'])

        if not self.devices:
            self.status_bar.showMessage("Error: No input devices found!")

    def toggle_recording(self):
        if self.record_btn.isChecked():
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        # Stop any playback
        self.sidebar.stop_playback()

        device_id = self.device_combo.currentData()
        if device_id is None:
            self.show_toast("No device selected")
            self.record_btn.setChecked(False)
            return

        self.audio_worker = AudioWorker(device_id)
        self.audio_worker.data_available.connect(self.visualizer.update_data)
        self.audio_worker.error_occurred.connect(self.handle_recording_error)
        self.audio_worker.recording_finished.connect(self.process_recording)

        self.record_btn.setText("■  STOP")
        self.status_bar.showMessage("Recording...")
        self.start_time = datetime.datetime.now()
        self.timer.start(100)
        self.audio_worker.start()

    def stop_recording(self):
        if self.audio_worker:
            self.status_bar.showMessage("Encoding...")
            self.audio_worker.stop()
            self.timer.stop()
            self.record_btn.setText("●  RECORD")

    def update_timer(self):
        if self.start_time:
            delta = datetime.datetime.now() - self.start_time
            seconds = int(delta.total_seconds())
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def process_recording(self, pcm_data):
        fmt = 'mp3' if self.rb_mp3.isChecked() else 'wav'
        bitrate = 320 if self.rb_320.isChecked() else 192

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audix_{timestamp}.{fmt}"
        filepath = os.path.join(self.storage_path, filename)

        try:
            save_recording(pcm_data, filepath, format=fmt, bitrate=bitrate)
            self.status_bar.showMessage(f"Saved: {filename}")
            self.sidebar.refresh_list()
            self.show_toast("Recording saved successfully!")
        except Exception as e:
            self.handle_recording_error(f"Save failed: {str(e)}")

        self.timer_label.setText("00:00:00")
        self.visualizer.clear()

    def handle_recording_error(self, error_msg):
        self.status_bar.showMessage(f"Error: {error_msg}")
        self.show_toast(f"Error: {error_msg}")
        self.record_btn.setChecked(False)
        self.record_btn.setText("●  RECORD")
        self.timer.stop()

    def show_toast(self, message):
        toast = Toast(message, self)
        toast.show_toast()
