# Importações e comandos de instalação
from flask import Flask, render_template, request   # pip install Flask  - Framework web para criação de aplicativos web.
import pandas as pd                                 # pip install pandas - Manipulação de dados e arquivos.
from fuzzywuzzy import fuzz, process                # pip install fuzzywuzzy - Biblioteca para comparação de strings.
import pickle                                       # Biblioteca para serialização de objetos Python.
import webbrowser                                   # Biblioteca para abrir URLs em um navegador.
import cx_Oracle                                    # pip install cx_Oracle - Conexão e interação com bancos de dados Oracle.
import json
import random

# pip install python-Levenshtein

app = Flask(__name__, template_folder='.')

# Abrie e ler o arquivo JSON
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

user = config["database"]["user"]
password = config["database"]["password"]
host = config["database"]["host"]
port = config["database"]["port"]
service_name = config["database"]["service_name"]

# Função para conectar ao Oracle e buscar os dados
def fetch_data_from_oracle():
    # Informações de conexão Oracle XE Buscando do JSON
    dsn_tns = cx_Oracle.makedsn(host, port, service_name)
    conn = cx_Oracle.connect(user=user, password=password, dsn=dsn_tns)
   
    # Consulta SQL para buscar os dados
    query = "SELECT * FROM FILMES_PTBR"
    df = pd.read_sql(query, con=conn)

    conn.close() 
    #print(df) 

    return df

# Carregar os dados dos filmes do Oracle
df2 = fetch_data_from_oracle()

# Carregar os dados do pickle (se necessário)
with open('C:\IA\data.pkl', 'rb') as f:
    data = pickle.load(f)
    similaridade = data['cosine_sim']
    indices = data['indices']

# Dicionário que mapeia os índices de volta para os títulos originais
indices_to_titles = {v: k for k, v in indices.items()}



# Função consolidada para obter recomendações com base no título ou na similaridade
def get_recommendations(input_title, similaridade, df):
    print("input_title: ", input_title)
    input_title = input_title.strip()       # Remove espaços em branco extras no título de entrada
    movies = [title for title in indices]   # Cria uma lista de todos os títulos de filmes disponíveis no índice


    # Pesquisa por nome (título exato ou semelhante)
    # BASICAMENTE UM SELECT NO DATA PICKLE atraves de FUZZY por palavra parcial, busca parte do texto no Piclke
    name_matches = process.extract(input_title, movies, scorer=fuzz.partial_ratio)
    name_matches = sorted(name_matches, key=lambda x: x[1], reverse=True)
    print("name_matches: ", name_matches)

    # Filtra os resultados que tenham pelo menos 70% de similaridade (ajustar necessário)
    filtered_name_matches = [match for match in name_matches if match[1] >= 70]
    print("filtered_name_matches: ", filtered_name_matches)

    if filtered_name_matches:
        # Se houver resultados com pelo menos 70% de similaridade no nome, retorne até 10 melhores
        top_names = filtered_name_matches[:10]
        top_indices = [indices[match[0]] for match in top_names]
        sim_scores = None  # Define sim_scores como None para evitar o erro posterior
    else:
        # Caso contrário, retorne os 10 melhores resultados com base na similaridade
        if similaridade is not None:
            sim_scores = similaridade.mean(axis=0)  # Defina sim_scores aqui
            top_indices = sorted(range(len(sim_scores)), key=lambda i: sim_scores[i], reverse=True)
            top_indices = [i for i in top_indices if i not in indices_list]
            top_indices = top_indices[:10]
        else:
            top_indices = []

    # Se ainda não houver 10 resultados, complete com recomendações de similaridade
    if len(top_indices) < 10 and sim_scores is not None:
        remaining_indices = [i for i in range(len(sim_scores)) if i not in top_indices]
        remaining_indices = sorted(remaining_indices, key=lambda i: sim_scores[i], reverse=True)
        remaining_indices = remaining_indices[:10 - len(top_indices)]
        top_indices.extend(remaining_indices)

    top_filmes = df.iloc[top_indices]
    result = top_filmes.to_dict(orient='records')

    return result


# Rota principal
@app.route('/', methods=['GET', 'POST'])
def index():
    tabela_html = None
    if request.method == 'POST':
        input_list = request.form.get('input_list')
        input_list = input_list.split(',')
        nomes_filmes = []

        # Verifique se há apenas um elemento na lista
        if len(input_list) == 1:
            movie_title = get_recommendations(input_list[0].strip(), similaridade, df2)
            if movie_title is not None:
                nomes_filmes.extend(movie_title)
        else:
            for title in input_list:
                movie_title = get_recommendations(title.strip(), similaridade, df2)
                if movie_title is not None:
                    nomes_filmes.extend(movie_title)

        if nomes_filmes:
            # Inicialize a tabela HTML
            tabela_html = '<table>'
            count = 0  # Contador para controlar as colunas

            for filme in nomes_filmes:
                # Abra uma nova linha a cada 5 filmes
                if count % 5 == 0:
                    tabela_html += '<tr>'

                # Adicione uma célula para o filme atual
                tabela_html += '<td>'
                tabela_html += f'<img src="{filme["POSTER_PATH"]}" alt="{filme["TITLE"]}" width="100">'
                tabela_html += f'<p>{filme["TITLE"]}</p>'
                tabela_html += '</td>'

                count += 1  # Incrementar o contador de filmes

                # Feche a linha a cada 5 filmes ou na última iteração
                if count % 5 == 0 or count == len(nomes_filmes):
                    tabela_html += '</tr>'

            # Feche a tabela HTML
            tabela_html += '</table>'
        else:
            tabela_html = '<p>Nenhum resultado encontrado.</p>'

    return render_template('index.html', tabela_html=tabela_html)

if __name__ == '__main__':
    # URL da página que você deseja abrir
    url = 'http://localhost:80'

    # Abre a URL no navegador padrão
    webbrowser.open(url, new=2)
    
    # Alterar o host para que ele escute em todas as interfaces de rede
    app.run(port=80, host='0.0.0.0', debug=False)
