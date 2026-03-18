import lameenc
import wave
import numpy as np
import os

def encode_to_mp3(pcm_data, output_path, sample_rate=44100, bitrate=320):
    """
    Encodes raw PCM data (float32 numpy array) to an MP3 file using lameenc.
    """
    # Convert float32 [-1.0, 1.0] to int16 with clipping
    pcm_clipped = np.clip(pcm_data, -1.0, 1.0)
    pcm_int16 = (pcm_clipped * 32767).astype(np.int16)

    encoder = lameenc.Encoder()
    encoder.set_bit_rate(bitrate)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1) # For now we're mono, can be adjusted
    encoder.set_quality(2) # High quality

    mp3_data = encoder.encode(pcm_int16.tobytes())
    mp3_data += encoder.flush()

    with open(output_path, 'wb') as f:
        f.write(mp3_data)

def encode_to_wav(pcm_data, output_path, sample_rate=44100):
    """
    Encodes raw PCM data (float32 numpy array) to a 16-bit PCM WAV file.
    """
    # Convert float32 [-1.0, 1.0] to int16 with clipping
    pcm_clipped = np.clip(pcm_data, -1.0, 1.0)
    pcm_int16 = (pcm_clipped * 32767).astype(np.int16)

    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_int16.tobytes())

def save_recording(pcm_data, output_path, format='mp3', sample_rate=44100, bitrate=320):
    """
    Main entry point to save recording in the specified format.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if format.lower() == 'mp3':
        encode_to_mp3(pcm_data, output_path, sample_rate, bitrate)
    elif format.lower() == 'wav':
        encode_to_wav(pcm_data, output_path, sample_rate)
    else:
        raise ValueError(f"Unsupported format: {format}")
