import unittest
import numpy as np
import os
import shutil
from audix.encoder import save_recording

class TestEncoder(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_output"
        os.makedirs(self.test_dir, exist_ok=True)
        # Generate 1 second of silence (float32)
        self.sample_rate = 44100
        self.duration = 1.0
        self.pcm_data = np.zeros(int(self.sample_rate * self.duration), dtype=np.float32)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_wav(self):
        path = os.path.join(self.test_dir, "test.wav")
        save_recording(self.pcm_data, path, format='wav', sample_rate=self.sample_rate)
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)

    def test_save_mp3(self):
        path = os.path.join(self.test_dir, "test.mp3")
        save_recording(self.pcm_data, path, format='mp3', sample_rate=self.sample_rate, bitrate=192)
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)

if __name__ == '__main__':
    unittest.main()
