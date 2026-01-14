import os
import sys
from dotenv import load_dotenv
from ai_movie_maker.content_dubber.dubbing_pipeline import DubbingPipeline

# Load env for API keys
load_dotenv()

def main():
    # Check Gemini Key
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY not found in .env")
        return

    # Input video (change this to a real video with speech)
    input_video = "test_output_video.mp4" 
    output_video = "test_dubbed_video.mp4"
    target_lang = "Vietnamese" # Prompt uses full name usually or code
    
    if not os.path.exists(input_video):
        print(f"Input video {input_video} not found. Please provide a video file.")
        # Create a dummy video if needed? No, user should provide.
        return

    print(f"Start Dubbing: {input_video} -> {output_video} ({target_lang})")
    
    pipeline = DubbingPipeline()
    try:
        pipeline.run(
            video_path=input_video, 
            target_language=target_lang, 
            output_path=output_video,
            voice_name="vi-VN-HoaiMyNeural" # Example Vietnamese voice
        )
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
