import pickle 

# Carregar o arquivo pickle
with open('C:\IA\data.pkl', 'rb') as f:
    loaded_data = pickle.load(f)

# Imprimir a matriz de similaridade
print(loaded_data['cosine_sim'])
print(loaded_data['indices'])