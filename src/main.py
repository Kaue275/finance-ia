from datetime import datetime
from uuid import uuid4
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from agents.base_agent.app import executa_agent
from routes import route_user

app = FastAPI()

# Webhook do WhatsApp: POST /uazapi/webhook
app.include_router(route_user.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)