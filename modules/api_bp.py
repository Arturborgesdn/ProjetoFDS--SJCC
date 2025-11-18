# modules/api_bp.py

from flask import Blueprint, jsonify, request
import uuid
import bcrypt
import mysql.connector
from datetime import datetime, date
# Importa a classe de configuração
from config import Config

# Importa TODAS as funções e dados necessários do módulo de Gamificação
from modules.gamification import (
    get_db_connection, 
    get_user_data, 
    check_and_award_daily_missions,
    adicionar_xp_jc, 
    check_and_award_medals,
    calcular_nivel, 
    calcular_categoria_e_medalha, 
    MEDALHAS,
    MISSOES_DIARIAS,
    get_completed_daily_missions,
    get_leaderboard,
    get_user_rank,
    get_user_streak 
)
from modules.benefits import (
    BENEFITS, 
    XP_MULTIPLIERS, 
    JC_MULTIPLIERS, 
    redeem_benefit, 
    activate_multiplier
)
from modules.db_services import (
    get_db_connection, 
    get_user_data_from_db, 
    update_xp_jc_in_db, 
    insert_medal_in_db, 
    get_completed_missions_from_db, 
    insert_daily_mission_in_db,
    get_leaderboard_from_db,
    get_user_rank_from_db,
    get_user_streak_from_db,
    get_user_inventory_from_db 
)

# Cria o Blueprint com o prefixo '/api'
api_bp = Blueprint('api', __name__, url_prefix='/api')

# ===============================================
# ROTAS DE AUTENTICAÇÃO
# ===============================================

# (Seu código original, mantido)
@api_bp.route('/usuario/<string:user_id>/ping_tempo', methods=['POST'])
def api_ping_tempo(user_id):
    """Incrementa o tempo online e verifica missões."""
    user_data_check = get_user_data(user_id)
    if not user_data_check:
        return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404
    
    conn = get_db_connection()
    if not conn: return jsonify({"sucesso": False, "mensagem": "Erro de conexão"}), 500
    
    try:
        cursor = conn.cursor()
        incremento_minutos = 1
        cursor.execute(
            "UPDATE gamificacao SET tempo_online_hoje_minutos = tempo_online_hoje_minutos + %s WHERE usuario_id = %s",
            (incremento_minutos, user_id)
        )
        conn.commit()
        cursor.close()

        user_data = get_user_data(user_id) 
        if not user_data: return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404
        
        missoes_completadas_agora = check_and_award_daily_missions(user_id, user_data, conn)
        novas_medalhas_conquistadas = check_and_award_medals(user_id, user_data)
    
        tempo_total_hoje = user_data.get('tempo_online_hoje_minutos', 0)

        return jsonify({
            "sucesso": True,
            "mensagem": "Tempo online atualizado.",
            "tempo_hoje_minutos": tempo_total_hoje,
            "novas_missoes_diarias": missoes_completadas_agora,
            "novas_medalhas": novas_medalhas_conquistadas,
        })

    except Exception as e:
        if conn: conn.rollback()
        print(f"Erro no ping_tempo: {e}")
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if conn: conn.close() 

