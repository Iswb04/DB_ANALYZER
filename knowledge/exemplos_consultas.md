# Exemplos de consultas

## Exemplo 1 — Produto com maior estoque

**Pergunta:**

Qual produto possui a maior quantidade em estoque?

**SQL:**

```sql
SELECT produto, SUM(quantidade) AS estoque_total
FROM produtos
GROUP BY produto
ORDER BY estoque_total DESC
LIMIT 1;
```

## Exemplo 2 — Marca com maior estoque

**Pergunta:**

Qual marca possui mais produtos em estoque?

**SQL:**

```sql
SELECT marca, SUM(quantidade) AS estoque_total
FROM produtos
GROUP BY marca
ORDER BY estoque_total DESC
LIMIT 1;
```

## Exemplo 3 — Valor total do estoque

**Pergunta:**

Qual é o valor total dos produtos em estoque?

**SQL:**

```sql
SELECT SUM(preco * quantidade) AS valor_total_estoque
FROM produtos;
```

## Exemplo 4 — Quantidade de mouses em estoque

**Pergunta:**

Quantos mouses estão disponíveis em estoque?

**SQL:**

```sql
SELECT SUM(quantidade) AS estoque_total
FROM produtos
WHERE produto = 'Mouse';
```

## Exemplo 5 — Mouse da Multilaser com maior estoque

**Pergunta:**

Qual modelo de mouse da Multilaser possui mais unidades em estoque?

**SQL:**

```sql
SELECT modelo, SUM(quantidade) AS estoque_total
FROM produtos
WHERE produto = 'Mouse'
AND marca = 'Multilaser'
GROUP BY modelo
ORDER BY estoque_total DESC
LIMIT 1;
```

## Exemplo 6 — Listar todos os produtos

**Pergunta:**

Mostre todos os produtos cadastrados no banco.

**SQL:**

```sql
SELECT * FROM produtos;
```

## Exemplo 7 — Listar marcas disponíveis

**Pergunta:**

Quais marcas estão cadastradas?

**SQL:**

```sql
SELECT DISTINCT marca
FROM produtos;
```

## Exemplo 8 — Produto mais caro

**Pergunta:**

Qual é o produto mais caro?

**SQL:**

```sql
SELECT produto, marca, modelo, preco
FROM produtos
ORDER BY preco DESC
LIMIT 1;
```

## Exemplo 9 — Produto mais barato

**Pergunta:**

Qual é o produto mais barato?

**SQL:**

```sql
SELECT produto, marca, modelo, preco
FROM produtos
ORDER BY preco ASC
LIMIT 1;
```

## Exemplo 10 — Quantidade total de produtos em estoque

**Pergunta:**

Quantas unidades existem no estoque?

**SQL:**

```sql
SELECT SUM(quantidade) AS estoque_total
FROM produtos;
```

## Exemplo 11 — Quantidade de registros cadastrados

**Pergunta:**

Quantos itens estão cadastrados no banco?

**SQL:**

```sql
SELECT COUNT(*) AS total_registros
FROM produtos;
```

## Exemplo 12 — Produtos de uma marca

**Pergunta:**

Quais produtos da Logitech estão cadastrados?

**SQL:**

```sql
SELECT produto, marca, modelo, preco, quantidade
FROM produtos
WHERE marca = 'Logitech';
```

## Regras importantes

- A coluna `quantidade` representa unidades disponíveis em estoque.
- A coluna `preco` representa o preço unitário do produto.
- A tabela `produtos`, apesar do nome, contém informações de produtos e estoque.
- Não existem registros de produtos realizadas.
- Não utilizar expressões como `total_vendido`, `quantidade_vendida` ou `faturamento`.
- Quando o usuário perguntar sobre produtos realizadas, informar que o banco não possui histórico de produtos.
- Nunca interpretar estoque como quantidade vendida.