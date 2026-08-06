from fastmcp import FastMCP

# Servidor MCP onde o agente GoogleSheets faz as suas ações

mcp = FastMCP()

@mcp.tool
def hello_word(name: str) -> str:
    return f"Hello Word! {name}"

"""Para a tool de inserir os valores na célula a função primeiro deve ler o valor, para não
substituir uma célular que já tenha valor a função puxa o valor da célula e se tiver um valor
ela soma o valor da célula com o novo valor e depois sim faz o update"""

@mcp.tool
