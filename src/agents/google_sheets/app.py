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
    temperature=0.7,
)

agent_sheets = create_agent(
    __llm,
    system_prompt=system_prompt,
)

