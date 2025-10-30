# modules/gamification.py

# Camada de Lógica de Negócios (Business Logic Layer)
# Responsável PELAS REGRAS, cálculos e orquestração da gamificação.
# NÃO executa SQL, chama o db_services.py para isso.

from datetime import date
# Importa as funções de banco de dados do novo arquivo
from modules.db_services import (
    get_db_connection,
    get_user_data_from_db, 
    update_xp_jc_in_db, 
    insert_medal_in_db, 
    get_completed_missions_from_db, 
    insert_daily_mission_in_db
)

# ===============================================
# DEFINIÇÕES E REGRAS (LÓGICA PURA)
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

# --- Missões Diárias Definidas ---
MISSOES_DIARIAS = {
    "Fica de olho, visse?": {
        "descricao": "Passar 10 minutos no site",
        "xp": 100,
        "jc_points": 20,
        "metrica": "tempo_online_hoje_minutos", 
        "requisito": 10,
        "check": lambda u: u.get('tempo_online_hoje_minutos', 0) >= 10
    },
    # (Adicione outras missões aqui)
    # --- NOVAS MISSÕES DE COMPARTILHAMENTO ---
    "Compartilha aí, na moral": {
        "descricao": "Compartilhar 1 matéria",
        "xp": 75,
        "jc_points": 15, # (Nota: PDF diz 15, imagem diz 75JC. Ajuste se necessário)
        "metrica": "compartilhamentos_hoje",
        "requisito": 1,
        "check": lambda u: u.get('compartilhamentos_hoje', 0) >= 1
    },
    "Compartilhamento arretado": {
        "descricao": "Compartilhar 2 matérias",
        "xp": 200, # (Nota: PDF diz 200, imagem diz 250XP. Ajuste se necessário)
        "jc_points": 40, # (Nota: PDF diz 40, imagem diz 50JC. Ajuste se necessário)
        "metrica": "compartilhamentos_hoje",
        "requisito": 2,
        "check": lambda u: u.get('compartilhamentos_hoje', 0) >= 2
    },
    "Na resenha": { 
        "descricao": "Compartilhar 5 notícias",
        "xp": 400,
        "jc_points": 80,
        "metrica": "compartilhamentos_hoje",
        "requisito": 5,
        "check": lambda u: u.get('compartilhamentos_hoje', 0) >= 5
    }
    # (Adicione as outras missões aqui depois, como "Leitura massa", etc.)

}

# --- Funções de Cálculo (Lógica Pura) ---

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
        if xp <= 8500: medalha = "Bronze"       # 7501 - 8500
        elif xp <= 9500: medalha = "Prata"      # 8501 - 9500
        else: medalha = "Ouro"                  # 9501+

    return categoria, medalha


def calcular_nivel(xp: int):
    """Calcula o Nível e o Progresso da Barra de XP (XP Total / Limite Categoria)."""
    
    nivel, xp_limite_categoria, xp_base_nivel_atual = 1, 1500, 0
    
    while xp >= xp_limite_categoria:
        nivel += 1
        xp_base_nivel_atual = xp_limite_categoria
        xp_limite_categoria += 1500 
        
    xp_no_ciclo_atual = xp - xp_base_nivel_atual
    xp_total_do_ciclo = xp_limite_categoria - xp_base_nivel_atual

    progresso_percentual = int((xp_no_ciclo_atual / xp_total_do_ciclo) * 100) if xp_total_do_ciclo > 0 else 0
    
    return {
        "nivel": nivel,
        "progresso_xp_texto": f"{xp} / {xp_limite_categoria}",
        "progresso_percentual": progresso_percentual
    }


# ===============================================
# FUNÇÕES DE SERVIÇO (Orquestração da Lógica)
# ===============================================

def get_user_data(user_id):
    """Busca dados do utilizador e suas medalhas."""
    # Chama a função de serviço de banco de dados
    return get_user_data_from_db(user_id)

def adicionar_xp_jc(user_id, xp_ganho=0, jc_ganho=0):
    """Adiciona XP e/ou JC Points a um utilizador."""
    # Chama a função de serviço de banco de dados
    return update_xp_jc_in_db(user_id, xp_ganho, jc_ganho)

def award_medal(user_id, medalha_nome, jc_points_ganhos):
    """Lógica de negócio para conceder uma medalha."""
    try:
        # 1. Tenta inserir a medalha no DB
        if insert_medal_in_db(user_id, medalha_nome):
            # 2. Se foi inserida com sucesso (não a possuía), adiciona os pontos
            print(f"🏅 Medalha '{medalha_nome}' concedida! +{jc_points_ganhos} JC Points.")
            if jc_points_ganhos > 0:
                adicionar_xp_jc(user_id, jc_ganho=jc_points_ganhos)
            return True
        else:
            # Se já possuía a medalha
            return False
    except Exception as e:
        print(f"Erro na lógica de award_medal para {user_id}: {e}")
        return False

def get_completed_daily_missions(user_id, conn):
    """Busca as missões diárias já completadas pelo usuário HOJE."""
    # Chama a função de serviço de banco de dados
    return get_completed_missions_from_db(user_id, conn)

def mark_daily_mission_complete(user_id, missao_nome, conn):
    """Marca uma missão diária como completa para o usuário HOJE."""
    # Chama a função de serviço de banco de dados
    return insert_daily_mission_in_db(user_id, missao_nome, conn)

def check_and_award_daily_missions(user_id, user_data, conn):
    """
    Verifica TODAS as missões diárias e concede recompensas (Lógica de Negócio).
    """
    if not conn:
        print("Erro Crítico: Conexão com DB é necessária para check_and_award_daily_missions")
        return [] 

    completed_today = get_completed_daily_missions(user_id, conn)
    newly_completed_missions = [] 

    for nome_missao, dados_missao in MISSOES_DIARIAS.items():
        
        # REGRA DE NEGÓCIO: A missão foi cumprida E ainda não foi completada hoje?
        if nome_missao not in completed_today and dados_missao['check'](user_data):
            
            print(f"Tentando completar missão '{nome_missao}' para {user_id}...")
            
            # Tenta marcar no DB
            if mark_daily_mission_complete(user_id, nome_missao, conn):
                
                # Tenta adicionar recompensas
                if adicionar_xp_jc(user_id, xp_ganho=dados_missao['xp'], jc_ganho=dados_missao['jc_points']):
                    print(f"✅ Missão Diária '{nome_missao}' completada E recompensada para {user_id}!")
                    newly_completed_missions.append({
                        "nome": nome_missao,
                        "xp": dados_missao['xp'],
                        "jc_points": dados_missao['jc_points']
                    })
                else:
                    print(f"⚠️ Alerta: Falha ao conceder recompensa para missão '{nome_missao}' (já marcada como completa) para {user_id}.")
            else:
                 print(f"⚠️ Alerta: Falha ao MARCAR missão '{nome_missao}' como completa para {user_id}.")

    return newly_completed_missions