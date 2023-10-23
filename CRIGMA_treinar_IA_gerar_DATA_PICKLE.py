import pandas as pd
import numpy as np
import cx_Oracle
import json
import pickle
import re
import unidecode
from sklearn.feature_extraction.text import CountVectorizer  # Importe CountVectorizer


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
    # Informações de conexão Oracle
    dsn_tns = cx_Oracle.makedsn(host, port, service_name)
    conn = cx_Oracle.connect(user=user, password=password, dsn=dsn_tns)

    # Consulta SQL para buscar os dados
    query = "SELECT * FROM FILMES_PTBR"
    df = pd.read_sql(query, con=conn)

    conn.close() 
    print(df) 

    return df

#################################TRATANDO OS DADOS########################################
# vamos usar as colunas genero e etc não apenas o resumo do filme
# passando as colunas str para array
df2 = fetch_data_from_oracle()
#print(df2)

from ast import literal_eval
#'RELEASE_DATE','TITLE','GENRES','DIRECTOR','ACTORS','POPULARITY','BUDGET','REVENUE','RUNTIME','VOTE_AVERAGE','VOTE_COUNT','KEYWORDS','OVERVIEW','POSTER_PATH'

features = ['RELEASE_DATE','TITLE','GENRES','DIRECTOR','ACTORS','KEYWORDS','OVERVIEW']

# Function to convert all strings to lower case and strip names of spaces
# Função para converter todas as strings para minúsculas e retirar nomes de espaços
def clean_data(x):
    if isinstance(x, list):
        return [clean_data(item) for item in x]
    elif isinstance(x, str):
        # Substitui vírgulas por espaços
        cleaned_str = x.replace(",", " ")                           # Remove espaços extras
        cleaned_str = re.sub(r'\s+', ' ', cleaned_str).strip()      # Remove acentos e deixa apenas letras sem acentuação
        #cleaned_str = unidecode.unidecode(cleaned_str)             # Remove acentos
        #cleaned_str = re.sub(r'[^a-zA-Z\s]', '', cleaned_str)      # Remove caracteres não alfabéticos
        #cleaned_str = str.lower(cleaned_str)                       # Converte para Minusculo
        return cleaned_str
    else:
        return ''

        # Apply clean_data function to your features.
        # Aplique a função clean_data aos seus recursos.
features = ['RELEASE_DATE','TITLE','GENRES','DIRECTOR','ACTORS','KEYWORDS','OVERVIEW']
for feature in features:
    df2[feature] = df2[feature].apply(clean_data)


#for feature in features:
#    df2[feature] = df2[feature].apply(literal_eval)

# Função para criar o atributo "soup" com base nas colunas especificadas em features
# Função para criar o atributo "soup" com base nas colunas especificadas em features
def create_soup(x):
    return (
        str(x['RELEASE_DATE']) + ' ' +
        ''.join(x['TITLE']) + ' ' +
        ''.join(x['GENRES']) + ' ' +
        ''.join(x['DIRECTOR']) + ' ' +
        ''.join(x['ACTORS']) + ' ' +
        ''.join(x['KEYWORDS']) + ' ' +
        ''.join(x['OVERVIEW'])
    )



# Aplicar a função create_soup para criar o atributo "soup" no DataFrame
df2['soup'] = df2.apply(create_soup, axis=1)

print("Soup")
print("\n")
print(df2['soup'])

### TRATAR SOUP PARA COSINE

# Importe CountVectorizer e crie a matriz de contagem
from sklearn.feature_extraction.text import CountVectorizer

