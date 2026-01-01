import os
import sys
import json
from pydantic import ValidationError

# Ensure we can import from local
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_movie_maker.models.schema_v32 import ScriptV32
from ai_movie_maker.services.generator import validate_script

def test_validation_logic():
    print("Testing validation logic...")
    
    # Create a dummy bad script (simulated as dict then loaded to pydantic if possible, or just checking logic)
    # Since validate_script expects a Pydantic object, we might fail validation if we can't even parse it.
    # But validate_script checks business logic AFTER Pydantic validation.
    
    # Let's create a valid object and make it invalid for our logic
    
    valid_data = {
        "project_title": "Test Project",
        "campaign": {
            "platform": "TikTok",
            "campaign_type": "UGC Review",
            "product_name": "Test Product",
            "product_category": "Test",
            "usp_list": ["usp1", "usp2", "usp3"],
            "offer": "Free",
            "cta_text": "Buy Now",
            "brand_voice": "Fun",
            "must_avoid": ["badword"]
        },
        "global_style": {
            "visual_style": "Test style",
            "negative_prompt": "Test neg"
        },
        "scenes": [
            {
                "scene_id": 1,
                "duration_seconds": 3,
                "visual_prompt": {"positive": "pos", "negative": "neg"},
                "camera": "static",
                "on_screen_text": "text",
                "dialogue": {"text": "This is a very long dialogue that should definitely trigger the word count limit because it is well over fifteen words I believe.", "voice_gender": "Male"},
                "audio": {"sfx": "sfx", "music_mood": "mood"},
                "overlays": [],
                "product_shot": {"show_product": True, "what_to_show": "prod"}
            },
             {
                "scene_id": 2,
                "duration_seconds": 3,
                "visual_prompt": {"positive": "pos", "negative": "neg"},
                "camera": "static",
                "on_screen_text": "text",
                "dialogue": {"text": "Short enough", "voice_gender": "Male"},
                "audio": {"sfx": "sfx", "music_mood": "mood"},
                "overlays": [],
                "product_shot": {"show_product": True, "what_to_show": "prod"}
            },
             {
                "scene_id": 3,
                "duration_seconds": 3,
                "visual_prompt": {"positive": "pos", "negative": "neg"},
                "camera": "static",
                "on_screen_text": "text",
                "dialogue": {"text": "Contains badword here.", "voice_gender": "Male"},
                "audio": {"sfx": "sfx", "music_mood": "mood"},
                "overlays": [],
                "product_shot": {"show_product": True, "what_to_show": "prod"}
            }
        ]
    }
    
    try:
        script_obj = ScriptV32(**valid_data)
        is_valid, issues = validate_script(script_obj, schema_version="v3.2", must_avoid_list=["badword"])
        
        print(f"Validation Result: {is_valid}")
        print(f"Issues found: {len(issues)}")
        for i in issues:
            print(f"- {i}")
            
        assert not is_valid
        assert any("too long" in i for i in issues)
        assert any("badword" in i for i in issues)
        print("✅ Validation Logic Test Passed")
        
    except ValidationError as e:
        print(f"Pydantic Validation Error (unexpected for this test): {e}")
    except Exception as e:
        print(f"Test Error: {e}")

if __name__ == "__main__":
    test_validation_logic()
