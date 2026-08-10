from datetime import datetime
from uuid import uuid4

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.agents.base_agent.app import executa_agent

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    # Momento em que a mensagem foi enviada. É a referência que o agente usa para
    # resolver "agora", "ontem", "dia 5". Se o cliente não mandar, usamos o momento
    # da chamada.
    timestamp: datetime = Field(default_factory=datetime.now)
    # Identifica a conversa na memória do agente.
    # Vazio = conversa nova, o servidor gera um id e devolve na resposta.
    # Para continuar a conversa, o cliente reenvia o mesmo id na próxima mensagem.
    # ATENÇÃO: não gere um id novo a cada requisição — isso zera a memória do agente,
    # que deixa de lembrar do que perguntou no turno anterior.
    thread_id: str | None = None


class ChatResponse(BaseModel):
    resposta: str
    # Sempre devolvido: é este valor que o cliente deve reenviar para manter o contexto.
    thread_id: str


@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest) -> ChatResponse:
    # Primeira mensagem da conversa: o servidor cunha o id. Nas seguintes, o cliente
    # reenvia o mesmo id e o agente reabre o histórico.
    # No futuro, com WhatsApp, o número do usuário já é um id estável e este uuid
    # deixa de ser necessário.
    thread_id = chat_request.thread_id or str(uuid4())

    resposta = await executa_agent(
        chat_request.message,
        chat_request.timestamp,
        thread_id,
    )

    return ChatResponse(resposta=resposta, thread_id=thread_id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
