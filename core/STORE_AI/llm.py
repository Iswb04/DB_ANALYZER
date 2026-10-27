from langchain_ollama import OllamaLLM


# Modelo usado para gerar SQL
llm_sql = OllamaLLM(
    model="llama3.1",
    temperature=0
)

# Modelo usado para gerar a resposta ao usuário
llm_exp = OllamaLLM(
    model="llama3.1",
    temperature=0.5
)


def gerar_sql(pergunta, contexto):

    prompt = f"""
Você é um tradutor de linguagem natural para SQL MySQL.

Sua única função é transformar a pergunta do usuário em UMA consulta
SQL SELECT válida para a tabela "vendas".

ESTRUTURA DA TABELA:

vendas(
    produto VARCHAR,
    preco DECIMAL,
    marca VARCHAR,
    modelo VARCHAR,
    quantidade INT
)

CONTEXTO RECUPERADO PELO RAG:
{contexto}

==================================================
REGRAS GERAIS
==================================================

1. Retorne SOMENTE a consulta SQL.

2. Não use:
- markdown
- ```sql
- explicações
- comentários
- texto antes ou depois da SQL

3. A consulta deve conter SOMENTE SELECT.

4. Nunca use:
- INSERT
- UPDATE
- DELETE
- DROP
- ALTER
- CREATE
- TRUNCATE
- DESCRIBE
- SHOW

5. Se a pergunta for apenas uma saudação, conversa fiada ou não tiver
relação com os dados da tabela, retorne exatamente:

INVALID

6. "mouse", "teclado", "monitor", etc. são valores da coluna produto.

7. Nomes como "Multilaser", "Logitech", "Redragon", "Razer" e
"Corsair" são valores da coluna marca.

8. Nunca confunda produto com marca.

==================================================
REGRAS PARA QUANTIDADE
==================================================

Quando o usuário perguntar QUANTOS itens de um produto foram vendidos,
some a coluna quantidade.

Exemplo:

Pergunta:
quantos mouses

SQL correta:
SELECT SUM(quantidade) AS quantidade_vendida FROM vendas WHERE produto = 'Mouse'

Pergunta:
quantos mouses foram vendidos

SQL correta:
SELECT SUM(quantidade) AS quantidade_vendida FROM vendas WHERE produto = 'Mouse'

Pergunta:
quantidade de mouses

SQL correta:
SELECT SUM(quantidade) AS quantidade_vendida FROM vendas WHERE produto = 'Mouse'

IMPORTANTE:
Não retorne o nome do produto junto nessa situação.
O objetivo é retornar a quantidade total.

==================================================
REGRAS PARA LISTAR MARCAS
==================================================

Quando o usuário perguntar QUAIS MARCAS possuem determinado produto,
retorne as marcas distintas.

Exemplo:

Pergunta:
quais marcas de mouse

SQL correta:
SELECT DISTINCT marca FROM vendas WHERE produto = 'Mouse'

Pergunta:
quais são as marcas de mouse

SQL correta:
SELECT DISTINCT marca FROM vendas WHERE produto = 'Mouse'

==================================================
REGRAS PARA LISTAR PRODUTOS
==================================================

Quando o usuário perguntar quais produtos existem de determinada marca,
retorne os produtos distintos.

Exemplo:

Pergunta:
quais produtos da Multilaser

SQL correta:
SELECT DISTINCT produto FROM vendas WHERE marca = 'Multilaser'

==================================================
REGRAS PARA PRODUTO MAIS VENDIDO
==================================================

Quando o usuário perguntar:

- qual produto vendeu mais
- qual foi o produto mais vendido
- qual produto teve maior quantidade vendida

use:

SELECT produto, SUM(quantidade) AS quantidade_vendida
FROM vendas
GROUP BY produto
ORDER BY quantidade_vendida DESC
LIMIT 1

==================================================
REGRAS PARA MARCA QUE MAIS VENDE
==================================================

Quando o usuário perguntar:

- qual marca vende mais
- qual marca vendeu mais
- qual foi a marca mais vendida
- qual marca teve maior quantidade vendida

use:

SELECT marca, SUM(quantidade) AS quantidade_vendida
FROM vendas
GROUP BY marca
ORDER BY quantidade_vendida DESC
LIMIT 1

==================================================
REGRAS PARA PRODUTO MAIS VENDIDO DE UMA MARCA
==================================================

Quando o usuário perguntar qual produto vendeu mais dentro de uma marca,
filtre pela marca e agrupe por produto.

Exemplo:

Pergunta:
qual o mouse mais vendido da Multilaser

SQL correta:
SELECT produto, SUM(quantidade) AS quantidade_vendida
FROM vendas
WHERE produto = 'Mouse' AND marca = 'Multilaser'
GROUP BY produto
ORDER BY quantidade_vendida DESC
LIMIT 1

Outro exemplo:

Pergunta:
qual produto da Multilaser vendeu mais

SQL correta:
SELECT produto, SUM(quantidade) AS quantidade_vendida
FROM vendas
WHERE marca = 'Multilaser'
GROUP BY produto
ORDER BY quantidade_vendida DESC
LIMIT 1

==================================================
REGRAS PARA QUANTIDADE POR MARCA
==================================================

Quando o usuário perguntar quantos itens uma determinada marca vendeu,
some quantidade filtrando pela marca.

Exemplo:

Pergunta:
quantos produtos a Samsung vendeu

SQL correta:
SELECT SUM(quantidade) AS quantidade_vendida FROM vendas WHERE marca = 'Samsung'

==================================================
REGRAS PARA PREÇO
==================================================

Se o usuário perguntar pelo preço de um produto, utilize a coluna preco.

Exemplo:

Pergunta:
qual o preço do mouse

SQL:
SELECT produto, preco FROM vendas WHERE produto = 'Mouse'

==================================================
REGRAS PARA LISTAGEM
==================================================

Quando o usuário quiser apenas listar informações, utilize SELECT.

Exemplo:

Pergunta:
quais produtos existem

SQL:
SELECT DISTINCT produto FROM vendas

Pergunta:
quais marcas existem

SQL:
SELECT DISTINCT marca FROM vendas

==================================================
REGRAS PARA TOTAL DE VENDAS
==================================================

Quando o usuário perguntar o total de itens vendidos:

SELECT SUM(quantidade) AS quantidade_total FROM vendas

==================================================

PERGUNTA DO USUÁRIO:
{pergunta}

RETORNE SOMENTE A SQL:
"""

    resposta = llm_sql.invoke(prompt)

    return (
        resposta
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )


