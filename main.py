from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import os
import re
import os
from werkzeug.utils import secure_filename



app = Flask(__name__)


# Configuração do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'e_commerce'

app.secret_key = 'jrirj39u434394939493'  # Chave para gerenciar sessões

mysql = MySQL(app)
bcrypt = Bcrypt(app)  # Inicializa o Flask-Bcrypt


@app.route('/')
def page_home():
    return redirect(url_for('page_produto'))


@app.route('/cadastro')
def form():
    return render_template('cadastro.html')

@app.route('/sobre')
def page_sobre():
    return render_template('sobre.html')


@app.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']  # Captura o username
        email = request.form['email']
        telephone = request.form['telephone']
        password = request.form['password']

        # Verificar se o e-mail ou o username já estão registrados no banco de dados
        conn = mysql.connection
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            # Passando a variável erro_email para destacar o campo de e-mail
            return render_template('cadastro.html',
                                   mensagem="Este e-mail já está registrado. Tente outro.",
                                   erro_email=True)

        # Verificar se o username já está em uso
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_username = cursor.fetchone()

        if existing_username:
            cursor.close()
            # Passando a variável erro_username para destacar o campo de username
            return render_template('cadastro.html',
                                   mensagem="Este nome de usuário já está em uso. Escolha outro.",
                                   erro_username=True)

        # Se o e-mail e o username não existirem, faz o cadastro
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')  # Gera o hash seguro

        cursor.execute("INSERT INTO users (name, username, email, telephone, password) VALUES (%s, %s, %s, %s, %s)",
                       (name, username, email, telephone, hashed_password))

        conn.commit()
        cursor.close()

        # Após o cadastro, realiza o login do usuário automaticamente
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        # Criar a sessão para o usuário logado
        session['logged_in'] = True
        session['user_id'] = user[0]
        session['user_name'] = user[1]

        # Redirecionar para o dashboard
        return redirect(url_for('dashboard'))




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = mysql.connection
        cursor = conn.cursor()

        cursor.execute("SELECT id, password, username, name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.check_password_hash(user[1], password):  # Usa a função correta
            session['logged_in'] = True
            session['user_id'] = user[0]
            mensagem = "Login realizado com sucesso!"
            return redirect(url_for('page_produto', mensagem=mensagem))
        else:
            mensagem = "Email ou senha inválidos!"
            return render_template('login.html', mensagem=mensagem)

    return render_template('login.html')


@app.route('/logout')
def logout():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    else:
        session.clear()  # Limpa a sessão
        return redirect(url_for('login'))


@app.route('/produtos')
def page_produto():
    conn = mysql.connection
    cursor = conn.cursor()

    query = """
        SELECT p.id, p.nome_produto, p.descricao, p.preco, p.imagem, u.username,
        COALESCE(SUM(CASE WHEN l.tipo = 'like' THEN 1 ELSE 0 END), 0) as likes,
        COALESCE(SUM(CASE WHEN l.tipo = 'dislike' THEN 1 ELSE 0 END), 0) as dislikes
        FROM produtos p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN likes l ON p.id = l.produto_id
        GROUP BY p.id
    """

    cursor.execute(query)
    itens = cursor.fetchall()
    cursor.close()

    return render_template("produtos.html", itens=itens)


@app.route('/like/<int:produto_id>', methods=['POST'])
def like(produto_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = mysql.connection
    cursor = conn.cursor()

    # Verifica se o usuário já votou
    cursor.execute("SELECT tipo FROM likes WHERE user_id = %s AND produto_id = %s", (user_id, produto_id))
    voto_existente = cursor.fetchone()

    if voto_existente:
        if voto_existente[0] != 'like':
            # Se o usuário deu dislike antes, troca para like
            cursor.execute("UPDATE likes SET tipo = 'like' WHERE user_id = %s AND produto_id = %s",
                           (user_id, produto_id))
            conn.commit()
    else:
        cursor.execute("INSERT INTO likes (user_id, produto_id, tipo) VALUES (%s, %s, 'like')", (user_id, produto_id))
        conn.commit()

    cursor.close()
    return redirect(url_for('page_produto'))


@app.route('/dislike/<int:produto_id>', methods=['POST'])
def dislike(produto_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = mysql.connection
    cursor = conn.cursor()

    # Verifica se o usuário já votou
    cursor.execute("SELECT tipo FROM likes WHERE user_id = %s AND produto_id = %s", (user_id, produto_id))
    voto_existente = cursor.fetchone()

    if voto_existente:
        if voto_existente[0] != 'dislike':
            cursor.execute("UPDATE likes SET tipo = 'dislike' WHERE user_id = %s AND produto_id = %s",
                           (user_id, produto_id))
            conn.commit()
    else:
        # Registra um novo dislike
        cursor.execute("INSERT INTO likes (user_id, produto_id, tipo) VALUES (%s, %s, 'dislike')",
                       (user_id, produto_id))
        conn.commit()

    cursor.close()
    return redirect(url_for('page_produto'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = mysql.connection
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email, telephone FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    mensagem = None  # Variável para a mensagem
    erro_email = False  # Variável para indicar erro no e-mail
    erro_telefone = False  # Variável para indicar erro no telefone

    if request.method == 'POST':
        # Captura os novos valores do formulário
        name = request.form['name']
        email = request.form['email']
        telephone = request.form['telephone']

        # Verificar se o e-mail já está registrado, excluindo o e-mail do usuário atual
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", (email, user_id))
        existing_user = cursor.fetchone()

        if existing_user:
            erro_email = True
            mensagem = "Este e-mail já está registrado. Tente outro."

        # Verificar se o telefone já está registrado, excluindo o telefone do usuário atual
        cursor.execute("SELECT id FROM users WHERE telephone = %s AND id != %s", (telephone, user_id))
        existing_telephone = cursor.fetchone()

        if existing_telephone:
            erro_telefone = True
            mensagem = "Este telefone já está registrado. Tente outro."

        # Se não houver erros, faz a atualização dos dados
        if not erro_email and not erro_telefone:
            cursor.execute("UPDATE users SET name = %s, email = %s, telephone = %s WHERE id = %s",
                           (name, email, telephone, user_id))
            conn.commit()
            cursor.close()

            # Defina a mensagem que será exibida após o sucesso
            mensagem = "Informações atualizadas com sucesso!"

            # Atualiza os dados na sessão
            session['user_name'] = name

            # Recarrega os dados mais recentes do banco de dados após a atualização
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, telephone FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()  # Recarrega os dados do banco
            cursor.close()

    return render_template('dashboard.html', user=user, mensagem=mensagem, erro_email=erro_email, erro_telefone=erro_telefone)





@app.route('/vender', methods=['GET', 'POST'])
def vender_produto():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome_produto = request.form['nome_produto']
        descricao = request.form['descricao']
        preco = request.form['preco']
        imagem = request.files['imagem']

        # Convertendo o preço para um formato aceito pelo MySQL
        preco = re.sub(r'[^\d,]', '', preco)  # Remove "R$" e caracteres inválidos
        preco = preco.replace(',', '.')  # Substitui a vírgula por ponto

        # Salvar imagem no diretório 'static/uploads'
        imagem_path = os.path.join('static', 'uploads', imagem.filename)
        imagem.save(imagem_path)

        # Inserir produto no banco de dados
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO produtos (nome_produto, descricao, preco, imagem, user_id) 
            VALUES (%s, %s, %s, %s, %s)
        """, (nome_produto, descricao, float(preco), imagem_path, session['user_id']))

        conn.commit()
        cursor.close()

        return render_template('vender.html', mensagem="Produto anunciado com sucesso!")

    return render_template('vender.html')


def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/anuncios', methods=['GET', 'POST'])
def anuncios():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = mysql.connection
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome_produto, descricao, preco, imagem, user_id, likes, dislikes FROM produtos WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    mensagem = None
    erro_email = False
    erro_telefone = False

    if request.method == 'GET':
        nome_produto = request.form['nome_produto']
        descricao = request.form['descricao']
        preco = request.form['preco']
        imagem = request.form['imagem']
        user_id = request.form['user_id']
        likes = request.form['likes']
        dislikes = request.form['dislikes']

    return render_template('anuncios.html', nome_produto=nome_produto, descricao=descricao)

    #     if not erro_email and not erro_telefone:
    #         cursor.execute("UPDATE users SET name = %s, email = %s, telephone = %s WHERE id = %s",
    #                        (name, email, telephone, user_id))
    #         conn.commit()
    #         cursor.close()
    #
    #         # Defina a mensagem que será exibida após o sucesso
    #         mensagem = "Informações atualizadas com sucesso!"
    #
    #         # Atualiza os dados na sessão
    #         session['user_name'] = name
    #
    #         # Recarrega os dados mais recentes do banco de dados após a atualização
    #         cursor = conn.cursor()
    #         cursor.execute("SELECT id, name, email, telephone FROM users WHERE id = %s", (user_id,))
    #         user = cursor.fetchone()  # Recarrega os dados do banco
    #         cursor.close()
    #
    # return render_template('dashboard.html', user=user, mensagem=mensagem, erro_email=erro_email, erro_telefone=erro_telefone)


if __name__ == '__main__':
    app.run(debug=True)
