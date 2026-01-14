import os
from pydub import AudioSegment

class AudioMixer:
    def __init__(self):
        pass

    def mix_audio(self, background_path: str, segments: list, output_path: str):
        """
        Mixes the background music with the generated speech segments.
        
        Args:
            background_path (str): Path to the background audio (no vocals).
            segments (list): List of segments containing 'audio_path', 'start' (in seconds).
            output_path (str): Path to save the final mixed audio.
            
        Returns:
            str: Path to the mixed audio file.
        """
        if not os.path.exists(background_path):
            raise FileNotFoundError(f"Background audio not found: {background_path}")

        try:
            print(f"Loading background: {background_path}")
            final_mix = AudioSegment.from_file(background_path)
            
            # Reduce background volume slightly to make voice clearer (Ducking logic can be improved later)
            # final_mix = final_mix - 3 
            
            for i, seg in enumerate(segments):
                speech_path = seg.get('audio_path')
                if not speech_path or not os.path.exists(speech_path):
                    print(f"Warning: Speech file missing for segment {i}, skipping.")
                    continue
                
                start_ms = int(seg['start'] * 1000)
                speech = AudioSegment.from_file(speech_path)
                
                # Check consistency
                # If speech is too long, it might overlap next. 
                # For now, just overlay.
                final_mix = final_mix.overlay(speech, position=start_ms)
            
            # Ensure output dir
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Determine format from extension
            fmt = output_path.split('.')[-1]
            if fmt not in ['mp3', 'wav', 'ogg', 'flac']:
                fmt = 'mp3'
                
            print(f"Exporting mixed audio to {output_path}...")
            final_mix.export(output_path, format=fmt)
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Audio mixing failed: {str(e)}")
