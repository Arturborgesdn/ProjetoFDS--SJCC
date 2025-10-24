# modules/api_bp.py

from flask import Blueprint, jsonify, request
import uuid
import bcrypt
import mysql.connector
from datetime import datetime, date
# Importa TODAS as funções e dados necessários do módulo de Gamificação
from modules.gamification import (
    get_db_connection, 
    get_user_data, 
    adicionar_xp_jc, 
    award_medal, 
    calcular_nivel, 
    calcular_categoria_e_medalha, 
    MEDALHAS
)

# Cria o Blueprint com o prefixo '/api'
api_bp = Blueprint('api', __name__, url_prefix='/api')

# ===============================================
# ROTAS DE AUTENTICAÇÃO
# ===============================================

# modules/api_bp.py (Com a correção)

@api_bp.route('/registrar', methods=['POST'])
def registrar():
    """Registra um novo utilizador, cria sua conta de gamificação e retorna seu ID."""
    conn = get_db_connection() # Usa a função do módulo de gamificação
    if conn is None: return jsonify({'sucesso': False, 'mensagem': 'Erro ao conectar ao DB'}), 500
    cursor = conn.cursor()
    try:
        dados = request.get_json()
        novo_id = str(uuid.uuid4())
        hashed_senha = bcrypt.hashpw(dados['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        data_br = dados.get('data_nascimento')
        try: data_mysql = datetime.strptime(data_br, '%d/%m/%Y').strftime('%Y-%m-%d')
        except (ValueError, TypeError): return jsonify({'sucesso': False, 'mensagem': 'Formato de data inválido. Use DD/MM/YYYY.'}), 400
        
        # Insere utilizador e gamificacao (Lógica migrada)
        cursor.execute("INSERT INTO usuarios (id, nome, data_nascimento, email, senha) VALUES (%s, %s, %s, %s, %s)",
                       (novo_id, dados['nome'], data_mysql, dados['email'], hashed_senha))
        cursor.execute("INSERT INTO gamificacao (usuario_id, xps, jc_points) VALUES (%s, %s, %s)",
                       (novo_id, 30, 10))
        conn.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Utilizador registado! +30 XP e +10 JC Points!', 'id': novo_id}), 201
    except mysql.connector.IntegrityError:
        return jsonify({'sucesso': False, 'mensagem': 'Este email já está em uso'}), 409
    # Remova a linha anterior e deixe o comentário na mesma linha do except:
    except Exception as e: # pylint: disable=broad-except
        conn.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 400
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ... o resto do código continua
@api_bp.route('/login', methods=['POST'])
def login():
    conn = get_db_connection()
    if conn is None: return jsonify({'sucesso': False, 'mensagem': 'Erro ao conectar ao DB'}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        dados = request.get_json()
        cursor.execute("SELECT id, nome, senha FROM usuarios WHERE email = %s", (dados['email'],))
        usuario = cursor.fetchone()
        
        if usuario and bcrypt.checkpw(dados['senha'].encode('utf-8'), usuario['senha'].encode('utf-8')):
            usuario_id_logado = usuario['id']
            xp_login = 15
            
            # Adiciona XP de login (Lógica migrada)
            cursor.execute("UPDATE gamificacao SET xps = xps + %s WHERE usuario_id = %s", (xp_login, usuario_id_logado))
            conn.commit()
            
            return jsonify({'sucesso': True, 'mensagem': f'Login bem-sucedido! +{xp_login} XP!', 'usuario_id': usuario_id_logado, 'nome': usuario['nome'] }), 200
        else:
            return jsonify({'sucesso': False, 'mensagem': 'Email ou senha inválidos'}), 401
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ===============================================
# ROTAS DE GAMIFICAÇÃO
# ===============================================

@api_bp.route("/usuario/<string:usuario_id>", methods=['GET'])
def get_dados_usuario(usuario_id):
    """Retorna os dados completos do perfil do utilizador, incluindo medalhas."""
    user = get_user_data(usuario_id) # Usa a função de serviço

    if not user:
        return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404

    # Calcula os dados dinâmicos usando as funções de serviço
    dados_nivel = calcular_nivel(user['xps'])
    categoria, medalha_emblema = calcular_categoria_e_medalha(user['xps'])

    resposta = {
        "id": user['usuario_id'],
        "nome": user['nome'],
        "xps": user['xps'],
        "jc_points": user['jc_points'],
        "nivel": dados_nivel['nivel'],
        "progresso_xp_texto": dados_nivel['progresso_xp_texto'],
        "progresso_percentual": dados_nivel['progresso_percentual'],
        "categoria": categoria,
        "medalha": medalha_emblema,
        "medalhas_conquistadas": user.get('medalhas_conquistadas', [])
    }
    return jsonify({"sucesso": True, "dados": resposta})


@api_bp.route('/usuario/<string:user_id>/ler_noticia', methods=['POST'])
def api_ler_noticia(user_id):
    """Regista a leitura, atualiza XP e verifica medalhas."""
    user_antes = get_user_data(user_id)
    if not user_antes: return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404
    
    conn = get_db_connection()
    if not conn: return jsonify({"sucesso": False, "mensagem": "Erro de conexão"}), 500
    cursor = conn.cursor(dictionary=True)

    try:
        # Lógica de atualização (Migrada integralmente)
        agora = datetime.now()
        hoje = agora.date()
        acessou_madrugada = (3 <= agora.hour < 5)

        dias_consecutivos = user_antes.get('dias_consecutivos_acesso', 0)
        ultimo_acesso_str = user_antes.get('ultimo_acesso')
        
        if ultimo_acesso_str:
            if isinstance(ultimo_acesso_str, datetime): ultimo_acesso_date = ultimo_acesso_str.date()
            else: 
                 try: ultimo_acesso_date = date.fromisoformat(str(ultimo_acesso_str))
                 except (TypeError, ValueError): ultimo_acesso_date = None

            if ultimo_acesso_date:
                 diferenca = (hoje - ultimo_acesso_date).days
                 if diferenca == 1: dias_consecutivos += 1
                 elif diferenca > 1: dias_consecutivos = 1
            else: dias_consecutivos = 1
        else: dias_consecutivos = 1

        xp_por_noticia = 25
        cursor.execute("""
            UPDATE gamificacao SET
                xps = xps + %s,
                noticias_completas_total = noticias_completas_total + 1,
                ultimo_acesso = %s,
                dias_consecutivos_acesso = %s
            WHERE usuario_id = %s
        """, (xp_por_noticia, hoje, dias_consecutivos, user_id))
        conn.commit()

        # Lógica de verificação de medalhas (Migrada integralmente)
        user_depois = get_user_data(user_id)
        if not user_depois: return jsonify({"sucesso": False, "mensagem": "Erro ao buscar dados atualizados do utilizador"}), 500
             
        user_depois['acessou_madrugada'] = acessou_madrugada 

        novas_medalhas_conquistadas = []
        for nome_medalha, dados_medalha in MEDALHAS.items():
            if nome_medalha not in user_depois.get('medalhas_conquistadas', []) and dados_medalha['check'](user_depois):
                if award_medal(user_id, nome_medalha, dados_medalha['jc_points']):
                    novas_medalhas_conquistadas.append(nome_medalha)

        user_final = get_user_data(user_id)
        if not user_final: return jsonify({"sucesso": False, "mensagem": "Erro ao buscar dados finais do utilizador"}), 500

        categoria_final, medalha_final = calcular_categoria_e_medalha(user_final['xps'])
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"+{xp_por_noticia} XP por ler a notícia!",
            "xp_atual": user_final['xps'],
            "jc_points_atual": user_final['jc_points'],
            "novas_medalhas": novas_medalhas_conquistadas,
            "categoria": categoria_final,
            "medalha": medalha_final
        })

    except Exception as e:
        if conn: conn.rollback()
        print(f"Erro na rota ler_noticia: {e}")
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()