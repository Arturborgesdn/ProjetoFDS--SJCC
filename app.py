from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
import uuid
import bcrypt
from datetime import datetime
import os


app = Flask(__name__, static_folder='src')
CORS(app)


db_config = {
    'user': 'root', 
    'password': 'root', 
    'host': 'localhost',
    'database': 'dbjc',
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Erro ao conectar: {err}")
        return None



@app.route('/')
def serve_login_page():
    return send_from_directory('src', 'login.html')


@app.route('/<path:filename>')
def serve_html_pages(filename):
    return send_from_directory('src', filename)


@app.route('/api/registrar', methods=['POST'])
def registrar():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao conectar ao DB'}), 500
    
    cursor = conn.cursor()
    try:
        dados = request.get_json()
        novo_id = str(uuid.uuid4())
        hashed_senha = bcrypt.hashpw(dados['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        data_br = dados.get('data_nascimento')
        try:
            data_obj = datetime.strptime(data_br, '%d/%m/%Y')
            data_mysql = data_obj.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return jsonify({'sucesso': False, 'mensagem': 'Formato de data inválido. Use DD/MM/YYYY.'}), 400
        
        query = "INSERT INTO usuarios (id, nome, data_nascimento, email, senha) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (novo_id, dados['nome'], data_mysql, dados['email'], hashed_senha))
        
        query_gam = "INSERT INTO gamificacao (usuario_id) VALUES (%s)"
        cursor.execute(query_gam, (novo_id,))
        conn.commit()
        
        return jsonify({'sucesso': True, 'mensagem': 'Utilizador registado!', 'id': novo_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao conectar ao DB'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        dados = request.get_json()
        query = "SELECT * FROM usuarios WHERE email = %s"
        cursor.execute(query, (dados['email'],))
        usuario = cursor.fetchone()
        
        if usuario and bcrypt.checkpw(dados['senha'].encode('utf-8'), usuario['senha'].encode('utf-8')):
            return jsonify({'sucesso': True, 'mensagem': 'Login bem-sucedido!', 'usuario_id': usuario['id']}), 200
        else:
            return jsonify({'sucesso': False, 'mensagem': 'Email ou senha inválidos'}), 401
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/conectar', methods=['POST'])
def conectar():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao conectar ao DB'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        dados = request.get_json()
        acao = dados.get('acao')
        usuario_id = dados.get('usuario_id')
        
        if acao in ['gastar', 'busca'] and usuario_id:
            query = "UPDATE gamificacao SET jc_points = jc_points + 10 WHERE usuario_id = %s"
            cursor.execute(query, (usuario_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                return jsonify({'sucesso': False, 'mensagem': 'Utilizador não encontrado'}), 404
            
            cursor.execute("SELECT jc_points FROM gamificacao WHERE usuario_id = %s", (usuario_id,))
            resultado = cursor.fetchone()
            
            return jsonify({'sucesso': True, 'mensagem': f'Ação: {acao} registada!', 'jc_points': resultado['jc_points']}), 200
        else:
            return jsonify({'sucesso': False, 'mensagem': 'Ação ou ID inválido'}), 400
    except Exception as e:
        conn.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)