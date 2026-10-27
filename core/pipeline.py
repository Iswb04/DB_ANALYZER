
import logging
import re
import time
import unicodedata

import sqlglot
from sqlglot import exp

from core.STORE_AI.llm import gerar_sql, llm_exp
from core.STORE_AI.rag import buscar_contexto
from core.DB.create import conectar
from core.STORE_AI.charts import gerar_grafico
from core.STORE_AI.exports import salvar_csv


# ==========================================
# CONFIGURAÇÕES
# ==========================================

# Desativa os logs técnicos do pipeline no terminal
logger = logging.getLogger("DB_READER")
logger.handlers.clear()
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.disabled = True


# ==========================================
# VALIDAÇÃO DE PERGUNTAS
# ==========================================

def normalizar(texto):
    texto = unicodedata.normalize(
        "NFKD", texto.lower().strip()
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    return re.sub(r"\s+", " ", texto).strip("!?., ")


def verificar_saudacao(pergunta):
    saudacoes = {
        "oi",
        "ola",
        "opa",
        "e ai",
        "bom dia",
        "boa tarde",
        "boa noite",
        "tudo bem",
        "oi tudo bem",
    }

    return normalizar(pergunta) in saudacoes


# ==========================================
# VALIDAÇÃO SQL
# ==========================================

def validar_sql(sql):
    try:
        consultas = sqlglot.parse(sql, read="mysql")

        # Permite somente uma instrução
        if len(consultas) != 1:
            return False

        consulta = consultas[0]

        # Permite apenas SELECT
        if not isinstance(consulta, exp.Select):
            return False

        # Bloqueia operações não permitidas
        tipos_proibidos = (
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Create,
            exp.Drop,
            exp.Alter,
            exp.Command,
            exp.Subquery,
            exp.Union,
        )

        if any(
            isinstance(no, tipos_proibidos)
            for no in consulta.walk()
        ):
            return False

        # Permite acesso somente à tabela produtos
        tabelas = list(consulta.find_all(exp.Table))

        if not tabelas:
            return False

        if any(
            tabela.name.lower() != "produtos"
            or tabela.db
            or tabela.catalog
            for tabela in tabelas
        ):
            return False

        return True

    except Exception:
        return False


# ==========================================
# IDENTIFICAÇÃO DE LISTAGENS
# ==========================================

def verificar_listagem(pergunta):
    texto = normalizar(pergunta)

    termos = (
        "listar",
        "liste",
        "mostre",
        "mostrar",
        "retorne os itens",
        "retornar os itens",
        "todos os itens",
        "todos os produtos",
        "todos os registros",
        "verifique o banco",
        "consulte o banco",
    )

    return any(termo in texto for termo in termos)


# ==========================================
# FORMATAÇÃO DE LISTAGENS
# ==========================================

def formatar_listagem(dados_formatados):
    linhas = []

    for registro in dados_formatados:
        partes = []

        for coluna, valor in registro.items():
            if valor is not None:
                partes.append(f"{coluna}: {valor}")

        linhas.append(" | ".join(partes))

    return "\n".join(linhas)


# ==========================================
# PIPELINE PRINCIPAL
# ==========================================

def rodar_pipeline(pergunta):

    pergunta = str(pergunta).strip()

    # 1. Verifica pergunta vazia
    if not pergunta:
        print("\nDigite uma pergunta válida.")
        return

    # 2. Trata cumprimentos sem chamar a IA
    if verificar_saudacao(pergunta):
        print(
            "\nOlá! Sou o DB Reader. "
            "Como posso te ajudar?"
        )
        return

    # 3. Busca contexto no RAG
    try:
        contexto = buscar_contexto(pergunta)

    except Exception:
        print(
            "\nNão foi possível recuperar as "
            "informações necessárias."
        )
        return

    # 4. Gera SQL com Ollama
    try:
        sql = gerar_sql(pergunta, contexto).strip()

    except Exception:
        print(
            "\nNão foi possível interpretar sua pergunta."
        )
        return

    # 5. Trata consultas inválidas
    if sql.upper() == "INVALID":
        print(
            "\nNão identifiquei uma consulta relacionada "
            "ao banco de dados."
        )
        return

    # 6. Valida a SQL
    if not validar_sql(sql):
        print(
            "\nNão foi possível realizar essa consulta. "
            "Tente reformular sua pergunta."
        )
        return

    # 7. Consulta o MySQL
    con = None
    cursor = None

    try:
        con = conectar("store")
        cursor = con.cursor()

        cursor.execute(sql)

        colunas = [
            descricao[0]
            for descricao in cursor.description
        ] if cursor.description else []

        dados = cursor.fetchall() if colunas else []

    except Exception:
        print(
            "\nOcorreu um erro ao consultar o banco. "
            "Por favor, reformule sua pergunta."
        )
        return

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None:
            con.close()

    # 8. Verifica se existem resultados
    if not dados:
        print(
            "\nNão foram encontrados dados "
            "para essa pergunta."
        )
        return

    # 9. Formata os resultados
    dados_formatados = [
        dict(zip(colunas, linha))
        for linha in dados
    ]

    # 10. Gera a resposta
    if verificar_listagem(pergunta):

        # Listagens são exibidas diretamente,
        # evitando que o LLM omita registros.
        resposta = formatar_listagem(dados_formatados)

    else:
        try:
            prompt = f"""
Você é o DB Reader, um assistente de análise de dados.

Responda à pergunta do usuário usando SOMENTE
os dados retornados pelo banco de dados.

REGRAS:
- Responda em português brasileiro.
- Responda exatamente ao que foi solicitado.
- Não invente informações.
- Não utilize informações de perguntas anteriores.
- Não repita a pergunta.
- Não faça introduções desnecessárias.
- Não destaque preços ou quantidades se isso
  não tiver sido solicitado.
- Para análises, responda em até 2 frases.
- Se houver apenas um resultado, seja direto.
- Se houver vários resultados, respeite
  a intenção da pergunta.

PERGUNTA DO USUÁRIO:
{pergunta}

DADOS RETORNADOS PELO BANCO:
{dados_formatados}

RESPOSTA:
"""

            resposta = llm_exp.invoke(prompt).strip()

        except Exception:
            print(
                "\nNão foi possível gerar a resposta."
            )
            return

    # 11. Exibe a resposta na interface
    print(f"\n{resposta}")

    # 12. Pergunta sobre gráfico
    try:
        opcao = input(
            "\nGerar gráfico? (S ou N): "
        ).strip().upper()

        if opcao in ("S", "SIM"):
            gerar_grafico(colunas, dados)

    except Exception:
        print("\nNão foi possível gerar o gráfico.")

    # 13. Pergunta sobre CSV
    try:
        opcao = input(
            "\nExportar CSV? (S ou N): "
        ).strip().upper()

        if opcao in ("S", "SIM"):
            salvar_csv(colunas, dados)

    except Exception:
        print("\nNão foi possível exportar o CSV.")
