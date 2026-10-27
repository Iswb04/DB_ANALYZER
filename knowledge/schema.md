# Estrutura do banco de dados

## Tabela: produtos

A tabela `produtos` armazena informações sobre os produtos cadastrados e suas quantidades disponíveis em estoque.

**Importante:** a tabela armazena estoque, não registros de vendas realizadas.

## Colunas

### id
Identificador único de cada registro.

Tipo: `INT`

### produto
Categoria ou tipo do produto.

Tipo: `VARCHAR(100)`

Exemplos: Notebook, Mouse, Teclado, Monitor, Headset e Celular.

### preco
Preço unitário do produto, em reais.

Tipo: `DECIMAL(10,2)`

### marca
Marca ou fabricante do produto.

Tipo: `VARCHAR(100)`

Exemplos: Multilaser, Logitech, Dell e Samsung.

### modelo
Modelo específico do produto.

Tipo: `VARCHAR(100)`

### quantidade
Quantidade de unidades disponíveis em estoque.

Tipo: `INT`

A coluna `quantidade` não representa unidades vendidas.

## Regras importantes

### Produto mais caro

Para identificar o produto mais caro, ordenar pela coluna `preco` em ordem decrescente.

```sql
SELECT produto, marca, modelo, preco
FROM produtos
ORDER BY preco DESC
LIMIT 1;
```

### Produto mais barato

Para identificar o produto mais barato, ordenar pela coluna `preco` em ordem crescente.

```sql
SELECT produto, marca, modelo, preco
FROM produtos
ORDER BY preco ASC
LIMIT 1;
```

### Produto com maior estoque

Para identificar a categoria de produto com mais unidades disponíveis, somar a coluna `quantidade`, agrupando por `produto`.

```sql
SELECT produto, SUM(quantidade) AS estoque_total
FROM produtos
GROUP BY produto
ORDER BY estoque_total DESC
LIMIT 1;
```

### Quantidade total em estoque

```sql
SELECT SUM(quantidade) AS estoque_total
FROM produtos;
```

### Valor total do estoque

O valor do estoque é calculado multiplicando o preço unitário pela quantidade disponível.

```sql
SELECT SUM(preco * quantidade) AS valor_total_estoque
FROM produtos;
```

### Listagem completa dos produtos

```sql
SELECT id, produto, preco, marca, modelo, quantidade
FROM produtos;
```

## Restrições

- A tabela contém produtos cadastrados e informações de estoque.
- Não existem informações sobre vendas realizadas.
- Não interpretar `quantidade` como quantidade vendida.
- Não interpretar o valor total do estoque como faturamento.
- Não inventar vendas, receitas ou histórico de transações.
- Utilizar exclusivamente as colunas existentes na tabela.
- Gerar somente consultas SQL `SELECT` para consultar os dados.