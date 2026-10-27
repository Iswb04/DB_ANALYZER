# Estrutura do banco de dados

## Tabela: vendas

A tabela vendas armazena informações sobre produtos vendidos.

### Colunas

- id:
  Identificador único da venda.

- produto:
  Categoria ou tipo do produto vendido.
  Exemplos: Notebook, Mouse, Teclado, Monitor, Headset, Celular.

- preco:
  Preço unitário do produto.

- marca:
  Marca do produto.
  Exemplos: Multilaser, Logitech, Dell, Samsung.

- modelo:
  Modelo específico do produto.

- quantidade:
  Quantidade de unidades vendidas.

## Regras importantes

Quando for necessário calcular o valor total de uma venda:

preco \* quantidade

Quando for necessário descobrir o produto mais vendido:

SUM(quantidade)

Quando for necessário descobrir a marca que mais vendeu:

SUM(quantidade) agrupado por marca.

Quando for necessário descobrir o produto mais caro:

MAX(preco)

Quando for necessário descobrir o produto mais barato:

MIN(preco)
