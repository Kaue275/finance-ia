import os
import re
from datetime import datetime

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks

from src.agents.base_agent.app import executa_agent

load_dotenv()

"""Integração com a uazapi (WhatsApp).

Fluxo:
  grupo do WhatsApp -> uazapi -> POST /uazapi/webhook -> agente -> POST /send/text

O agente vive dentro de um grupo, então ele NÃO responde tudo: só entra em ação
quando é marcado com @ na mensagem. Sem esse filtro, ele responderia a cada
conversa do grupo — e, pior, responderia ao eco das próprias mensagens.
"""

UAZAPI_URL = (os.getenv("UAZAPI_URL") or "").rstrip("/")
UAZAPI_TOKEN = os.getenv("UAZAPI_TOKEN") or ""

# Em conversa privada não existe "marcar com @". Como o pedido é um bot de grupo,
# deixe False se quiser que ele ignore mensagens diretas também.
RESPONDE_EM_PRIVADO = True

router = APIRouter(prefix="/uazapi", tags=["uazapi"])


def _foi_mencionado(mensagem: dict, numero_do_bot: str) -> bool:
    """Diz se o bot foi marcado com @ na mensagem.

    No WhatsApp a menção aparece de duas formas: o texto cru contém o número
    ("@558185464605") e o contextInfo traz a lista de marcados. Checamos as duas
    porque a segunda nem sempre vem no payload."""
    if not numero_do_bot:
        return False

    if f"@{numero_do_bot}" in (mensagem.get("text") or ""):
        return True

    conteudo = mensagem.get("content")
    if not isinstance(conteudo, dict):
        return False

    contexto = conteudo.get("contextInfo") or {}
    marcados = contexto.get("mentionedJid") or contexto.get("mentionedJID") or []
    return any(numero_do_bot in str(jid) for jid in marcados)


def _limpa_mencao(texto: str, numero_do_bot: str) -> str:
    """Tira o "@numero" do texto. O agente deve receber só o que o usuário
    realmente escreveu — a marcação é endereçamento, não conteúdo."""
    sem_mencao = re.sub(rf"@{re.escape(numero_do_bot)}\b", " ", texto or "")
    return re.sub(r"\s{2,}", " ", sem_mencao).strip()


def _extrai_timestamp(mensagem: dict) -> datetime:
    """Momento em que a mensagem foi enviada. A uazapi manda epoch em ms
    (ou em segundos, dependendo do evento)."""
    bruto = mensagem.get("messageTimestamp") or mensagem.get("timestamp") or 0
    if not bruto:
        return datetime.now()

    segundos = bruto / 1000 if bruto > 1e12 else bruto
    return datetime.fromtimestamp(segundos)


async def envia_texto(numero: str, texto: str, replyid: str | None = None) -> None:
    """POST /send/text da uazapi. `numero` aceita o chatid do grupo (...@g.us).
    `replyid` faz a resposta sair citando a mensagem original."""
    if not UAZAPI_URL or not UAZAPI_TOKEN:
        raise RuntimeError("Configure UAZAPI_URL e UAZAPI_TOKEN no .env")

    corpo = {"number": numero, "text": texto}
    if replyid:
        corpo["replyid"] = replyid

    async with httpx.AsyncClient(timeout=30) as http:
        resposta = await http.post(
            f"{UAZAPI_URL}/send/text",
            json=corpo,
            headers={"token": UAZAPI_TOKEN, "Content-Type": "application/json"},
        )
        resposta.raise_for_status()


async def _processa_e_responde(
    texto: str,
    timestamp: datetime,
    chatid: str,
    replyid: str | None,
) -> None:
    """Roda o agente e devolve a resposta ao WhatsApp.

    Vai em background porque o agente leva alguns segundos (LLM + tools) e a
    uazapi reenvia o webhook se a resposta HTTP demorar."""
    try:
        resposta = await executa_agent(texto, timestamp, thread_id=chatid)
        await envia_texto(chatid, resposta, replyid)
    except Exception as e:
        # Nunca deixa a exceção morrer em silêncio: avisa o grupo e loga.
        print(f"[uazapi] erro ao processar mensagem de {chatid}: {e!r}", flush=True)
        try:
            await envia_texto(chatid, "Deu ruim aqui no meu processador. Tenta de novo?", replyid)
        except Exception:
            pass


@router.post("/webhook")
async def webhook(payload: dict, background: BackgroundTasks) -> dict:
    """Recebe os eventos da uazapi.

    Responde 200 na hora e processa depois — a uazapi não fica esperando o LLM.
    """
    if payload.get("EventType") != "messages":
        return {"status": "ignorado", "motivo": "evento nao e de mensagem"}

    mensagem = payload.get("message") or {}

    # `owner` é o número da própria instância — ou seja, o número do bot.
    numero_do_bot = str(payload.get("owner") or mensagem.get("owner") or "")

    # A uazapi ecoa de volta as mensagens que NÓS enviamos (fromMe=true).
    # Sem este corte o bot responde a si mesmo em loop.
    if mensagem.get("fromMe"):
        return {"status": "ignorado", "motivo": "mensagem propria"}

    # Por enquanto só texto. Imagem/áudio/arquivo entram numa próxima etapa.
    texto = mensagem.get("text") or ""
    if not texto.strip():
        return {"status": "ignorado", "motivo": "sem texto"}

    chatid = mensagem.get("chatid") or ""
    if not chatid:
        return {"status": "ignorado", "motivo": "sem chatid"}

    if mensagem.get("isGroup"):
        # A regra principal: em grupo, só responde se for marcado.
        if not _foi_mencionado(mensagem, numero_do_bot):
            return {"status": "ignorado", "motivo": "nao fui marcado"}
        texto = _limpa_mencao(texto, numero_do_bot)
        if not texto:
            return {"status": "ignorado", "motivo": "so a marcacao, sem conteudo"}
    elif not RESPONDE_EM_PRIVADO:
        return {"status": "ignorado", "motivo": "mensagem privada"}

    background.add_task(
        _processa_e_responde,
        texto,
        _extrai_timestamp(mensagem),
        chatid,
        mensagem.get("id"),  # formato composto "owner:messageid", usado no replyid
    )

    return {"status": "processando"}
