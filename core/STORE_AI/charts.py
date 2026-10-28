from pathlib import Path
from datetime import datetime
from decimal import Decimal
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PASTA_GRAFICOS = Path.home() / "Downloads"
LIMITE_CATEGORIAS = 25
TEMA = "plotly_dark"

IDENTIFICADORES = {"id", "codigo", "codigo_produto",}

PRIORIDADE_NUMERICA = [
    "estoque_total",
    "total_estoque",
    "quantidade",
    "valor_total_estoque",
    "preco",
    "preco_unitario",
]

PRIORIDADE_CATEGORICA = ["produto", "marca", "modelo",]

def preparar_dados(colunas, dados):

    df = pd.DataFrame(dados, columns=colunas)
    if df.empty:
        return df


    for coluna in df.columns:
        if df[coluna].map(lambda valor: isinstance(valor, Decimal)).any():
            df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    return df

def classificar_colunas(df):

    numericas = []
    categorias = []
    for coluna in df.columns:
        nome = str(coluna).lower()
        if nome in IDENTIFICADORES:
            continue
        if pd.api.types.is_numeric_dtype(df[coluna]):
            numericas.append(coluna)
        else:
            categorias.append(coluna)
    return numericas, categorias

def ordenar_prioridade(colunas, prioridades):

    return sorted(
        colunas,
        key=lambda coluna: (
            prioridades.index(str(coluna).lower())
            if str(coluna).lower() in prioridades
            else len(prioridades)
        )
    )

def nome_legivel(nome):
    return str(nome).replace("_", " ").capitalize()

def medida_aditiva(coluna):

    nome = str(coluna).lower()
    return nome in {
        "quantidade",
        "estoque_total",
        "total_estoque",
        "valor_total_estoque",
        "valor_estoque",
        "total_unidades",
    }

def criar_indicador(df, coluna):

    valor = df[coluna].iloc[0]
    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=float(valor),
            title={
                "text": nome_legivel(coluna)
            },
            number={
                "valueformat": ",.2f"
            }
        )
    )
    fig.update_layout(template=TEMA, height=400, title="Resultado da consulta")
    return fig

def criar_histograma(df, coluna):

    fig = px.histogram(
        df,
        x=coluna,
        nbins=min(20, max(5, len(df) // 2)),
        title=f"Distribuição de {nome_legivel(coluna)}",
        template=TEMA,
        labels={
            coluna: nome_legivel(coluna)
        }
    )
    return fig

def criar_lista(df, coluna):

    valores = (df[coluna] .fillna("Não informado") .astype(str) .head(50) .tolist())
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=[nome_legivel(coluna)],
                    fill_color="#253247",
                    font=dict(
                        color="white",
                        size=15
                    ),
                    align="left"
                ),
                cells=dict(
                    values=[valores],
                    fill_color="#161e2e",
                    font=dict(
                        color="white",
                        size=12
                    ),
                    align="left",
                    height=30
                )
            )
        ]
    )
    fig.update_layout(
        title=f"Lista de {nome_legivel(coluna)}",
        template=TEMA,
        height=max(350, len(valores) * 30 + 120)
    )
    return fig

def criar_barras(df, categoria, valor):

    dados = df[[categoria, valor]].copy()
    dados = dados.dropna(subset=[valor])
    if medida_aditiva(valor):
        dados = (dados.groupby(categoria, as_index=False, dropna=False)[valor] .sum())
    dados = (dados.sort_values(valor, ascending=False) .head(LIMITE_CATEGORIAS))
    fig = px.bar(
        dados,
        x=valor,
        y=categoria,
        orientation="h",
        text_auto=True,
        title=f"{nome_legivel(valor)} por {nome_legivel(categoria)}",
        template=TEMA
    )
    fig.update_layout(
        height=max(450, len(dados) * 35),
        yaxis={
            "categoryorder": "total ascending"
        }
    )
    return fig

