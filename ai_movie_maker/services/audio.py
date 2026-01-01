import edge_tts
import asyncio
import os

# Voice Mapping with Pitch/Rate adjustments to simulate characters
# Edge TTS typically only has 2 VN voices: NamMinh (Male) and HoaiMy (Female).
# We create variations using pitch and rate.
VOICE_MAP = {
    "Male - Default": {"voice": "vi-VN-NamMinhNeural", "pitch": "+0Hz", "rate": "+0%"},
    "Male - Deep": {"voice": "vi-VN-NamMinhNeural", "pitch": "-20Hz", "rate": "-5%"},
    "Male - Fast": {"voice": "vi-VN-NamMinhNeural", "pitch": "+0Hz", "rate": "+10%"},
    "Female - Default": {"voice": "vi-VN-HoaiMyNeural", "pitch": "+0Hz", "rate": "+0%"},
    "Female - Soft": {"voice": "vi-VN-HoaiMyNeural", "pitch": "+10Hz", "rate": "-5%"},
    "Female - Fast": {"voice": "vi-VN-HoaiMyNeural", "pitch": "+0Hz", "rate": "+10%"},
}

async def generate_audio_async(text, voice_style, output_file):
    """
    Generates audio file from text using edge-tts with specific style.
    voice_style can be a key in VOICE_MAP or just "Male"/"Female".
    """
    # Fallback logic
    if voice_style not in VOICE_MAP:
        if "male" in voice_style.lower():
            settings = VOICE_MAP["Male - Default"]
        elif "female" in voice_style.lower():
            settings = VOICE_MAP["Female - Default"]
        else:
            settings = VOICE_MAP["Male - Default"]
    else:
        settings = VOICE_MAP[voice_style]
        
    voice = settings["voice"]
    pitch = settings["pitch"]
    rate = settings["rate"]
    
    communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
    await communicate.save(output_file)

def generate_audio_sync(text, voice_style, output_file):
    """
    Synchronous wrapper for generate_audio_async.
    """
    try:
        asyncio.run(generate_audio_async(text, voice_style, output_file))
        return True
    except Exception as e:
        print(f"Error generating audio: {e}")
        return False
