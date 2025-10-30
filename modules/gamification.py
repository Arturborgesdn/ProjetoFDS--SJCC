# modules/gamification.py

import mysql.connector
from datetime import datetime, date
from config import Config

# ===============================================
# LÓGICA DE GAMIFICAÇÃO (MEDALHAS E CATEGORIAS)
# (Migrado integralmente do seu código)
# ===============================================

# --- Medalhas Definidas ---
MEDALHAS = {
    "Novinho em folha": {"jc_points": 10, "check": lambda u: u.get('noticias_completas_total', 0) >= 1},
    "Pegou ar": {"jc_points": 50, "check": lambda u: u.get('dias_consecutivos_acesso', 0) >= 7},
    "Inimigo do sono": {"jc_points": 100, "check": lambda u: u.get('acessou_madrugada', False)},
    "Sem Leseira": {"jc_points": 100, "check": lambda u: u.get('noticias_completas_total', 0) >= 50},
    "Mil conto": {"jc_points": 80, "check": lambda u: u.get('jc_points', 0) >= 1000},
    "Êta bicho insistente": {"jc_points": 100, "check": lambda u: u.get('dias_consecutivos_acesso', 0) >= 30}
}

# --- Funções de Categoria, Nível e XP ---

# modules/gamification.py

# ... (imports e MEDALHAS omitidos) ...

def calcular_categoria_e_medalha(xp: int):
    """Calcula Categoria e Medalha (Bronze, Prata, Ouro) com base no XP."""
    
    # 1. Leitor Leigo (0 a 1500 XP)
    if xp <= 1500:
        categoria = "Leitor Leigo"
        if xp <= 500: medalha = "Bronze"       # 0 - 500
        elif xp <= 1000: medalha = "Prata"      # 501 - 1000
        else: medalha = "Ouro"                  # 1001 - 1500
        
    # 2. Leitor Massa (1501 a 3000 XP)
    elif xp <= 3000:
        categoria = "Leitor Massa"
        if xp <= 2000: medalha = "Bronze"       # 1501 - 2000
        elif xp <= 2500: medalha = "Prata"      # 2001 - 2500
        else: medalha = "Ouro"                  # 2501 - 3000

    # 3. Leitor Engajado (3001 a 4500 XP)
    elif xp <= 4500:
        categoria = "Leitor Engajado"
        if xp <= 3500: medalha = "Bronze"       # 3001 - 3500
        elif xp <= 4000: medalha = "Prata"      # 3501 - 4000
        else: medalha = "Ouro"                  # 4001 - 4500

    # 4. Leitor Arretado (4501 a 6000 XP)
    elif xp <= 6000:
        categoria = "Leitor Arretado"
        if xp <= 5000: medalha = "Bronze"       # 4501 - 5000
        elif xp <= 5500: medalha = "Prata"      # 5001 - 5500
        else: medalha = "Ouro"                  # 5501 - 6000

    # 5. Leitor Desenrolado (6001 a 7500 XP)
    elif xp <= 7500:
        categoria = "Leitor Desenrolado"
        if xp <= 6500: medalha = "Bronze"       # 6001 - 6500
        elif xp <= 7000: medalha = "Prata"      # 6501 - 7000
        else: medalha = "Ouro"                  # 7001 - 7500
        
    # 6. Leitor Topado (7501+ XP)
    else:
        categoria = "Leitor Topado"
        # Regras de XP Topado: Bronze (7501-8500) / Prata (8501-9500) / Ouro (9501+)
        if xp <= 8500: medalha = "Bronze"
        elif xp <= 9500: medalha = "Prata"
        else: medalha = "Ouro" # 9501+

    return categoria, medalha


# modules/gamification.py

# ... (código anterior omitido) ...

