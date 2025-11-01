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
        # ... (A lógica de RESET DIÁRIO que já existe aqui está correta) ...
        today = date.today()
        cursor.execute(
            "SELECT ultima_atualizacao_diaria FROM gamificacao WHERE usuario_id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
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
                        ultima_atualizacao_diaria = %s
                    WHERE usuario_id = %s
                    """,
                    (today, user_id)
                )
                conn.commit()
                print(f"Contadores para {user_id} zerados com sucesso para o dia {today}.")
        # --- FIM DO RESET ---

        # --- CORREÇÃO DO SQL: ADICIONADO 'g.compartilhamentos_hoje' ---
        cursor.execute(
            """
            SELECT u.id AS usuario_id, u.nome, g.xps, g.jc_points, 
                   g.dias_consecutivos_acesso, g.noticias_completas_total, 
                   g.ultimo_acesso, g.tempo_online_hoje_minutos, 
                   g.compartilhamentos_hoje,  -- <--- ADICIONADO AQUI
                   g.noticias_lidas_hoje
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
            
            # --- CORREÇÃO: ADICIONADO O VALOR PADRÃO ---
            user_data['compartilhamentos_hoje'] = user_data['compartilhamentos_hoje'] or 0
            
            user_data['noticias_lidas_hoje'] = user_data['noticias_lidas_hoje'] or 0

            # Busca medalhas
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

# --- NOVA FUNÇÃO PARA ZERAR CONTADORES DIÁRIOS ---
def reset_daily_metrics_if_needed(user_id, conn):
    """
    Verifica se a última atualização foi em um dia anterior ao de hoje.
    Se sim, zera todos os contadores diários ('_hoje').
    """
    if not conn:
        print("AVISO: reset_daily_metrics_if_needed requer uma conexão com o DB.")
        return

    cursor = conn.cursor(dictionary=True)
    today = date.today()

    try:
        # 1. Pega a data da última atualização para este usuário
        cursor.execute(
            "SELECT ultima_atualizacao_diaria FROM gamificacao WHERE usuario_id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        last_update = result['ultima_atualizacao_diaria'] if result else None

        # 2. Se nunca houve uma atualização ou se a data é de um dia anterior
        if not last_update or last_update < today:
            print(f"NOVO DIA: Zerando contadores diários para o usuário {user_id}.")
            
            # 3. Executa o UPDATE para zerar os contadores
            cursor.execute(
                """
                UPDATE gamificacao
                SET
                    tempo_online_hoje_minutos = 0,
                    compartilhamentos_hoje = 0,
                    noticias_lidas_hoje = 0,
                    ultima_atualizacao_diaria = %s
                WHERE usuario_id = %s
                """,
                (today, user_id)
            )
            conn.commit()
            print(f"Contadores para {user_id} zerados com sucesso para o dia {today}.")

    except Exception as e:
        print(f"Erro ao tentar zerar as métricas diárias para {user_id}: {e}")
        # Não fazemos rollback aqui para não atrapalhar a operação principal que chamou esta função
    finally:
        if cursor:
            cursor.close()