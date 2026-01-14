import streamlit as st
import os
import sys
import tempfile
import time
import yt_dlp
import pandas as pd

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_movie_maker.content_dubber.dubbing_pipeline import DubbingPipeline

st.set_page_config(page_title="Voice Translator", page_icon="🎙️", layout="wide")

st.title("🎙️ AI Voice Translator & Dubber")
st.markdown("Extract speech from video, translate it, and re-dub with AI voices.")

# --- SIDEBAR CONFIG ---
st.sidebar.header("Configuration")

# API Keys
api_key = st.session_state.get('api_key_confirmed')
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    st.sidebar.success("✅ API Key Loaded")
else:
    st.sidebar.warning("⚠️ Missing Gemini API Key")

st.sidebar.divider()
st.sidebar.markdown("### Settings")

target_language = st.sidebar.selectbox(
    "Target Language", 
    ["Vietnamese", "English", "Spanish", "French", "German", "Japanese", "Korean", "Chinese"]
)

# Simple voice mapping for demo (Expand this later with a proper config)
voice_options = {
    "Vietnamese (Female - HoaiMy)": "vi-VN-HoaiMyNeural",
    "Vietnamese (Male - NamMinh)": "vi-VN-NamMinhNeural",
    "English (Female - Jenny)": "en-US-JennyNeural",
    "English (Male - Guy)": "en-US-GuyNeural",
    "Japanese (Female - Nanami)": "ja-JP-NanamiNeural",
    "Korean (Female - SunHi)": "ko-KR-SunHiNeural"
}

selected_voice_label = st.sidebar.selectbox("AI Voice", list(voice_options.keys()))
selected_voice_id = voice_options[selected_voice_label]

st.sidebar.info("Note: First step extracts audio using Demucs. Second step translates and dubs.")

# --- HELPER FUNCTIONS ---
def download_video_from_url(url, output_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

# --- SESSION STATE ---
if "dubbing_step" not in st.session_state:
    st.session_state.dubbing_step = 1
if "dubbing_context" not in st.session_state:
    st.session_state.dubbing_context = None

# --- MAIN UI ---

# STEP 1: INPUT & ANALYSIS
if st.session_state.dubbing_step == 1:
    st.header("Step 1: Input Video")
    
    tab_upload, tab_url = st.tabs(["📤 Upload File", "🔗 Video URL"])
    
    input_video_path = None
    original_name = "video"
    
    with tab_upload:
        uploaded_video = st.file_uploader("Upload Video (mp4, mov, mkv)", type=["mp4", "mov", "mkv"])
        if uploaded_video:
            st.video(uploaded_video)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
                tmp_in.write(uploaded_video.getbuffer())
                input_video_path = tmp_in.name
            original_name = uploaded_video.name
            st.session_state.temp_input_path = input_video_path
            st.session_state.original_name = original_name

    with tab_url:
        video_url = st.text_input("Paste Video URL (YouTube, etc.)")
        if video_url:
             st.info("Video will be downloaded for analysis.")
    
    st.divider()
    
    if st.button("� Analyze & Extract Text", type="primary"):
        if not api_key:
            st.error("Please provide Gemini API Key first.")
            st.stop()
            
        process_path = st.session_state.get('temp_input_path')
        
        # Handle URL download
        if not process_path and video_url:
            with st.spinner("Downloading video from URL..."):
                try:
                    fd, tmp_download_path = tempfile.mkstemp(suffix=".mp4")
                    os.close(fd)
                    download_video_from_url(video_url, tmp_download_path)
                    process_path = tmp_download_path
                    st.session_state.temp_input_path = process_path
                    st.session_state.original_name = "downloaded_video.mp4"
                except Exception as e:
                    st.error(f"Download failed: {e}")
                    st.stop()
        
        if not process_path or not os.path.exists(process_path):
            st.error("Please provide a valid video.")
            st.stop()
            
        # Run Pipeline Phase 1
        pipeline = DubbingPipeline(gemini_api_key=api_key)
        
        try:
            with st.spinner("Extracting audio, separating vocals, and transcribing..."):
                context = pipeline.extract_and_transcribe(process_path)
                st.session_state.dubbing_context = context
                st.session_state.dubbing_step = 2
                st.rerun()
        except Exception as e:
             st.error(f"Analysis failed: {e}")


# STEP 2: REVIEW & DUB
elif st.session_state.dubbing_step == 2:
    st.header("Step 2: Review & Dub")
    
    context = st.session_state.dubbing_context
    segments = context["segments"] # List of dicts {start, end, text}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Transcript (Read-only)")
        if segments:
            full_text = "\n".join([s['text'] for s in segments])
            st.text_area("Extracted Text", value=full_text, height=400, disabled=True)
        else:
            st.warning("No speech detected.")

    with col2:
        st.subheader("Subtitle Editor (Editable)")
        st.caption("Edit the text below to correct the transcript before dubbing.")
        
        if segments:
            # Convert to DataFrame for easier editing
            df = pd.DataFrame(segments)
            # Reorder columns
            df = df[['start', 'end', 'text']]
            
            edited_df = st.data_editor(
                df, 
                num_rows="dynamic",
                height=400,
                key="subtitle_editor",
                use_container_width=True
            )
        else:
            st.info("No content to edit.")
            edited_df = pd.DataFrame()

    st.divider()
    
    col_back, col_go = st.columns([1, 4])
    
    with col_back:
        if st.button("⬅️ Restart"):
            st.session_state.dubbing_step = 1
            st.session_state.dubbing_context = None
            st.rerun()
            
    with col_go:
        if st.button("🎬 Translate & Dub Video", type="primary"):
            # Update segments from editor
            if not edited_df.empty:
                # Convert back to list of dicts
                updated_segments = edited_df.to_dict('records')
                context["segments"] = updated_segments
            
            pipeline = DubbingPipeline(gemini_api_key=api_key)
            
            output_filename = f"dubbed_{st.session_state.original_name}"
            # Save to project output dir if possible, else temp
            output_dir = os.path.dirname(context['video_path'])
            output_path = os.path.join(output_dir, output_filename)
            
            try:
                with st.spinner("Translating, Synthesizing, and Mixing..."):
                    final_path = pipeline.generate_video_from_segments(
                        context, 
                        target_language, 
                        output_path, 
                        selected_voice_id
                    )
                
                st.success("Dubbing Complete!")
                st.video(final_path)
                
                with open(final_path, "rb") as f:
                    st.download_button(
                        label="Download Final Video",
                        data=f,
                        file_name=output_filename,
                        mime="video/mp4"
                    )
                    
            except Exception as e:
                st.error(f"Dubbing failed: {e}")
