import pandas as pd
import alive_progress
from geopy import distance
from alive_progress import alive_bar

def carregar_anatel(arquivo):
    df = pd.read_csv(arquivo, encoding ="latin-1")
    df = df[["NomeEntidade", "NumEstacao", "Latitude", "Longitude"]]
    df = df.drop_duplicates(subset=["NumEstacao"])
    return df

def carregar_torres(arquivo):
    df = pd.read_excel(arquivo)
    return df

def normalizar_lat_long(df):
    df = df[df["Latitude"] > -90]
    df = df[df["Longitude"] > -90]
    return df

def gerar_coordendas(df):
    df['Coordenadas'] = list(zip(df['Latitude'], df['Longitude']))
    return df

def calcular_distancia(coordenada1, coordenada2):
    return distance.distance(coordenada1, coordenada2).m

# Constantes
RAIO = 100

# Configuração dos arquivos
arquivoDestino = "data/anatel.csv"
arquivoOrigem = "data/torres.xlsx"

# Carregar arquivos no dataframe
tblDestino = carregar_anatel(arquivoDestino)
tblOrigem = carregar_torres(arquivoOrigem)
print("Carregamento OK")
tblDestino = normalizar_lat_long(tblDestino)
tblOrigem = normalizar_lat_long(tblOrigem)
print("Normalização OK")

# Limpar relatorio.txt
with open('relatorio.txt', 'w') as file:
    file.write('')




# criar uma lista de índices para percorrer com um loop for
indices_origem = tblOrigem.index.tolist()

# usar o alive_bar para criar a barra de progresso
with alive_bar(len(indices_origem), force_tty=True) as bar:
    # Loop através das localidades de origem
    for i in indices_origem:
        # Seleciona a localidade de origem
        origem = tblOrigem.loc[i]

        # Lista para armazenar as distâncias
        distancias = []

        # Loop através das localidades de destino
        for j, destino in tblDestino.iterrows():
            # Calcula a distância entre as coordenadas
            distancia = calcular_distancia((origem['Latitude'], origem['Longitude']),
                                           (destino['Latitude'], destino['Longitude']))
            # Armazena o nome e a distância da localidade de destino na lista
            distancias.append((destino['NomeEntidade'], distancia))

        # Filtra as distâncias para as menores que um raio de x metros
        distancias_raio = [(nome, dist) for (nome, dist) in distancias if dist <= RAIO]

        # Imprime o relatório em um arquivo
        relatorio = 40 * "-" + "\n"
        relatorio += f"Localidade de origem: {origem['ID']}  {origem['Empresa']}\n"

        if len(distancias_raio) > 0:
            relatorio += f"Distâncias de até: {RAIO} metros \n"
            relatorio += 40 * "-" + "\n"
            for (nome, dist) in distancias_raio:
                relatorio += f"{nome}: {dist:.2f}m\n"
        else:
            relatorio += "Não há localidades de destino a menos de 100m\n"
        relatorio += 40 * "-" + "\n"

        # Imprime o relatório no console e em um arquivo de texto
        print(relatorio)

        with open("relatorio.txt", "a") as f:
            f.write(relatorio)

        bar()  # atualiza a barra de progresso

