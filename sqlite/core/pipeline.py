import logging
import re
import sqlite3
import unicodedata
from pathlib import Path

import sqlglot
from sqlglot import exp
from core.STORE_AI.llm import gerar_sql, explicar
from core.STORE_AI.rag import buscar_contexto
from core.STORE_AI.charts import gerar_grafico
from core.STORE_AI.exports import salvar_csv

LOG = logging.getLogger("db_reader")
LOG.setLevel(logging.ERROR)
LOG.propagate = False
if not LOG.handlers:
    handler = logging.FileHandler(Path(__file__).resolve().parents[1] / "erro_pipeline.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOG.addHandler(handler)

COLUNAS = "id, produto, preco, marca, modelo, quantidade"

# Banco SQLite localizado na raiz da pasta sqlite
DB_PATH = Path(__file__).resolve().parents[1] / "store.db"


def conectar_banco():
    """Conecta ao banco SQLite existente em modo somente leitura."""
    if not DB_PATH.is_file():
        raise FileNotFoundError(
            f"Banco SQLite não encontrado: {DB_PATH}"
        )

    conexao = sqlite3.connect(DB_PATH.as_uri() + "?mode=ro", uri=True)

    tabela = conexao.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name = 'produtos'"
    ).fetchone()

    if tabela is None:
        conexao.close()
        raise RuntimeError(
            f"A tabela 'produtos' não existe no banco: {DB_PATH}"
        )

    return conexao


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto).lower().strip())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip("!?., ")


def verificar_saudacao(pergunta):
    return normalizar(pergunta) in {
        "oi", "ola", "opa", "e ai", "bom dia", "boa tarde",
        "boa noite", "tudo bem", "oi tudo bem"
    }


def pergunta_sobre_vendas(pergunta):
    texto = normalizar(pergunta)
    return any(re.search(p, texto) for p in (
        r"\bvendid[oa]s?\b", r"\bvendeu\b", r"\bvenderam\b",
        r"\bvendas?\b", r"\bvender\b", r"\bfaturamento\b",
        r"\breceita(?:s)?\b", r"\blucro(?:s)?\b",
        r"\bcomercializad[oa]s?\b", r"\bmais vendido\b",
        r"\bmenos vendido\b"
    ))


def validar_sql(sql):
    """Aceita SELECT simples apenas em produtos; evita GROUP BY inválido."""
    try:
        statements = sqlglot.parse(sql, read="sqlite")

        if len(statements) != 1 or not isinstance(statements[0], exp.Select):
            return False

        consulta = statements[0]

        bloqueados = (
            exp.Insert, exp.Update, exp.Delete, exp.Create,
            exp.Drop, exp.Alter, exp.Command, exp.Union,
            exp.Subquery, exp.With, exp.Join, exp.Into
        )

        if any(isinstance(n, bloqueados) for n in consulta.walk()):
            return False

        tabelas = list(consulta.find_all(exp.Table))

        if (
            len(tabelas) != 1
            or tabelas[0].name.lower() != "produtos"
            or tabelas[0].db
            or tabelas[0].catalog
        ):
            return False

        for no in consulta.walk():
            if isinstance(no, exp.Anonymous) and no.name.upper() in {
                "LOAD_FILE", "SLEEP", "BENCHMARK",
                "GET_LOCK", "RELEASE_LOCK"
            }:
                return False

        grupo = consulta.args.get("group")

        if grupo:
            chaves = {
                g.sql(dialect="sqlite").lower()
                for g in grupo.expressions
            }

            for proj in consulta.expressions:
                expr = proj.this if isinstance(proj, exp.Alias) else proj

                if isinstance(expr, exp.Star):
                    return False

                if any(isinstance(n, exp.AggFunc) for n in expr.walk()):
                    continue

                if isinstance(expr, exp.Literal):
                    continue

                if expr.sql(dialect="sqlite").lower() not in chaves:
                    return False

        elif any(
            isinstance(n, exp.AggFunc)
            for expr in consulta.expressions
            for n in expr.walk()
        ):
            for proj in consulta.expressions:
                expr = proj.this if isinstance(proj, exp.Alias) else proj

                if isinstance(expr, (exp.Column, exp.Star)):
                    return False

        return True

    except Exception:
        return False


