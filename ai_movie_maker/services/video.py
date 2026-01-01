import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip, ColorClip, VideoFileClip, CompositeAudioClip
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

def render_scene_video(image_path, audio_path, subtitle_text, output_path, resolution=(1080, 1920), fontsize=70, color='white', video_clip_path=None):
    """
    Renders a single scene video: Image/Video + Audio + Subtitle.
    Resolution determines aspect ratio (e.g. 1080x1920 for 9:16, 1920x1080 for 16:9).
    """
    try:
        # Load Audio
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        
        # Load Video or Image as Base Clip
        base_clip = None
        
        if video_clip_path and os.path.exists(video_clip_path):
            # Use generated AI video
            # Load video
            raw_video = VideoFileClip(video_clip_path)
            
            # Loop video if shorter than audio, or cut if longer
            if raw_video.duration < duration:
                # Loop
                # Calculate how many times to loop
                # n_loops = int(duration / raw_video.duration) + 1
                base_clip = raw_video.loop(duration=duration)
            else:
                base_clip = raw_video.subclip(0, duration)
                
            # Mute raw video audio if present
            base_clip = base_clip.without_audio()
            
        elif image_path and os.path.exists(image_path):
            base_clip = ImageClip(image_path).set_duration(duration)
        else:
            # Fallback black screen
            base_clip = ColorClip(size=resolution, color=(0,0,0)).set_duration(duration)
            
        # Smart Resize/Crop to fill screen without distortion
        # Same logic for Image or Video
        img_w, img_h = base_clip.size
        # Caluclate target ratios
        target_ratio = resolution[0] / resolution[1]
        img_ratio = img_w / img_h
        
        if img_ratio > target_ratio:
            # Wide: resize by height then center crop width
            base_clip = base_clip.resize(height=resolution[1])
            # Crop center
            req_width = resolution[0]
            current_width = base_clip.w
            x_center = current_width / 2
            base_clip = base_clip.crop(x1=x_center - req_width/2, width=req_width)
        else:
            # Tall: resize by width then center crop height
            base_clip = base_clip.resize(width=resolution[0])
            req_height = resolution[1]
            current_height = base_clip.h
            y_center = current_height / 2
            base_clip = base_clip.crop(y1=y_center - req_height/2, height=req_height)
            
        base_clip = base_clip.set_position("center")
            
        # Create Subtitle (using Pillow -> numpy array -> ImageClip)
        txt_img = generate_text_image(subtitle_text, size=resolution, fontsize=fontsize, color=color)
        txt_clip = ImageClip(txt_img).set_duration(duration).set_position("center")
        
        # Composite
        video = CompositeVideoClip([base_clip, txt_clip])
        video = video.set_audio(audio)
        video = video.set_duration(duration)
        
        # Write file
        video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)
        
        # Close clips to release resources
        if video_clip_path and os.path.exists(video_clip_path):
             # Explicitly close the raw video reader to avoid file locks
             try:
                 raw_video.reader.close()
                 if raw_video.audio: raw_video.audio.reader.close_proc()
             except: pass

        return True, output_path
    
    except Exception as e:
        print(f"Error rendering scene: {e}")
        return False, str(e)

def assemble_full_movie(scene_videos, output_path, bg_music_path=None, transition_duration=0.5):
    """
    Concatenates rendered scene videos into a final movie.
    Adds background music (looped/ducked) and simple crossfade transitions if supported.
    """
    try:
        clips = []
        for v in scene_videos:
            clip = VideoFileClip(v)
            # Add simple fadein/out for smoothness
            clip = clip.fadein(0.2).fadeout(0.2)
            clips.append(clip)
            
        final_video = concatenate_videoclips(clips, method="compose") # compose supports potential overlaps/transitions better
        
        # Background Music
        if bg_music_path and os.path.exists(bg_music_path):
            bg_music = AudioFileClip(bg_music_path)
            # Loop bg_music to match video duration
            if bg_music.duration < final_video.duration:
                 bg_music = bg_music.loop(duration=final_video.duration)
            else:
                 bg_music = bg_music.subclip(0, final_video.duration)
                 
            # Ducking: Bg music should be quieter (e.g. 20%)
            bg_music = bg_music.volumex(0.2)
            
            # Mix with original audio (Voice)
            final_audio = CompositeAudioClip([final_video.audio, bg_music])
            final_video = final_video.set_audio(final_audio)
        
        final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
        return True, output_path
    except Exception as e:
         return False, str(e)
