from flask import Flask, render_template, request, redirect, url_for, jsonify

import mysql.connector

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# Local  Configurações do banco de dados

db_config = {
    'host': 'projetoint.mysql.pythonanywhere-services.com',
    'user': 'projetoint',
    'password': 'databases453453534',
    'database': 'projetoint$emprestimo'
}

"""
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'projeto3',
    'database': 'projeto3'
}
"""

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')
    



# Rota principal para exibir o formulário de cadastro
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

# Rota para processar o formulário de cadastro
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    try:
        # Obter dados do formulário
        numero_do_tombo = request.form['numero_do_tombo']
        nome_do_livro = request.form['nome_do_livro']
        data_retirada = request.form['data_retirada']
        data_devolucao = request.form['data_devolucao']
        nome_aluno = request.form['nome_aluno']
        serie = request.form['serie']
        

        # Conectar ao banco de dados
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Inserir dados na tabela
        query = "INSERT INTO emprestimo_livros (numero_do_tombo, nome_do_livro, data_retirada, data_devolucao, nome_aluno, serie, devolvido) VALUES (%s, %s, %s, %s, %s, %s, 'n')"
        values = (numero_do_tombo, nome_do_livro, data_retirada, data_devolucao, nome_aluno, serie)
        cursor.execute(query, values)

        # Confirmar a transação
        conn.commit()

        # Fechar a conexão com o banco de dados
        cursor.close()
        conn.close()

        return redirect(url_for('livros_emprestados'))


    except Exception as e:
        return render_template('erro.html', mensagem=str(e))

############################################
####### Historico 
############################################

def get_db():
    return mysql.connector.connect(**db_config)

def close_db(e=None):
    db = getattr(app, 'db', None)
    if db is not None:
        db.close()

app.teardown_appcontext(close_db)

def query_db(query, args=(), one=False):
    with app.app_context():
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute(query, args)
            r = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            cur.close()
            return (r[0] if r else None) if one else r
        finally:
            conn.close()

# Historico de livros emprestados 
def get_historico():
    query = "SELECT * FROM emprestimo_livros ORDER BY data_retirada DESC"
    return query_db(query)


@app.route('/historico')
def historico():
    historico = get_historico()
    return render_template('historico.html', historico=historico)
    

############################################
####### 
############################################


# livros NÃO devolvidos 
def get_livros_emprestados():
    query = "SELECT * FROM emprestimo_livros WHERE DEVOLVIDO != 's' ORDER BY data_devolucao ASC"
    return query_db(query)


@app.route('/livros_emprestados')
def livros_emprestados():
    livros_emprestados = get_livros_emprestados()
    

    return render_template('livros_emprestados.html', livros_emprestados=livros_emprestados)
    
    #editar Acervo ---------------------------------------------
@app.route('/atualizar_acervo/<int:id>', methods=['GET', 'POST'])
def atualizar_acervo(id):
    # Conectar ao banco de dados
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)  # Retorna resultados como dicionários

    # Obtém os dados do livro com base no ID
    cursor.execute("SELECT * FROM acervo WHERE id = %s", (id,))
    acervo = cursor.fetchone()

    if request.method == 'POST':
        # Obtém os novos dados do formulário
        novo_tombo = request.form['novo_tombo']
        novo_nome_livro = request.form['novo_nome_livro']
        novo_nome_autor = request.form['novo_nome_autor']
       
        # Atualiza os dados do livro no banco de dados
        cursor.execute("UPDATE acervo SET numero_do_tombo = %s, nome_do_livro = %s, "
                       "autor = %s WHERE id = %s",
                       (novo_tombo, novo_nome_livro, novo_nome_autor, id))
        conn.commit()

        # Fechar o cursor e a conexão após as operações
        cursor.close()
        conn.close()

        return redirect(url_for('acervo', message='Acervo atualizado com sucesso!'))

    # Fechar o cursor e a conexão após as operações
    cursor.close()
    conn.close()

    return render_template('editar_acervo.html', acervo=acervo)



 
#editar livros ---------------------------------------------

@app.route('/editar_livro/<int:id>', methods=['GET', 'POST'])
def editar_livro(id):
    # Conectar ao banco de dados
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)  # Retorna resultados como dicionários

    # Obtém os dados do livro com base no ID
    cursor.execute("SELECT * FROM emprestimo_livros WHERE id = %s", (id,))
    livro = cursor.fetchone()

    if request.method == 'POST':
        # Obtém os novos dados do formulário
        novo_tombo = request.form['novo_tombo']
        novo_nome_livro = request.form['novo_nome_livro']
        nova_data_retirada = request.form['nova_data_retirada']
        nova_data_devolucao = request.form['nova_data_devolucao']
        novo_nome_aluno = request.form['novo_nome_aluno']
        nova_serie = request.form['nova_serie']

        # Atualiza os dados do livro no banco de dados
        cursor.execute("UPDATE emprestimo_livros SET numero_do_tombo = %s, nome_do_livro = %s, data_retirada = %s, data_devolucao = %s, "
                       "nome_aluno = %s, serie = %s WHERE id = %s",
                       (novo_tombo, novo_nome_livro, nova_data_retirada, nova_data_devolucao, novo_nome_aluno, nova_serie, id))
        conn.commit()

        # Fechar o cursor e a conexão após as operações
        cursor.close()
        conn.close()

        return redirect(url_for('livros_emprestados', message='Livro atualizado com sucesso!'))

    # Fechar o cursor e a conexão após as operações
    cursor.close()
    conn.close()

    return render_template('editar_livro.html', livro=livro)
    
  
