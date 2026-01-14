import os
import asyncio
import shutil
from .audio_extractor import AudioExtractor
from .vocal_separator import VocalSeparator
from .speech_transcriber import SpeechTranscriber
from .text_translator import TextTranslator
from .voice_synthesizer import VoiceSynthesizer
from .audio_mixer import AudioMixer

class DubbingPipeline:
    def __init__(self, gemini_api_key: str = None):
        self.audio_extractor = AudioExtractor()
        self.vocal_separator = VocalSeparator()
        self.speech_transcriber = SpeechTranscriber(model_size="base")
        self.text_translator = TextTranslator(api_key=gemini_api_key)
        self.voice_synthesizer = VoiceSynthesizer() # Can param voice
        self.audio_mixer = AudioMixer()

    def extract_and_transcribe(self, video_path: str, work_dir: str = None) -> dict:
        """
        Step 1-3: Extract, Separate, and Transcribe.
        Returns a context dict with paths and segments.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
            
        if not work_dir:
            base_dir = os.path.dirname(os.path.abspath(video_path))
            work_dir = os.path.join(base_dir, "dubbing_temp")
            
        os.makedirs(work_dir, exist_ok=True)
        
        print("=== Step 1: Extract Audio ===")
        original_audio = os.path.join(work_dir, "original.wav")
        self.audio_extractor.extract_audio(video_path, original_audio)
        
        print("=== Step 2: Separate Vocals ===")
        separation_out = os.path.join(work_dir, "separation")
        stems = self.vocal_separator.separate_vocals(original_audio, separation_out)
        vocals_path = stems['vocals']
        bg_path = stems['no_vocals']
        
        print("=== Step 3: Transcribe ===")
        segments = self.speech_transcriber.transcribe(vocals_path)
        
        return {
            "segments": segments,
            "work_dir": work_dir,
            "bg_path": bg_path,
            "vocals_path": vocals_path,
            "video_path": video_path
        }

    def generate_video_from_segments(self, context: dict, target_language: str, output_path: str, voice_name: str) -> str:
        """
        Step 4-7: Translate, TTS, Mix, Mux.
        """
        segments = context["segments"]
        work_dir = context["work_dir"]
        bg_path = context["bg_path"]
        video_path = context["video_path"]
        
        # Update voice
        self.voice_synthesizer.voice_name = voice_name
        
        print("=== Step 4: Translate ===")
        translated_segments = self.text_translator.translate_segments(segments, target_language)
        
        print("=== Step 5: Synthesize Speech ===")
        tts_out = os.path.join(work_dir, "tts_audio")
        # Run async synthesis
        final_segments = asyncio.run(
            self.voice_synthesizer.synthesize_segments(translated_segments, tts_out)
        )
        
        print("=== Step 6: Mix Audio ===")
        mixed_audio_path = os.path.join(work_dir, "mixed_audio.mp3")
        self.audio_mixer.mix_audio(bg_path, final_segments, mixed_audio_path)
        
        print("=== Step 7: Final Mux (Replace Audio in Video) ===")
        # Use moviepy to swap audio
        from moviepy.editor import VideoFileClip, AudioFileClip
        
        video = VideoFileClip(video_path)
        new_audio = AudioFileClip(mixed_audio_path)
        
        final_video = video.set_audio(new_audio)
        final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)
        
        video.close()
        new_audio.close()
        
        print(f"Dubbing completed! Output: {output_path}")
        return output_path

    def run(self, video_path: str, target_language: str, output_path: str, voice_name: str = "vi-VN-HoaiMyNeural"):
        """
        Executes the full video dubbing pipeline.
        """
        context = self.extract_and_transcribe(video_path)
        return self.generate_video_from_segments(context, target_language, output_path, voice_name)
