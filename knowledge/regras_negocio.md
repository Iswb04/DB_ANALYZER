# Regras de negócio

## Vendas

A quantidade representa o número de unidades vendidas.

## Produto mais vendido

Quando o usuário perguntar qual produto vendeu mais, deve-se utilizar:

SUM(quantidade)

agrupando por produto e ordenando do maior para o menor.

## Marca que mais vendeu

Quando o usuário perguntar qual marca vendeu mais, deve-se utilizar:

SUM(quantidade)

agrupando por marca e ordenando do maior para o menor.

## Faturamento

Quando o usuário perguntar sobre faturamento ou valor total das vendas, considerar:

preco \* quantidade

O faturamento total deve ser calculado utilizando:

SUM(preco \* quantidade)

## Preço

Quando o usuário perguntar pelo produto mais caro, considerar o maior valor da coluna preco.

Quando perguntar pelo produto mais barato, considerar o menor valor da coluna preco.

## Filtros

Quando o usuário mencionar uma marca, utilizar a coluna marca.

Quando mencionar um produto, utilizar a coluna produto.

Quando mencionar um modelo, utilizar a coluna modelo.
