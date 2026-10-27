
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def conectar(banco=None):
    """Estabelece conexão com o MySQL."""

    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD")
    }

    if banco:
        config["database"] = banco

    return mysql.connector.connect(**config)


def criar_banco():
    """Cria o banco e a tabela caso não existam."""

    con = None
    cursor = None

    try:
        con = conectar()
        cursor = con.cursor()

        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS store"
        )

        cursor.execute("USE store")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                produto VARCHAR(100),
                preco DECIMAL(10,2),
                marca VARCHAR(100),
                modelo VARCHAR(100),
                quantidade INT
            )
        """)

        con.commit()

        print("Banco 'store' e tabela 'produtos' prontos!")

    except mysql.connector.Error as erro:
        print(f"Erro ao configurar o banco: {erro}")
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None:
            con.close()


if __name__ == "__main__":
    criar_banco()
