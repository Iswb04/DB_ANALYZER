import os
import csv
from itertools import count
from datetime import datetime


def salvar_csv(colunas, dados):

    if not colunas or not dados:
        print("Dados insuficientes para exportar CSV.")

    pasta = "TCC/DOWNLOADS"
    os.makedirs(pasta, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d")

    for i in count(1):
        caminho = os.path.join(pasta, f"dados{i}_{timestamp}.csv")
        if not os.path.exists(caminho):
            break

    try:
        with open(caminho, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(colunas)
            writer.writerows(dados)

        print(f"CSV salvo em: {caminho}")
        return f"CSV salvo em: {caminho}"

    except Exception as e:
        return f"Erro ao salvar CSV: {e}"