# só pra verificar se preencheu a tabela mesmo

import sqlite3
from pathlib import Path

caminho = Path(__file__).resolve().parents[2] / "store.db"

print("Banco acessado:", caminho)

conn = sqlite3.connect(caminho)
cursor = conn.cursor()

cursor.execute("SELECT * FROM produtos")

for linha in cursor.fetchall():
    print(linha)

conn.close()