from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session
import os
import requests

from config import BASE_DIR, DATA_FILE,UPLOAD_FOLDER
from models.data_manager import upload_imagem, load_data, save_data, load_avaliation, save_avaliation

# Cria um Blueprint para as rotas
front_controller = Blueprint('front_controller', __name__)
# Blueprint (front_controller) no controlador (front_controller.py) é um módulo que agrupa rotas relacionadas.
# Flask precisa saber que o front_controller existe, então você o registra, no APP.PY, com app.register_blueprint(front_controller).

@front_controller.route('/', methods=["GET", "POST"])
def home( ):
    data = load_data( )
    return(render_template('home.html', data = data))

@front_controller.route("/cadastrados", methods=["GET", "POST"])
def cadastrados():
    data = load_data()
    return render_template("cadastrados.html", data=data)

@front_controller.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if(session.get('userLogado')):
        flash("Você precisa deslogar!", "warning")
        return redirect(url_for('front_controller.home'))
    data = load_data()
    return render_template("cadastro.html", data=data)

@front_controller.route("/add", methods=["GET", "POST"])
def add():
    verifica = 0
    data = load_data( )

    # Obtém os dados do formulário
    user = request.form.get("textNome")
    password = request.form.get('textSenha')
    tel = request.form.get("textTel")
    mail = request.form.get("textMail")    
    imagem = request.files.get("fileFoto")
    imagem_path = upload_imagem(imagem)
 
    for users in data:
        if(mail == users['mail']):
            verifica = 1
    if (verifica == 1):
        flash("Usuário já cadastrado!", "warning")
        return (redirect(url_for("front_controller.cadastro")))
    else:
        # Adiciona novo registro
        data.append({"nome": user, "senha": password, "tel": tel, "mail": mail, "imagem": imagem_path})
        data.sort(key=lambda x: x['nome'])
        save_data(data)
        flash("Usuário cadastrado com sucesso!", "success")
        return (redirect(url_for("front_controller.home")))

@front_controller.route('/login', methods=["GET", "POST"])
def login( ):
    verifica = 0
    data = load_data( )

    if(session.get('userLogado')):
        flash("Você já está logado!", "warning")
        return redirect(url_for('front_controller.home'))
    else:
        if (request.method == "POST"):
            maillog = request.form.get('textMail')
            passlog = request.form.get('textSenha')
            for users in data:
                if(maillog == users['mail'] and passlog == users['senha']):
                    verifica = 1
            if (verifica == 1):
                session['userLogado'] = maillog
                flash("Usuário logado com sucesso!", "success")
                return(redirect(url_for('front_controller.home')))
            
            else:
                flash("Erro de login. Confira seu email e/ou senha.", "danger")
                return render_template("login.html")    
        return render_template("login.html")        

@front_controller.route("/edit/<item_mail>", methods=["GET", "POST"])
def edit(item_mail):
    # Carrega os dados (arquivo JSON)
    data = load_data()
       
    # Encontra o item correspondente
    item = next((item for item in data if item["mail"] == item_mail), None)
    
    if not item:
        flash("Os dados não foram encontrados!")
        return "Contato não encontrado", 404
    
    if request.method == "POST":
        # Atualiza os dados do contato
        item["nome"] = request.form.get("textNome")
        item["mail"] = request.form.get("textMail")
        item["senha"] = request.form.get("textSenha")
        item["tel"] = request.form.get("textTel")
        # Verifica se um novo arquivo foi enviado
        nova_imagem = request.files.get("fileFoto")
        
        novo_caminho = upload_imagem(nova_imagem) #reuso de função
        caminho_antigo = os.path.join(BASE_DIR, "static", item["imagem"])

        if (nova_imagem and nova_imagem.filename != ""):

            if (item["imagem"] != "image/padrao.png"):
                if os.path.exists(caminho_antigo):
                    os.remove(caminho_antigo)
                    # Atualiza o caminho da imagem no JSON (relativo)
                    item["imagem"] = novo_caminho 
            else:
                item["imagem"] = novo_caminho 
        else:
            if(caminho_antigo != os.path.join(BASE_DIR, "static", "image/padrao.png")):
                os.remove(caminho_antigo)
            item["imagem"] = novo_caminho 
 
        # Ordena os contatos por nome e salva os dados no JSON
        data.sort(key=lambda x: x["nome"])
        save_data(data)
        flash("Contato atualizado.", "primary")
        return redirect(url_for("front_controller.home"))

    return render_template("editar.html", item=item)

