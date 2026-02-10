from google import genai
from google.genai import types
from typing import List, Dict, Any
import json
from app.config import get_settings
from app.tools import TOOLS, ToolExecutor

class DroneAgent:
    def __init__(self):
        settings = get_settings()
        
        # 1. Initialize the new Client
        self.client = genai.Client(api_key=settings.google_api_key)
        
        # 2. Set the correct model ID (Gemini 2.0 Flash is the latest stable)
        self.model_id = "gemini-2.5-flash"
        
        # 3. Setup Tool Configuration
        # In the new SDK, 'automatic_function_calling' handles the execution loop for you.
        # Note: 'TOOLS' should be a list of the actual Python functions from your tools.py
        self.config = types.GenerateContentConfig(
            tools=TOOLS,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False
            )
        )
        
        # 4. Create a chat session to maintain history automatically
        self._setup_session()

    def _setup_session(self):
        """Internal helper to initialize or restart the chat session"""
        self.chat_session = self.client.chats.create(
            model=self.model_id,
            config=self.config
        )

    def chat(self, user_message: str) -> str:
        """
        Send message to agent and get response.
        The SDK handles function calls and history internally.
        """
        try:
            # Send message to the session
            response = self.chat_session.send_message(user_message)
            
            # The SDK automatically executes tools and re-prompts the model 
            # until a final text response is generated.
            return response.text
            
        except Exception as e:
            print(f"Error in DroneAgent.chat: {str(e)}")
            return f"I encountered an error processing your request: {str(e)}"

    def reset(self):
        """Reset chat history by creating a fresh session"""
        self._setup_session()
        return "Chat history reset."

    def get_history(self):
        """Optional: Helper to view current session history"""
        return self.chat_session.history