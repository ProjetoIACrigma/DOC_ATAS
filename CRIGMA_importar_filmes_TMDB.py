import os
import requests
import pandas as pd
import xlsxwriter
from datetime import datetime

# Chave da API e Token de Leitura da API
api_key = "03020af090346d4c086732a8ff2aac2c"
api_read_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwMzAyMGFmMDkwMzQ2ZDRjMDg6NzMyYThmZjJhYWMyYyIsInN1YiI6IjY0ZWI8N2MzNTk0Yzk0MDEzOWM5ODIzMiIsInSjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.noHUylNifHPrvslKZd240Ijz_Y8YddlAHfk8I5fb8gw"

# URL base da API do The Movie Database
base_url = "https://api.themoviedb.org/3"

# Buscar filmes em português do Brasil
limite_filmes = 10000
linguagem = "pt-BR"
contador_filmes = 1

# Função para obter a URL completa da imagem do campo poster_path
def obter_url_imagem(poster_path):
    base_imagem_url = "https://image.tmdb.org/t/p/w600_and_h900_bestv2/"
    return base_imagem_url + poster_path if poster_path else ""

# Função para formatar a data no formato brasileiro
#def formatar_data_br(data):
#    if data:
#        data_obj = datetime.strptime(data, "%Y-%m-%d")
#        return data_obj.strftime("%d-%m-%Y")
#    return ""


# Função para converter a data em um timestamp UNIX
def converter_data_para_numero(data):
    try:
        if data:
            data_obj = datetime.strptime(data, "%Y-%m-%d")
            
            #timestamp = int(data_obj.timestamp())
            return data_obj.strftime("%d-%m-%Y")
    except (ValueError, TypeError):
        pass  # Ignorar datas inválidas ou nulas
    return None  # Ou outro valor adequado para datas ausentes


# Função para converter o campo runtime em horas e minutos
def converter_runtime(runtime):
    if runtime:
        horas = runtime // 60
        minutos = runtime % 60
        return f"{horas}h {minutos}min"
    return ""

# Função para formatar números com pontos e vírgulas
def formatar_numero(valor):
    if valor is not None:
        try:
            # Converter para float e formatar com pontos e vírgulas
            return "{:,.2f}".format(float(valor)).replace(",", "X").replace(".", ",").replace("X", ".")
        except ValueError:
            return valor
    return ""

# Função para obter as três primeiras keywords
def obter_tres_primeiras_keywords(keywords):
    if "keywords" in keywords and isinstance(keywords["keywords"], list):
        keyword_names = [keyword["name"] for keyword in keywords["keywords"][:3]]
        return ", ".join(keyword_names)
    return ""

# Função para obter os nomes dos gêneros separados por vírgula
def obter_nomes_generos(genres):
    if isinstance(genres, list):
        genre_names = [genre["name"] for genre in genres]
        return ", ".join(genre_names)
    return ""

