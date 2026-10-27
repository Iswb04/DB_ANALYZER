# Regras de negócio

## Estoque

A coluna `quantidade` representa a quantidade de unidades disponíveis em estoque.

**Nenhum registro da tabela `produtos` representa uma venda realizada.**

A quantidade não deve ser interpretada como unidades vendidas.

## Produto com maior estoque

Quando o usuário perguntar qual produto possui mais unidades em estoque, utilizar:

`SUM(quantidade)`

Agrupar por `produto` e ordenar da maior quantidade para a menor.

Exemplo:

```sql
SELECT produto, SUM(quantidade) AS estoque_total
FROM produtos
GROUP BY produto
ORDER BY estoque_total DESC
LIMIT 1;
```

## Marca com maior estoque

Quando o usuário perguntar qual marca possui mais unidades em estoque, utilizar:

`SUM(quantidade)`

Agrupar por `marca` e ordenar da maior quantidade para a menor.

## Estoque total

Quando o usuário perguntar quantas unidades existem no banco ou qual é o estoque total, utilizar:

```sql
SELECT SUM(quantidade) AS estoque_total
FROM produtos;
```

## Valor do estoque

Quando o usuário perguntar sobre o valor total dos produtos disponíveis em estoque, calcular:

`preco * quantidade`

O valor total do estoque deve ser calculado utilizando:

```sql
SELECT SUM(preco * quantidade) AS valor_estoque
FROM produtos;
```

**O valor do estoque não representa faturamento ou receita de produtos.**

## Preço

Quando o usuário perguntar pelo produto mais caro, considerar o maior valor da coluna `preco`.

Quando perguntar pelo produto mais barato, considerar o menor valor da coluna `preco`.

## Listagem de itens

Quando o usuário solicitar todos os itens, produtos ou registros do banco, apresentar os produtos cadastrados, sem limitar a consulta aos produtos com maior estoque.

Exemplo:

```sql
SELECT * FROM produtos;
```

## Filtros

Quando o usuário mencionar uma marca, utilizar a coluna `marca`.

Quando mencionar um produto, utilizar a coluna `produto`.

Quando mencionar um modelo, utilizar a coluna `modelo`.

## Perguntas sobre produtos

A tabela `produtos` contém informações de produtos e estoque, mas não possui registros de transações de produtos.

Portanto, não é possível determinar:

- Qual produto foi mais vendido.
- Qual marca vendeu mais.
- Quantas unidades foram vendidas.
- O faturamento obtido com produtos.
- A receita total de produtos.

Quando o usuário fizer essas perguntas, informar que o banco contém apenas dados de estoque e não possui histórico de produtos.

**Nunca apresentar a quantidade em estoque como quantidade vendida.**