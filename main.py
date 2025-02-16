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
        username = request.form['username']
        email = request.form['email']
        telephone = request.form['telephone']
        password = request.form['password']

        conn = mysql.connection
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return render_template('cadastro.html',
                                   mensagem="Este e-mail já está registrado. Tente outro.",
                                   erro_email=True)

        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_username = cursor.fetchone()

        if existing_username:
            cursor.close()
            return render_template('cadastro.html',
                                   mensagem="Este nome de usuário já está em uso. Escolha outro.",
                                   erro_username=True)

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor.execute("INSERT INTO users (name, username, email, telephone, password) VALUES (%s, %s, %s, %s, %s)",
                       (name, username, email, telephone, hashed_password))

        conn.commit()
        cursor.close()

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

    cursor.execute("SELECT tipo FROM likes WHERE user_id = %s AND produto_id = %s", (user_id, produto_id))
    voto_existente = cursor.fetchone()

    if voto_existente:
        if voto_existente[0] != 'like':
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

@app.route('/<username>/<produto_name>')
def produto(produto_name, username):
    conn = mysql.connection
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.id, u.name, u.username, p.id, p.nome_produto, p.descricao, p.preco, p.imagem
        FROM users u
        JOIN produtos p ON u.id = p.user_id
        WHERE u.username = %s AND p.nome_produto = %s
    """, (username, produto_name))

    produto_info = cursor.fetchone()
    cursor.close()

    if produto_info:
        user_id, name, user_name,  produto_id, produto_nome, descricao, preco, imagem = produto_info
        image_path = imagem.replace("static/", "")
        return render_template('produto_info.html', produto_id=produto_id, produto_name=produto_nome, descricao=descricao, name=name, user_name=user_name, preco=preco, image_path=image_path)
    else:
        return 'pagina nano ecntrdkmskn'


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = mysql.connection
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email, telephone, username FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    mensagem = None
    erro_email = False
    erro_telefone = False
    erro_username = False

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        telephone = request.form['telephone']
        username = request.form['username']

        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", (email, user_id))
        existing_email = cursor.fetchone()
        if existing_email:
            erro_email = True
            mensagem = "Este e-mail já está registrado. Tente outro."

        cursor.execute("SELECT id FROM users WHERE telephone = %s AND id != %s", (telephone, user_id))
        existing_telephone = cursor.fetchone()
        if existing_telephone:
            erro_telefone = True
            mensagem = "Este telefone já está registrado. Tente outro."

        cursor.execute("SELECT id FROM users WHERE username = %s AND id != %s", (username, user_id))
        existing_username = cursor.fetchone()
        if existing_username:
            erro_username = True
            mensagem = "Este username já está em uso. Escolha outro."

        # Se não houver erros, atualiza os dados do usuário
        if not erro_email and not erro_telefone and not erro_username:
            cursor.execute("UPDATE users SET name = %s, email = %s, telephone = %s, username = %s WHERE id = %s",
                           (name, email, telephone, username, user_id))
            conn.commit()
            cursor.close()

            session['user_name'] = name

            mensagem = "Informações atualizadas com sucesso!"

            # Recarregar os dados do usuário
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, telephone, username FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()

    return render_template('dashboard.html', user=user, mensagem=mensagem, erro_email=erro_email, erro_telefone=erro_telefone, erro_username=erro_username)

@app.route('/vender', methods=['GET', 'POST'])
def vender_produto():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome_produto = request.form['nome_produto']
        descricao = request.form['descricao']
        preco = request.form['preco']
        imagem = request.files['imagem']

        preco = re.sub(r'[^\d,]', '', preco)  # Remove "R$" e caracteres inválidos
        preco = preco.replace(',', '.')  # Substitui a vírgula por ponto

        imagem_path = os.path.join('static', 'uploads', imagem.filename)
        imagem.save(imagem_path)

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

    cursor.execute("SELECT id, nome_produto, descricao, preco, imagem, likes, dislikes FROM produtos WHERE user_id = %s", (user_id,))
    anuncios = cursor.fetchall()  # Pega todos os anúncios do usuário
    cursor.close()

    return render_template('anuncios.html', anuncios=anuncios)

@app.route('/editar_anuncio/<int:anuncio_id>', methods=['GET', 'POST'])
def editar_anuncio(anuncio_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()

    # Buscar os dados do anúncio
    cursor.execute("SELECT id, nome_produto, descricao, preco FROM produtos WHERE id = %s", (anuncio_id,))
    anuncio = cursor.fetchone()

    if request.method == 'POST':
        nome_produto = request.form['nome_produto']
        descricao = request.form['descricao']
        preco = request.form['preco']

        cursor.execute("UPDATE produtos SET nome_produto = %s, descricao = %s, preco = %s WHERE id = %s",
                       (nome_produto, descricao, preco, anuncio_id))
        conn.commit()
        cursor.close()

        return redirect(url_for('anuncios'))

    return render_template('editar_anuncio.html', anuncio=anuncio)

@app.route('/remover_anuncio/<int:anuncio_id>')
def remover_anuncio(anuncio_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()

    cursor.execute("DELETE FROM produtos WHERE id = %s", (anuncio_id,))
    conn.commit()
    cursor.close()

    return redirect(url_for('anuncios'))

@app.route('/<username>')
def page_perfil(username):
    conn = mysql.connection
    cursor = conn.cursor()

    # Buscar usuário pelo username
    cursor.execute("SELECT id, name, email, telephone, username FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    # Se o usuário não existir, retorna erro 404
    if not user:
        return 'USER NAO ENCONTRADO'

    return render_template('perfil.html', user=user)




if __name__ == '__main__':
    app.run(debug=True)
