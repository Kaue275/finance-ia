from datetime import datetime

from src.services.monta_celula import monta_celula

if __name__ == "__main__":
    casos = [
        (datetime(2026, 8, 1), "AT3"),    # dia 1 cai na linha 3 (cabeçalho)
        (datetime(2026, 8, 2), "AT4"),
        (datetime(2026, 1, 1), "D3"),
        (datetime(2026, 3, 15), "P17"),
        (datetime(2026, 12, 31), "BR33"),  # último dia do último mês
    ]

    for timestamp, esperado in casos:
        obtido = monta_celula(timestamp)
        status = "OK " if obtido == esperado else "FALHOU"
        print(f"{status} {timestamp:%d/%m/%Y} -> {obtido} (esperado {esperado})")