@front_controller.route("/delete/<item_mail>", methods=["GET", "POST"])
def delete(item_mail):
    data = load_data( )
    dataNew = [ ]
    
    # Remove o item correspondente, copiando os itens que não foram removidos
    #data = [item for item in data if item["mail"] != item_mail]
    for item in data:
        if(item["mail"] != item_mail):
            dataNew.append(item)    
        if(item["mail"] == item_mail):
            if (item["imagem"] != "image/padrao.png"):
                if os.path.exists(UPLOAD_FOLDER):
                    caminho = os.path.join(BASE_DIR,"static",item["imagem"])
                    os.remove(caminho)

    session.pop('userLogado', None)
    save_data(dataNew)
    flash("Contato excluido.", "primary")
    return redirect(url_for("front_controller.home"))

@front_controller.route('/recuperar', methods=["GET", "POST"])
def recuperar():
    data = load_data( )

    if(session.get('userLogado')):
        flash("Você precisa deslogar!", "warning")
        return redirect(url_for('front_controller.home'))
    
    if (request.method == "POST"):
        recmail = request.form.get('rec')
        for users in data:
            if(recmail == users['mail']):
                email = users['mail']
                return render_template("recuperar2.html", email = email)
        flash("Usuário Inexistente!", "warning")
        return render_template("login.html")
    
    return render_template("recuperar.html")

@front_controller.route('/recsenha', methods=["GET", "POST"])
def recsenha():
    data = load_data( )

    if (request.method == "POST"):
        passwd = request.form.get('new')
        email = request.form.get('mail')
        for users in data:
            if(email == users['mail']):
                users['senha'] = passwd
                flash("Senha alterada com sucesso! Nova senha: " + passwd, "success")
                data.sort(key=lambda x: x["nome"])
                save_data(data)
                return render_template("login.html")
            
    return render_template("login.html")

@front_controller.route('/sair', methods=["GET", "POST"])
def sair():
    session['userLogado'] = None
    return(redirect(url_for('front_controller.home')))

@front_controller.route('/personagens', methods=["GET", "POST"])
def personagens():
    if(not session.get('userLogado')):
        flash("Você precisa logar!", "warning")
        return redirect(url_for('front_controller.home'))
    
    api_url='https://hp-api.onrender.com/api/characters'
    resposta = requests.get(api_url)
    avaliacao = load_avaliation()

    if(resposta.status_code == 200):
            dados = resposta.json( )
            dados = dados[0:20]
    else:
        dados = {"ERRO: não foi possível obter os dados"}

    return(render_template('personagens.html', dados=dados, avaliacao=avaliacao))

@front_controller.route('/avaliacao', methods=["GET", "POST"])
def avaliacao():
    if (request.method == "POST"):
        personagem = request.form.get('personagem')
    return(render_template('avaliar.html', personagem=personagem))

@front_controller.route('/avaliar', methods=["GET", "POST"])
def avaliar():
    avaliacao = load_avaliation()
    if (request.method == "POST"):
        id = max([item['id'] for item in avaliacao], default=0) + 1
        personagem = request.form.get('personagem')
        nota = request.form.get('nota')
        review = request.form.get('review')

        avaliacao.append({"id": id, "user":session.get('userLogado'),"personagem":personagem, "nota":nota, "review":review})
        save_avaliation(avaliacao)
    flash("Avaliação adicionada", "sucess")
    return(redirect(url_for('front_controller.personagens')))

@front_controller.route("/editarpersonagem/<int:info_id>", methods=["GET", "POST"])
def editarpersonagem(info_id):
    if session.get('userLogado'):
        avaliacao = load_avaliation()
        item = next((item for item in avaliacao if item["id"] == info_id), None)

        if (not item):
            flash("Personagem não encontrado!", "warning")
            return redirect(url_for('front_controller.personagens'))

        if (request.method == "POST"):
            item["nota"] = request.form.get("nota_edit")
            item["review"] = request.form.get("review_edit")
            save_avaliation(avaliacao)
            flash("Avaliação do personagem atualizada com sucesso.", "primary")
            return redirect(url_for('front_controller.personagens'))

        return render_template("editarpersonagem.html", item=item)

    else:
        flash("Você precisa logar!", "warning")
        return redirect(url_for('front_controller.home'))
    
@front_controller.route("/apagarpersonagem/<int:info_id>", methods=["GET", "POST"])
def apagarpersonagem(info_id):
    if session.get('userLogado'):
        avaliacao = load_avaliation()
        novo = [ ]

        for item in avaliacao:
            if(item["id"] != info_id):
                novo.append(item)    
                
        save_avaliation(novo)
        flash("Avaliação do personagem deletada com sucesso.", "primary")
        return redirect(url_for("front_controller.personagens"))
    
    else:
        flash("Você precisa logar!", "warning")
        return redirect(url_for('front_controller.home'))

    
    

    