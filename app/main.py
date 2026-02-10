from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agent import DroneAgent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Drone Fleet AI Agent")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = DroneAgent()


class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint"""
    try:
        response = agent.chat(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/reset")
async def reset():
    """Reset chat history"""
    agent.reset()
    return {"message": "Chat history reset"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)