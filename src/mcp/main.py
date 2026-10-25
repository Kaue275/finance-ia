import sys
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Este arquivo é iniciado pelo cliente MCP como um script solto ("python .../mcp/main.py"),
# então o pacote `src` ainda não está no sys.path. Colocamos a raiz do projeto no path
# antes de importar os serviços.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.services.monta_celula import monta_celula  # noqa: E402

# Servidor MCP onde o agente GoogleSheets faz as suas ações

mcp = FastMCP()

"""A tool NÃO recebe o endereço da célula do agente. Ela recebe a data do gasto e
chama o serviço `monta_celula`, que conhece o mapa mês -> coluna e o deslocamento do
cabeçalho (dia 1 = linha 3). Assim o LLM nunca inventa uma célula.

Antes de gravar, a tool lê o valor atual da célula: se já houver um gasto registrado
naquele dia, o novo valor é somado ao existente em vez de sobrescrevê-lo.

Para a chamada no Google Sheets usamos o modelo REST: monta-se a URL, definem-se os
parâmetros e então a chamada de leitura/atualização da célula é feita.
"""

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

CREDENTIALS_FILE = Path(__file__).parent / 'credentials.json'

# O ID da planilha (encontrado na URL do navegador)
SPREADSHEET_ID = '1CefGlcPkqGkIGQ9H9XLhzCcdZDYXav5F2yzSPwl058I'


def _parse_data(data: str) -> datetime:
    """Converte a data enviada pelo agente (ISO-8601) em datetime."""
    return datetime.fromisoformat(data.strip().replace("Z", "+00:00"))


def _para_numero(bruto) -> float:
    """Converte o conteúdo lido da célula em número. A célula pode voltar como
    número, vazia, ou como texto formatado ("R$ 1.234,56")."""
    if isinstance(bruto, (int, float)):
        return float(bruto)

    texto = str(bruto).strip().replace("R$", "").replace(" ", "")
    if not texto:
        return 0.0
    if "," in texto:  # formato pt-BR: 1.234,56
        texto = texto.replace(".", "").replace(",", ".")
    return float(texto)


@mcp.tool
def registra_gasto(valor: float, data: str) -> str:
    """Registra um gasto na planilha financeira do usuário.

    Use somente quando o usuário quiser lançar um gasto que já aconteceu.
    Os dois argumentos são obrigatórios: se você não souber o valor, pergunte ao
    usuário antes de chamar esta tool, em vez de chutar.

    A célula de destino é calculada automaticamente a partir da data.
    NÃO envie endereço de célula — envie apenas o valor e a data.

    Se o dia já tiver um gasto registrado, o novo valor é SOMADO ao existente.

    Args:
        valor: quantia gasta pelo usuário, ex: 50.90
        data: data do gasto em ISO-8601, ex: "2026-08-10". Resolva expressões
              como "hoje", "ontem" ou "dia 5" a partir do momento atual
              informado no system prompt, e envie a data já calculada.
    """
    try:
        timestamp = _parse_data(data)
    except ValueError:
        return f"Data inválida: {data!r}. Use o formato ISO-8601, ex: 2026-08-10."

    celula = monta_celula(timestamp)

    try:
        credenciais = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )

        # Constrói o serviço da API
        service = build('sheets', 'v4', credentials=credenciais)

        # 1. Lê o valor que já está na célula para não sobrescrever o dia
        leitura = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=celula,
            valueRenderOption='UNFORMATTED_VALUE',  # devolve número, não texto formatado
        ).execute()

        linhas = leitura.get('values', [])
        anterior = _para_numero(linhas[0][0]) if linhas and linhas[0] else 0.0

        # 2. Soma o novo gasto ao que já existia
        total = anterior + float(valor)

        body = {'values': [[total]]}

        # 3. Faz a chamada REST para atualizar a célula
        resultado = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=celula,
            valueInputOption='RAW',  # 'RAW' insere o texto puro, 'USER_ENTERED' processa fórmulas
            body=body,
        ).execute()

        celulas = resultado.get('updatedCells', 0)
        if celulas >= 1:
            dia = timestamp.strftime('%d/%m/%Y')
            if anterior:
                return (f"Sucesso: gasto de {valor} somado aos {anterior} que já havia "
                        f"em {dia} (célula {celula}). Novo total do dia: {total}.")
            return f"Sucesso: {total} registrado em {dia} (célula {celula})."
        return f"A chamada foi feita, mas nenhuma célula foi atualizada em {celula}."

    except HttpError as e:
        # Devolve o erro ao cliente; um print só apareceria no stderr do servidor
        return f"Ocorreu um erro ao acessar a planilha: {e}"
    except ValueError as e:
        return f"Não consegui interpretar o valor atual da célula {celula}: {e}"


if __name__ == "__main__":
    mcp.run()
