import matplotlib
matplotlib.use('Agg')
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from itertools import count
from datetime import datetime

def gerar_grafico(colunas, dados):
    df = pd.DataFrame(dados, columns=colunas)

    if len(df.columns) < 2:
        print("Dados insuficientes para gráfico! Contém menos de duas colunas.")
        return

    pasta = "TCC/DOWNLOADS"
    os.makedirs(pasta, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d")

    for i in count(1):
        caminho = os.path.join(pasta, f"grafico{i}_{timestamp}.png")
        if not os.path.exists(caminho):
            break

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    sns.barplot(
        data=df,
        x=df.columns[0],
        y=df.columns[1]
    )

    plt.title("Gráfico de Dados")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(caminho)
    plt.close()

    print(f"Gráfico salvo em: {caminho}")