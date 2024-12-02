from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

# Configuração do MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',  # Altere para o seu usuário
    'password': '',  # Altere para a sua senha
    'database': 'catalogo_livros'
}

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Chave para o uso do flash

# Função para conectar ao banco de dados
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None

# Página inicial - Listagem de livros
@app.route('/')
def index():
    conn = get_db_connection()
    if not conn:
        flash('Erro ao conectar ao banco de dados', 'danger')
        return render_template('index.html', livros=[])

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM livros')
        livros = cursor.fetchall()
    except Error as err:
        flash(f'Erro ao recuperar livros: {err}', 'danger')
        livros = []
    finally:
        cursor.close()
        conn.close()

    return render_template('index.html', livros=livros)

# Página para adicionar um novo livro
@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        genero = request.form['genero']
        ano_publicacao = request.form['ano_publicacao']

        # Validação simples dos dados
        if not titulo or not autor or not genero or not ano_publicacao:
            flash('Todos os campos são obrigatórios', 'danger')
            return redirect(url_for('adicionar'))

        conn = get_db_connection()
        if not conn:
            flash('Erro ao conectar ao banco de dados', 'danger')
            return redirect(url_for('adicionar'))

        try:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO livros (titulo, autor, genero, ano_publicacao) VALUES (%s, %s, %s, %s)',
                           (titulo, autor, genero, ano_publicacao))
            conn.commit()
            flash('Livro adicionado com sucesso!', 'success')
        except Error as err:
            flash(f'Erro ao adicionar livro: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('index'))

    return render_template('adicionar.html')

# Página para editar um livro
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    if not conn:
        flash('Erro ao conectar ao banco de dados', 'danger')
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM livros WHERE id = %s', (id,))
        livro = cursor.fetchone()

        if not livro:
            flash('Livro não encontrado!', 'danger')
            return redirect(url_for('index'))

        if request.method == 'POST':
            titulo = request.form['titulo']
            autor = request.form['autor']
            genero = request.form['genero']
            ano_publicacao = request.form['ano_publicacao']

            # Validação simples dos dados
            if not titulo or not autor or not genero or not ano_publicacao:
                flash('Todos os campos são obrigatórios', 'danger')
                return redirect(url_for('editar', id=id))

            cursor.execute('UPDATE livros SET titulo = %s, autor = %s, genero = %s, ano_publicacao = %s WHERE id = %s',
                           (titulo, autor, genero, ano_publicacao, id))
            conn.commit()
            flash('Livro atualizado com sucesso!', 'success')
            return redirect(url_for('index'))

    except Error as err:
        flash(f'Erro ao editar livro: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return render_template('editar.html', livro=livro)

# Página para excluir um livro
@app.route('/excluir/<int:id>', methods=['GET'])
def excluir(id):
    conn = get_db_connection()
    if not conn:
        flash('Erro ao conectar ao banco de dados', 'danger')
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM livros WHERE id = %s', (id,))
        livro = cursor.fetchone()

        if not livro:
            flash('Livro não encontrado!', 'danger')
            return redirect(url_for('index'))

        cursor.execute('DELETE FROM livros WHERE id = %s', (id,))
        conn.commit()
        flash('Livro excluído com sucesso!', 'success')
    except Error as err:
        flash(f'Erro ao excluir livro: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
