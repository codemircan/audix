import sounddevice as sd

def get_audio_devices():
    """
    Returns a list of audio input devices.
    Identifies 'monitor' sources as 'System Audio'.
    Each device is represented as a dict with 'id', 'name', and 'is_monitor'.
    """
    devices = sd.query_devices()
    input_devices = []

    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            name = dev['name']
            is_monitor = 'monitor' in name.lower()

            # User-friendly label
            display_name = name
            if is_monitor:
                display_name = f"System Audio ({name})"
            else:
                display_name = f"Microphone ({name})"

            input_devices.append({
                'id': i,
                'name': name,
                'display_name': display_name,
                'is_monitor': is_monitor,
                'hostapi': dev['hostapi']
            })

    return input_devices
