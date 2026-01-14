import os
import subprocess
import shutil
from pathlib import Path

class VocalSeparator:
    def __init__(self, model_name: str = "htdemucs"):
        self.model_name = model_name

    def separate_vocals(self, audio_path: str, output_dir: str):
        """
        Separates vocals from the background audio using Demucs.
        
        Args:
            audio_path (str): Path to the input audio file.
            output_dir (str): Directory to save the separated tracks.
            
        Returns:
            dict: Paths to 'vocals' and 'no_vocals' (accompaniment) files.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Separating vocals for {audio_path} using model {self.model_name}...")
        
        # Construct Demucs command
        # --two-stems=vocals: Splits into 'vocals' and 'no_vocals'
        # -n: Model name
        # -o: Output directory
        import sys
        
        # Construct Demucs command
        # Use sys.executable -m demucs to avoid path issues and win32 errors with script wrappers
        cmd = [
            sys.executable, "-m", "demucs.separate",
            "--two-stems=vocals",
            "-n", self.model_name,
            "-o", output_dir,
            audio_path
        ]
        
        try:
            # Run Demucs
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Demucs output structure: output_dir/model_name/audio_filename_no_ext/
            audio_filename = Path(audio_path).stem
            model_output_dir = Path(output_dir) / self.model_name / audio_filename
            
            vocals_path = model_output_dir / "vocals.wav"
            no_vocals_path = model_output_dir / "no_vocals.wav"
            
            if not vocals_path.exists() or not no_vocals_path.exists():
                raise RuntimeError(f"Demucs output files not found in {model_output_dir}")
                
            return {
                "vocals": str(vocals_path),
                "no_vocals": str(no_vocals_path)
            }
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Demucs separation failed: {e.stderr.decode()}")
        except Exception as e:
            raise RuntimeError(f"Error during vocal separation: {str(e)}")
