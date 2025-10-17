# ============================================
# CÓDIGO PYTHON ATUALIZADO: Integração Completa com MySQL
# ============================================
# Conceito Geral: Este app Flask usa MySQL para gerenciar dados reais.
# Agora, as rotas podem inserir usuários e atualizar gamificação.
# Passos: Conectar ao DB, executar queries seguras, e responder ao JS.

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import uuid  # Para gerar IDs únicos.

app = Flask(__name__)
CORS(app)

# Configuração do MySQL (ajuste conforme o seu setup).
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'dbjc',
}

def get_db_connection():
     try:
         conn = mysql.connector.connect(**db_config)
         print("Conectado ao MySQL com sucesso!")  # Novo log.
         return conn
     except mysql.connector.Error as err:
         print(f"Erro ao conectar: {err}")  # Mostra o erro específico.
         return None


# Nova Rota: /api/criar-usuario (POST) - Insere um novo usuário na tabela 'usuarios'.
@app.route('/api/criar-usuario', methods=['POST'])
def criar_usuario():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao conectar ao DB'}), 500
    
    cursor = conn.cursor()
    
    try:
        dados = request.get_json()
        novo_id = str(uuid.uuid4())  # Gera um ID único.
        
        query = """
            INSERT INTO usuarios (id, nome, data_nascimento, email, senha)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            novo_id,
            dados.get('nome'),
            dados.get('data_nascimento'),
            dados.get('email'),
            dados.get('senha')  # Nota: Use hashing para senhas reais!
        ))
        conn.commit()
        
        return jsonify({'sucesso': True, 'mensagem': 'Usuário criado!', 'id': novo_id}), 201  # 201: Created
    except mysql.connector.Error as err:
        return jsonify({'sucesso': False, 'mensagem': str(err)}), 400
    finally:
        cursor.close()
        conn.close()

# Rota Atualizada: /api/conectar (POST) - Agora atualiza gamificacao.
@app.route('/api/conectar', methods=['POST'])
def conectar():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao conectar ao DB'}), 500
    
    cursor = conn.cursor(dictionary=True)  # Retorna resultados como dicionários.
    
    try:
        dados = request.get_json()
        acao = dados.get('acao', 'desconhecida')
        usuario_id = dados.get('usuario_id')  # Espera o ID do usuário do JS.
        
        if acao in ['gastar', 'busca'] and usuario_id:
            # Atualiza JC Points (exemplo: +10 por ação).
            query = """
                UPDATE gamificacao 
                SET jc_points = jc_points + 10, 
                    ultima_atualizacao = CURRENT_TIMESTAMP
                WHERE usuario_id = %s
            """
            cursor.execute(query, (usuario_id,))
            conn.commit()
            
            if cursor.rowcount == 0:  # Se não afetou linhas, o usuário não existe.
                return jsonify({'sucesso': False, 'mensagem': 'Usuário não encontrado'}), 404
            
            # Pega os novos dados para retornar.
            cursor.execute("SELECT jc_points FROM gamificacao WHERE usuario_id = %s", (usuario_id,))
            resultado = cursor.fetchone()
            
            return jsonify({
                'sucesso': True,
                'mensagem': f'Conexão OK! Ação: {acao}. Novos JC Points: {resultado["jc_points"]}',
                'jc_points': resultado["jc_points"]
            }), 200
        else:
            return jsonify({'sucesso': False, 'mensagem': 'Ação ou ID inválido'}), 400
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
