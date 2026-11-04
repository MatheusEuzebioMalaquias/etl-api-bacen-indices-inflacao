import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados"
parametros = {"formato": "json", "dataInicial": "01/01/2022"}

response = requests.get(url, params=parametros, timeout=60)
response.raise_for_status()

df = pd.DataFrame(response.json())
df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
df["valor"] = df["valor"].astype(float)

df["fator"] = 1 + df["valor"] / 100
df["acum12"] = (np.exp(np.log(df["fator"]).rolling(12).sum()) - 1) * 100

# Mostra só a partir de 2023, quando o acumulado de 12 meses fica completo
df = df[df["data"] >= "2023-01-01"]

plt.figure(figsize=(10, 5))
plt.plot(df["data"], df["acum12"], color="#1f77b4", linewidth=2)
plt.title("IPCA: acumulado em 12 meses")
plt.ylabel("%")
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("images/ipca_acum12.png", dpi=150)
plt.show()