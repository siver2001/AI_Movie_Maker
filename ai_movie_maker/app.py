import streamlit as st
import json
import os
from google import genai
from dotenv import load_dotenv

# Import our modules
# Assuming running from the root of the workspace or module installed
# We will use relative imports if possible or absolute if running as script
# We will use relative imports if possible or absolute if running as script
try:
    from ai_movie_maker.templates.prompts_v32 import USER_WRAPPER_V32
    from ai_movie_maker.templates.prompts_v31 import USER_WRAPPER_V31
    from ai_movie_maker.services.generator import (
        generate_script, validate_script, repair_script, regenerate_scene
    )
    from ai_movie_maker.services.marketing import (
        generate_hooks, generate_ctas, generate_variations
    )
    from ai_movie_maker.services.audio import generate_audio_sync
    # Load presets
    with open(os.path.join(os.path.dirname(__file__), 'config/presets.json'), 'r', encoding='utf-8') as f:
        PRESETS = json.load(f)
except ImportError:
    # Fallback for when running directly inside the folder without package structure
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ai_movie_maker.templates.prompts_v32 import USER_WRAPPER_V32
    from ai_movie_maker.templates.prompts_v31 import USER_WRAPPER_V31
    from ai_movie_maker.services.generator import (
        generate_script, validate_script, repair_script, regenerate_scene
    )
    from ai_movie_maker.services.marketing import (
        generate_hooks, generate_ctas, generate_variations
    )
    from ai_movie_maker.services.audio import generate_audio_sync
    with open('ai_movie_maker/config/presets.json', 'r', encoding='utf-8') as f:
        PRESETS = json.load(f)

# Page Config
st.set_page_config(page_title="AI Movie Maker v3.2", layout="wide", page_icon="🎬")

# Title & Intro
st.title("🎬 AI Movie Maker v3.2 — Ad-Ready Edition")
st.markdown("Dynamic Config + Campaign Mode + Hook/CTA Lab + Auto-Repair")

