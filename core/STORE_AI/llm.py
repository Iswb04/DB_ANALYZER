
from langchain_ollama import OllamaLLM


# ==========================================
# CONFIGURAÇÕES DOS MODELOS
# ==========================================

MODELO = "qwen2.5:3b"
MODELO2 = "llama3.2:3b" 

# Modelo para gerar SQL
llm_sql = OllamaLLM(
    model=MODELO,
    temperature=0,
    num_predict=180,
    keep_alive="30m"
)

# Modelo para gerar respostas naturais
llm_exp = OllamaLLM(
    model=MODELO2,
    temperature=0.2,
    num_predict=300,
    keep_alive="30m"
)


# ==========================================
# GERAÇÃO DE SQL
# ==========================================

def gerar_sql(pergunta, contexto):

    prompt = f"""
Você é um especialista em converter perguntas
em consultas SQL para MySQL.

Sua única tarefa é gerar UMA consulta SELECT
que responda EXATAMENTE à pergunta do usuário.

ESTRUTURA DO BANCO:

Tabela: produtos

Colunas:
- id: identificador do registro
- produto: nome do produto
- preco: preço do produto
- marca: fabricante
- modelo: modelo do produto
- quantidade: quantidade de unidades vendidas

REGRAS OBRIGATÓRIAS:

1. Retorne SOMENTE a SQL, sem explicações,
   comentários ou Markdown.

2. Utilize apenas a tabela produtos.

3. Gere somente consultas SELECT.

4. Nunca gere INSERT, UPDATE, DELETE, DROP,
   ALTER, CREATE, TRUNCATE ou SHOW.

5. Se a pergunta não estiver relacionada aos
   dados da tabela, retorne exatamente INVALID.

6. Responda à pergunta ATUAL. Não copie SQL
   do contexto ou de exemplos sem verificar
   se corresponde ao pedido.

7. Produto e marca são campos diferentes.
   Mouse, Teclado e Monitor são produtos.
   Logitech, Razer e Multilaser são marcas.

8. A coluna quantidade representa unidades
   vendidas, não estoque disponível.

9. Não utilize LIMIT ou ORDER BY se o usuário
   não solicitar classificação ou ordenação.

10. Não transforme pedidos de listagem em
    análises de maior preço ou maior quantidade.

11. Utilize SUM(quantidade) para perguntar
    quantas unidades foram vendidas.

12. Utilize COUNT(*) quando a pergunta for
    sobre a quantidade de registros.

13. Utilize DISTINCT para listar valores únicos
    de produtos ou marcas.

EXEMPLOS:

Pergunta: oi
SQL: INVALID

Pergunta: mostre todos os itens do banco
SQL: SELECT * FROM produtos

Pergunta: verifique o banco e retorne os itens
SQL: SELECT * FROM produtos

Pergunta: liste todos os registros
SQL: SELECT * FROM produtos

Pergunta: quais produtos existem
SQL: SELECT DISTINCT produto FROM produtos

Pergunta: quais marcas existem
SQL: SELECT DISTINCT marca FROM produtos

Pergunta: quais marcas de mouse existem
SQL: SELECT DISTINCT marca FROM produtos
WHERE produto = 'Mouse'

Pergunta: quais produtos da Multilaser existem
SQL: SELECT DISTINCT produto FROM produtos
WHERE marca = 'Multilaser'

Pergunta: quantos registros existem
SQL: SELECT COUNT(*) AS total_registros FROM produtos

Pergunta: quantos mouses foram vendidos
SQL: SELECT SUM(quantidade) AS quantidade_vendida
FROM produtos WHERE produto = 'Mouse'

Pergunta: quantos produtos a Samsung vendeu
SQL: SELECT SUM(quantidade) AS quantidade_vendida
FROM produtos WHERE marca = 'Samsung'

Pergunta: quantas unidades foram vendidas
SQL: SELECT SUM(quantidade) AS quantidade_total
FROM produtos

Pergunta: qual produto vendeu mais
SQL: SELECT produto,
SUM(quantidade) AS quantidade_vendida
FROM produtos GROUP BY produto
ORDER BY quantidade_vendida DESC LIMIT 1

Pergunta: qual marca vendeu mais
SQL: SELECT marca,
SUM(quantidade) AS quantidade_vendida
FROM produtos GROUP BY marca
ORDER BY quantidade_vendida DESC LIMIT 1

Pergunta: qual produto da Multilaser vendeu mais
SQL: SELECT produto,
SUM(quantidade) AS quantidade_vendida
FROM produtos WHERE marca = 'Multilaser'
GROUP BY produto
ORDER BY quantidade_vendida DESC LIMIT 1

Pergunta: qual o mouse mais vendido da Multilaser
SQL: SELECT modelo,
SUM(quantidade) AS quantidade_vendida
FROM produtos
WHERE produto = 'Mouse' AND marca = 'Multilaser'
GROUP BY modelo
ORDER BY quantidade_vendida DESC LIMIT 1

Pergunta: qual o preço do mouse
SQL: SELECT produto, preco FROM produtos
WHERE produto = 'Mouse'

Pergunta: qual o produto mais caro
SQL: SELECT produto, preco FROM produtos
ORDER BY preco DESC LIMIT 1

CONTEXTO AUXILIAR DO RAG:
{contexto}

ATENÇÃO:
O contexto serve apenas como referência.
A pergunta do usuário tem prioridade.
Nunca invente colunas ou tabelas.

PERGUNTA ATUAL:
{pergunta}

SQL:
"""

    resposta = llm_sql.invoke(prompt).strip()

    # Remove possíveis blocos Markdown
    resposta = (
        resposta
        .replace("```sql", "")
        .replace("```SQL", "")
        .replace("```", "")
        .strip()
    )

    # Remove prefixo ocasional
    if resposta.upper().startswith("SQL:"):
        resposta = resposta[4:].strip()

    # Normaliza resposta inválida
    if resposta.upper() == "INVALID":
        return "INVALID"

    return resposta


# ==========================================
# EXPLICAÇÃO DOS RESULTADOS
# ==========================================

def explicar(pergunta, dados):

    prompt = f"""
Você é o DB Reader, um assistente de análise
de dados conectado a um banco MySQL.

Responda à pergunta usando EXCLUSIVAMENTE
os dados retornados pelo banco.

REGRAS:

1. Responda em português brasileiro.

2. Responda exatamente ao que foi solicitado.

3. Não invente informações.

4. Não utilize dados de perguntas anteriores.

5. Não repita a pergunta.

6. Não faça introduções desnecessárias.

7. Não diga "Com base nos dados fornecidos",
   "Os dados mostram" ou "Podemos observar".

8. Se o usuário pedir uma listagem, apresente
   todos os registros recebidos, um por linha.

9. Não resuma nem omita registros em listagens.

10. Não destaque maior preço ou maior quantidade
    quando isso não tiver sido solicitado.

11. Para resultados únicos, responda
    objetivamente em até duas frases.

12. Não confunda unidades vendidas com
    estoque disponível.

13. Se não houver dados suficientes, informe
    que não foi possível responder.

PERGUNTA DO USUÁRIO:
{pergunta}

DADOS RETORNADOS PELO BANCO:
{dados}

RESPOSTA:
"""

    return llm_exp.invoke(prompt).strip()
