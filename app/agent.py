import google.generativeai as genai
from typing import List, Dict, Any
import json
from app.config import get_settings
from app.tools import TOOLS, ToolExecutor


class DroneAgent:
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.google_api_key)

        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            tools=TOOLS
        )

        self.tool_executor = ToolExecutor()
        self.chat_history = []

    def _execute_function_call(self, function_call) -> str:
        """Execute function call and return result"""
        function_name = function_call.name
        function_args = {}
        
        # Extract arguments
        for key, value in function_call.args.items():
            function_args[key] = value
        
        # Execute tool
        result = self.tool_executor.execute(function_name, function_args)
        
        return result
    
    def chat(self, user_message: str) -> str:
        """Send message to agent and get response"""
        
        # Add user message to history
        self.chat_history.append({
            "role": "user",
            "parts": [user_message]
        })
        
        # Start chat with history
        chat = self.model.start_chat(history=self.chat_history[:-1])
        
        # Send message
        response = chat.send_message(user_message)
        
        # Handle function calls
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            # Check if there are function calls
            if not response.candidates[0].content.parts:
                break
            
            function_calls = [
                part.function_call 
                for part in response.candidates[0].content.parts 
                if hasattr(part, 'function_call') and part.function_call
            ]
            
            if not function_calls:
                break
            
            # Execute all function calls
            function_responses = []
            for fc in function_calls:
                result = self._execute_function_call(fc)
                function_responses.append({
                    "function_call": fc,
                    "function_response": {
                        "name": fc.name,
                        "response": {"result": result}
                    }
                })
            
            # Send function results back
            response = chat.send_message([
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=fr["function_call"].name,
                        response={"result": fr["function_response"]["response"]["result"]}
                    )
                )
                for fr in function_responses
            ])
            
            iteration += 1
        
        # Get final text response
        final_response = response.text
        
        # Update history
        self.chat_history.append({
            "role": "model",
            "parts": [final_response]
        })
        
        return final_response