def criar_barras_agrupadas(df, categoria1, categoria2, valor):

    dados = df[[categoria1, categoria2, valor]].copy()
    dados = dados.dropna(subset=[valor])
    if medida_aditiva(valor):
        dados = (
            dados.groupby(
                [categoria1, categoria2],
                as_index=False,
                dropna=False
            )[valor]
            .sum()
        )
    dados = (dados.sort_values(valor, ascending=False) .head(LIMITE_CATEGORIAS))
    fig = px.bar(
        dados,
        x=categoria1,
        y=valor,
        color=categoria2,
        barmode="group",
        title=(
            f"{nome_legivel(valor)} por "
            f"{nome_legivel(categoria1)} e "
            f"{nome_legivel(categoria2)}"
        ),
        template=TEMA,
        hover_data=[categoria1, categoria2, valor]
    )
    fig.update_layout(height=650, xaxis_tickangle=-35)
    return fig

def criar_dispersao(df, numero1, numero2, categoria=None):

    colunas = [numero1, numero2]
    if categoria is not None:
        colunas.append(categoria)
    dados = df[colunas].copy()
    dados = dados.dropna(subset=[numero1, numero2])
    argumentos = {
        "data_frame": dados,
        "x": numero1,
        "y": numero2,
        "title": (
            f"{nome_legivel(numero2)} × "
            f"{nome_legivel(numero1)}"
        ),
        "template": TEMA,
        "hover_data": colunas
    }
    if categoria is not None:
        argumentos["color"] = categoria
    fig = px.scatter(**argumentos)
    fig.update_traces(marker=dict(size=12, opacity=0.8))
    fig.update_layout(height=600)
    return fig

def criar_tabela(df):

    dados = df.head(40).copy()
    for coluna in dados.columns:
        dados[coluna] = (dados[coluna] .fillna("Não informado") .astype(str))
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(dados.columns),
                    fill_color="#253247",
                    font=dict(
                        color="white",
                        size=13
                    ),
                    align="left"
                ),
                cells=dict(
                    values=[
                        dados[coluna].tolist()
                        for coluna in dados.columns
                    ],
                    fill_color="#161e2e",
                    font=dict(
                        color="white",
                        size=11
                    ),
                    align="left",
                    height=28
                )
            )
        ]
    )
    fig.update_layout(
        title="Dados da consulta",
        template=TEMA,
        height=max(400, len(dados) * 28 + 120)
    )
    return fig

def selecionar_grafico(df):

    numericas, categorias = classificar_colunas(df)
    numericas = ordenar_prioridade(numericas, PRIORIDADE_NUMERICA)
    categorias = ordenar_prioridade(categorias, PRIORIDADE_CATEGORICA)
    qtd_num = len(numericas)
    qtd_cat = len(categorias)


    if qtd_num == 1 and qtd_cat == 0:
        if len(df) == 1:
            return criar_indicador(df, numericas[0])
        return criar_histograma(df, numericas[0])


    if qtd_num == 0 and qtd_cat == 1:
        return criar_lista(df, categorias[0])
    if qtd_num == 0:
        return criar_tabela(df)


    if qtd_num == 1 and qtd_cat == 1:
        return criar_barras(df, categorias[0], numericas[0])


    if qtd_num == 1 and qtd_cat >= 2:
        return criar_barras_agrupadas(df, categorias[0], categorias[1], numericas[0])


    if qtd_num >= 2 and qtd_cat >= 1:
        return criar_dispersao(df, numericas[0], numericas[1], categorias[0])


    if qtd_num >= 2:
        return criar_dispersao(df, numericas[0], numericas[1])
    return criar_tabela(df)

def gerar_grafico(colunas, dados):

    try:
        df = preparar_dados(colunas, dados)
        if df.empty:
            print("\nNão existem dados para gerar o gráfico.")
            return
        fig = selecionar_grafico(df)
        PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)
        data_hora = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        caminho = (PASTA_GRAFICOS / f"grafico_{data_hora}.png")
        altura = fig.layout.height or 600
        fig.write_image(str(caminho), width=1400, height=int(altura), scale=2)
        print(f"\nGráfico salvo em: {caminho}")


        if os.name == "nt":
            try:
                os.startfile(str(caminho))
            except OSError:
                print("\nA imagem foi salva, mas não " "foi possível abri-la automaticamente.")
        return caminho
    except Exception:
        print(
            "\nNão foi possível gerar a visualização. "
            "Verifique os dados e as dependências "
            "do Plotly/Kaleido."
        )
        return None
