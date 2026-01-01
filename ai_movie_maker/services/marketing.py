from google.genai import types
import time
import random
from pydantic import BaseModel
from typing import List

class HookList(BaseModel):
    hooks: List[str]

class CTAList(BaseModel):
    ctas: List[str]

class VariationItem(BaseModel):
    name: str
    script: dict # flexible to hold either V31 or V32 dict structure

class VariationList(BaseModel):
    variations: List[VariationItem]

def retry_api_call(func, *args, **kwargs):
    max_retries = 5
    base_delay = 2
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                if attempt == max_retries - 1:
                    raise e
                sleep_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit hit. Retrying in {sleep_time:.2f}s...")
                time.sleep(sleep_time)
            else:
                raise e

def generate_hooks(client, model_name, platform, must_avoid_csv):
    """
    Generates 5 hooks for the first scene.
    """
    prompt = f"""
Generate 5 HOOK lines in Vietnamese only (6–10 words each),
for a short-form ad on {platform}.

Constraints:
- No emojis, no English words.
- Strong curiosity/pain point.
- Avoid: {must_avoid_csv}

Return ONLY JSON:
{{"hooks":[...]}}.
"""
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=HookList,
    )
    
    try:
        resp = retry_api_call(
            client.models.generate_content,
            model=model_name,
            contents=prompt,
            config=config,
        )
        return resp.parsed.hooks
    except Exception as e:
        print(f"Error generating hooks: {e}")
        return []

def generate_ctas(client, model_name, platform, brand_voice):
    """
    Generates 10 CTA options.
    """
    prompt = f"""
Generate 10 CTA lines in Vietnamese only (max 8 words each)
for {platform}, brand voice: {brand_voice}.

Return ONLY JSON:
{{"ctas":[...]}}.
"""
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=CTAList,
    )
    
    try:
        resp = retry_api_call(
            client.models.generate_content,
            model=model_name,
            contents=prompt,
            config=config,
        )
        return resp.parsed.ctas
    except Exception as e:
        print(f"Error generating CTAs: {e}")
        return []

def generate_variations(client, model_name, current_script_obj, schema_version="v3.2"):
    """
    Generates 3 variations (A, B, C) of the script.
    """
    current_json = current_script_obj.model_dump_json(indent=2)
    
    prompt = f"""
Create 3 variations of the same script.
Return ONLY JSON with this schema:

{{
  "variations": [
    {{"name":"A","script":{{...}}}},
    {{"name":"B","script":{{...}}}},
    {{"name":"C","script":{{...}}}}
  ]
}}

Rules:
- Keep campaign + global_style consistent.
- Each script must follow the same schema version: {schema_version}.
- A changes hook; B changes ending; C changes CTA.
- Vietnamese-only dialogue.

Ref Script:
<<<
{current_json}
>>>
"""
    # Note: VariationList script field is generic dict because we might have V32 or V31
    #Ideally we would use the specific schema, but for A/B container, generic dict is safer for parsing the container first.
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=VariationList,
    )
    
    try:
        resp = retry_api_call(
            client.models.generate_content,
            model=model_name,
            contents=prompt,
            config=config,
        )
        return resp.parsed.variations
    except Exception as e:
        print(f"Error generating variations: {e}")
        return []