# (Seu código original, mantido)
@api_bp.route('/registrar', methods=['POST'])
def registrar():
    """Registra um novo utilizador, cria sua conta de gamificação e retorna seu ID."""
    conn = get_db_connection() 
    if conn is None: return jsonify({'sucesso': False, 'mensagem': 'Erro ao conectar ao DB'}), 500
    cursor = conn.cursor()
    try:
        dados = request.get_json()
        novo_id = str(uuid.uuid4())
        hashed_senha = bcrypt.hashpw(dados['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        data_br = dados.get('data_nascimento')
        try: data_mysql = datetime.strptime(data_br, '%d/%m/%Y').strftime('%Y-%m-%d')
        except (ValueError, TypeError): return jsonify({'sucesso': False, 'mensagem': 'Formato de data inválido. Use DD/MM/YYYY.'}), 400
        
        cursor.execute("INSERT INTO usuarios (id, nome, data_nascimento, email, senha) VALUES (%s, %s, %s, %s, %s)",
                       (novo_id, dados['nome'], data_mysql, dados['email'], hashed_senha))
        cursor.execute("INSERT INTO gamificacao (usuario_id, xps, jc_points) VALUES (%s, %s, %s)",
                       (novo_id, 30, 10))
        conn.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Utilizador registado! +30 XP e +10 JC Points!', 'id': novo_id}), 201
    except mysql.connector.IntegrityError:
        return jsonify({'sucesso': False, 'mensagem': 'Este email já está em uso'}), 409
    except Exception as e: # pylint: disable=broad-except
        conn.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 400
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# (Seu código original, mantido)
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

# (Seu código original, mantido)
@api_bp.route("/usuario/<string:usuario_id>", methods=['GET'])
def get_dados_usuario(usuario_id):
    """Retorna os dados completos do perfil do utilizador, incluindo medalhas."""
    user = get_user_data(usuario_id) 

    if not user:
        return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404

    dados_nivel = calcular_nivel(user['xps'])
    categoria, medalha_emblema = calcular_categoria_e_medalha(user['xps'])
    xp_proximo_limite = dados_nivel['xp_proximo_limite']
    categoria_proxima, medalha_proxima = calcular_categoria_e_medalha(xp_proximo_limite)

    resposta = {
        "id": user['usuario_id'],
        "nome": user['nome'],
        "xps": user['xps'],
        "jc_points": user['jc_points'],
        "nivel": dados_nivel['nivel'],
        "progresso_xp_texto": dados_nivel['progresso_xp_total_texto'],
        "progresso_percentual": dados_nivel['progresso_percentual'],
        "categoria": categoria,
        "medalha": medalha_emblema,
        "categoria_proxima": categoria_proxima, 
        "medalha_proxima": medalha_proxima,
        "medalhas_conquistadas": user.get('medalhas_conquistadas', [])
    }
    return jsonify({"sucesso": True, "dados": resposta})

# (Seu código original, mantido)
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
        
        acessou_madrugada = (3 <= agora.hour < 5)
        
        dias_consecutivos = user_antes.get('dias_consecutivos_acesso', 0)
        ultimo_acesso = user_antes.get('ultimo_acesso')
        if ultimo_acesso:
            diferenca = (hoje - ultimo_acesso).days
            if diferenca == 1:
                dias_consecutivos += 1
            elif diferenca > 1:
                dias_consecutivos = 1 
        else:
            dias_consecutivos = 1 

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
        
        user_depois = get_user_data(user_id)
        user_depois['acessou_madrugada'] = acessou_madrugada 

        missoes_completadas_agora = check_and_award_daily_missions(user_id, user_depois, conn) 
        novas_medalhas_conquistadas = check_and_award_medals(user_id, user_depois)
        
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
        if 'cursor' in locals() and cursor: 
            cursor.close()
        if conn: 
            conn.close()

# (Seu código original, mantido)
@api_bp.route('/usuario/<string:user_id>/share', methods=['POST'])
def api_compartilhar(user_id):
    """
    Incrementa o contador de compartilhamentos diários do usuário
    e verifica se alguma missão de compartilhamento foi completada.
    """
    user_data_check = get_user_data(user_id)
    if not user_data_check:
        return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404

    conn = get_db_connection()
    if not conn: return jsonify({"sucesso": False, "mensagem": "Erro de conexão com o DB"}), 500
    
    try:
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE gamificacao SET compartilhamentos_hoje = compartilhamentos_hoje + 1 WHERE usuario_id = %s",
            (user_id,)
        )
        conn.commit()
        cursor.close()

        user_data = get_user_data(user_id) 
        if not user_data: 
            return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404
        
        missoes_completadas_agora = check_and_award_daily_missions(user_id, user_data, conn)
        novas_medalhas_conquistadas = check_and_award_medals(user_id, user_data)
        
        user_final = get_user_data(user_id)
        categoria_final, medalha_final = calcular_categoria_e_medalha(user_final['xps'])

        return jsonify({
            "sucesso": True,
            "mensagem": "Compartilhamento registrado!",
            "compartilhamentos_hoje": user_final.get('compartilhamentos_hoje', 0),
            "novas_missoes_diarias": missoes_completadas_agora,
            "novas_medalhas": novas_medalhas_conquistadas,
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
        if 'cursor' in locals() and cursor: cursor.close() # Correção de 'cursor'
        if conn: conn.close()

# (Seu código original, mantido)
@api_bp.route('/usuario/<string:user_id>/medalhas', methods=['GET'])
def get_medalhas_usuario(user_id):
    """
    Retorna uma lista de TODAS as medalhas do sistema,
    indicando quais o usuário completou.
    """
    user_data = get_user_data(user_id)
    if not user_data:
        return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404

    try:
        medalhas_conquistadas_set = set(user_data.get('medalhas_conquistadas', []))
        
        lista_completa_medalhas = []
        
        for nome, dados in MEDALHAS.items():
            is_complete = nome in medalhas_conquistadas_set
            
            lista_completa_medalhas.append({
                "nome": nome,
                "descricao": dados.get("descricao", "Descrição pendente"),
                "jc_points": dados.get("jc_points", 0),
                "raridade": dados.get("raridade", "comum"),
                "icone": dados.get("icone", "fa-question-circle"),
                "is_complete": is_complete
            })
        
        lista_completa_medalhas.sort(key=lambda x: x['is_complete'], reverse=True)

        total_medalhas = len(MEDALHAS)
        conquistadas_count = len(medalhas_conquistadas_set)
        
        jc_points_ganhos = 0
        for nome_conquistada in medalhas_conquistadas_set:
            if nome_conquistada in MEDALHAS:
                jc_points_ganhos += MEDALHAS[nome_conquistada].get('jc_points', 0)

        resumo = {
            "conquistadas_texto": f"{conquistadas_count}/{total_medalhas}",
            "jc_points_ganhos": jc_points_ganhos
        }

        return jsonify({
            "sucesso": True, 
            "resumo": resumo,
            "medalhas": lista_completa_medalhas
        })

    except Exception as e:
        print(f"Erro ao buscar medalhas: {e}")
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500

# (Seu código original, mantido)
@api_bp.route('/usuario/<string:user_id>/missoes', methods=['GET'])
def get_missoes_usuario(user_id):
    """
    Retorna uma lista de TODAS as missões diárias,
    o progresso atual do usuário e o status (completa/pendente).
    """
    user_data = get_user_data(user_id)
    if not user_data:
        return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404

    conn = get_db_connection()
    if not conn:
        return jsonify({"sucesso": False, "mensagem": "Erro de conexão com o DB"}), 500

    try:
        completed_today_set = get_completed_daily_missions(user_id, conn)
        
        lista_completa_missoes = []
        total_xp_possivel = 0
        total_xp_ganho = 0
        missoes_concluidas_count = 0
        total_missoes = len(MISSOES_DIARIAS)

        for nome, dados in MISSOES_DIARIAS.items():
            total_xp_possivel += dados.get('xp', 0)
            is_complete = nome in completed_today_set
            
            progresso_atual = user_data.get(dados.get('metrica'), 0)
            requisito = dados.get('requisito', 1)
            
            if is_complete:
                missoes_concluidas_count += 1
                total_xp_ganho += dados.get('xp', 0)
                progresso_percentual = 100
            else:
                progresso_percentual = int((progresso_atual / requisito) * 100) if requisito > 0 else 0
                progresso_percentual = min(progresso_percentual, 100) 

            lista_completa_missoes.append({
                "nome": nome,
                "descricao": dados.get("descricao"),
                "xp": dados.get("xp", 0),
                "jc_points": dados.get("jc_points", 0),
                "raridade": dados.get("raridade", "comum"),
                "icone": dados.get("icone", "fa-question-circle"),
                "is_complete": is_complete,
                "progresso_atual": progresso_atual,
                "requisito": requisito,
                "progresso_percentual": progresso_percentual
            })
        
        lista_completa_missoes.sort(key=lambda x: x['is_complete'])

        resumo = {
            "realizadas_texto": f"{missoes_concluidas_count}/{total_missoes}",
            "xp_conquistado_texto": f"{total_xp_ganho}/{total_xp_possivel}",
            "progresso_percentual": int((missoes_concluidas_count / total_missoes) * 100) if total_missoes > 0 else 0
        }

        return jsonify({
            "sucesso": True, 
            "resumo": resumo,
            "missoes": lista_completa_missoes
        })

    except Exception as e:
        print(f"Erro ao buscar missões: {e}")
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500
    finally:
        if conn:
            conn.close()

# (Seu código original, mantido)
@api_bp.route('/usuario/<string:user_id>/ler_noticia_destaque', methods=['POST'])
def api_ler_noticia_destaque(user_id):
    """
    Registra a leitura de uma notícia DESTAQUE, atualiza XP,
    e verifica medalhas E missões (incluindo "Destaque massa").
    """
    
    user_antes = get_user_data(user_id)
    if not user_antes: 
        return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404
    
    conn = get_db_connection()
    if not conn: 
        return jsonify({"sucesso": False, "mensagem": "Erro de conexão"}), 500

    try:
        agora = datetime.now()
        hoje = agora.date()
        
        acessou_madrugada = (3 <= agora.hour < 5)
        
        dias_consecutivos = user_antes.get('dias_consecutivos_acesso', 0)
        ultimo_acesso = user_antes.get('ultimo_acesso')
        if ultimo_acesso:
            diferenca = (hoje - ultimo_acesso).days
            if diferenca == 1:
                dias_consecutivos += 1
            elif diferenca > 1:
                dias_consecutivos = 1
        else:
            dias_consecutivos = 1 
        
        cursor = conn.cursor()
        xp_por_noticia = 25
        
        cursor.execute("""
            UPDATE gamificacao SET
                xps = xps + %s,
                noticias_completas_total = noticias_completas_total + 1,
                noticias_lidas_hoje = noticias_lidas_hoje + 1,
                noticias_destaque_lidas_hoje = noticias_destaque_lidas_hoje + 1,
                ultimo_acesso = %s,
                dias_consecutivos_acesso = %s
            WHERE usuario_id = %s
        """, (xp_por_noticia, hoje, dias_consecutivos, user_id))
        
        conn.commit()
        cursor.close()

        user_depois = get_user_data(user_id) 
        user_depois['acessou_madrugada'] = acessou_madrugada

        missoes_completadas_agora = check_and_award_daily_missions(user_id, user_depois, conn)
        novas_medalhas_conquistadas = check_and_award_medals(user_id, user_depois)
        user_final = get_user_data(user_id) 
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"+{xp_por_noticia} XP por ler a notícia de destaque!",
            "xp_atual": user_final['xps'],
            "jc_points_atual": user_final['jc_points'],
            "novas_medalhas": novas_medalhas_conquistadas,
            "novas_missoes_diarias": missoes_completadas_agora
        })

    except Exception as e:
        if conn: conn.rollback()
        print(f"Erro na rota ler_noticia_destaque: {e}")
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor: 
            cursor.close()
        if conn: 
            conn.close()

# (Seu código original, mantido)
@api_bp.route('/ranking/<string:user_id>', methods=['GET'])
def get_ranking_data(user_id):
    """
    Retorna o leaderboard (Top 10 por XP) e a posição específica
    do usuário logado.
    """
    try:
        leaderboard = get_leaderboard(limit=10, order_by="xps")
        user_rank = get_user_rank(user_id, order_by="xps")

        if not user_rank:
            user_data = get_user_data(user_id)
            if not user_data:
                return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404
            
            categoria, medalha = calcular_categoria_e_medalha(user_data['xps'])
            user_rank = {
                "posicao": "-",
                "usuario_id": user_id,
                "nome": user_data['nome'],
                "xps": user_data['xps'],
                "jc_points": user_data['jc_points'],
                "categoria": categoria,
                "medalha": medalha
            }

        return jsonify({
            "sucesso": True,
            "leaderboard": leaderboard,
            "user_rank": user_rank
        })

    except Exception as e:
        print(f"Erro ao buscar ranking: {e}")
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500
    
# ---
# 🚀 ATUALIZAÇÃO DA ROTA DE OFENSIVA
# ---
@api_bp.route('/usuario/<string:user_id>/ofensiva', methods=['GET'])
def get_ofensiva_usuario(user_id):
    """
    Retorna a SEQUÊNCIA ATUAL de dias consecutivos
    que o usuário completou pelo menos uma missão.
    """
    print(f"ROTA /ofensiva chamada para user: {user_id}") # Log para debug
    try:
        # 1. Chama a função NOVA (get_user_streak) do gamification.py
        # Ela já retorna o JSON no formato correto:
        # {"sucesso": True, "dias_consecutivos": X}
        resultado_streak = get_user_streak(user_id)
        
        return jsonify(resultado_streak), 200

    except Exception as e:
        print(f"Erro ao buscar ofensiva na ROTA: {e}")
        return jsonify({"sucesso": False, "dias_consecutivos": 0, "erro": str(e)}), 500
    
@api_bp.route('/recompensas/<string:user_id>', methods=['GET'])
def get_recompensas_loja(user_id):
    """
    Retorna a lista de todos os itens da loja e os JC Points atuais do usuário.
    """
    try:
        user_data = get_user_data(user_id)
        if not user_data:
            return jsonify({"sucesso": False, "mensagem": "Utilizador não encontrado"}), 404

        pontos = user_data.get('jc_points', 0)
        
        # Combina todos os dicionários de benefícios em uma única lista
        itens_loja = []
        
        for nome, dados in BENEFITS.items():
            itens_loja.append({
                "id": nome,
                "nome": nome,
                "descricao": dados.get("duracao", "Benefício"),
                "custo": dados["custo"],
                "tipo": "beneficio",
                "raridade": "raro" # (Definindo raridade para o front)
            })
            
        for nome, dados in XP_MULTIPLIERS.items():
            itens_loja.append({
                "id": f"xp_{nome}",
                "nome": f"XP Boost ({nome})",
                "descricao": f"+{int((dados['bonus']-1)*100)}% XP por {dados['duracao_horas']}h",
                "custo": dados["custo"],
                "tipo": "xp",
                "nivel": nome,
                "raridade": "epico" if nome in ["Grande", "Épico"] else "raro"
            })

        for nome, dados in JC_MULTIPLIERS.items():
            itens_loja.append({
                "id": f"jc_{nome}",
                "nome": f"JC Points Boost ({nome})",
                "descricao": f"+{int((dados['bonus']-1)*100)}% JC Points por {dados['duracao_horas']}h",
                "custo": dados["custo"],
                "tipo": "jc",
                "nivel": nome,
                "raridade": "lendario"
            })

        return jsonify({
            "sucesso": True, 
            "jc_points": pontos,
            "itens": itens_loja
        })

    except Exception as e:
        print(f"Erro ao buscar recompensas: {e}")
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500


@api_bp.route('/recompensas/comprar', methods=['POST'])
def comprar_recompensa():
    """
    Processa a compra de um item da loja.
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        item_id = data.get('item_id') # O nome/ID do item
        tipo = data.get('tipo')       # 'beneficio', 'xp', ou 'jc'
        nivel = data.get('nivel')     # 'Pequeno', 'Médio', etc. (só para multiplicadores)

        if not all([user_id, item_id, tipo]):
            return jsonify({"sucesso": False, "mensagem": "Dados incompletos."}), 400

        resultado = None
        if tipo == 'beneficio':
            resultado = redeem_benefit(user_id, item_id)
        elif tipo in ['xp', 'jc']:
            resultado = activate_multiplier(user_id, tipo, nivel)
        else:
            return jsonify({"sucesso": False, "mensagem": "Tipo de item inválido."}), 400

        # Verifica se a função de benefício retornou um erro
        if 'erro' in resultado:
            return jsonify({"sucesso": False, "mensagem": resultado['erro']}), 400
        
        # Sucesso
        return jsonify({"sucesso": True, "mensagem": resultado['mensagem'], "saldo_atual": resultado['saldo_atual']}), 200

    except Exception as e:
        print(f"Erro ao comprar recompensa: {e}")
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500
    
@api_bp.route('/recompensas/inventario/<string:user_id>', methods=['GET'])
def get_inventario_usuario(user_id):
    """
    Retorna a lista de itens comprados pelo usuário.
    """
    try:
        items = get_user_inventory_from_db(user_id)
        
        # Formata as datas para string
        for item in items:
            if item['data_resgate']:
                item['data_resgate'] = item['data_resgate'].strftime('%d/%m/%Y')
            if item['data_expiracao']:
                item['data_expiracao'] = item['data_expiracao'].strftime('%d/%m/%Y')
            else:
                item['data_expiracao'] = "Permanente"

        return jsonify({"sucesso": True, "inventario": items})

    except Exception as e:
        print(f"Erro na rota inventario: {e}")
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500