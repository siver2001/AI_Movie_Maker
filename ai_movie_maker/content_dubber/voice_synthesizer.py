import os
import asyncio
import edge_tts

class VoiceSynthesizer:
    def __init__(self, voice_name: str = "vi-VN-HoaiMyNeural"):
        self.voice_name = voice_name

    async def _synthesize_one(self, text: str, output_path: str):
        communicate = edge_tts.Communicate(text, self.voice_name)
        await communicate.save(output_path)

    async def synthesize_segments(self, segments: list, output_dir: str) -> list:
        """
        Synthesizes speech for each translated segment.
        
        Args:
            segments (list): List of translated segments.
            output_dir (str): Directory to save individual audio clips.
            
        Returns:
            list: Updated segments with 'audio_path' pointing to the generated file.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Synthesizing {len(segments)} segments using {self.voice_name}...")
        
        tasks = []
        updated_segments = []
        
        for i, seg in enumerate(segments):
            text = seg['text']
            audio_filename = f"segment_{i:04d}.mp3"
            audio_path = os.path.join(output_dir, audio_filename)
            
            # Create task
            tasks.append(self._synthesize_one(text, audio_path))
            
            # Update segment info
            new_seg = seg.copy()
            new_seg['audio_path'] = audio_path
            updated_segments.append(new_seg)
            
        # Run all synthesis tasks concurrently
        await asyncio.gather(*tasks)
        
        return updated_segments
