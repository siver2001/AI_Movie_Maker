import os
from moviepy.editor import VideoFileClip

class AudioExtractor:
    def __init__(self):
        pass

    def extract_audio(self, video_path: str, output_path: str) -> str:
        """
        Extracts audio from a video file.
        
        Args:
            video_path (str): Path to the input video file.
            output_path (str): Path to save the extracted audio file (e.g., .wav or .mp3).
            
        Returns:
            str: Path to the extracted audio file.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        try:
            video = VideoFileClip(video_path)
            if video.audio is None:
                raise ValueError("Video has no audio track")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            video.audio.write_audiofile(output_path, logger=None)
            video.close()
            return output_path
        except Exception as e:
            raise RuntimeError(f"Failed to extract audio: {str(e)}")
