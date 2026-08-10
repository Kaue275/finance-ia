"""Monta o endereço (notação A1) da célula da planilha financeira.

Regras da planilha:

1. Cada mês ocupa uma coluna fixa. O mapa `MESES` guarda essa normalização
   (janeiro -> "D", fevereiro -> "J", ...).

2. Os dias 1..31 ocupam linhas sequenciais, MAS a planilha tem cabeçalho:
   a primeira linha de dados (dia 1) é a linha 3, não a linha 1.
   Portanto:  linha = dia + (PRIMEIRA_LINHA_DE_DADOS - 1)

   dia 1  -> linha 3
   dia 2  -> linha 4
   dia 31 -> linha 33
"""

from datetime import datetime

MESES = {
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
    12: "BR",
}

# A planilha tem cabeçalho: o dia 1 começa na linha 3.
PRIMEIRA_LINHA_DE_DADOS = 3


def monta_coluna(timestamp: datetime) -> str:
    """Devolve a letra da coluna correspondente ao mês do timestamp."""
    return MESES[timestamp.month]


def monta_linha(timestamp: datetime) -> int:
    """Devolve o número da linha correspondente ao dia do timestamp,
    já deslocado pelo cabeçalho da planilha."""
    return timestamp.day + PRIMEIRA_LINHA_DE_DADOS - 1


def monta_celula(timestamp: datetime) -> str:
    """Monta a célula da planilha com base no timestamp da mensagem do usuário,
    usando o mês para a coluna e o dia (deslocado pelo cabeçalho) para a linha."""
    return f"{monta_coluna(timestamp)}{monta_linha(timestamp)}"
