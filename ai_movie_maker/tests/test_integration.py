import sys
import os
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ai_movie_maker.services.audio import generate_audio_sync
from ai_movie_maker.services.video import render_scene_video, generate_text_image
import threading

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_output")
        self.test_dir.mkdir(exist_ok=True)
        self.audio_path = self.test_dir / "test_audio.mp3"
        self.video_path = self.test_dir / "test_video.mp4"
        self.image_path = self.test_dir / "test_image.png" # Optional, can be missing

    def tearDown(self):
        # Clean up
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_audio_generation(self):
        print("Testing Audio Generation...")
        text = "Xin chào, đây là bài kiểm tra âm thanh từ hệ thống AI Movie Maker."
        voice = "Female - Default" # Matches key in audio.py
        
        success = generate_audio_sync(text, voice, str(self.audio_path))
        self.assertTrue(success)
        self.assertTrue(self.audio_path.exists())
        self.assertGreater(self.audio_path.stat().st_size, 0)
        print("Audio Generation Passed.")

    def test_video_rendering(self):
        print("Testing Video Rendering...")
        # First ensure we have audio
        self.test_audio_generation() 
        
        caption = "Test Subtitle Overlay"
        
        # Test with missing image (should use black placeholder)
        success, msg = render_scene_video(None, str(self.audio_path), caption, str(self.video_path))
        
        if not success:
            print(f"Video rendering failed: {msg}")
        
        self.assertTrue(success, f"Video render failed: {msg}")
        self.assertTrue(self.video_path.exists())
        self.assertGreater(self.video_path.stat().st_size, 0)
        print("Video Rendering Passed.")

    def test_custom_video_rendering(self):
        print("Testing Custom Video Rendering (16:9)...")
        self.test_audio_generation()
        custom_video = self.test_dir / "test_video_16x9.mp4"
        
        # Test 16:9 resolution (1920x1080) with custom fonts
        success, msg = render_scene_video(None, str(self.audio_path), "Custom Subtitle", str(custom_video), resolution=(1920, 1080), fontsize=50, color='yellow')
        
        self.assertTrue(success, f"Custom render failed: {msg}")
        self.assertTrue(custom_video.exists())
        print("Custom Video Rendering Passed.")

if __name__ == '__main__':
    unittest.main()
