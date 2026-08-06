from datetime import datetime

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


if __name__ == "__main__":
    # SIMULAÇÃO: Criando um timestamp para o dia 15 de Março de 2026 às 14:30
    timestamp_simulado = datetime(2026, 3, 15, 14, 30)
    
    # Executa a função com o timestamp simulado
    resultado = monta_coluna(timestamp_simulado)
    
    print(f"Output gerado: {resultado}") 