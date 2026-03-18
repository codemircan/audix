import pyqtgraph as pg
from PySide6.QtCore import Qt, QTimer
import numpy as np

class WaveformVisualizer(pg.PlotWidget):
    """
    Real-time waveform visualizer using pyqtgraph for 60 FPS performance.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackground('#181818')
        self.showAxis('left', False)
        self.showAxis('bottom', False)
        self.setMouseEnabled(x=False, y=False)
        self.setMenuEnabled(False)
        self.setYRange(-1.1, 1.1)

        # Color: Electric Cyan (#00D1FF)
        self.curve = self.plot(pen=pg.mkPen('#00D1FF', width=2))

        # Buffer for visualization
        self.max_points = 2000
        self.data = np.zeros(self.max_points)

    def update_data(self, new_data):
        """
        Expects a numpy array of PCM data.
        """
        # Take the absolute mean or just slice? Let's slice for real waveform feel
        # or downsample if too large.
        if len(new_data) > 0:
            # Flatten if multi-channel (though we handle mono for now)
            new_data = new_data.flatten()

            # Simple scrolling effect or fixed window? Let's do a scrolling window.
            n = len(new_data)
            if n >= self.max_points:
                self.data = new_data[-self.max_points:]
            else:
                self.data = np.roll(self.data, -n)
                self.data[-n:] = new_data

            self.curve.setData(self.data)

    def clear(self):
        self.data = np.zeros(self.max_points)
        self.curve.setData(self.data)
