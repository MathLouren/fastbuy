from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuração do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'e_commerce'
app.secret_key = 'jrirj39u434394939493'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Constantes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads'

def get_db_cursor():
    conn = mysql.connection
    return conn.cursor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return file_path
    return None

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

        cursor = get_db_cursor()

        cursor.execute("SELECT id FROM users WHERE email = %s OR username = %s", (email, username))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return render_template('cadastro.html',
                                   mensagem="Este e-mail ou nome de usuário já está registrado. Tente outro.",
                                   erro_email=True)

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor.execute("INSERT INTO users (name, username, email, telephone, password) VALUES (%s, %s, %s, %s, %s)",
                       (name, username, email, telephone, hashed_password))

        mysql.connection.commit()
        cursor.close()

        cursor = get_db_cursor()
        cursor.execute("SELECT id, name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        session['logged_in'] = True
        session['user_id'] = user[0]
        session['user_name'] = user[1]

        return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = get_db_cursor()
        cursor.execute("SELECT id, password, username, name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.check_password_hash(user[1], password):
            session['logged_in'] = True
            session['user_id'] = user[0]
            return redirect(url_for('page_produto'))
        else:
            return render_template('login.html', mensagem="Email ou senha inválidos!")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/produtos')
def page_produto():
    # Obtém o número da página da URL (padrão: 1)
    pagina = request.args.get('page', 1, type=int)

    # Define a quantidade de produtos por página
    produtos_por_pagina = 8  # Altere conforme necessário

    # Calcula o offset (deslocamento) para a consulta SQL
    offset = (pagina - 1) * produtos_por_pagina

    cursor = get_db_cursor()

    # Consulta SQL para buscar produtos com paginação
    query = """
        SELECT p.id, p.nome_produto, p.descricao, p.preco, p.imagem, u.username,
        COALESCE(SUM(CASE WHEN l.tipo = 'like' THEN 1 ELSE 0 END), 0) as likes,
        COALESCE(SUM(CASE WHEN l.tipo = 'dislike' THEN 1 ELSE 0 END), 0) as dislikes
        FROM produtos p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN likes l ON p.id = l.produto_id
        GROUP BY p.id
        LIMIT %s OFFSET %s
    """
    cursor.execute(query, (produtos_por_pagina, offset))
    itens = cursor.fetchall()

    # Conta o total de produtos para calcular o número total de páginas
    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]
    cursor.close()

    # Calcula o número total de páginas
    total_paginas = (total_produtos + produtos_por_pagina - 1) // produtos_por_pagina

    return render_template("produtos.html", itens=itens, pagina=pagina, total_paginas=total_paginas)

@app.route('/like/<int:produto_id>', methods=['POST'])
def like(produto_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = get_db_cursor()
    cursor.execute("SELECT tipo FROM likes WHERE user_id = %s AND produto_id = %s", (user_id, produto_id))
    voto_existente = cursor.fetchone()

    if voto_existente:
        if voto_existente[0] != 'like':
            cursor.execute("UPDATE likes SET tipo = 'like' WHERE user_id = %s AND produto_id = %s",
                           (user_id, produto_id))
    else:
        cursor.execute("INSERT INTO likes (user_id, produto_id, tipo) VALUES (%s, %s, 'like')", (user_id, produto_id))

    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('page_produto'))

@app.route('/dislike/<int:produto_id>', methods=['POST'])
def dislike(produto_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = get_db_cursor()
    cursor.execute("SELECT tipo FROM likes WHERE user_id = %s AND produto_id = %s", (user_id, produto_id))
    voto_existente = cursor.fetchone()

    if voto_existente:
        if voto_existente[0] != 'dislike':
            cursor.execute("UPDATE likes SET tipo = 'dislike' WHERE user_id = %s AND produto_id = %s",
                           (user_id, produto_id))
    else:
        cursor.execute("INSERT INTO likes (user_id, produto_id, tipo) VALUES (%s, %s, 'dislike')",
                       (user_id, produto_id))

    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('page_produto'))

@app.route('/<username>/<produto_name>')
def produto(produto_name, username):
    cursor = get_db_cursor()
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
        return 'Página não encontrada', 404

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = get_db_cursor()
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

        cursor = get_db_cursor()
        cursor.execute("SELECT id FROM users WHERE (email = %s OR telephone = %s OR username = %s) AND id != %s",
                       (email, telephone, username, user_id))
        existing_user = cursor.fetchone()

        if existing_user:
            erro_email = True
            mensagem = "Este e-mail, telefone ou nome de usuário já está registrado. Tente outro."
        else:
            cursor.execute("UPDATE users SET name = %s, email = %s, telephone = %s, username = %s WHERE id = %s",
                           (name, email, telephone, username, user_id))
            mysql.connection.commit()
            session['user_name'] = name
            mensagem = "Informações atualizadas com sucesso!"

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

        preco_limpo = re.sub(r'[^\d,]', '', preco)  # Remove "R$" e caracteres inválidos
        preco_limpo = preco_limpo.replace(',', '.')  # Substitui a vírgula por ponto
        preco_float = float(preco_limpo)  # Converte para float

        imagem_path = os.path.join('static', 'uploads', secure_filename(imagem.filename))
        imagem_path = imagem_path.replace("\\", "/")  # Substitui barras invertidas por barras normais
        imagem.save(imagem_path)

        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO produtos (nome_produto, descricao, preco, imagem, user_id) 
            VALUES (%s, %s, %s, %s, %s)
        """, (nome_produto, descricao, preco_float, imagem_path, session['user_id']))

        conn.commit()
        cursor.close()

        return render_template('vender.html', mensagem="Produto anunciado com sucesso!")

    return render_template('vender.html')

@app.route('/anuncios')
def anuncios():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = get_db_cursor()
    cursor.execute("SELECT id, nome_produto, descricao, preco, imagem, likes, dislikes FROM produtos WHERE user_id = %s", (user_id,))
    anuncios = cursor.fetchall()
    cursor.close()
    return render_template('anuncios.html', anuncios=anuncios)

@app.route('/editar_anuncio/<int:anuncio_id>', methods=['GET', 'POST'])
def editar_anuncio(anuncio_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    cursor = get_db_cursor()
    cursor.execute("SELECT id, nome_produto, descricao, preco FROM produtos WHERE id = %s", (anuncio_id,))
    anuncio = cursor.fetchone()

    if request.method == 'POST':
        nome_produto = request.form['nome_produto']
        descricao = request.form['descricao']
        preco = request.form['preco']
        preco_limpo = re.sub(r'[^\d,]', '', preco)
        preco_limpo = preco_limpo.replace(',', '.')
        preco_float = float(preco_limpo)

        cursor.execute("UPDATE produtos SET nome_produto = %s, descricao = %s, preco = %s WHERE id = %s",
                       (nome_produto, descricao, preco_float, anuncio_id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('anuncios'))

    return render_template('editar_anuncio.html', anuncio=anuncio)

@app.route('/remover_anuncio/<int:anuncio_id>')
def remover_anuncio(anuncio_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    cursor = get_db_cursor()
    cursor.execute("DELETE FROM produtos WHERE id = %s", (anuncio_id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('anuncios'))

@app.route('/<username>')
def page_perfil(username):
    cursor = get_db_cursor()
    cursor.execute("SELECT id, name, email, telephone, username FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return render_template('perfil.html', user=user)
    else:
        return 'Página não encontrada', 404

@app.route('/buscar', methods=['GET'])
def buscar_produtos():
    termo_busca = request.args.get('q', '').strip()

    termo_busca = re.sub(r'[^\w\s]', '', termo_busca)  # Remove caracteres especiais
    palavras_chave = termo_busca.lower().split()  # Divide em palavras e converte para minúsculas

    cursor = get_db_cursor()

    query = """
        SELECT p.id, p.nome_produto, p.descricao, p.preco, p.imagem, u.username,
        COALESCE(SUM(CASE WHEN l.tipo = 'like' THEN 1 ELSE 0 END), 0) as likes,
        COALESCE(SUM(CASE WHEN l.tipo = 'dislike' THEN 1 ELSE 0 END), 0) as dislikes
        FROM produtos p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN likes l ON p.id = l.produto_id
        WHERE {}
        GROUP BY p.id
    """
    where_clause = " AND ".join(
        ["LOWER(p.nome_produto) LIKE %s OR LOWER(p.descricao) LIKE %s" for _ in palavras_chave]
    )
    query = query.format(where_clause)

    parametros = []
    for palavra in palavras_chave:
        parametros.extend([f"%{palavra}%", f"%{palavra}%"])

    cursor.execute(query, parametros)
    itens = cursor.fetchall()
    cursor.close()

    return render_template("produtos.html", itens=itens)

if __name__ == '__main__':
    app.run(debug=True)