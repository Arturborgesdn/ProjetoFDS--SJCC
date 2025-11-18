# modules/db_services.py
# Camada de Acesso a Dados (Data Access Layer)
# Responsável EXCLUSIVAMENTE por executar SQL e interagir com o banco.

import mysql.connector
from datetime import date, datetime
from config import Config

# --- Conexão ---

def get_db_connection():
    """Tenta conectar ao banco de dados MySQL."""
    try:
        return mysql.connector.connect(**Config.MYSQL_CONFIG)
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao DB: {err}")
        return None

# --- Funções de Leitura (SELECT) ---

def get_user_data_from_db(user_id):
    """
    Busca dados brutos do utilizador.
    Usa LEFT JOIN e agora INCLUI 'compartilhamentos_hoje'.
    """
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    user_data = None
    
    try:
        # Lógica de RESET DIÁRIO (Otimizada para usar a mesma conexão)
        today = date.today()
        cursor.execute(
            "SELECT ultima_atualizacao_diaria FROM gamificacao WHERE usuario_id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        
        last_update = None
        if result:
            last_update = result['ultima_atualizacao_diaria']
            
        if not last_update or last_update < today:
            print(f"NOVO DIA: Zerando contadores diários para o usuário {user_id} (via get_user_data).")
            cursor.execute(
                """
                UPDATE gamificacao
                SET
                    tempo_online_hoje_minutos = 0,
                    compartilhamentos_hoje = 0,
                    noticias_lidas_hoje = 0,
                    noticias_destaque_lidas_hoje = 0,
                    ultima_atualizacao_diaria = %s
                WHERE usuario_id = %s
                """,
                (today, user_id)
            )
            conn.commit() # Commit do reset é seguro aqui
            print(f"Contadores para {user_id} zerados com sucesso para o dia {today}.")
        # --- FIM DO RESET ---

        # Busca principal dos dados do usuário
        cursor.execute(
            """
            SELECT u.id AS usuario_id, u.nome, g.xps, g.jc_points, 
                   g.dias_consecutivos_acesso, g.noticias_completas_total, 
                   g.ultimo_acesso, g.tempo_online_hoje_minutos, 
                   g.compartilhamentos_hoje,  
                   g.noticias_lidas_hoje,
                   g.noticias_destaque_lidas_hoje
            FROM usuarios u
            LEFT JOIN gamificacao g ON u.id = g.usuario_id
            WHERE u.id = %s
            """,
             (user_id,)
        )
        user_data = cursor.fetchone()
        
        if user_data:
            # Define valores padrão (0) para evitar erros
            user_data['xps'] = user_data['xps'] or 0
            user_data['jc_points'] = user_data['jc_points'] or 0
            user_data['dias_consecutivos_acesso'] = user_data['dias_consecutivos_acesso'] or 0
            user_data['noticias_completas_total'] = user_data['noticias_completas_total'] or 0
            user_data['tempo_online_hoje_minutos'] = user_data['tempo_online_hoje_minutos'] or 0
            user_data['compartilhamentos_hoje'] = user_data['compartilhamentos_hoje'] or 0
            user_data['noticias_lidas_hoje'] = user_data['noticias_lidas_hoje'] or 0
            user_data['noticias_destaque_lidas_hoje'] = user_data['noticias_destaque_lidas_hoje'] or 0

            # Busca medalhas
            cursor.execute("SELECT medalha_nome FROM medalhas_usuario WHERE usuario_id = %s", (user_id,))
            medalhas = [row['medalha_nome'] for row in cursor.fetchall()]
            user_data['medalhas_conquistadas'] = medalhas
            
    except Exception as e:
        print(f"Erro ao buscar dados do utilizador {user_id} no DB: {e}")
        if conn: conn.rollback() # Rollback em caso de erro no Try
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return user_data

def get_completed_missions_from_db(user_id, conn):
    """Busca os nomes das missões diárias já completadas HOJE."""
    if not conn: return set() 
    
    cursor = conn.cursor()
    completed_missions = set()
    today_str = date.today().isoformat()
    try:
        cursor.execute(
            "SELECT missao_nome FROM missoes_diarias_usuario WHERE usuario_id = %s AND data_conclusao = %s",
            (user_id, today_str)
        )
        for row in cursor.fetchall():
            completed_missions.add(row[0])
    except Exception as e:
        print(f"Erro ao buscar missões completas do DB para {user_id}: {e}")
    finally:
        if cursor: cursor.close()
    return completed_missions

# --- Funções de Escrita (INSERT/UPDATE) ---

def update_xp_jc_in_db(user_id, xp_ganho=0, jc_ganho=0):
    """Atualiza XP e/ou JC Points no DB."""
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
        print(f"DB Update: Utilizador {user_id}: +{xp_ganho} XP, +{jc_ganho} JC Points")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar XP/JC no DB para {user_id}: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def insert_medal_in_db(user_id, medalha_nome):
    """Insere o registro de uma nova medalha no DB."""
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO medalhas_usuario (usuario_id, medalha_nome) VALUES (%s, %s)",
            (user_id, medalha_nome)
        )
        conn.commit()
        print(f"DB Insert: Medalha '{medalha_nome}' concedida a {user_id}.")
        return True
    except mysql.connector.IntegrityError:
        print(f"DB Info: Utilizador {user_id} já possui a medalha '{medalha_nome}'.")
        return False
    except Exception as e:
        conn.rollback()
        print(f"Erro ao inserir medalha no DB para {user_id}: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def insert_daily_mission_in_db(user_id, missao_nome, conn):
    """Insere o registro de uma missão diária completa no DB HOJE."""
    if not conn: return False
    
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    try:
        cursor.execute(
            "INSERT INTO missoes_diarias_usuario (usuario_id, missao_nome, data_conclusao) VALUES (%s, %s, %s)",
            (user_id, missao_nome, today_str)
        )
        
        # 🚀 ATUALIZAÇÃO CRÍTICA: COMMIT REMOVIDO DAQUI
        # A função 'check_and_award_daily_missions' fará o commit.
        # conn.commit() <-- REMOVIDO
        
        print(f"DB Insert: Missão '{missao_nome}' marcada (pendente de commit) para {user_id} hoje.")
        return True # Retorna True se a INSERÇÃO ocorreu
    
    except mysql.connector.IntegrityError: # Se já completou hoje
        print(f"DB Info: Missão '{missao_nome}' já estava completa para {user_id} hoje.")
        return False # Retorna False pois não foi uma *nova* inserção
    
    except Exception as e:
        # 🚀 ATUALIZAÇÃO CRÍTICA: ROLLBACK REMOVIDO DAQUI
        # A função 'check_and_award_daily_missions' fará o rollback.
        # if conn: conn.rollback() <-- REMOVIDO
        print(f"Erro ao inserir missão diária no DB para {user_id}: {e}")
        return False
    finally:
        if cursor: cursor.close()

def reset_daily_metrics_if_needed(user_id, conn):
    """
    Verifica se a última atualização foi em um dia anterior ao de hoje.
    Se sim, zera todos os contadores diários ('_hoje').
    (Esta função é chamada por get_user_data_from_db, que usa sua própria conexão)
    """
    pass # A lógica já foi movida para dentro de get_user_data_from_db

def get_leaderboard_from_db(limit=10, order_by="xps"):
    """
    Retorna o ranking geral dos usuários com base em XP ou JC Points.
    """
    conn = get_db_connection()
    if not conn:
        print("❌ Falha na conexão ao banco.")
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        if order_by not in ("xps", "jc_points"):
            order_by = "xps"

        query = f"""
            SELECT 
                u.id AS usuario_id,
                u.nome,
                g.xps,
                g.jc_points,
                g.dias_consecutivos_acesso,
                g.noticias_completas_total
            FROM gamificacao g
            JOIN usuarios u ON g.usuario_id = u.id
            ORDER BY g.{order_by} DESC, g.xps DESC
            LIMIT %s;
        """
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    
    except Exception as e:
        print(f"❌ Erro ao buscar ranking: {e}")
        return []
    
    finally:
        cursor.close()
        conn.close()


def get_user_rank_from_db(user_id, order_by="xps"):
    """
    Retorna a posição do usuário no ranking geral (por XP ou JC Points).
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor(dictionary=True)
    try:
        if order_by not in ("xps", "jc_points"):
            order_by = "xps"

        query = f"""
            SELECT posicao, usuario_id, nome, xps, jc_points FROM (
                SELECT 
                    u.id AS usuario_id,
                    u.nome,
                    g.xps,
                    g.jc_points,
                    RANK() OVER (ORDER BY g.{order_by} DESC, g.xps DESC) AS posicao
                FROM gamificacao g
                JOIN usuarios u ON g.usuario_id = u.id
            ) ranked
            WHERE usuario_id = %s;
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
    
    except Exception as e:
        print(f"❌ Erro ao buscar posição do usuário: {e}")
        return None
    
    finally:
        cursor.close()
        conn.close()

# ---
# 🚀 FUNÇÃO DE OFENSIVA (ADICIONADA)
# ---
def get_user_streak_from_db(user_id):
    """
    Calcula a sequência ATUAL de dias consecutivos com missões completas.
    A sequência é "atual" se o último dia foi HOJE ou ONTEM.
    """
    conn = get_db_connection()
    if not conn:
        print("❌ Falha na conexão ao banco (get_user_streak_from_db).")
        return 0
    
    cursor = conn.cursor(dictionary=True)
    
    query = """
        WITH Sequencias AS (
            SELECT 
                data_registro,
                DATE_SUB(data_registro, INTERVAL ROW_NUMBER() OVER (ORDER BY data_registro) DAY) as grupo_seq
            FROM ofensiva_usuario
            WHERE usuario_id = %s
        ),
        ContagemSeq AS (
            SELECT 
                COUNT(*) as dias_consecutivos,
                MAX(data_registro) as ultimo_dia_seq
            FROM Sequencias
            GROUP BY grupo_seq
        )
        SELECT 
            CASE
                WHEN ultimo_dia_seq >= CURDATE() - INTERVAL 1 DAY THEN dias_consecutivos
                ELSE 0
            END as dias_consecutivos
        FROM ContagemSeq
        ORDER BY ultimo_dia_seq DESC
        LIMIT 1;
    """
    
    try:
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        
        if result:
            return int(result['dias_consecutivos'])
        else:
            return 0
            
    except Exception as e:
        print(f"❌ Erro ao buscar sequência (streak) do DB: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()
        
def get_user_inventory_from_db(user_id):
    """
    Busca todos os itens ativos que o usuário já resgatou.
    """
    conn = get_db_connection()
    if not conn: return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Busca itens que ainda não expiraram ou que são permanentes
        query = """
            SELECT nome_beneficio, data_resgate, data_expiracao, ativo
            FROM beneficios_resgatados
            WHERE usuario_id = %s 
            ORDER BY data_resgate DESC
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao buscar inventário: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()