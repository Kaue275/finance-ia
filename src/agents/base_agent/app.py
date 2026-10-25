import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

"""Agente conversacional e supervisor. Ele é o ponto inicial da conversa e
distribui as tarefas para os agentes especializados.

O agente conversa normalmente sobre finanças. A tool do MCP só entra em cena quando
ELE identifica intenção de registrar um gasto — não há nada no código forçando isso.

Sobre o timestamp: ele NÃO vai dentro da mensagem do usuário. A mensagem chega limpa,
como o usuário escreveu. O momento do envio entra no system prompt, que é remontado a
cada turno, porque é contexto do agente e não conteúdo da conversa. Assim o agente
consegue resolver "agora", "ontem", "dia 5" sem que o histórico fique poluído com
carimbos de data a cada mensagem.

Quem traduz a data em célula é o serviço `monta_celula`, chamado dentro da tool no
servidor MCP (mês -> coluna, dia + cabeçalho -> linha). O agente nunca monta nem vê
um endereço de célula, então não tem como errar a posição.
"""

# Caminho absoluto do servidor MCP: .../src/agents/base_agent/app.py -> .../src/mcp/main.py
_MCP_SERVER = Path(__file__).resolve().parents[2] / "mcp" / "main.py"


# `%A` do strftime sai em inglês (depende do locale do SO), e o prompt é em português.
# Mapear na mão evita "Monday" no meio do texto e não depende de locale instalado.
_DIAS_SEMANA = (
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
)


def _monta_system_prompt(agora: datetime) -> str:
    """Remonta o system prompt a cada turno, carimbando o momento atual.
    É por aqui que o agente sabe que dia é hoje para resolver datas relativas."""
    dia_semana = _DIAS_SEMANA[agora.weekday()]
    return f"""
Você é um assistente de finanças bem humorado, com um humor meio robótico. Seu papel é conversar com as
pessoas e fazer análises financeiras, sugerir investimentos, e responder perguntas sobre finanças.
Você deve ser capaz de fornecer informações precisas e úteis, mas também deve ser capaz de fazer piadas e manter a conversa leve e divertida.
Lembre-se de que você é um assistente financeiro, então suas respostas devem ser relevantes para o contexto financeiro.

## Momento atual
A mensagem que você está recebendo agora foi enviada em: {agora.strftime('%d/%m/%Y')} ({dia_semana}), às {agora.strftime('%H:%M')}.
Em formato ISO: {agora.isoformat()}.
Use SEMPRE essa referência para resolver datas relativas. Nunca invente a data de hoje.

## Quando usar a planilha
Você tem a tool `registra_gasto` para lançar gastos na planilha do usuário.
Use-a APENAS quando identificar a intenção de registrar um gasto que já aconteceu.
Conversa normal sobre finanças, dúvidas, análises, simulações e piadas NÃO usam tool nenhuma.

## Parâmetros obrigatórios
Para chamar `registra_gasto` você precisa de DOIS dados:
  1. `valor` — a quantia gasta, como número (ex: 25.90).
  2. `data`  — a data do gasto, em ISO-8601 (ex: "2026-08-10").

Se faltar o VALOR, não chame a tool: pergunte ao usuário quanto foi.
Se o usuário só disser algo vago como "preciso registrar um gasto", pergunte o valor
e o dia da compra na mesma resposta, de forma leve.
Nunca chute um valor. Nunca registre duas vezes o mesmo gasto.

## Como resolver a data
Interprete a expressão de tempo da mensagem em relação ao momento atual:
  - "agora", "hoje", "acabei de", "hoje de manhã"  -> a data de hoje
  - "ontem"                                        -> hoje menos 1 dia
  - "anteontem"                                    -> hoje menos 2 dias
  - "dia 5", "no dia 5"                            -> dia 5 do mês atual; se esse dia
    ainda não chegou, entenda como o dia 5 do mês passado
  - "segunda passada", "semana passada"            -> calcule a partir de hoje
  - datas explícitas ("05/08", "5 de agosto")      -> use-as diretamente
Se a mensagem traz o valor mas NENHUMA pista de tempo, assuma que foi hoje e diga isso
na resposta ("registrei em {agora.strftime('%d/%m')}, me avisa se foi outro dia").

## Exemplos
  "Gastei agora 25 reais em um almoço"   -> registra_gasto(valor=25, data=<hoje>)
  "Ontem gastei 80 no mercado"           -> registra_gasto(valor=80, data=<ontem>)
  "No dia 5 eu gastei 120 com remédio"   -> registra_gasto(valor=120, data=<dia 5>)
  "Preciso registrar um gasto"           -> sem tool; pergunte valor e dia
  "Vale a pena investir em CDB?"         -> sem tool; responda normalmente

## Depois de registrar
Confirme ao usuário o valor e a data que foram lançados, em linguagem natural.
Nunca mencione células, colunas, linhas ou endereços da planilha — isso é detalhe interno.
"""


__llm = init_chat_model(
    model='gpt-4o',
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
)

async def executa_agent(
    texto_usuario: str,
    timestamp: datetime,
    thread_id: str,
) -> str:
    """Executa o agente conversacional e retorna a resposta do agente.

    Args:
        texto_usuario: a mensagem do usuário, exatamente como ele escreveu.
        timestamp: momento em que a mensagem foi enviada, capturado no /chat.
            Vai para o system prompt, não para a mensagem.
        thread_id: identifica a conversa no checkpointer. Precisa ser o MESMO
            valor durante toda a conversa — é ele que faz o agente lembrar dos
            turnos anteriores. Sem default de propósito: quem chama tem que
            decidir conscientemente, porque um id novo a cada turno apaga a
            memória sem dar erro nenhum. No futuro, o número de WhatsApp.
    """

    # O agente é remontado a cada turno porque o system prompt carrega o momento atual.
    # É só construção de objeto em memória (sem I/O); as tools e o checkpointer, que são
    # os caros, ficam cacheados.
    # agent = create_agent(
    #     __llm,
    #     tools=tools,
    #     system_prompt=_monta_system_prompt(timestamp),
    #     checkpointer=checkpointer,
    # )

    # agent_result = await agent.ainvoke(
    #     {"messages": [HumanMessage(content=texto_usuario)]},
    #     config={"configurable": {"thread_id": thread_id}},
    # )

    # return agent_result["messages"][-1].content
    pass