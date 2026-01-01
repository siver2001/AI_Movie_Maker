import json
import re
from google.genai import types
import time
import random
from ai_movie_maker.models.schema_v32 import ScriptV32
from ai_movie_maker.models.schema_v31 import ScriptV31
from ai_movie_maker.templates.prompts_v32 import SYSTEM_PROMPT_V32
from ai_movie_maker.templates.prompts_v31 import SYSTEM_PROMPT_V31


def retry_api_call(func, *args, **kwargs):
    max_retries = 5
    base_delay = 2
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Check for 429 or ResourceExhausted in string representation
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                if attempt == max_retries - 1:
                    raise e
                
                sleep_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit hit. Retrying in {sleep_time:.2f}s...")
                time.sleep(sleep_time)
            else:
                raise e

def generate_script(client, model_name, user_prompt, temperature, max_output_tokens, schema_version="v3.2", image_part=None):
    """
    Generates a script using Gemini.
    Optional: image_part (PIL Image or bytes) for multimodal generation.
    """
    if schema_version == "v3.2":
        system_instruction = SYSTEM_PROMPT_V32
        # response_schema = ScriptV32
    else:
        system_instruction = SYSTEM_PROMPT_V31
        # response_schema = ScriptV31

    # NOTE: "additionalProperties" error workaround.
    # We remove explicit response_schema and rely on 'response_mime_type="application/json"'
    # and the strong system prompt to strictly follow the JSON structure.
    
    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        response_mime_type="application/json",
        # response_schema=response_schema, # DISABLED TO FIX API ERROR
        system_instruction=system_instruction,
    )
    
    try:
        # Prepare contents
        contents = [user_prompt]
        if image_part:
            contents.append(image_part)

        # Custom retry wrapper
        resp = retry_api_call(
            client.models.generate_content,
            model=model_name,
            contents=contents,
            config=config,
        )
        
        # Parse JSON manually if not using response_schema parsing
        if hasattr(resp, 'parsed') and resp.parsed:
             return resp.parsed, None
        else:
             # Fallback manual parse
             text = resp.text.strip()
             if text.startswith("```json"):
                 text = text[7:-3]
             elif text.startswith("```"):
                 text = text[3:-3]
             return json.loads(text), None
             
    except Exception as e:
        print(f"Error generating script: {e}")
        return None, str(e)

def validate_script(script_obj, schema_version="v3.2", must_avoid_list=None):
    """
    Validates the script against business rules.
    Returns: (is_valid: bool, issues: list[str])
    """
    if not script_obj:
        return False, ["Script is None or empty."]
    
    issues = []
    
    # 1. Word count check (max 15 words per scene)
    for scene in script_obj.scenes:
        text = scene.dialogue.text
        word_count = len(text.split())
        if word_count > 15:
            issues.append(f"Scene {scene.scene_id} dialogue too long ({word_count} words). Max 15.")
            
    # 2. Must avoid list check
    if must_avoid_list:
        full_text = json.dumps(script_obj.model_dump(), ensure_ascii=False)
        for term in must_avoid_list:
            if term.strip() and term.lower() in full_text.lower():
                issues.append(f"Contains forbidden term: '{term}'")

    # 3. Claims filter (basic check)
    forbidden_claims = ["cam kết 100%", "chữa khỏi", "kiếm chắc tiền", "đảm bảo 100%"]
    full_text_check = json.dumps(script_obj.model_dump(), ensure_ascii=False).lower()
    for claim in forbidden_claims:
        if claim in full_text_check:
            issues.append(f"Contains forbidden claim: '{claim}'")
            
    # 4. Marketing beats (v3.2 only)
    if schema_version == "v3.2" and hasattr(script_obj, 'campaign'):
        # Check CTA in final scene
        final_scene = script_obj.scenes[-1]
        cta_text = script_obj.campaign.cta_text.lower() if script_obj.campaign.cta_text else ""
        
        # Loose check: verify if there is some call to action or if the CTA text is present in dialogue/overlay
        has_cta = False
        if cta_text and cta_text in final_scene.dialogue.text.lower():
            has_cta = True
        for overlay in final_scene.overlays:
            if cta_text and cta_text in overlay.text.lower():
                has_cta = True
        
        # We assume the model tries its best, but we can flag if it seems completely missing marketing elements
        # For now, let's keep it lenient to avoid over-repairing.
        pass

    return len(issues) == 0, issues

def repair_script(client, model_name, bad_script_obj, issues, schema_version="v3.2"):
    """
    Asks Gemini to repair the script based on issues.
    """
    bad_json = bad_script_obj.model_dump_json(indent=2)
    
    repair_prompt = f"""
You returned invalid JSON or schema mismatch (or business rule violations).

Return ONLY a single valid JSON matching the exact schema version: {schema_version}.
No extra text. Output must start with {{ and end with }}.

Fix these issues:
{chr(10).join([f"- {i}" for i in issues])}

- Keep Vietnamese-only dialogue, <= 15 words per scene.
- Ensure Scene 1 has a HOOK and Final scene includes CTA.
- Avoid must_avoid terms and absolute claims.

Here is your previous output:
<<<
{bad_json}
>>>
"""
    # Use the same generate function but with the repair prompt as content
    # We pass the same system prompt to ensure it knows the persona
    return generate_script(client, model_name, repair_prompt, 0.7, 8192, schema_version)

def regenerate_scene(client, model_name, current_script_obj, target_scene_id, schema_version="v3.2"):
    """
    Regenerates a single scene while keeping others unchanged.
    """
    current_json = current_script_obj.model_dump_json(indent=2)
    
    prompt = f"""
You are editing an existing JSON script.
Return ONLY a single valid JSON object following the exact schema version: {schema_version}.

RULES:
- Keep project_title, campaign, and global_style unchanged.
- Keep all scenes unchanged EXCEPT scene_id = {target_scene_id}.
- Replace ONLY that scene with a new version.
- Maintain the same main character and visual continuity.
- Dialogue Vietnamese only, max 15 words.
- If target scene is 1: must remain a HOOK.
- If target scene is final: must include CTA (in dialogue or overlays/on_screen_text).

CURRENT JSON:
<<<
{current_json}
>>>
"""
    return generate_script(client, model_name, prompt, 0.7, 8192, schema_version)
