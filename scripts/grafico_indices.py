import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

SERIES = {
    "IPCA": "433",
    "INPC": "188",
    "IGP-M": "189",
    "INCC": "7456",
}

CORES = {
    "IPCA": "#1F3A5F",
    "INPC": "#2A9D8F",
    "IGP-M": "#E9A23B",
    "INCC": "#C8553D",
}


def obter_serie_sgs(codigo_serie, data_inicial):

    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados"

    parametros = {
        "formato": "json",
        "dataInicial": data_inicial
    }

    response = requests.get(url, params=parametros, timeout=60)
    response.raise_for_status()

    df = pd.DataFrame(response.json())
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = df["valor"].astype(float)

    return df


def calcular_acumulado_12_meses(df):

    fator = 1 + df["valor"] / 100

    return (np.exp(np.log(fator).rolling(12).sum()) - 1) * 100


resultados = {}

for nome, codigo in SERIES.items():

    df = obter_serie_sgs(codigo, "01/01/2022")
    df["acum12"] = calcular_acumulado_12_meses(df)

    # Mantém só a partir de 2023, quando a janela de 12 meses fica completa
    df = df[df["data"] >= "2023-01-01"]

    resultados[nome] = df

    print(f"{nome}: acumulado de jan/2023 = {df['acum12'].iloc[0]:.4f}%")


inicio = min(df["data"].min() for df in resultados.values())
fim = max(df["data"].max() for df in resultados.values())

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#BBBBBB",
    "xtick.color": "#555555",
    "ytick.color": "#555555",
})

fig, ax = plt.subplots(figsize=(12, 6.5), facecolor="white")
ax.set_facecolor("#FAFAFA")

for nome, df in resultados.items():

    cor = CORES[nome]

    ax.plot(
        df["data"],
        df["acum12"],
        color=cor,
        linewidth=2.2,
        marker="o",
        markersize=4,
        markerfacecolor="white",
        markeredgewidth=1.3,
        label=nome
    )

    # Valor do último mês de cada índice, ao lado da linha
    ultimo = df.iloc[-1]
    ax.annotate(
        f"{ultimo['acum12']:.2f}%",
        xy=(ultimo["data"], ultimo["acum12"]),
        xytext=(9, 0),
        textcoords="offset points",
        color=cor,
        fontsize=10,
        fontweight="bold",
        va="center"
    )

# Espaço à direita para os rótulos não ficarem cortados
ax.set_xlim(inicio, fim + pd.DateOffset(months=4))

ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))

ax.yaxis.grid(True, color="#E5E5E5", linewidth=0.8)
ax.set_axisbelow(True)

ax.set_title(
    f"Inflação acumulada em 12 meses · jan/2023 a {fim:%m/%Y}",
    loc="left",
    fontsize=15,
    fontweight="bold",
    color="#1F1F1F",
    pad=16
)

ax.legend(
    frameon=False,
    ncol=4,
    loc="upper center",
    bbox_to_anchor=(0.5, -0.1)
)

fig.text(
    0.01, 0.01,
    "Fonte: Banco Central do Brasil (SGS)",
    color="#888888",
    fontsize=8
)

fig.tight_layout()
fig.savefig("images/indices_acum12.png", dpi=200, bbox_inches="tight")
plt.show()