import os
import replicate
import requests
import time

def generate_video_clip(api_token: str, image_path: str, output_path: str, model_id: str = "stability-ai/stable-video-diffusion:39ed52f2-d819-4729-8e39-39dc33250fb1"):
    """
    Generates a short video clip from an image using Replicate API (Stable Video Diffusion).
    """
    try:
        if not api_token:
            return False, "Missing Replicate API Token"
        
        os.environ["REPLICATE_API_TOKEN"] = api_token
        
        if not os.path.exists(image_path):
             return False, f"Image path not found: {image_path}"

        print(f"Generating video for {image_path}...")
        
        # Open file for upload
        # Replicate python client handles file uploads if passed as file handle
        with open(image_path, "rb") as file_handle:
            output = replicate.run(
                model_id,
                input={
                    "cond_aug": 0.02,
                    "decoding_t": 7,
                    "input_image": file_handle,
                    "video_length": "25_frames_with_svd_xt",
                    "sizing_strategy": "maintain_aspect_ratio",
                    "motion_bucket_id": 127,
                    "frames_per_second": 6
                }
            )
        
        # Output is usually a URI string or list of URIs
        video_url = output
        if isinstance(output, list):
            video_url = output[0]
            
        print(f"Video URL: {video_url}")
        
        # Download video
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return True, output_path
        else:
            return False, f"Failed to download video: {response.status_code}"

    except Exception as e:
        return False, str(e)
