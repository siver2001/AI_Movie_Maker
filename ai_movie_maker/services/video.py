import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip, ColorClip, VideoFileClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap

def generate_text_image(text, size=(1920, 1080), fontsize=60, color=(255, 255, 255), bgcolor=None):
    """
    Generates a transparent image with text using Pillow to avoid ImageMagick dependency.
    """
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except IOError:
        font = ImageFont.load_default()
    
    # Wrap text
    max_char = int(size[0] / (fontsize * 0.6))  # Rough estimate
    lines = textwrap.wrap(text, width=max_char)
    
    # Calculate text height
    # Use getbbox if available (Pillow >= 9.2.0) or getsize (deprecated)
    # We'll use a simple approximation for line height
    line_height = fontsize * 1.5
    total_height = len(lines) * line_height
    
    y_text = (size[1] - total_height) / 2
    if bgcolor:
         # Draw background box if needed (optional)
         pass

    for line in lines:
        # Check text width
        try:
             bbox = font.getbbox(line)
             w = bbox[2] - bbox[0]
        except:
             w = fontsize * len(line) * 0.5 # fallback

        x_text = (size[0] - w) / 2
        
        # Shadow/Outline
        draw.text((x_text+2, y_text+2), line, font=font, fill=(0,0,0))
        draw.text((x_text, y_text), line, font=font, fill=color)
        y_text += line_height
        
    return np.array(img)

def render_scene_video(image_path, audio_path, subtitle_text, output_path, resolution=(1080, 1920)):
    """
    Renders a single scene video: Image + Audio + Subtitle.
    Vertical resolution (1080x1920) default for Shorts/Reels.
    """
    try:
        # Load Audio
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        
        # Load Image
        if image_path and os.path.exists(image_path):
            img_clip = ImageClip(image_path).set_duration(duration)
        else:
            # Fallback black screen
            img_clip = ColorClip(size=resolution, color=(0,0,0)).set_duration(duration)
            
        # Resize/Crop Image to fill screen
        # img_clip = img_clip.resize(height=resolution[1]) # Simple resize, improvement: crop to center
        # Center crop check
        img_clip = img_clip.resize(height=resolution[1])
        if img_clip.w < resolution[0]:
             img_clip = img_clip.resize(width=resolution[0])
        img_clip = img_clip.set_position("center")
            
        # Create Subtitle (using Pillow -> numpy array -> ImageClip)
        # 1080x1920
        # Text bottom area
        txt_img = generate_text_image(subtitle_text, size=resolution, fontsize=70)
        txt_clip = ImageClip(txt_img).set_duration(duration).set_position("center")
        
        # Composite
        video = CompositeVideoClip([img_clip, txt_clip])
        video = video.set_audio(audio)
        video = video.set_duration(duration)
        
        video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)
        return True, output_path
    
    except Exception as e:
        print(f"Error rendering scene: {e}")
        return False, str(e)

def assemble_full_movie(scene_videos, output_path):
    """
    Concatenates rendered scene videos into a final movie.
    """
    try:
        clips = [VideoFileClip(v) for v in scene_videos]
        final_video = concatenate_videoclips(clips)
        final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
        return True, output_path
    except Exception as e:
         return False, str(e)
