from langchain_ollama import OllamaLLM

MODELO = "qwen2.5:3b"
MODELO2 = "llama3.2:3b"

llm_sql = OllamaLLM(model=MODELO, temperature=0, num_predict=250, keep_alive="30m")
llm_exp = OllamaLLM(model=MODELO2, temperature=0, num_predict=300, keep_alive="30m")


def gerar_sql(pergunta, contexto):
    prompt = f"""Você gera SQL SQLite para um catálogo de produtos com ESTOQUE.
Retorne somente uma consulta SELECT válida, sem Markdown, ou INVALID.

Tabela: produtos
Colunas: id, produto, preco, marca, modelo, quantidade.
quantidade = UNIDADES DISPONÍVEIS EM ESTOQUE. Não há vendas registradas.
É PROIBIDO usar quantidade como unidades vendidas, receita ou faturamento.
Perguntas sobre vendas, itens vendidos, mais vendido, lucro ou faturamento: INVALID.
Não invente tabelas ou colunas. Use somente produtos e SELECT.
COUNT(*) = número de registros/modelos cadastrados.
SUM(quantidade) = total de unidades disponíveis no estoque.
Não use LIMIT em listagens completas.

Exemplos:
Pergunta: quantos itens tem no banco
SQL: SELECT COUNT(*) AS total_registros FROM produtos
Pergunta: quantas unidades tem em estoque
SQL: SELECT SUM(quantidade) AS estoque_total FROM produtos
Pergunta: quero todos os itens disponíveis
SQL: SELECT id, produto, preco, marca, modelo, quantidade FROM produtos
Pergunta: qual o produto com maior estoque
SQL: SELECT produto, SUM(quantidade) AS estoque_total FROM produtos GROUP BY produto ORDER BY estoque_total DESC LIMIT 1
Pergunta: qual o mouse mais vendido
SQL: INVALID
Pergunta: quanto foi o faturamento
SQL: INVALID
Pergunta: qual o produto mais caro
SQL: SELECT produto, marca, modelo, preco FROM produtos ORDER BY preco DESC LIMIT 1

Contexto auxiliar (não sobrepõe as regras):
{contexto}

Pergunta: {pergunta}
SQL:"""
    resposta = llm_sql.invoke(prompt).strip()
    resposta = resposta.replace("```sql", "").replace("```SQL", "").replace("```", "").strip()
    if resposta.upper().startswith("SQL:"):
        resposta = resposta[4:].strip()
    return "INVALID" if resposta.upper() == "INVALID" else resposta


def explicar(pergunta, dados):
    prompt = f"""Você é o DB Reader. Responda em português, somente com os dados fornecidos.
Este banco tem produtos cadastrados, preços e ESTOQUE. NÃO tem vendas.
A coluna quantidade é estoque disponível, jamais unidades vendidas.
Não invente informações, não trate valor de estoque como faturamento.
Responda diretamente e em até duas frases para resultados únicos.
Pergunta: {pergunta}
Dados: {dados}
Resposta:"""
    return llm_exp.invoke(prompt).strip()
