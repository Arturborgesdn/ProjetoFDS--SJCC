import mysql.connector
import os
from datetime import date, datetime

# ==========================================================
# 🔌 CONEXÃO INTELIGENTE (Centralizada)
# ==========================================================
def get_db_connection():
    """
    Estabelece conexão com o banco de dados.
    Prioriza variáveis de ambiente (Nuvem/Railway), 
    senão usa fallback local (Windows).
    """
    db_url = os.getenv("DATABASE_URL")
    
    # Se existirem variáveis de ambiente, usa a Nuvem
    if db_url or os.getenv("MYSQLHOST"):
        return mysql.connector.connect(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE"),
            port=os.getenv("MYSQLPORT")
        )
    else:
        # Fallback: Seu banco local
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="senhabanco123@", 
            database="dbjc"
        )

# ==========================================================
# FUNÇÕES DE LEITURA (SELECT)
# ==========================================================

def get_user_data_from_db(user_id):
    """
    Busca dados brutos do utilizador.
    Inclui lógica de RESET DIÁRIO dos contadores.
    """
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    
    try:
        # --- Lógica de RESET DIÁRIO ---
        today = date.today()
        cursor.execute("SELECT ultima_atualizacao_diaria FROM gamificacao WHERE usuario_id = %s", (user_id,))
        result = cursor.fetchone()
        
        last_update = result['ultima_atualizacao_diaria'] if result else None
            
        if not last_update or last_update < today:
            # print(f"NOVO DIA: Zerando contadores diários para {user_id}.")
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
            conn.commit()
        # --- FIM DO RESET ---

        # Busca principal
        query = """
            SELECT u.id AS usuario_id, u.nome, u.email,
                   g.xps, g.jc_points, 
                   g.dias_consecutivos_acesso, g.noticias_completas_total, 
                   g.ultimo_acesso, g.tempo_online_hoje_minutos, 
                   g.compartilhamentos_hoje,  
                   g.noticias_lidas_hoje,
                   g.noticias_destaque_lidas_hoje
            FROM usuarios u
            LEFT JOIN gamificacao g ON u.id = g.usuario_id
            WHERE u.id = %s
        """
        cursor.execute(query, (user_id,))
        user_data = cursor.fetchone()
        
        if user_data:
            # Define valores padrão para evitar None
            keys_to_check = ['xps', 'jc_points', 'dias_consecutivos_acesso', 'noticias_completas_total', 
                             'tempo_online_hoje_minutos', 'compartilhamentos_hoje', 
                             'noticias_lidas_hoje', 'noticias_destaque_lidas_hoje']
            for key in keys_to_check:
                user_data[key] = user_data[key] or 0

            # Busca medalhas
            cursor.execute("SELECT medalha_nome FROM medalhas_usuario WHERE usuario_id = %s", (user_id,))
            medalhas = [row['medalha_nome'] for row in cursor.fetchall()]
            user_data['medalhas_conquistadas'] = medalhas
            
        return user_data

    except Exception as e:
        print(f"Erro ao buscar dados do utilizador {user_id}: {e}")
        if conn: conn.rollback()
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_completed_missions_from_db(user_id, conn=None):
    """Busca os nomes das missões diárias já completadas HOJE."""
    # Se a conexão não for passada, cria uma nova
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
        
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
        print(f"Erro ao buscar missões completas: {e}")
    finally:
        if cursor: cursor.close()
        if close_conn: conn.close()
    return completed_missions

def get_leaderboard_from_db(limit=10, order_by="xps"):
    conn = get_db_connection()
    if not conn: return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        if order_by not in ("xps", "jc_points"): order_by = "xps"
        
        query = f"""
            SELECT u.nome, g.xps, g.jc_points 
            FROM gamificacao g
            JOIN usuarios u ON g.usuario_id = u.id
            ORDER BY g.{order_by} DESC, g.xps DESC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro no leaderboard: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_user_rank_from_db(user_id, order_by="xps"):
    conn = get_db_connection()
    if not conn: return None
    
    cursor = conn.cursor(dictionary=True)
    try:
        if order_by not in ("xps", "jc_points"): order_by = "xps"

        # Usa Window Functions (MySQL 8.0+ suportado pela Railway)
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
        print(f"Erro no user rank: {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_user_streak_from_db(user_id):
    """Calcula a sequência (streak) de dias consecutivos."""
    conn = get_db_connection()
    if not conn: return 0
    
    cursor = conn.cursor(dictionary=True)
    try:
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
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        return int(result['dias_consecutivos']) if result else 0
    except Exception as e:
        print(f"Erro streak: {e}")
        return 0
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_user_inventory_from_db(user_id):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM beneficios_resgatados WHERE usuario_id = %s ORDER BY data_resgate DESC", (user_id,))
        return cursor.fetchall()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ==========================================================
# FUNÇÕES DE ESCRITA (INSERT/UPDATE)
# ==========================================================

def update_xp_jc_in_db(user_id, xp_ganho, jc_ganho):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE gamificacao SET xps = xps + %s, jc_points = jc_points + %s WHERE usuario_id = %s",
            (xp_ganho, jc_ganho, user_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro update XP/JC: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def insert_medal_in_db(user_id, medalha_nome):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO medalhas_usuario (usuario_id, medalha_nome) VALUES (%s, %s)",
            (user_id, medalha_nome)
        )
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        return False 
    except Exception as e:
        print(f"Erro insert medalha: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def insert_daily_mission_in_db(user_id, missao_nome, conn):
    """
    Insere missão diária.
    NOTA: Não faz commit nem fecha a conexão, pois é parte de uma transação maior.
    """
    if not conn: return False
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    try:
        cursor.execute(
            "INSERT INTO missoes_diarias_usuario (usuario_id, missao_nome, data_conclusao) VALUES (%s, %s, %s)",
            (user_id, missao_nome, today_str)
        )
        return True
    except mysql.connector.IntegrityError:
        return False
    except Exception as e:
        print(f"Erro insert missao: {e}")
        return False
    finally:
        if cursor: cursor.close()