# Função para buscar detalhes de filmes
def buscar_detalhes_filme(filme_id):
    url = f"{base_url}/movie/{filme_id}"
    params = {
        "api_key": api_key,
        "append_to_response": "keywords",  # Apenas "keywords" é necessário
        "language": linguagem
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Falha ao buscar detalhes para o filme com ID {filme_id}. Código de Status: {response.status_code}")
        return None

# Função para buscar os diretores de um filme
def buscar_diretores(filme_id):
    url = f"{base_url}/movie/{filme_id}/credits"
    params = {
        "api_key": api_key,
        "language": linguagem
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        credits = response.json()
        directors = [credit["name"] for credit in credits ["crew"][:3] if credit["job"] == "Director"]
        return ", ".join(directors)
    else:
        print(f"Falha ao buscar diretores para o filme com ID {filme_id}. Código de Status: {response.status_code}")
        return ""

# Função para buscar os principais atores de um filme
def buscar_principais_atores(filme_id, limite=5):
    url = f"{base_url}/movie/{filme_id}/credits"
    params = {
        "api_key": api_key,
        "language": linguagem
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        credits = response.json()
        cast = [actor["name"] for actor in credits["cast"][:limite]]
        return ", ".join(cast)
    else:
        print(f"Falha ao buscar atores para o filme com ID {filme_id}. Código de Status: {response.status_code}")
        return ""

# Função para buscar os filmes populares com limite de resultados
def buscar_filmes_populares(limit):
    filmes = []
    page = 1
    while len(filmes) < limit:
        url = f"{base_url}/movie/popular"
        params = {
            "api_key": api_key,
            "page": page,
            "language": linguagem
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            resultados = response.json()["results"]
            if not resultados:
                break  # Nenhum resultado encontrado, sair do loop
            filmes.extend(resultados)
            page += 1
        else:
            print(f"Falha ao buscar filmes na página {page}. Código de Status: {response.status_code}")
            break  # Erro na resposta da API, sair do loop
    return filmes[:limit]  # Retornar apenas os primeiros 'limit' filmes

# Construir o caminho completo para o arquivo XLSX
arquivo_xlsx = os.path.join("C:\IA\dados_filmes.xlsx")

filmes_populares = buscar_filmes_populares(limit=limite_filmes)

# Criar um arquivo XLSX
workbook = xlsxwriter.Workbook(arquivo_xlsx)
worksheet = workbook.add_worksheet()

# Definir os cabeçalhos
colunas = ["release_date", "title", "genres", "director", "actors", "popularity", "budget", "revenue", "runtime",
           "vote_average", "vote_count", "keywords", "overview", "poster_path"]

# Escrever os cabeçalhos na primeira linha
for col_num, cabecalho in enumerate(colunas):
    worksheet.write(0, col_num, cabecalho)

# Iniciar a linha na planilha
linha = 1

# Preencher os detalhes dos filmes e imprimir no terminal
for filme in filmes_populares:
    detalhes_filme = buscar_detalhes_filme(filme["id"])
    if detalhes_filme:
        dados_filme = []

        # Preencher os dados do filme
        for coluna in colunas:
            if coluna == "director":
                dados_filme.append(buscar_diretores(filme["id"]))
            elif coluna == "actors":
                dados_filme.append(buscar_principais_atores(filme["id"]))
            elif coluna == "poster_path":
                dados_filme.append(obter_url_imagem(detalhes_filme["poster_path"]))
            elif coluna == "keywords":
                dados_filme.append(obter_tres_primeiras_keywords(detalhes_filme.get("keywords", {})))
            elif coluna == "genres":
                dados_filme.append(obter_nomes_generos(detalhes_filme.get("genres", [])))
            elif coluna in ["budget", "revenue"]:
                dados_filme.append(formatar_numero(detalhes_filme.get(coluna, "")))
            elif coluna == "release_date":
                dados_filme.append(converter_data_para_numero(detalhes_filme.get("release_date", "")))
            elif coluna == "runtime":
                dados_filme.append(converter_runtime(detalhes_filme.get("runtime", "")))
            else:
                # Verificar se a coluna existe nos detalhes do filme
                if coluna in detalhes_filme:
                    # Converter listas em strings
                    if isinstance(detalhes_filme[coluna], list):
                        dados_filme.append(", ".join(map(str, detalhes_filme[coluna])))
                    # Converter dicionários em strings
                    elif isinstance(detalhes_filme[coluna], dict):
                        dados_filme.append(str(detalhes_filme[coluna]))
                    else:
                        dados_filme.append(detalhes_filme[coluna])
                else:
                    dados_filme.append("")  # Coluna ausente, preencher com string vazia

        # Imprimir detalhes do filme no terminal com a contagem
        print(f"{contador_filmes}:\t{filme['title']}")
        contador_filmes += 1

        # Escrever os dados do filme na planilha
        for col_num, dado in enumerate(dados_filme):
            worksheet.write(linha, col_num, dado)
        linha += 1
    else:
        print(f"Falha ao buscar detalhes para o filme com ID {filme['id']}")

# Salvar o arquivo XLSX
workbook.close()

print(f"\n{limite_filmes} filmes \nSalvos em: '{arquivo_xlsx}'\n")