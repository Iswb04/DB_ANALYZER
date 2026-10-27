from core.DB.create import conectar


def inserir_item(produto, preco, marca, modelo, quantidade):
    con = conectar("store")
    cursor = con.cursor()
    try:
        cursor.execute("""
            INSERT INTO produtos (produto, preco, marca, modelo, quantidade)
            VALUES (%s, %s, %s, %s, %s)
        """, (produto, preco, marca, modelo, quantidade))
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        cursor.close()
        con.close()
