# modules/db_services.py
# Camada de Acesso a Dados (Data Access Layer)
# Responsável EXCLUSIVAMENTE por executar SQL e interagir com o banco.

import mysql.connector
from datetime import date
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
    """Busca dados brutos do utilizador e suas medalhas do DB."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    user_data = None
    try:
        # 1. Busca dados da tabela gamificacao e usuarios
        cursor.execute(
            "SELECT g.*, u.nome FROM gamificacao g JOIN usuarios u ON g.usuario_id = u.id WHERE g.usuario_id = %s",
             (user_id,)
        )
        user_data = cursor.fetchone()
        
        # 2. Se o usuário existe, busca suas medalhas
        if user_data:
            cursor.execute("SELECT medalha_nome FROM medalhas_usuario WHERE usuario_id = %s", (user_id,))
            medalhas = [row['medalha_nome'] for row in cursor.fetchall()]
            user_data['medalhas_conquistadas'] = medalhas
            
    except Exception as e:
        print(f"Erro ao buscar dados do utilizador {user_id} no DB: {e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return user_data

def get_completed_missions_from_db(user_id, conn):
    """Busca os nomes das missões diárias já completadas HOJE."""
    # Reutiliza a conexão (passada como argumento) para performance
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
        # Não fechamos a conexão, pois ela é gerenciada pela função que chamou
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
    except mysql.connector.IntegrityError: # Se já possui a medalha
        print(f"DB Info: Utilizador {user_id} já possui a medalha '{medalha_nome}'.")
        return False # Retorna False pois não foi uma *nova* inserção
    except Exception as e:
        conn.rollback()
        print(f"Erro ao inserir medalha no DB para {user_id}: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def insert_daily_mission_in_db(user_id, missao_nome, conn):
    """Insere o registro de uma missão diária completa no DB HOJE."""
    # Reutiliza a conexão
    if not conn: return False
    
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    try:
        cursor.execute(
            "INSERT INTO missoes_diarias_usuario (usuario_id, missao_nome, data_conclusao) VALUES (%s, %s, %s)",
            (user_id, missao_nome, today_str)
        )
        conn.commit()
        print(f"DB Insert: Missão '{missao_nome}' marcada como completa para {user_id} hoje.")
        return True
    except mysql.connector.IntegrityError: # Se já completou hoje
        print(f"DB Info: Missão '{missao_nome}' já estava completa para {user_id} hoje.")
        return True # Considera sucesso
    except Exception as e:
        if conn: conn.rollback()
        print(f"Erro ao inserir missão diária no DB para {user_id}: {e}")
        return False
    finally:
        if cursor: cursor.close()