# --- SIDEBAR CONFIG ---
st.sidebar.header("1. Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
model_name = st.sidebar.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"], index=0)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
max_tokens = st.sidebar.number_input("Max Tokens", 1000, 10000, 8192)

st.sidebar.header("2. Script Controls")
scene_count = st.sidebar.slider("Scene Count", 3, 5, 3)
mood = st.sidebar.selectbox("Mood", ["Cinematic Drama", "High Energy", "Funny", "Emotional", "Horror"])
ending_style = st.sidebar.selectbox("Ending Style", ["Twist", "Call to Action", "Cliffhanger", "Happy Ending", "Emotional pay-off"])
dialect_hint = st.sidebar.selectbox("Dialect", ["Neutral", "Southern casual", "Northern subtle", "Central"])
visual_theme_key = st.sidebar.selectbox("Visual Theme Preset", ["Custom"] + list(PRESETS["visual_styles"].keys()))

if visual_theme_key == "Custom":
    visual_theme = st.sidebar.text_area("Custom Visual Theme", "cinematic, 8k, highly detailed")
else:
    visual_theme = PRESETS["visual_styles"][visual_theme_key]
    st.sidebar.caption(f"Theme: {visual_theme}")

# --- MAIN UI ---
st.subheader("3. Input & Campaign Mode")

col1, col2 = st.columns([1, 1])

with col1:
    user_input_raw = st.text_area("Your Idea / Plot / Product", height=200, placeholder="Describe your ad idea or product here...")
    user_character_name = st.text_input("Main Character Name", "N/A")
    user_seed = st.number_input("Seed (Optional, for reproducibility)", value=0, min_value=0)

with col2:
    schema_version = st.radio("Schema Version", ["v3.2 (Ad-Ready)", "v3.1 (Legacy)"], horizontal=True)
    
    # Export / Import Tools
    with st.expander("💾 Load / Save Project"):
        uploaded_file = st.file_uploader("Load JSON Script", type=["json"])
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                # Simple validation - checking if 'scenes' exists
                if "scenes" in data:
                    # We reload it into Pydantic models to ensure validity
                    if schema_version.startswith("v3.2"):
                        from ai_movie_maker.models.schema_v32 import ScriptV32
                        st.session_state['current_script'] = ScriptV32(**data)
                        st.session_state['schema_version'] = "v3.2"
                    else:
                        from ai_movie_maker.models.schema_v31 import ScriptV31
                        st.session_state['current_script'] = ScriptV31(**data)
                        st.session_state['schema_version'] = "v3.1"
                    st.success("Script loaded!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error loading file: {e}")

    # Campaign Mode UI only active if v3.2
    campaign_data = {}
    if schema_version == "v3.2 (Ad-Ready)":
        enable_campaign = st.checkbox("Enable Campaign Mode", value=True)
        if enable_campaign:
            with st.expander("Campaign Details", expanded=True):
                c_platform = st.selectbox("Platform", PRESETS["platforms"])
                c_type = st.selectbox("Campaign Type", PRESETS["campaign_types"])
                c_product = st.text_input("Product Name")
                c_category = st.text_input("Category")
                c_usp1 = st.text_input("USP 1")
                c_usp2 = st.text_input("USP 2")
                c_usp3 = st.text_input("USP 3")
                c_offer = st.text_input("Offer (Optional)")
                
                # CTA Tools
                c_col_cta, c_col_btn = st.columns([3, 1])
                with c_col_cta:
                    c_cta_text = st.text_input("CTA Text")
                with c_col_btn:
                    if st.button("Generate CTAs"):
                        if not api_key:
                            st.error("Need API Key")
                        else:
                            client = genai.Client(api_key=api_key)
                            ctas = generate_ctas(client, model_name, c_platform, "General")
                            st.session_state['generated_ctas'] = ctas
                
                if 'generated_ctas' in st.session_state and st.session_state['generated_ctas']:
                    selected_cta = st.selectbox("Select Generated CTA", st.session_state['generated_ctas'])
                    if st.button("Use this CTA"):
                        c_cta_text = selected_cta 
                
                c_voice = st.selectbox("Brand Voice", list(PRESETS["brand_voices"].keys()))
                c_voice_desc = PRESETS["brand_voices"][c_voice]
                c_must_avoid = st.text_area("Must Avoid (CSV)", "cam kết 100%, lừa đảo, chữa khỏi")
                
                campaign_data = {
                    "platform": c_platform,
                    "campaign_type": c_type,
                    "product_name": c_product,
                    "product_category": c_category,
                    "usp_1": c_usp1,
                    "usp_2": c_usp2,
                    "usp_3": c_usp3,
                    "offer": c_offer,
                    "cta_text": c_cta_text,
                    "brand_voice": c_voice_desc,
                    "must_avoid_csv": c_must_avoid
                }

# --- GENERATE TABS ---
tab_main, tab_hook, tab_variations = st.tabs(["Main Generator", "Hook Lab", "A/B Variations"])

with tab_hook:
    st.header("Hook Lab")
    if st.button("Generate 5 Hooks"):
        if not api_key:
            st.error("Please enter Gemini API Key")
        else:
            client = genai.Client(api_key=api_key)
            # Default to TikTok if not set
            p = campaign_data.get("platform", "TikTok")
            avoid = campaign_data.get("must_avoid_csv", "")
            hooks = generate_hooks(client, model_name, p, avoid)
            for h in hooks:
                st.code(h, language="text")

with tab_variations:
    st.header("A/B Variations")
    st.info("Generate a main script first, then you can create variations here.")
    if st.button("Generate Variations (A/B/C)"):
        if 'current_script' not in st.session_state:
            st.error("No script generated yet.")
        elif not api_key:
            st.error("Need API Key")
        else:
            client = genai.Client(api_key=api_key)
            variations = generate_variations(client, model_name, st.session_state['current_script'], schema_version="v3.2")
            for v in variations:
                with st.expander(f"Variation {v.name}"):
                    st.json(v.script)

with tab_main:
    # Prompt Preview feature
    with st.expander("👁 Preview Prompt (Debug)"):
        if schema_version == "v3.2 (Ad-Ready)":
             preview_wrapper = USER_WRAPPER_V32
             # Mock data for preview if empty
             p_campaign_data = campaign_data if campaign_data else {k: "N/A" for k in ["platform", "campaign_type", "product_name", "product_category", "offer", "cta_text", "must_avoid_csv"]}
             if not campaign_data:
                p_campaign_data["usp_1"] = "N/A"; p_campaign_data["usp_2"] = "N/A"; p_campaign_data["usp_3"] = "N/A"; p_campaign_data["brand_voice"] = "Cinematic"
             
             try:
                 st.code(preview_wrapper.format(
                    user_input_raw=user_input_raw if user_input_raw else "[User Input]",
                    scene_count=scene_count,
                    mood=mood,
                    user_character_name=user_character_name,
                    dialect_hint=dialect_hint,
                    ending_style=ending_style,
                    visual_theme=visual_theme,
                    **p_campaign_data
                ))
             except:
                 st.caption("Fill in all fields to preview.")
        else:
             st.code(USER_WRAPPER_V31)

    generate_btn = st.button("GENERATE SCRIPT", type="primary", use_container_width=True)
    
    if generate_btn:
        if not api_key:
            st.error("Please enter Gemini API Key in the sidebar.")
        elif not user_input_raw:
            st.warning("Please enter your idea/plot.")
        else:
            client = genai.Client(api_key=api_key)
            
            # Prepare Prompt
            if schema_version == "v3.2 (Ad-Ready)":
                sv_code = "v3.2"
                wrapper = USER_WRAPPER_V32
                if not campaign_data:
                    campaign_data = {k: "N/A" for k in ["platform", "campaign_type", "product_name", "product_category", "offer", "cta_text", "must_avoid_csv"]}
                    campaign_data["usp_1"] = "N/A"
                    campaign_data["usp_2"] = "N/A"
                    campaign_data["usp_3"] = "N/A"
                    campaign_data["brand_voice"] = "Cinematic"

                final_prompt = wrapper.format(
                    user_input_raw=user_input_raw,
                    scene_count=scene_count,
                    mood=mood,
                    user_character_name=user_character_name,
                    dialect_hint=dialect_hint,
                    ending_style=ending_style,
                    visual_theme=visual_theme,
                    **campaign_data
                )
            else:
                sv_code = "v3.1"
                wrapper = USER_WRAPPER_V31
                final_prompt = wrapper.format(
                    user_input_raw=user_input_raw,
                    scene_count=scene_count,
                    mood=mood,
                    user_character_name=user_character_name,
                    dialect_hint=dialect_hint,
                    ending_style=ending_style,
                    visual_theme=visual_theme
                )

            with st.spinner("Generating script..."):
                # We are passing the user_seed if > 0, though we didn't firmly implement it in gen.py yet as API might vary.
                # But we have the input now.
                script_obj = generate_script(client, model_name, final_prompt, temperature, max_tokens, sv_code)
                
                if script_obj:
                    # Validate
                    must_avoid = []
                    if sv_code == "v3.2" and campaign_data.get("must_avoid_csv"):
                         must_avoid = campaign_data.get("must_avoid_csv").split(",")
                         
                    is_valid, issues = validate_script(script_obj, sv_code, must_avoid)
                    
                    if not is_valid:
                        st.warning(f"Validation Issues Found: {len(issues)} issues. Auto-repairing...")
                        for i in issues:
                            st.caption(f"- {i}")
                        
                        script_obj = repair_script(client, model_name, script_obj, issues, sv_code)
                        st.success("Auto-repair completed.")
                    
                    st.session_state['current_script'] = script_obj
                    st.session_state['schema_version'] = sv_code
                else:
                    st.error("Failed to generate script.")

    # Display Result
    if 'current_script' in st.session_state:
        script = st.session_state['current_script']
        sv = st.session_state['schema_version']
        
        st.divider()
        c_title, c_dl = st.columns([4, 1])
        with c_title:
             st.subheader(f"Project: {script.project_title}")
        with c_dl:
            # Download Button
            json_str = script.model_dump_json(indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"script_{script.project_title}.json",
                mime="application/json"
            )
        
        # Display each scene
        for i, scene in enumerate(script.scenes):
            with st.container(border=True):
                c1, c2 = st.columns([1, 4])
                with c1:
                    st.markdown(f"**Scene {scene.scene_id}**")
                    st.caption(f"{scene.duration_seconds}s")
                    if st.button(f"Regenerate Scene {scene.scene_id}", key=f"regen_{i}"):
                        if not api_key:
                            st.error("No API key")
                        else:
                            client = genai.Client(api_key=api_key)
                            new_script = regenerate_scene(client, model_name, script, scene.scene_id, sv)
                            if new_script:
                                st.session_state['current_script'] = new_script
                                st.rerun()
                
                with c2:
                    st.markdown(f"**Visual:** {scene.visual_prompt.positive}")
                    st.markdown(f"**Audio:** {scene.audio.sfx} | {scene.audio.music_mood}")
                    st.info(f"🗣 **{scene.dialogue.voice_gender}:** {scene.dialogue.text}")
                    
                    # Audio Generation UI
                    from ai_movie_maker.services.audio import VOICE_MAP
                    default_voice = "Male - Default" if "Male" in scene.dialogue.voice_gender else "Female - Default"
                    
                    # Allow user to pick specific character voice variant
                    voice_choice = st.selectbox(
                        "Voice/Style", 
                        options=list(VOICE_MAP.keys()), 
                        index=list(VOICE_MAP.keys()).index(default_voice) if default_voice in VOICE_MAP else 0,
                        key=f"v_select_{i}"
                    )
                    
                    audio_key = f"audio_{scene.scene_id}_{i}"
                    if st.button(f"🎵 Generate Audio", key=f"btn_audio_{i}"):
                        with st.spinner("Generating audio..."):
                            # Create temp file path
                            temp_audio_path = f"audio_scene_{scene.scene_id}.mp3"
                            success = generate_audio_sync(scene.dialogue.text, voice_choice, temp_audio_path)
                            if success:
                                st.audio(temp_audio_path)
                            else:
                                st.error("Audio generation failed.")
                    
                    if sv == "v3.2":
                        if hasattr(scene, 'overlays') and scene.overlays:
                             st.markdown("**Overlays:**")
                             for o in scene.overlays:
                                 st.caption(f"[{o.start_sec}-{o.end_sec}s] {o.text} ({o.position})")
                        if hasattr(scene, 'camera'):
                            st.caption(f"Camera: {scene.camera}")

                    # --- MEDIA & RENDERING ---
                    st.divider()
                    m1, m2 = st.columns([1, 1])
                    
                    with m1:
                        # Image Upload
                        img_key = f"img_{scene.scene_id}_{i}"
                        uploaded_img = st.file_uploader(f"🖼 Image for Scene {scene.scene_id}", type=["jpg", "png"], key=img_key)
                        
                        # Use session state to store image path if uploaded
                        if uploaded_img:
                            # Save temp
                            img_path = f"img_scene_{scene.scene_id}.png"
                            with open(img_path, "wb") as f:
                                f.write(uploaded_img.getbuffer())
                            st.image(img_path, width=200)
                    
                    with m2:
                        # Render Scene Button
                        if st.button(f"🎬 Render Scene {scene.scene_id}", key=f"render_{i}"):
                            # Check inputs
                            audio_path = f"audio_scene_{scene.scene_id}.mp3"
                            if not os.path.exists(audio_path):
                                st.error("Please generate audio first!")
                            else:
                                img_path = f"img_scene_{scene.scene_id}.png"
                                if not os.path.exists(img_path):
                                     st.warning("No image uploaded, using black background.")
                                     img_path = None # service handles None
                                
                                output_video = f"scene_{scene.scene_id}.mp4"
                                with st.spinner("Rendering video..."):
                                    # Assuming import is available
                                    # We need to import inside or top. Let's do lazy import or assume top.
                                    # We added import to app.py? Not yet.
                                    from ai_movie_maker.services.video import render_scene_video
                                    success, res = render_scene_video(img_path, audio_path, scene.dialogue.text, output_video)
                                    if success:
                                        st.video(output_video)
                                    else:
                                        st.error(f"Render failed: {res}")
        
        st.divider()
        if st.button("🎞 Render Full Movie", type="primary"):
             # Check if all scenes have videos
             videos = []
             all_ready = True
             for s in script.scenes:
                 v_path = f"scene_{s.scene_id}.mp4"
                 if not os.path.exists(v_path):
                     st.error(f"Scene {s.scene_id} video not rendered yet.")
                     all_ready = False
                 else:
                     videos.append(v_path)
             
             if all_ready:
                 with st.spinner("Assembling Full Movie..."):
                     from ai_movie_maker.services.video import assemble_full_movie
                     final_out = f"final_movie_{script.project_title.replace(' ', '_')}.mp4"
                     success, msg = assemble_full_movie(videos, final_out)
                     if success:
                         st.success("Movie Rendered Successfully!")
                         st.video(final_out)
                         with open(final_out, "rb") as f:
                             st.download_button("Download Movie", f, file_name=final_out)
                     else:
                         st.error(f"Assembly failed: {msg}")
             
        with st.expander("View Raw JSON"):
            st.json(script.model_dump())
