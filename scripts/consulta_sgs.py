import requests
import pandas as pd

url = (
    "https://api.bcb.gov.br/dados/serie/"
    "bcdata.sgs.433/dados"
)

parametros = {
    "formato": "json",
    "dataInicial": "01/01/2022"
}

response = requests.get(url, params=parametros, timeout=60)
response.raise_for_status()

dados = response.json()
df = pd.DataFrame(dados)

print(df.head())
print(f"Quantidade de registros: {len(df)}")