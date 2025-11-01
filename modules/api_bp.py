# modules/api_bp.py

from flask import Blueprint, jsonify, request
import uuid
import bcrypt
import mysql.connector
from datetime import datetime, date
from modules.gamification import get_db_connection, get_user_data, check_and_award_daily_missions, calcular_categoria_e_medalha # Importe as funções necessárias
# Importa TODAS as funções e dados necessários do módulo de Gamificação
from modules.gamification import (
    get_db_connection, 
    get_user_data, 
    check_and_award_daily_missions,
    adicionar_xp_jc, 
    check_and_award_medals,
    calcular_nivel, 
    calcular_categoria_e_medalha, 
    
)

# Cria o Blueprint com o prefixo '/api'
api_bp = Blueprint('api', __name__, url_prefix='/api')

# ===============================================
# ROTAS DE AUTENTICAÇÃO
# ===============================================

# modules/api_bp.py (Com a correção)
@api_bp.route('/usuario/<string:user_id>/ping_tempo', methods=['POST'])
def api_ping_tempo(user_id):
    """Incrementa o tempo online e verifica missões."""
# --- CORREÇÃO AQUI ---
    # 1. Chama get_user_data PRIMEIRO para garantir que o reset diário seja executado.
    user_data_check = get_user_data(user_id)
    if not user_data_check:
        return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404
    # --- FIM DA CORREÇÃO ---
    
    conn = get_db_connection()
    if not conn: return jsonify({"sucesso": False, "mensagem": "Erro de conexão"}), 500
    
    try:
        # O RESET É FEITO AUTOMATICAMENTE QUANDO get_user_data() É CHAMADO ABAIXO
        
        cursor = conn.cursor()
        incremento_minutos = 1
        cursor.execute(
            "UPDATE gamificacao SET tempo_online_hoje_minutos = tempo_online_hoje_minutos + %s WHERE usuario_id = %s",
            (incremento_minutos, user_id)
        )
        conn.commit()
        cursor.close()

        # Esta chamada agora faz o reset (se for o primeiro ping do dia)
        # E também pega o valor ATUALIZADO (ex: 1)
        user_data = get_user_data(user_id) 
        if not user_data: return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404
        
        missoes_completadas_agora = check_and_award_daily_missions(user_id, user_data, conn)

        # --- CORREÇÃO DO BUG 1 (Duplo Incremento) ---
        # O valor correto já está em user_data
        tempo_total_hoje = user_data.get('tempo_online_hoje_minutos', 0)

        return jsonify({
            "sucesso": True,
            "mensagem": "Tempo online atualizado.",
            "tempo_hoje_minutos": tempo_total_hoje, # <-- CORRIGIDO
            "novas_missoes_diarias": missoes_completadas_agora
        })

    except Exception as e:
        if conn: conn.rollback()
        print(f"Erro no ping_tempo: {e}")
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500
    finally:
        # O cursor já foi fechado, então limpamos a referência
        if 'cursor' in locals() and cursor: cursor.close()
        if conn: conn.close()  

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
    """Regista a leitura, atualiza XP e verifica medalhas E missões."""
    
    user_antes = get_user_data(user_id)
    if not user_antes: return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404
    
    conn = get_db_connection()
    if not conn: return jsonify({"sucesso": False, "mensagem": "Erro de conexão"}), 500

    try:
        agora = datetime.now()
        hoje = agora.date()
        
        # <--- MUDANÇA AQUI: Cálculo do 'acessou_madrugada' ---
        # (Este cálculo já existia, mas agora sabemos que ele é crucial)
        acessou_madrugada = (3 <= agora.hour < 5)
        
        # (Cálculo de dias_consecutivos - o seu código existente vai aqui)
        dias_consecutivos = user_antes.get('dias_consecutivos_acesso', 0)
        # ... (lógica de 'diferenca' e 'dias_consecutivos') ...

        cursor = conn.cursor()
        xp_por_noticia = 25
        cursor.execute("""
            UPDATE gamificacao SET
                xps = xps + %s,
                noticias_completas_total = noticias_completas_total + 1,
                noticias_lidas_hoje = noticias_lidas_hoje + 1,
                ultimo_acesso = %s,
                dias_consecutivos_acesso = %s
            WHERE usuario_id = %s
        """, (xp_por_noticia, hoje, dias_consecutivos, user_id))
        conn.commit()
        cursor.close()
        # --- FIM DA ATUALIZAÇÃO DE STATS ---

        
        # --- 2. VERIFICAÇÃO DE MEDALHAS (LÓGICA CORRIGIDA) ---
        user_depois = get_user_data(user_id) # Pega os dados atualizados do DB
        user_depois['acessou_madrugada'] = acessou_madrugada # Adiciona a métrica temporária

        # <--- MUDANÇA CRÍTICA AQUI ---
        # Passamos o objeto 'user_depois' para a função de verificação
        novas_medalhas_conquistadas = check_and_award_medals(user_id, user_depois) 
        # --- FIM DA VERIFICAÇÃO DE MEDALHAS ---

        
        # --- 3. VERIFICAÇÃO DE MISSÕES DIÁRIAS (Lógica existente) ---
        missoes_completadas_agora = check_and_award_daily_missions(user_id, user_depois, conn) 

        
        # --- 4. BUSCA DADOS FINAIS E RETORNA ---
        user_final = get_user_data(user_id) 
        categoria_final, medalha_final = calcular_categoria_e_medalha(user_final['xps'])
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"+{xp_por_noticia} XP por ler a notícia!",
            "xp_atual": user_final['xps'],
            "jc_points_atual": user_final['jc_points'],
            "novas_medalhas": novas_medalhas_conquistadas,
            "novas_missoes_diarias": missoes_completadas_agora,
            "categoria": categoria_final,
            "medalha": medalha_final
        })

    except Exception as e:
        if conn: conn.rollback()
        print(f"Erro na rota ler_noticia: {e}")
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor: # <--- Correção aplicada aqui
            cursor.close()
        if conn: 
            conn.close()
        
