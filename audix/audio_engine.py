import numpy as np
import sounddevice as sd
from PySide6.QtCore import QThread, Signal
import time

class AudioWorker(QThread):
    data_available = Signal(np.ndarray)
    error_occurred = Signal(str)
    recording_finished = Signal(np.ndarray)

    def __init__(self, device_id, sample_rate=44100, channels=1):
        super().__init__()
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self._buffer = []

    def run(self):
        self._buffer = []
        self.is_recording = True

        try:
            with sd.InputStream(device=self.device_id,
                                channels=self.channels,
                                samplerate=self.sample_rate,
                                callback=self._audio_callback):
                while self.is_recording:
                    time.sleep(0.1)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if self._buffer:
                full_data = np.concatenate(self._buffer, axis=0)
                self.recording_finished.emit(full_data)
            self.is_recording = False

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            # We could emit a signal for status errors but let's keep it simple for now
            # and only report if it's critical.
            pass
        if self.is_recording:
            data_copy = indata.copy()
            self._buffer.append(data_copy)
            self.data_available.emit(data_copy)

    def stop(self):
        self.is_recording = False
