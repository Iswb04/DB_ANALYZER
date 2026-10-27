from TCC.STORE_AI.llm import gerar_sql
from TCC.STORE_AI.rag import buscar_contexto
from TCC.DB.create import conectar
from TCC.STORE_AI.charts import gerar_grafico
from TCC.STORE_AI.exports import salvar_csv


def rodar_pipeline(pergunta):

    # 1. Busca contexto no RAG
    contexto = buscar_contexto(pergunta)

    # 2. IA gera a SQL
    sql = gerar_sql(
        pergunta,
        contexto
    )

    # 3. Validação básica de segurança
    if not sql.lower().strip().startswith("select"):
        print(
            "\nNão foi possível realizar essa consulta."
        )
        return

    # 4. Conecta ao banco
    con = conectar("store")
    cursor = con.cursor()

    try:

        # 5. Executa SQL
        cursor.execute(sql)

        if cursor.description:

            colunas = [
                desc[0]
                for desc in cursor.description
            ]

            dados = cursor.fetchall()

        else:

            colunas = []
            dados = []

        # 6. Fecha conexão
        con.close()

        # 7. Verifica se encontrou dados
        if not dados:

            print(
                "\nNão foram encontrados dados para essa pergunta."
            )

            return

    except Exception as e:

        con.close()

        print(
            "\033[31m"
            "\nOcorreu um erro. Por favor, reformule sua pergunta."
            "\033[0m"
        )

        print(
            f"\033[31mErro técnico:\033[0m {e}"
        )

        return

    # 8. Formata os dados
    dados_formatados = [
        dict(
            zip(
                colunas,
                linha
            )
        )
        for linha in dados
    ]

    # 9. Gera resposta natural
    from TCC.STORE_AI.llm import llm_exp

    prompt = f"""
Você é um assistente de análise de dados.

Responda à pergunta do usuário de forma natural,
direta e curta, usando exclusivamente os dados
retornados pelo banco.

REGRAS:

- Responda em português.
- Não comece com "Com base nos dados fornecidos".
- Não comece com "Os dados mostram".
- Não diga "podemos observar".
- Não repita a pergunta.
- Não faça introduções desnecessárias.
- Não invente informações.
- Use no máximo 2 frases.
- Dê destaque ao principal resultado.

Pergunta do usuário:
{pergunta}

Dados retornados pelo banco:
{dados_formatados}

Resposta:
"""

    resposta = llm_exp.invoke(
        prompt
    )

    # 10. Mostra a resposta
    print(
        f"\n{resposta}"
    )

    # 11. Pergunta sobre gráfico
    if input(
        "\nGerar gráfico? (S ou N): "
    ).upper() in ["S", "SIM"]:

        gerar_grafico(
            colunas,
            dados
        )

    # 12. Pergunta sobre CSV
    if input(
        "\nExportar CSV? (S ou N): "
    ).upper() in ["S", "SIM"]:

        salvar_csv(
            colunas,
            dados
        )