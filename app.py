import streamlit as st
from utils import run_agent_sync

st.set_page_config(page_title="MCP POC", page_icon="🤖", layout="wide")
st.title("Model Context Protocol(MCP) - Learning Path Generator")

# Session state init
for key in ['current_step', 'progress', 'last_section', 'is_generating']:
    if key not in st.session_state:
        st.session_state[key] = "" if key in ['current_step', 'last_section'] else 0 if key == 'progress' else False

# --- Hardcoded Configuration ---
google_api_key = "AIzaSyBH2roEWbCrBWlLubP0SpOS73gVJAd6M2U"
youtube_pipedream_url = "https://mcp.pipedream.net/862a4968-17da-4a80-bdc4-bfcd3d1704a9/youtube_data_api"
drive_pipedream_url = "https://mcp.pipedream.net/862a4968-17da-4a80-bdc4-bfcd3d1704a9/google_drive"
notion_pipedream_url = None  # Not used

# Guide
st.info("""
**Quick Guide:**
- Your API key and integration URLs are preconfigured.
- Just enter a clear learning goal like:
    - "I want to learn Python basics in 3 days"
    - "I want to learn machine learning in 10 days"
""")

# Goal input
st.header("Enter Your Goal")
user_goal = st.text_input("Enter your learning goal:")

# Progress
progress_container = st.container()
progress_bar = st.empty()

def update_progress(message: str):
    st.session_state.current_step = message
    section = st.session_state.last_section or "Progress"
    if "Setting up agent" in message:
        section, st.session_state.progress = "Setup", 0.1
    elif "Added Google Drive" in message:
        section, st.session_state.progress = "Integration", 0.2
    elif "Creating AI agent" in message:
        section, st.session_state.progress = "Setup", 0.3
    elif "Generating your learning path" in message:
        section, st.session_state.progress = "Generation", 0.5
    elif "Learning path generation complete" in message:
        section, st.session_state.progress = "Complete", 1.0
        st.session_state.is_generating = False

    st.session_state.last_section = section
    progress_bar.progress(st.session_state.progress)

    with progress_container:
        if section != "Complete":
            st.write(f"**{section}**")
        if message == "Learning path generation complete!":
            st.success("All steps completed! 🎉")
        else:
            prefix = "✓" if st.session_state.progress >= 0.5 else "→"
            st.write(f"{prefix} {message}")

# Trigger
if st.button("Generate Learning Path", type="primary", disabled=st.session_state.is_generating):
    if not user_goal:
        st.warning("Please enter your learning goal.")
    else:
        try:
            st.session_state.is_generating = True
            st.session_state.current_step = ""
            st.session_state.progress = 0
            st.session_state.last_section = ""

            result = run_agent_sync(
                google_api_key=google_api_key,
                youtube_pipedream_url=youtube_pipedream_url,
                drive_pipedream_url=drive_pipedream_url,
                notion_pipedream_url=notion_pipedream_url,
                user_goal=user_goal,
                progress_callback=update_progress
            )

            st.header("Your Learning Path")
            if result and "messages" in result:
                for msg in result["messages"]:
                    st.markdown(f"📚 {msg.content}")
            else:
                st.error("No results generated. Try again.")
                st.session_state.is_generating = False
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Please check your API key and service URLs.")
            st.session_state.is_generating = False
