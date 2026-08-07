from fastmcp import FastMCP
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Servidor MCP onde o agente GoogleSheets faz as suas ações

mcp = FastMCP()

@mcp.tool
def hello_word(name: str) -> str:
    return f"Hello Word! {name}"

"""Para a tool de inserir os valores na célula a função primeiro deve ler o valor, para não
substituir uma célular que já tenha valor a função puxa o valor da célula e se tiver um valor
ela soma o valor da célula com o novo valor e depois sim faz o update

Para a chamada no Google Sheets vamos utilizar o modelo REST, primeiro a URL deve ser montada,
depois os parâmetros devem ser definidios e após isso, fazer a chamada para alterar a célula
"""

# O CORRETO é apenas a string pura:
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

CREDENTIALS_FILE = Path(__file__).parent / 'credentials.json'

# O ID da planilha (encontrado na URL do navegador)
SPREADSHEET_ID = '1CefGlcPkqGkIGQ9H9XLhzCcdZDYXav5F2yzSPwl058I'
# O intervalo que você deseja atualizar (Notação A1)

@mcp.tool
def atualiza_celula(range, valor):
    """
    Arg:
        range: Representa a posição da célula na planilha.
        
    Kwargs:
        valor: referente ao conteúdo da célula, valor das compras. 
    """

    credenciais = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    if range and valor:
        RANGE_NAME = range
    else:
        return "Ambos os campos devem estar preenchidos"

    try:
        # Constrói o serviço da API
        service = build('sheets', 'v4', credentials=credenciais)

        # Dados que serão inseridos
        values = [
            [valor]
        ] 

        body = {
            'values': values
        }

        # Faz a chamada REST para atualizar os valores
        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW', # 'RAW' insere o texto puro, 'USER_ENTERED' processa fórmulas
            body=body
        ).execute()

        celulas = result.get('updatedCells', 0)
        if celulas >= 1:
            return f"Sucesso, {celulas} célula(s) atualizada(s) em {RANGE_NAME}."
        return f"A chamada foi feita, mas nenhuma célula foi atualizada em {RANGE_NAME}."

    except HttpError as e:
        # Devolve o erro ao cliente; um print só apareceria no stderr do servidor
        return f"Ocorreu um erro: {e}"

        
