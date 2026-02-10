import streamlit as st
import requests
import os

# Config
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="🚁 Drone Fleet Manager", page_icon="🚁")

st.title("🚁 Drone Fleet AI Manager")
st.caption("AI-powered pilot and drone assignment system")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about pilots, drones, or missions..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"message": prompt}
                )
                
                if response.status_code == 200:
                    ai_response = response.json()["response"]
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
                st.info("Make sure FastAPI server is running on port 8000")

# Sidebar
with st.sidebar:
    st.header("Quick Actions")
    
    if st.button("🔄 Reset Conversation"):
        try:
            requests.post(f"{API_URL}/reset")
            st.session_state.messages = []
            st.rerun()
        except:
            st.error("Could not reset")
    
    st.divider()
    
    st.markdown("""
    ### Example Commands
    - "Show me available pilots"
    - "Find pilots with commercial license in Boston"
    - "Assign pilot to mission M001"
    - "Check conflicts for mission M002"
    - "List all missions"
    - "Show drones with thermal imaging in NYC"
    """)