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
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    # Garante que ele procura na subpasta 'assets' dentro de 'src'
    return send_from_directory(os.path.join('src', 'assets'), filename)


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
# Função para calcular Nível e Progresso da Barra de XP
def calcular_nivel(xp: int):
    nivel = 1
    xp_para_proximo_nivel = 300 
    xp_base_nivel_atual = 0
    while xp >= xp_para_proximo_nivel:
        nivel += 1
        xp_base_nivel_atual = xp_para_proximo_nivel
        xp_para_proximo_nivel += 300 + (nivel - 1) * 150 # Dificuldade progressiva
    xp_no_nivel_atual = xp - xp_base_nivel_atual
    xp_total_do_nivel = xp_para_proximo_nivel - xp_base_nivel_atual
    progresso_percentual = int((xp_no_nivel_atual / xp_total_do_nivel) * 100) if xp_total_do_nivel > 0 else 0
    return {
        "nivel": nivel,
        "progresso_xp_texto": f"{xp_no_nivel_atual} / {xp_total_do_nivel}", # Alterado nome para clareza
        "progresso_percentual": progresso_percentual
    }

# categoria para mandar p castilhos 
def calcular_categoria_e_medalha(xp: int):
    """
    Calcula a Categoria e a Medalha do utilizador com base no XP,
    seguindo as regras definidas para o projeto SJCC.
    Retorna uma tupla: (categoria, medalha)
    """
    if 0 <= xp <= 1500:
        categoria = "Leitor Leigo"
        if xp <= 500:
            medalha = "Bronze"
        elif xp <= 1000:
            medalha = "Prata"
        else: # 1001 a 1500
            medalha = "Ouro"
            
    elif 1501 <= xp <= 3000:
        categoria = "Leitor Massa"
        if xp <= 2000:
            medalha = "Bronze"
        elif xp <= 2500:
            medalha = "Prata"
        else: # 2501 a 3000
            medalha = "Ouro"

    elif 3001 <= xp <= 4500:
        categoria = "Leitor Engajado"
        if xp <= 3500:
            medalha = "Bronze"
        elif xp <= 4000:
            medalha = "Prata"
        else: # 4001 a 4500
            medalha = "Ouro"

    elif 4501 <= xp <= 6000:
        categoria = "Leitor Arretado" 
        if xp <= 5000:
            medalha = "Bronze"
        elif xp <= 5500:
            medalha = "Prata"
        else: # 5501 a 6000
            medalha = "Ouro"

    elif 6001 <= xp <= 7500:
        categoria = "Leitor Desenrolado"
        if xp <= 6500:
            medalha = "Bronze"
        elif xp <= 7000:
            medalha = "Prata"
        else: # 7001 a 7500
            medalha = "Ouro"

    else: # xp >= 7501
        categoria = "Leitor Topado" 
        if xp <= 8500:
            medalha = "Bronze"
        elif xp <= 9500:
            medalha = "Prata"
        else: # 9501+
            medalha = "Ouro"
            
    return categoria, medalha


@app.route("/api/usuario/<string:usuario_id>", methods=['GET'])
def get_dados_usuario(usuario_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"sucesso": False, "mensagem": "Erro de conexão com a base de dados"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT u.id, u.nome, g.xps, g.jc_points FROM usuarios u "
            "JOIN gamificacao g ON u.id = g.usuario_id WHERE u.id = %s",
            (usuario_id,)
        )
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404

        # --- ALTERAÇÃO AQUI ---
        # Chama a nova função para obter ambos os valores
        categoria, medalha = calcular_categoria_e_medalha(usuario['xps'])
        dados_nivel = calcular_nivel(usuario['xps']) # A função de nível continua igual

        # Monta a resposta completa, incluindo a categoria e a medalha
        resposta_completa = {
            "id": usuario['id'],
            "nome": usuario['nome'],
            "xps": usuario['xps'],
            "jc_points": usuario['jc_points'],
            "nivel": dados_nivel['nivel'],
            "progresso_xp_texto": dados_nivel['progresso_xp_texto'],
            "progresso_percentual": dados_nivel['progresso_percentual'],
            "categoria": categoria, # Categoria calculada
            "medalha": medalha      # Medalha calculada (Bronze, Prata, Ouro)
        }
        # --- FIM DA ALTERAÇÃO ---
        
        return jsonify({"sucesso": True, "dados": resposta_completa})
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)