@api_bp.route('/usuario/<string:user_id>/share', methods=['POST'])
def api_compartilhar(user_id):
    """
    Incrementa o contador de compartilhamentos diários do usuário
    e verifica se alguma missão de compartilhamento foi completada.
    """
# --- CORREÇÃO AQUI ---
    # 1. Chama get_user_data PRIMEIRO para garantir o reset diário.
    user_data_check = get_user_data(user_id)
    if not user_data_check:
        return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404
    # --- FIM DA CORREÇÃO ---

    conn = get_db_connection()
    if not conn: return jsonify({"sucesso": False, "mensagem": "Erro de conexão com o DB"}), 500

    
    try:


        cursor = conn.cursor()

        
        # 1. Incrementa o contador de compartilhamentos_hoje no DB
        cursor.execute(
            "UPDATE gamificacao SET compartilhamentos_hoje = compartilhamentos_hoje + 1 WHERE usuario_id = %s",
            (user_id,)
        )
        conn.commit()
        cursor.close()

        # 2. Pega os dados atualizados do usuário (incluindo o novo contador)
        user_data = get_user_data(user_id) 
        if not user_data: 
            return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404
        
        # 3. Verifica se o novo contador completou alguma missão
        # (check_and_award_daily_missions já concede o XP/JC se a missão for nova)
        missoes_completadas_agora = check_and_award_daily_missions(user_id, user_data, conn)

        # 4. Pega os dados finais (com o XP/JC atualizado, se houver)
        user_final = get_user_data(user_id)
        categoria_final, medalha_final = calcular_categoria_e_medalha(user_final['xps'])

        return jsonify({
            "sucesso": True,
            "mensagem": "Compartilhamento registrado!",
            "compartilhamentos_hoje": user_final.get('compartilhamentos_hoje', 0),
            "novas_missoes_diarias": missoes_completadas_agora,
            "xp_atual": user_final['xps'],
            "jc_points_atual": user_final['jc_points'],
            "categoria": categoria_final,
            "medalha": medalha_final
        })

    except Exception as e:
        if conn: conn.rollback()
        print(f"Erro na rota /share: {e}")
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()