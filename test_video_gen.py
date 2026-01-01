import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from ai_movie_maker.services.video import render_scene_video

def test_gen():
    img_path = "img_scene_1.png"
    audio_path = "audio_scene_1.mp3"
    output_path = "test_output_video.mp4"
    
    # Create dummy assets if missing
    if not os.path.exists(img_path):
        print("Creating dummy image...")
        from PIL import Image
        img = Image.new('RGB', (1080, 1920), color='blue')
        img.save(img_path)
        
    if not os.path.exists(audio_path):
        print("Creating dummy audio...")
        # Create a silent audio clip
        from moviepy.editor import AudioClip
        import numpy as np
        # 2 seconds of silence/noise
        def make_frame(t): return np.sin(2 * np.pi * 440 * t) # beep
        clip = AudioClip(make_frame, duration=2)
        clip.write_audiofile(audio_path, fps=44100)

    print("Starting render...")
    # This calls the function with the new signature (default video_clip_path=None)
    success, msg = render_scene_video(
        image_path=img_path,
        audio_path=audio_path,
        subtitle_text="This is a test subtitle",
        output_path=output_path
    )
    
    if success:
        print(f"Success! Video saved to {output_path}")
    else:
        print(f"Failed: {msg}")

if __name__ == "__main__":
    test_gen()
