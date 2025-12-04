import os #para acessar funções do sistema operacional
#Recuperar o diretório do arquivo app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#Definir o local do arquivo JSON com base no diretório do app.py (EX.: diretório "data")
DATA_FILE = os.path.join(BASE_DIR, "models", "data", "dados.json") 
AVALIATION_FILE = os.path.join(BASE_DIR, "models", "data", "avaliacao.json") 

#Diretório para upload de imagem
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "image")