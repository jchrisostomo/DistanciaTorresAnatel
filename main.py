import PySimpleGUI as sg
import os
import pandas as pd
import alive_progress
from geopy import distance
from alive_progress import alive_bar

def carregar_anatel(arquivo):
    df = pd.read_csv(arquivo, encoding ="latin-1")
    df = df[["NomeEntidade", "NumEstacao","DataPrimeiroLicenciamento", "Latitude", "Longitude"]]
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

def relatorio_distancias(origem, destino):
    # Constantes
    RAIO = 100

    # Configuração dos arquivos
    print(origem)
    print(destino)
    print("Diretório: OK")

    # Carregar arquivos no dataframe
    tblDestino = carregar_anatel(destino)
    tblOrigem = carregar_torres(origem)
    print("Carregamento: OK")
    tblDestino = normalizar_lat_long(tblDestino)
    tblOrigem = normalizar_lat_long(tblOrigem)
    print("Normalização: OK")

    # Limpar relatorio.txt
    with open('relatorio.txt', 'w') as file:
        file.write('')
    print("Limpar relatório: OK")
    # criar uma lista de índices para percorrer com um loop for
    indices_origem = tblOrigem.index.tolist()

    # usar o alive_bar para criar a barra de progresso
    # with alive_bar(len(indices_origem), force_tty=True) as bar:
    # Loop através das localidades de origem
    for i in indices_origem:
        # Seleciona a localidade de origem
        origem = tblOrigem.loc[i]

        # Contador
        print(f"Progresso: {i + 1} / {len(indices_origem)}")

        # Lista para armazenar as distâncias
        distancias = []

        with alive_bar(len(tblDestino), force_tty=True) as bar:
            # Loop através das localidades de destino
            for j, destino in tblDestino.iterrows():
                # Calcula a distância entre as coordenadas
                distancia = calcular_distancia((origem['Latitude'], origem['Longitude']),
                                               (destino['Latitude'], destino['Longitude']))
                # Armazena o nome e a distância da localidade de destino na lista
                distancias.append((destino['NomeEntidade'], destino['NumEstacao'], destino['DataPrimeiroLicenciamento'], distancia))
                bar()

        # Filtra as distâncias para as menores que um raio de x metros
        distancias_raio = [(nome, numero, data, dist) for (nome, numero, data, dist) in distancias if dist <= RAIO]

        # Imprime o relatório em um arquivo
        relatorio = 40 * "#" + "\n"
        relatorio += f"Localidade de origem: {origem['ID']}  {origem['Nome']}\n"

        if len(distancias_raio) > 0:
            relatorio += f"Distâncias de até: {RAIO} metros \n"
            relatorio += 40 * "-" + "\n"
            for (nome, numero, data, dist) in distancias_raio:
                relatorio += f"{nome} - {data} - {numero}: {dist:.2f} metros\n"
        else:
            relatorio += "Não há localidades de destino a menos de 100m\n"
        relatorio += 40 * "-" + "\n"
        relatorio += "\n"

        # Imprime o relatório no console e em um arquivo de texto
        print(relatorio)

        with open("relatorio.txt", "a") as f:
            f.write(relatorio)



# Seleciona o diretório atual
diretorio = os.getcwd()

#  Layout da janela
layout = [
    [sg.Text("Selecione a planilha de torres:")],
    [sg.InputText(key="-CAMINHO_TORRES-"),
     sg.FileBrowse(initial_folder=diretorio, file_types=(("Arquivo XLSX"), "*.xlsx"))],
    [sg.Text("Selecione a planilha de torres da ANATEL:")],
    [sg.InputText(key="-CAMINHO_ANATEL-"),
     sg.FileBrowse(initial_folder=diretorio, file_types=(("Arquivo CSV"), "*.csv"))],
    [sg.Button("Gerar relatório"), sg.Exit("Sair")]
]

nomeApp = 'Relatório de Distâncias entre Torres'

# Construir janela
window = sg.Window(nomeApp, layout, size=(600, 150))

# Cabeçalho
print(42 * "#")
print(2 * "#" + nomeApp.center(38) + 2 * "#")
print(42 * "#")
print(2 * "#" + "SQUAD AUTOMAÇÃO".center(38) + 2 * "#")
print(2 * "#" + "Gerência de Facilities".center(38) + 2 * "#")
print(42 * "#")
print(2 * "#" + "João Chrisóstomo Ribeiro Abegão".center(38) + 2 * "#")
print(42 * "#")

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Sair":
        break
    elif event == "Gerar relatório":
        print(values["-CAMINHO_TORRES-"])
        print(values["-CAMINHO_ANATEL-"])
        relatorio_distancias(values["-CAMINHO_TORRES-"], values["-CAMINHO_ANATEL-"])

window.close()