def calcular_nivel(xp: int):
    """
    Calcula o Nível e o Progresso da Barra de XP.
    
    A barra visual (percentual) se baseia no ciclo de 1500 XP.
    O texto (progresso_xp_texto) exibe o XP TOTAL / LIMITE DA CATEGORIA.
    """
    
    nivel, xp_limite_categoria, xp_base_nivel_atual = 1, 1500, 0
    
    # 1. Determinar o limite da categoria atual (1500, 3000, 4500, etc.)
    while xp >= xp_limite_categoria:
        nivel += 1
        xp_base_nivel_atual = xp_limite_categoria
        xp_limite_categoria += 1500 
        
    # 2. Calcular progresso DENTRO da categoria (para a barra visual)
    xp_no_ciclo_atual = xp - xp_base_nivel_atual # XP de 0 a 1500
    xp_total_do_ciclo = xp_limite_categoria - xp_base_nivel_atual # O limite do ciclo (1500)

    # 3. Calcular a porcentagem da barra (0-100%)
    progresso_percentual = int((xp_no_ciclo_atual / xp_total_do_ciclo) * 100) if xp_total_do_ciclo > 0 else 0
    
    # 4. Retornar o XP TOTAL / LIMITE DA CATEGORIA para o texto
    return {
        "nivel": nivel,
        "progresso_xp_texto": f"{xp} / {xp_limite_categoria}", # NOVO FORMATO SOLICITADO
        "progresso_percentual": progresso_percentual
    }


MISSOES_DIARIAS = {
    
    "Fica de olho, visse?": {
        "descricao": "Passar 10 minutos no site",
        "xp": 100,
        "jc_points": 20,
        "metrica": "tempo_online_hoje_minutos", 
        "requisito": 10,
        "check": lambda u: u.get('tempo_online_hoje_minutos', 0) >= 10
    },
    
}
# ===============================================
# FUNÇÕES AUXILIARES DA BASE DE DADOS
# ===============================================

def get_db_connection():
    """Tenta conectar ao banco de dados MySQL."""
    try:
        # Usa a configuração importada do arquivo config.py
        return mysql.connector.connect(**Config.MYSQL_CONFIG)
    except mysql.connector.Error as err:
        print(f"Erro ao conectar: {err}")
        return None

