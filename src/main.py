from datetime import datetime
from uuid import uuid4
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from agents.base_agent.app import executa_agent
from routes import route_user
from exceptions.user_exception import UserError


app = FastAPI()

@app.exception_handler(UserError)
async def user_error_handler(req: Request, exc: UserError):
    return JSONResponse(status_code=exc.status_code, content={"Detail": str(exc)})

# Webhook do WhatsApp: POST /uazapi/webhook
app.include_router(route_user.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)