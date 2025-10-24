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

def calcular_categoria_e_medalha(xp: int):
    """Calcula Categoria e Medalha com base no XP."""
    if xp <= 0: return "Sem Categoria", "Nenhuma"
    elif 0 <= xp <= 1500:
        categoria = "Leitor Leigo"
        if xp <= 500: medalha = "Bronze"
        elif xp <= 1000: medalha = "Prata"
        else: medalha = "Ouro"
    # ... (Restante da lógica da Categoria) ...
    elif 1501 <= xp <= 3000:
        categoria = "Leitor Massa"
        if xp <= 2000: medalha = "Bronze"
        elif xp <= 2500: medalha = "Prata"
        else: medalha = "Ouro"
    elif 3001 <= xp <= 4500:
        categoria = "Leitor Engajado"
        if xp <= 3500: medalha = "Bronze"
        elif xp <= 4000: medalha = "Prata"
        else: medalha = "Ouro"
    elif 4501 <= xp <= 6000:
        categoria = "Leitor Arretado"
        if xp <= 5000: medalha = "Bronze"
        elif xp <= 5500: medalha = "Prata"
        else: medalha = "Ouro"
    elif 6001 <= xp <= 7500:
        categoria = "Leitor Desenrolado"
        if xp <= 6500: medalha = "Bronze"
        elif xp <= 7000: medalha = "Prata"
        else: medalha = "Ouro"
    else: # xp >= 7501
        categoria = "Leitor Topado"
        if xp <= 8500: medalha = "Bronze"
        elif xp <= 9500: medalha = "Prata"
        else: medalha = "Ouro"
    return categoria, medalha

def calcular_nivel(xp: int):
    """Calcula Nível e Progresso da Barra de XP."""
    
    # === ALTERAÇÃO AQUI (Linha 1): Mudar o XP inicial para o próximo nível para 1500 ===
    # Assumindo que você quer que o Nível 1 vá de 0 a 1500.
    nivel, xp_para_proximo_nivel, xp_base_nivel_atual = 1, 1500, 0 # ALTERADO
    
    while xp >= xp_para_proximo_nivel:
        nivel += 1
        xp_base_nivel_atual = xp_para_proximo_nivel
        # O cálculo de progressão precisa ser ajustado se você quer um aumento diferente de 300 + 150*(n-1)
        # Se você quer que CADA nível seja 1500, simplifique a linha abaixo:
        xp_para_proximo_nivel += 1500 # Se cada nível aumenta 1500 XP
        
        # OU, se a progressão ORIGINAL (300 + 150*(n-1)) deve ser mantida APÓS o primeiro nível:
        # xp_para_proximo_nivel += 300 + (nivel - 1) * 150 
        
    xp_no_nivel_atual = xp - xp_base_nivel_atual
    xp_total_do_nivel = xp_para_proximo_nivel - xp_base_nivel_atual

    progresso_percentual = int((xp_no_nivel_atual / xp_total_do_nivel) * 100) if xp_total_do_nivel > 0 else 0
    return {
        "nivel": nivel,
        "progresso_xp_texto": f"{xp_no_nivel_atual} / {xp_total_do_nivel}",
        "progresso_percentual": progresso_percentual
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