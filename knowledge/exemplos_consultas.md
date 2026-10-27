# Exemplos de consultas

## Exemplo 1

Pergunta:

Qual foi o produto mais vendido?

SQL:

SELECT produto, SUM(quantidade) AS total_vendido
FROM vendas
GROUP BY produto
ORDER BY total_vendido DESC
LIMIT 1;

## Exemplo 2

Pergunta:

Qual marca vendeu mais?

SQL:

SELECT marca, SUM(quantidade) AS total_vendido
FROM vendas
GROUP BY marca
ORDER BY total_vendido DESC
LIMIT 1;

## Exemplo 3

Pergunta:

Quanto foi o faturamento total?

SQL:

SELECT SUM(preco \* quantidade) AS faturamento
FROM vendas;

## Exemplo 4

Pergunta:

Quantos mouses foram vendidos?

SQL:

SELECT SUM(quantidade) AS total_vendido
FROM vendas
WHERE produto = 'Mouse';

## Exemplo 5

Pergunta:

Qual o mouse da Multilaser mais vendido?

SQL:

SELECT modelo, SUM(quantidade) AS total_vendido
FROM vendas
WHERE produto = 'Mouse'
AND marca = 'Multilaser'
GROUP BY modelo
ORDER BY total_vendido DESC
LIMIT 1;
