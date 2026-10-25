from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

"""Agente conversacional e supervisor, ele é o ponto incial da conversa e
distribui as tarefas para os agentes especializados"""

client = MultiServerMCPClient(
    {
        "sheets": {
            "transport": "stdio",
            "command": "python",
            "args": ["/src/mcp/main.py"]
        }
    }
)

tools = client.get_tools()

system_prompt = """
Você é um agente que tem o objetivo de fazer registros 
"""

__llm = init_chat_model(
    model='gpt-3.5-turbo',
    temperature=0.7,
)

agent_sheets = create_agent(
    __llm,
    tools=tools,
    system_prompt=system_prompt,
)

