from TCC.DB.create import conectar

def inserir_item(produto, preco, marca, modelo, quantidade):
    con = conectar("store")
    cursor = con.cursor()

    cursor.execute("""
    INSERT INTO vendas (produto, preco, marca, modelo, quantidade)
    VALUES (%s, %s, %s, %s, %s)
    """, (produto, preco, marca, modelo, quantidade))

    con.commit()
    con.close()