# Stop words em português, Ignora essas palabras quando for gerar a MATRIZ de SIMILARIDADE
stop_words_portuguese = ["de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "é", "com", 
                         "não", "uma", "os", "no", "se", "na", "por", "mais", "as", "dos", "como", 
                         "mas", "ao", "ele", "das", "à", "seu", "sua", "ou", "quando", "muito", 
                         "nos", "já", "eu", "também", "só", "pelo", "pela", "até", "isso", 
                         "ela", "entre", "depois", "sem", "mesmo", "aos", "seus", "quem", "nas", 
                         "me", "esse", "eles", "você", "essa", "num", "nem", "suas", "meu", "às", 
                         "minha", "numa", "pelos", "elas", "qual", "nós", "lhe", "deles", "essas", 
                         "esses", "pelas", "este", "dele", "tu", "te", "vocês", "vos", "lhes", 
                         "meus", "minhas", "teu", "tua", "teus", "tuas", "nosso", "nossa", 
                         "nossos", "nossas", "dela", "delas", "esta", "estes", "estas", "aquele", 
                         "aquela", "aqueles", "aquelas", "isto", "aquilo", "estou", "está", "estamos", 
                         "estão", "estive", "esteve", "estivemos", "estiveram", "estava", "estávamos", 
                         "estavam", "estivera", "estivéramos", "esteja", "estejamos", "estejam", "estivesse", 
                         "estivéssemos", "estivessem", "estiver", "estivermos", "estiverem", "hei", "há", 
                         "havemos", "hão", "houve", "houvemos", "houveram", "houvera", "houvéramos", 
                         "haja", "hajamos", "hajam", "houvesse", "houvéssemos", "houvessem", "houver", 
                         "houvermos", "houverem", "houverei", "houverá", "houveremos", "houverão", 
                         "houveria", "houveríamos", "houveriam", "sou", "somos", "são", "era", "éramos", 
                         "eram", "fui", "foi", "fomos", "foram", "fora", "fôramos", "seja", "sejamos", 
                         "sejam", "fosse", "fôssemos", "fossem", "for", "formos", "forem", "serei", "será", 
                         "seremos", "serão", "seria", "seríamos", "seriam", "tenho", "tem", "temos", "tém", 
                         "tinha", "tínhamos", "tinham", "tive", "teve", "tivemos", "tiveram", "tivera", 
                         "tivéramos", "tenha", "tenhamos", "tenham", "tivesse", "tivéssemos", "tivessem", 
                         "tiver", "tivermos", "tiverem", "terei", "terá", "teremos", "terão", "teria", "teríamos", "teriam"]

# Import CountVectorizer and create the count matrix
from sklearn.feature_extraction.text import CountVectorizer

count           = CountVectorizer(stop_words=stop_words_portuguese)
count_matrix    = count.fit_transform(df2['soup'])


# Calcula a matriz de similaridade de cossenos com base em count_matrix
from sklearn.metrics.pairwise import cosine_similarity

count = CountVectorizer(stop_words=stop_words_portuguese)
count_matrix = count.fit_transform(df2['soup'])
cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

# Obtém a quantidade de filmes na base de dados
num_filmes_base = len(df2)

# Obtém a quantidade de filmes na matriz de similaridade
num_filmes_sim = cosine_sim2.shape[0]

# Verifica se a quantidade é a mesma
if num_filmes_base == num_filmes_sim:
    print("A quantidade de linhas treinadas é igual à quantidade de filmes na base de dados.")
else:
    print("A quantidade de linhas treinadas é diferente da quantidade de filmes na base de dados.")

#########SALVA MODELO#######
cosine_sim2 = cosine_similarity(count_matrix, count_matrix)
indice = {title: idx for idx, title in enumerate(df2['TITLE'])}


# Salve as variáveis que deseja em um dicionário
data = {
    'cosine_sim': cosine_sim2,
    'indices': indice
}


# Salva o dicionário em um arquivo pickle
with open('C:\IA\data.pkl', 'wb') as f:
    pickle.dump(data, f)


# Carregar o arquivo pickle
with open('C:\IA\data.pkl', 'rb') as f:
    loaded_cosine_sim = pickle.load(f)

# Imprimir a matriz de similaridade
print(loaded_cosine_sim)

