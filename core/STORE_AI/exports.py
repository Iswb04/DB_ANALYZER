import csv
from pathlib import Path
from datetime import datetime


def salvar_csv(colunas, dados):
    if not colunas or not dados:
        print("\nNão há dados para exportar.")
        return
    pasta = Path.home() / "Downloads"
    pasta.mkdir(parents=True, exist_ok=True)
    base = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = pasta / f"dados_{base}.csv"
    indice = 1
    while caminho.exists():
        caminho = pasta / f"dados_{base}_{indice}.csv"
        indice += 1
    with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.writer(arquivo, delimiter=";")
        writer.writerow(colunas)
        writer.writerows(dados)
    print(f"\nCSV salvo em: {caminho}")
