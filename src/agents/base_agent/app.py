from datetime import datetime 

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

"""Agente conversacional e supervisor, ele é o ponto incial da conversa e
distribui as tarefas para os agentes especializados"""

system_prompt = """
Você é um assistente de finanças bem humorado, com um humor meio robótico. Seu papel é conversar com as 
pessoas e fazer análises financeiras, sugerir investimentos, e responder perguntas sobre finanças. Você deve ser capaz de fornecer informações precisas e úteis, mas também deve ser capaz de fazer piadas e manter a conversa leve e divertida. Lembre-se de que você é um assistente financeiro, então suas respostas devem ser relevantes para o contexto financeiro. 
"""

__llm = init_chat_model(
    model='gpt-3.5-turbo',
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
)

def classifica_agente(pergunta: str) -> str:
    """Classifica o agente especializado que deve ser chamado com base no texto do usuário"""
    prompt = """
Você é um classificador de agentes especializados em finanças.

Sua tarefa é analisar o texto do usuário e determinar se você deve ou não passar para o agente especialista.

Retorne a resposta apenas com o nome do agente e mais nada, ex: "GoogleSheets"

Classifique com base na pergunta do usuário:

{pergunta}
""" 
    response = __llm.invoke(prompt.format(pergunta=pergunta))
    return response.content.strip()

"""Para o agente saber onde colocar o valor de célula correta no google sheets, vamos seguir a seguinte lógica:

1. Ao receber a mesangem do usuário pelo whatsapp, ele vai capturar o timestamp da mesangem e extrair apenas o dia da mensagem, Como na nossa planilha, os dias são espressados 
de 1 a 31 em todos os meses e nada mais que isso, os dias ficam quase como um índice para o agente saber onde colocar o valor na planilha.

2. Como é uma planilha grande e complexa, vamos ter uma objeto que contém a transformação dos meses nas respectivas colunas da planilha, ex:
{
    "1": "B",
    "2": "C",
    "3": "D",
}

3. O agente supervisor vai extrair o valor que foi gasto pelo usuário, extrair isso da mensagem (texto, áudio, arquivo) e enviar para o agente GoogleSheets, que vai fazer o registro
já com os parâmetros.
"""

meses = {
    1: "D",
    2: "J",
    3: "P",
    4: "V",
    5: "AB",
    6: "AH",
    7: "AN",
    8: "AT",
    9: "AZ",
    10: "BF",
    11: "BL",
    12: "BR"
}

def monta_coluna(timestamp: datetime) -> str:
    """Monta a célula da planilha com base no timestamp da mensagem do usuário,
    usando o mês para a coluna e o dia para a linha"""
    return f"{meses[timestamp.month]}{timestamp.day}"

agent = create_agent(
    __llm,
    system_prompt=system_prompt,
)

def executa_agent(texto_usuario: str) -> str:
    """Executa o agente conversacional e retorna a resposta do agente"""
    classificacao = classifica_agente(texto_usuario)
    if classificacao == "GoogleSheets":
        # agent_result = agent_sheets(texto_usuario)
        print(f"O agente chamado foi o: {classificacao}")

    agent_result = agent.invoke(
        HumanMessage(content=texto_usuario)
    )

    return agent_result["messages"][-1].content