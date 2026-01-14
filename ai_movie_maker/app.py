import streamlit as st
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="AI Movie Maker Studio",
    page_icon="🎥",
    layout="wide"
)

st.title("🎥 AI Movie Studio")

st.markdown("""
Welcome to the **AI Movie Studio**. This suite of tools helps you create and edit video content using AI.

### Available Modules:

#### 1. [🎬 Movie Maker](/Movie_Maker)
   - Create AI-generated video scripts from simple ideas.
   - Generate voiceovers, images, and video clips.
   - Assemble full marketing videos automagically.

#### 2. [🎙️ Voice Translator (Content Dubber)](/Voice_Translator) *(Coming Soon)*
   - Extract audio from existing videos.
   - Separate vocals and background music.
   - Translate speech to other languages and re-dub with AI voices.

---
**Usage**: Select a module from the sidebar to get started.
""")

st.sidebar.success("Select a tool above.")