def sql_frequente(pergunta):
    texto = normalizar(pergunta)

    if (
        re.search(r"\b(quantas|quantos|total|soma)\b", texto)
        and re.search(r"\b(unidades|estoque|quantidade)\b", texto)
        and not re.search(
            r"\b(maior|menor|marca|modelo|mouse|notebook|teclado|monitor)\b",
            texto
        )
    ):
        return (
            "SELECT COALESCE(SUM(quantidade), 0) "
            "AS unidades_em_estoque FROM produtos"
        )

    if (
        re.search(r"\b(quantos|quantas|numero de|total de)\b", texto)
        and re.search(r"\b(itens|produtos|registros|modelos)\b", texto)
        and not re.search(
            r"\b(unidades|estoque|marca|modelo|mouse|notebook|teclado|monitor)\b",
            texto
        )
    ):
        return "SELECT COUNT(*) AS total_registros FROM produtos"

    if (
        re.search(r"\b(itens|produtos|registros)\b", texto)
        and re.search(r"\b(disponiveis|disponivel|em estoque)\b", texto)
        and not re.search(
            r"\b(quantos|quantas|total|maior|menor|valor|preco)\b",
            texto
        )
    ):
        return (
            f"SELECT {COLUNAS} FROM produtos "
            "WHERE quantidade > 0 ORDER BY produto, marca, modelo"
        )

    if (
        re.search(
            r"\b(todos|todas|listar|liste|mostre|mostrar|exiba|quero|retorne|verifique|consulte)\b",
            texto
        )
        and re.search(r"\b(itens|produtos|registros)\b", texto)
        and not re.search(
            r"\b(quantos|quantas|maior|menor|caro|barato|marca|modelo|valor|preco)\b",
            texto
        )
    ):
        return (
            f"SELECT {COLUNAS} FROM produtos "
            "ORDER BY produto, marca, modelo"
        )

    return None


def verificar_listagem(pergunta):
    texto = normalizar(pergunta)
    return bool(re.search(
        r"\b(listar|liste|mostre|mostrar|exiba|todos|todas|itens disponiveis|produtos disponiveis|quero itens|quero produtos|retorne os itens)\b",
        texto
    ))


def formatar_listagem(registros):
    return "\n".join(
        " | ".join(
            f"{k}: {v}"
            for k, v in item.items()
            if v is not None
        )
        for item in registros
    )


def rodar_pipeline(pergunta, cancelado=None):
    """cancelado: threading.Event opcional para cancelamento cooperativo."""

    def interrompido():
        return cancelado is not None and cancelado.is_set()

    pergunta = str(pergunta).strip()

    if not pergunta or interrompido():
        return

    if verificar_saudacao(pergunta):
        print("\nOlá! Sou o DB Reader. Como posso te ajudar?")
        return

    if pergunta_sobre_vendas(pergunta):
        print(
            "\nNão há histórico de vendas. Este banco contém "
            "apenas produtos, preços e estoque disponível."
        )
        return

    sql_direto = sql_frequente(pergunta)

    try:
        sql = sql_direto or gerar_sql(
            pergunta, buscar_contexto(pergunta)
        ).strip()

    except Exception:
        LOG.exception("Falha ao gerar SQL ou recuperar RAG")

        if not interrompido():
            print(
                "\nNão foi possível interpretar a pergunta. "
                "Verifique se o Ollama está em execução."
            )
        return

    if interrompido():
        return

    if sql.upper() == "INVALID":
        print(
            "\nNão foi possível relacionar a pergunta "
            "aos dados de produtos e estoque."
        )
        return

    if not validar_sql(sql):
        LOG.error("SQL rejeitado: %s", sql)
        print(
            "\nA consulta gerada não é válida. "
            "Tente descrever a pergunta de outra forma."
        )
        return

    con = cursor = None

    try:
        # Conexão corrigida: utiliza o store.db da pasta sqlite
        con = conectar_banco()
        cursor = con.cursor()

        cursor.execute(sql)

        colunas = (
            [d[0] for d in cursor.description]
            if cursor.description else []
        )

        dados = cursor.fetchall() if colunas else []

    except Exception:
        LOG.exception("Falha ao executar consulta SQL: %s", sql)

        if not interrompido():
            print(
                "\nNão foi possível consultar o banco. "
                "Confira a conexão e o arquivo erro_pipeline.log."
            )
        return

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None:
            con.close()

    if interrompido():
        return

    if not dados:
        print("\nNenhum produto encontrado.")
        return

    registros = [
        dict(zip(colunas, linha))
        for linha in dados
    ]

    if sql_direto or verificar_listagem(pergunta):
        resposta = formatar_listagem(registros)

    else:
        try:
            resposta = explicar(pergunta, registros)

        except Exception:
            LOG.exception("Falha na explicação do Ollama")
            resposta = formatar_listagem(registros)

    if interrompido():
        return

    print("\n" + resposta)

    if interrompido():
        return

    try:
        if (
            input("\nGerar gráfico? (S ou N): ").strip().upper()
            in {"S", "SIM"}
            and not interrompido()
        ):
            gerar_grafico(colunas, dados)

    except (EOFError, KeyboardInterrupt):
        return

    except Exception:
        LOG.exception("Falha ao gerar gráfico")
        print("\nNão foi possível gerar o gráfico.")

    if interrompido():
        return

    try:
        if (
            input("\nExportar CSV? (S ou N): ").strip().upper()
            in {"S", "SIM"}
            and not interrompido()
        ):
            salvar_csv(colunas, dados)

    except (EOFError, KeyboardInterrupt):
        return

    except Exception:
        LOG.exception("Falha ao exportar CSV")
        print("\nNão foi possível exportar o CSV.")