def get_user_data(user_id):
    """Busca dados do utilizador e suas medalhas."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    user_data = None
    try:
        cursor.execute(
            "SELECT g.*, u.nome FROM gamificacao g JOIN usuarios u ON g.usuario_id = u.id WHERE g.usuario_id = %s",
             (user_id,)
        )
        user_data = cursor.fetchone()
        if user_data:
            cursor.execute("SELECT medalha_nome FROM medalhas_usuario WHERE usuario_id = %s", (user_id,))
            medalhas = [row['medalha_nome'] for row in cursor.fetchall()]
            user_data['medalhas_conquistadas'] = medalhas
    except Exception as e:
        print(f"Erro ao buscar dados do utilizador {user_id}: {e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return user_data

def adicionar_xp_jc(user_id, xp_ganho=0, jc_ganho=0):
    """Adiciona XP e/ou JC Points a um utilizador."""
    if xp_ganho == 0 and jc_ganho == 0: return True

    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE gamificacao SET xps = xps + %s, jc_points = jc_points + %s WHERE usuario_id = %s",
            (xp_ganho, jc_ganho, user_id)
        )
        conn.commit()
        print(f"Utilizador {user_id}: +{xp_ganho} XP, +{jc_ganho} JC Points")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao adicionar XP/JC Points para {user_id}: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def award_medal(user_id, medalha_nome, jc_points_ganhos):
    """Regista uma medalha conquistada e adiciona os JC Points."""
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO medalhas_usuario (usuario_id, medalha_nome) VALUES (%s, %s)",
            (user_id, medalha_nome)
        )
        conn.commit()
        print(f"🏅 Medalha '{medalha_nome}' concedida ao utilizador {user_id}!")
        if jc_points_ganhos > 0:
            adicionar_xp_jc(user_id, jc_ganho=jc_points_ganhos)
        return True
    except mysql.connector.IntegrityError:
        print(f"Utilizador {user_id} já possui a medalha '{medalha_nome}'.")
        return False
    except Exception as e:
        conn.rollback()
        print(f"Erro ao conceder medalha '{medalha_nome}' para {user_id}: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    
# modules/gamification.py
# ... (imports, Config, MEDALHAS, MISSOES_DIARIAS) ...

# --- NOVAS FUNÇÕES PARA GERENCIAR MISSÕES DIÁRIAS ---

def get_completed_daily_missions(user_id, conn=None):
    """Busca as missões diárias já completadas pelo usuário HOJE."""
    should_close_conn = False
    if not conn: 
        conn = get_db_connection()
        should_close_conn = True # Marcar para fechar a conexão no final
    if not conn: return set() # Retorna um conjunto vazio se não houver conexão
    
    cursor = conn.cursor()
    completed_missions = set()
    today_str = date.today().isoformat()
    try:
        # Busca na tabela missoes_diarias_usuario
        cursor.execute(
            "SELECT missao_nome FROM missoes_diarias_usuario WHERE usuario_id = %s AND data_conclusao = %s",
            (user_id, today_str)
        )
        for row in cursor.fetchall():
            completed_missions.add(row[0]) # Adiciona o nome da missão ao conjunto
    except Exception as e:
        print(f"Erro ao buscar missões completas para {user_id}: {e}")
    finally:
        if cursor: cursor.close()
        if should_close_conn and conn: conn.close() # Fecha a conexão só se foi criada aqui
    return completed_missions

def mark_daily_mission_complete(user_id, missao_nome, conn=None):
    """Marca uma missão diária como completa para o usuário HOJE no banco de dados."""
    should_close_conn = False
    if not conn: 
        conn = get_db_connection()
        should_close_conn = True
    if not conn: return False
    
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    try:
        # Insere o registro na tabela missoes_diarias_usuario
        cursor.execute(
            "INSERT INTO missoes_diarias_usuario (usuario_id, missao_nome, data_conclusao) VALUES (%s, %s, %s)",
            (user_id, missao_nome, today_str)
        )
        conn.commit()
        print(f"Missão '{missao_nome}' marcada como completa para {user_id} hoje.") # Log
        return True
    except mysql.connector.IntegrityError: # Caso a missão já tenha sido registrada hoje
        print(f"Missão '{missao_nome}' já estava completa para {user_id} hoje.") # Log
        return True # Considera sucesso, pois já está marcada
    except Exception as e:
        if conn: conn.rollback()
        print(f"Erro ao marcar missão '{missao_nome}' como completa para {user_id}: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if should_close_conn and conn: conn.close()

# ESTA É A FUNÇÃO PRINCIPAL DE VERIFICAÇÃO
def check_and_award_daily_missions(user_id, user_data, conn):
    """
    Verifica TODAS as missões diárias definidas em MISSOES_DIARIAS.
    Se uma missão foi cumprida (baseado em user_data) E ainda não foi marcada como
    completa hoje, marca como completa e concede XP/JC Points.
    Retorna uma lista das missões recém-completadas.
    """
    if not conn:
        print("Erro Crítico: Conexão com DB é necessária para check_and_award_daily_missions")
        return [] # Retorna lista vazia se não houver conexão

    # Busca quais missões o usuário já completou hoje
    completed_today = get_completed_daily_missions(user_id, conn)
    newly_completed_missions = [] # Lista para retornar as missões completadas AGORA

    # Itera sobre todas as missões definidas no dicionário MISSOES_DIARIAS
    for nome_missao, dados_missao in MISSOES_DIARIAS.items():
        
        # Condição 1: A missão ainda NÃO foi completada hoje
        # Condição 2: A função 'check' da missão retorna True (baseado nos dados atuais do usuário)
        if nome_missao not in completed_today and dados_missao['check'](user_data):
            
            print(f"Tentando completar missão '{nome_missao}' para {user_id}...") # Log
            
            # Tenta marcar a missão como completa no banco de dados
            if mark_daily_mission_complete(user_id, nome_missao, conn):
                
                # Se marcou com sucesso, tenta adicionar o XP e JC Points
                if adicionar_xp_jc(user_id, xp_ganho=dados_missao['xp'], jc_ganho=dados_missao['jc_points']):
                    print(f"✅ Missão Diária '{nome_missao}' completada E recompensada para {user_id}!") # Log
                    # Adiciona à lista de retorno para o frontend saber o que foi completado
                    newly_completed_missions.append({
                        "nome": nome_missao,
                        "xp": dados_missao['xp'],
                        "jc_points": dados_missao['jc_points']
                    })
                else:
                    # Se falhar ao dar XP/JC, loga um aviso. Idealmente, deveria desfazer a marcação.
                    print(f"⚠️ Alerta: Falha ao conceder recompensa para missão '{nome_missao}' (já marcada como completa) para {user_id}.")
            else:
                 print(f"⚠️ Alerta: Falha ao MARCAR missão '{nome_missao}' como completa para {user_id}.")

    return newly_completed_missions # Retorna a lista de missões completadas nesta verificação

# ... (Restante do seu gamification.py: calcular_categoria_e_medalha, calcular_nivel, etc.) ...