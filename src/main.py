from datetime import datetime
from fastapi import FastAPI
from agents.base_agent.app import executa_agent
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    timestamp: datetime

@app.post("/chat")
def chat_endpoint(chat_request: ChatRequest) -> str:
    return executa_agent(chat_request.message)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

