import os
import json
from google import genai
from google.genai import types

class TextTranslator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: Gemini API Key not found. Translator will fail unless key is provided.")
        else:
            self.client = genai.Client(api_key=self.api_key)

    def translate_segments(self, segments: list, target_language: str) -> list:
        """
        Translates a list of text segments to the target language using Gemini.
        Returns a JSON-structured list to maintain mapping.
        """
        if not self.client:
            raise RuntimeError("Gemini Client not initialized. Missing API Key.")

        # Prepare payload
        text_list = [seg['text'] for seg in segments]
        
        prompt = f"""
        You are a professional subtitle translator. Translate the following list of dialogue segments into {target_language}.
        Maintain the conversational tone and context.
        
        Input list:
        {json.dumps(text_list, ensure_ascii=False)}
        
        Return ONLY a JSON array of strings matching the input order. No markdown formatting.
        Example output: ["Hello", "How are you?"]
        """
        
        try:
            print(f"Translating {len(segments)} segments to {target_language}...")
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp', # Or use a variable model name
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            translated_texts = json.loads(response.text)
            
            if len(translated_texts) != len(segments):
                print(f"Warning: Segment count mismatch (Input: {len(segments)}, Output: {len(translated_texts)}).")
                # Handle mismatch strategy if needed
            
            # Update segments
            translated_segments = []
            for i, seg in enumerate(segments):
                new_seg = seg.copy()
                if i < len(translated_texts):
                    new_seg['text'] = translated_texts[i]
                translated_segments.append(new_seg)
                
            return translated_segments
            
        except Exception as e:
            raise RuntimeError(f"Translation failed: {str(e)}")