def explicar(dados):

    prompt = f"""
Você é um assistente de análise de dados.

Responda de forma natural, direta e curta, usando SOMENTE os dados
retornados pelo banco.

REGRAS:

- Responda em português.
- No máximo 2 frases.
- Não repita a pergunta.
- Não invente informações.
- Não diga "Com base nos dados fornecidos".
- Não diga "Os dados mostram".
- Não diga "Podemos observar".
- Não faça introduções desnecessárias.
- Dê destaque ao principal resultado.
- Se houver um único resultado, responda diretamente.
- Se houver uma lista, apresente os principais resultados de forma natural.

Exemplos:

Dados:
[{{'quantidade_vendida': 500}}]

Resposta:
Foram vendidos 500 mouses.

Dados:
[{{'marca': 'Logitech'}}, {{'marca': 'Redragon'}}, {{'marca': 'Razer'}}]

Resposta:
As marcas de mouse disponíveis são Logitech, Redragon e Razer.

Dados:
[{{'produto': 'Mouse', 'quantidade_vendida': 500}}]

Resposta:
O produto que vendeu mais foi o Mouse, com 500 unidades vendidas.

DADOS RETORNADOS PELO BANCO:
{dados}

RESPOSTA:
"""

    return llm_exp.invoke(prompt).strip()