# Deletar o livro emprestado
@app.route('/deletar_livro/<int:id>', methods=['POST'])
def deletar_livro(id):
    # Conectar ao banco de dados
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Deletar o livro com base no ID
    cursor.execute("DELETE FROM emprestimo_livros WHERE id = %s", (id,))
    conn.commit()

    # Fechar o cursor e a conexão após as operações
    cursor.close()
    conn.close()

    return redirect(url_for('historico', message='Livro deletado com sucesso!'))

# devolver o livro emprestado
@app.route('/livro_devolvido/<int:id>', methods=['POST'])
def livro_devolvido(id):
    # Conectar ao banco de dados
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # devolver o livro com base no ID
    cursor.execute("UPDATE emprestimo_livros SET DEVOLVIDO = 's' WHERE id = %s", (id,))
    conn.commit()

    # Fechar o cursor e a conexão após as operações
    cursor.close()
    conn.close()
    
    return redirect(url_for('livros_emprestados', message='Livro devolvido com sucesso!'))
    
#################
#Acervo 
#################


# Historico de livros emprestados 
def get_acervo():
    query = "SELECT * FROM acervo ORDER BY id DESC"
    return query_db(query)


@app.route('/acervo')
def acervo():
    acervo = get_acervo()
    return render_template('acervo.html', acervo=acervo)

# Deletar acervo
@app.route('/deletar_acervo/<int:id>', methods=['POST'])
def deletar_acervo(id):
    # Conectar ao banco de dados
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Deletar acervo com base no ID
    cursor.execute("DELETE FROM acervo WHERE id = %s", (id,))
    conn.commit()

    # Fechar o cursor e a conexão após as operações
    cursor.close()
    conn.close()

    return redirect(url_for('acervo', message='Acervo deletado com sucesso!'))    
  

# Rota principal para exibir o formulário de cadastro
@app.route('/cadastro_acervo')
def cadastro_acervo():
    return render_template('cadastro_acervo.html')

# Rota para processar o formulário de cadastro
@app.route('/cadastrar_acervo', methods=['POST'])
def cadastrar_acervo():
    try:
        # Obter dados do formulário
        numero_do_tombo = request.form['numero_do_tombo']
        nome_do_livro = request.form['nome_do_livro']
        autor = request.form['autor']
            

        # Conectar ao banco de dados
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Inserir dados na tabela
        query = "INSERT INTO acervo (numero_do_tombo, nome_do_livro, autor) VALUES (%s, %s, %s)"
        values = (numero_do_tombo, nome_do_livro, autor)
        cursor.execute(query, values)

        # Confirmar a transação
        conn.commit()

        # Fechar a conexão com o banco de dados
        cursor.close()
        conn.close()

        return redirect(url_for('acervo'))


    except Exception as e:
        return render_template('erro.html', mensagem=str(e))  



#######################################
# Rota para API CONEXÃO
#######################################


def get_db_connection():
    return mysql.connector.connect(**db_config)



#######################################
# Rota para API de ALERTA APP
#######################################
@app.route('/alerta/app', methods=['GET'])
def show_alerta():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM emprestimo_livros WHERE devolvido = %s', ('n',))  # Filtra onde devolvido é 'n'
    emprestimos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(emprestimos)  # Retorna os dados em formato JSON


#######################################
# Rota para API Acervo
#######################################


@app.route('/api/acervo', methods=['GET'])
def get_emprestimos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM acervo')
    emprestimos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(emprestimos)

@app.route('/api/acervo/<int:id>', methods=['GET'])
def get_emprestimo(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM acervo WHERE id = %s', (id,))
    emprestimo = cursor.fetchone()
    cursor.close()
    conn.close()
    if emprestimo is None:
        return jsonify({'message': 'Empréstimo não encontrado'}), 404
    return jsonify(emprestimo)



#######################################
# Rota para API ALERTA APP
#######################################


#######################################
# Rota para API Empréstimos
#######################################


@app.route('/api/emprestimos', methods=['POST'])
def create_emprestimo():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emprestimo_livros (numero_do_tombo, nome_do_livro, data_retirada, data_devolucao, nome_aluno, serie, devolvido)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (data['numero_do_tombo'], data['nome_do_livro'], data['data_retirada'], data['data_devolucao'], data['nome_aluno'], data['serie'], data['devolvido']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Empréstimo criado com sucesso'}), 201

@app.route('/api/emprestimos/<int:id>', methods=['PUT'])
def update_emprestimo(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE emprestimo_livros
        SET numero_do_tombo = %s, nome_do_livro = %s, data_retirada = %s, data_devolucao = %s, nome_aluno = %s, serie = %s, devolvido = %s
        WHERE id = %s
    ''', (data['numero_do_tombo'], data['nome_do_livro'], data['data_retirada'], data['data_devolucao'], data['nome_aluno'], data['serie'], data['devolvido'], id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Empréstimo atualizado com sucesso'})

@app.route('/api/emprestimos/<int:id>', methods=['DELETE'])
def delete_emprestimo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM emprestimo_livros WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Empréstimo excluído com sucesso'})



if __name__ == '__main__':
    app.run(debug=True)
