import sys
import os
import signal
from PySide6.QtWidgets import QApplication, QMessageBox
from audix.ui.main_window import MainWindow

def check_audio_subsystem():
    """
    Check for PulseAudio or PipeWire presence via pactl or pw-link.
    This provides useful feedback for Linux users.
    """
    pulse_active = os.system("pactl info > /dev/null 2>&1") == 0
    pipewire_active = os.system("pw-link -i > /dev/null 2>&1") == 0

    if not (pulse_active or pipewire_active):
        print("Warning: No PulseAudio or PipeWire detected. Recording might fail.")
        return False
    return True

def main():
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # To handle high-DPI displays
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("Audix Voice Recorder")

    # Check if audio subsystem is available
    if not check_audio_subsystem():
        # You could show a message box here, but let's proceed and handle device errors in UI
        pass

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
