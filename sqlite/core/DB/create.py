
import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def conectar(banco=None):
    """Estabelece conexão com o SQLite."""
    caminho = os.getenv("DB_PATH", str(Path(__file__).resolve().parents[2] / "store.db"))
    return sqlite3.connect(caminho)


def criar_banco():
    """Cria o banco e a tabela caso não existam."""
    con = None
    cursor = None
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto VARCHAR(100),
                preco DECIMAL(10,2),
                marca VARCHAR(100),
                modelo VARCHAR(100),
                quantidade INTEGER
            )
        """)
        con.commit()
        print("Banco 'store' e tabela 'produtos' prontos!")
    except sqlite3.Error as erro:
        print(f"Erro ao configurar o banco: {erro}")
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if con is not None:
            con.close()


if __name__ == "__main__":
    criar_banco()
