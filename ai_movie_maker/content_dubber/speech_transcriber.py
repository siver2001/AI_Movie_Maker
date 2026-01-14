import os
import whisper

class SpeechTranscriber:
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        print(f"Loading Whisper model ({model_size})...")
        self.model = whisper.load_model(model_size)

    def transcribe(self, audio_path: str):
        """
        Transcribes audio to text with timestamps.
        
        Args:
            audio_path (str): Path to the vocal audio file.
            
        Returns:
            list: List of segments, where each segment is a dict 
                  {'start': float, 'end': float, 'text': str}.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        print(f"Transcribing {audio_path}...")
        try:
            result = self.model.transcribe(audio_path)
            
            segments = []
            for seg in result.get('segments', []):
                segments.append({
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'].strip()
                })
            
            return segments
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {str(e)}")
