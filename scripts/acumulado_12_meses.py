import requests
import numpy as np
import pandas as pd

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


df = obter_serie_sgs("433", "01/01/2022")

# Converte o percentual mensal em fator (0,54% vira 1,0054)
df["fator"] = 1 + df["valor"] / 100

# Soma dos logaritmos dos 12 meses e volta com a exponencial
df["acum12"] = (np.exp(np.log(df["fator"]).rolling(12).sum()) - 1) * 100

print(df[["data", "valor", "acum12"]].tail(12))

jan_2023 = df.loc[df["data"] == pd.Timestamp("2023-01-01"), "acum12"]
print(f"Acumulado de jan/2023: {jan_2023.iloc[0]:.4f}%")