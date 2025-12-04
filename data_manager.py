import os
import json
import config
import uuid
from flask import flash
# funções de manipulação de json

def load_data():
    #verifica se exite o arquivo no caminho indicado, se existe, abre o arquivo para leitura 'r'
    if not os.path.exists(config.DATA_FILE):
        return [ ]
    with open(config.DATA_FILE, "r") as file:
        return (json.load(file))
        #jason.load(file) converte dados do arquivo json para um objeto Python (lista de dicionários)

def save_data(data):
    with open(config.DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)
        #jason.dump(data) converte objeto Python (lista de dicionários) em arquivo no formato JSON

def load_avaliation():
    #verifica se exite o arquivo no caminho indicado, se existe, abre o arquivo para leitura 'r'
    if not os.path.exists(config.AVALIATION_FILE):
        return [ ]
    with open(config.AVALIATION_FILE, "r") as file:
        return (json.load(file))
        #jason.load(file) converte dados do arquivo json para um objeto Python (lista de dicionários)

def save_avaliation(avaliacao):
    with open(config.AVALIATION_FILE, "w") as file:
        json.dump(avaliacao, file, indent=4)
        #jason.dump(data) converte objeto Python (lista de dicionários) em arquivo no formato JSON

# funções auxiliares
#Tipos de arquivos de imagens aceitas
TIPOS_IMAGEM = set(['png', 'jpg', 'jpeg', 'gif'])

def upload_imagem(imagem):    
    # Garante que a pasta de upload exista
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True) #garante que o diretório upload existe ou, caso contrário, ele é criado
    
    if (imagem.filename == ''):
        flash("Nenhum arquivo carregado.", "danger")
        return "image/padrao.png" 
    else:
        if (not verificarArquivos(imagem)):
            flash("Formato de arquivo não permitido.", "warning")
            return "image/padrao.png" 
    
        else:
        # Gera um nome ÚNICO para a imagem e salva no diretório de uploads
            filename = f"{uuid.uuid4()}.{imagem.filename.rsplit('.', 1)[1].lower()}"
            filepath = os.path.join(config.UPLOAD_FOLDER, filename)
            imagem.save(filepath)
            return f"uploads/image/{filename}"  # Caminho relativo para salvar no JSON, junto ao dados do contato
        
def verificarArquivos(imagem):
	return ('.' in imagem.filename and imagem.filename.rsplit('.', 1)[1].lower() in TIPOS_IMAGEM)
