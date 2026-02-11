import streamlit as st
import requests
import os
import time

# 1. Improved Config
# When running in Docker, the UI talks to the API via localhost
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Skylark Drone Manager", 
    page_icon="🚁",
    layout="wide" # Use wide layout for better data viewing
)

# Custom Styling for a cleaner look
st.markdown("""
    <style>
    .stChatMessage { border-radius: 10px; margin-bottom: 10px; }
    .stSpinner { text-align: center; }
    </style>
    """, unsafe_allow_resolve_html=True)

st.title("🚁 Drone Fleet AI Manager")
st.caption("Strategic Pilot Assignment & Mission Conflict Detection System")

# 2. Check Backend Health
def check_backend():
    try:
        # We assume the root or /chat exists
        response = requests.get(API_URL.replace("/chat", ""), timeout=2)
        return True
    except:
        return False

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Chat Input Logic
if prompt := st.chat_input("Ask about pilots, drones, or mission assignments..."):
    # Display user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Consulting Fleet Database..."):
            try:
                # Ensure timeout is long enough for AI tool execution (Google Sheets can be slow)
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"message": prompt},
                    timeout=60 
                )
                
                if response.status_code == 200:
                    ai_response = response.json()["response"]
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                else:
                    st.error(f"Backend Error ({response.status_code}): {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Connection Error: UI could not reach the Backend API.")
                st.info(f"Checking {API_URL}... Make sure the FastAPI server is running.")
            except Exception as e:
                st.error(f"Unexpected Error: {str(e)}")

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3120/3120301.png", width=100)
    st.header("Fleet Control")
    
    # Status Indicator
    if check_backend():
        st.success("API System: Online")
    else:
        st.error("API System: Offline")

    if st.button("🔄 Clear Chat History", use_container_width=True):
        try:
            requests.post(f"{API_URL}/reset")
            st.session_state.messages = []
            st.success("Memory cleared!")
            time.sleep(1)
            st.rerun()
        except:
            st.error("Reset failed. Is the API running?")
    
    st.divider()
    
    st.markdown("### 📋 Command Guide")
    with st.expander("Resource Queries"):
        st.markdown("""
        - "List all available pilots"
        - "Show drones in New York"
        - "Which pilots have 'thermal' skills?"
        """)
    
    with st.expander("Mission Operations"):
        st.markdown("""
        - "Show current missions"
        - "Check conflicts for Mission M102"
        - "Assign resources to Mission M105"
        """)
    
    st.divider()
    st.caption("v1.2 | Connected to Google Sheets & Groq/Gemini")