# modules/gamification.py

# Camada de Lógica de Negócios (Business Logic Layer)
# Responsável PELAS REGRAS, cálculos e orquestração da gamificação.
# NÃO executa SQL diretamente, chama o db_services.py para isso.

from datetime import date
from modules.db_services import (
    get_db_connection,
    get_user_data_from_db, 
    update_xp_jc_in_db, 
    insert_medal_in_db, 
    get_completed_missions_from_db, 
    insert_daily_mission_in_db,
    get_leaderboard_from_db,
    get_user_rank_from_db,
    get_user_streak_from_db
)

# ===============================================
# DEFINIÇÕES E REGRAS GLOBAIS
# ===============================================

MEDALHAS = {
    "Novinho em folha": {
        "jc_points": 10, 
        "check": lambda u: u.get('noticias_completas_total', 0) >= 1,
        "descricao": "Leia sua primeira notícia completa",
        "raridade": "comum",
        "icone": "fa-book"
    },
    "Pegou ar": {
        "jc_points": 50, 
        "check": lambda u: u.get('dias_consecutivos_acesso', 0) >= 7,
        "descricao": "Acesse o site por 7 dias consecutivos",
        "raridade": "rara",
        "icone": "fa-fire"
    },
    "Sem Leseira": {
        "jc_points": 100, 
        "check": lambda u: u.get('noticias_completas_total', 0) >= 50,
        "descricao": "Leia 50 notícias completas",
        "raridade": "epica",
        "icone": "fa-star"
    },
    "Mil conto": {
        "jc_points": 80, 
        "check": lambda u: u.get('jc_points', 0) >= 1000,
        "descricao": "Acumule 1000 JC Points",
        "raridade": "epica",
        "icone": "fa-coins"
    },
    "Inimigo do sono": {
        "jc_points": 100, 
        "check": lambda u: u.get('acessou_madrugada', False),
        "descricao": "Leia uma noticia antes das 6h da manhã",
        "raridade": "rara",
        "icone": "fa-clock"
    },
    "Êta bicho insistente": {
        "jc_points": 100, 
        "check": lambda u: u.get('dias_consecutivos_acesso', 0) >= 30,
        "descricao": "Acesse o app por 30 dias consecutivos",
        "raridade": "epica",
        "icone": "fa-fire"
    },
    "Bicho ta virado": {
        "jc_points": 100,
        "check": lambda u: u.get('missoes_completas_hoje_count', 0) >= len(MISSOES_DIARIAS), 
        "descricao": "Conclua todas as missões diárias em um único dia",
        "raridade": "epica",
        "icone": "fa-trophy"
    }
}

MISSOES_DIARIAS = {
    "Leitura Massa": {
        "descricao": "Leia 2 matérias completas",
        "xp": 50,      
        "jc_points": 10,
        "metrica": "noticias_lidas_hoje",
        "requisito": 2,
        "check": lambda u: u.get('noticias_lidas_hoje', 0) >= 2,
        "raridade": "comum", 
        "icone": "fa-book-open"
    },
    "Fica de olho, visse?": {
        "descricao": "Passar 10 minutos no site",
        "xp": 100,
        "jc_points": 20,
        "metrica": "tempo_online_hoje_minutos", 
        "requisito": 10,
        "check": lambda u: u.get('tempo_online_hoje_minutos', 0) >= 10,
        "raridade": "comum",
        "icone": "fa-fire"
    },
    "Noticia Bunitinha": {
        "descricao": "Ler uma matéria publicada hoje", 
        "xp": 50,
        "jc_points": 10,
        "metrica": "noticias_lidas_hoje", 
        "requisito": 1,
        "check": lambda u: u.get('noticias_lidas_hoje', 0) >= 1, 
        "raridade": "comum",
        "icone": "fa-calendar"
    },
    "Compartilha ai, na moral": {
        "descricao": "Compartilhe uma notícia",
        "xp": 75,
        "jc_points": 75, 
        "metrica": "compartilhamentos_hoje",
        "requisito": 1,
        "check": lambda u: u.get('compartilhamentos_hoje', 0) >= 1,
        "raridade": "comum",
        "icone": "fa-share-alt"
    },
    "Destaque massa": {
        "descricao": "Leia uma matéria em destaque",
        "xp": 100,
        "jc_points": 20,
        "metrica": "noticias_destaque_lidas_hoje",
        "requisito": 1,
        "check": lambda u: u.get('noticias_destaque_lidas_hoje', 0) >= 1,
        "raridade": "comum",
        "icone": "fa-star"
    },
    "Leitura Arretada": {
        "descricao": "Leia 5 matérias completas", 
        "xp": 150,      
        "jc_points": 30,
        "metrica": "noticias_lidas_hoje",
        "requisito": 5,
        "check": lambda u: u.get('noticias_lidas_hoje', 0) >= 5,
        "raridade": "rara",
        "icone": "fa-book-open"
    },
    "Compartilhamento arretado": {
        "descricao": "Compartilhar 2 notícias",
        "xp": 250, 
        "jc_points": 60, 
        "metrica": "compartilhamentos_hoje",
        "requisito": 2,
        "check": lambda u: u.get('compartilhamentos_hoje', 0) >= 2,
        "raridade": "rara",
        "icone": "fa-share-alt"
    },
    "Na resenha": { 
        "descricao": "Compartilhar 5 notícias",
        "xp": 400,
        "jc_points": 80,
        "metrica": "compartilhamentos_hoje",
        "requisito": 5,
        "check": lambda u: u.get('compartilhamentos_hoje', 0) >= 5,
        "raridade": "epica",
        "icone": "fa-crosshairs"
    }
}

# 🚀 MOVIDO PARA O ESCOPO GLOBAL (Para correção do bug)
CATEGORIAS_RANKING = [
    {
        "nome": "Leitor Leigo",
        "inicio": 0,
        "fim": 1500,
        "bronze": (0, 500),
        "prata": (501, 1000),
        "ouro": (1001, 1500),
    },
    {
        "nome": "Leitor Massa",
        "inicio": 1501,
        "fim": 3000,
        "bronze": (1501, 2000),
        "prata": (2001, 2500),
        "ouro": (2501, 3000),
    },
    {
        "nome": "Leitor Engajado",
        "inicio": 3001,
        "fim": 4500,
        "bronze": (3001, 3500),
        "prata": (3501, 4000),
        "ouro": (4001, 4500),
    },
    {
        "nome": "Leitor Arretado",
        "inicio": 4501,
        "fim": 6000,
        "bronze": (4501, 5000),
        "prata": (5001, 5500),
        "ouro": (5501, 6000),
    },
    {
        "nome": "Leitor Desenrolado",
        "inicio": 6001,
        "fim": 7500,
        "bronze": (6001, 6500),
        "prata": (6501, 7000),
        "ouro": (7001, 7500),
    },
    {
        "nome": "Leitor Topado",
        "inicio": 7501,
        "fim": 999999999,
        "bronze": (7501, 8500),
        "prata": (8501, 9500),
        "ouro": (9501, 999999999),
    },
]

# ===============================================
# FUNÇÕES DE CÁLCULO (LÓGICA PURA)
# ===============================================

def calcular_categoria_e_medalha(score_total):
    """
    Calcula categoria e medalha com base em faixas fixas de XP (CATEGORIAS_RANKING global).
    """
    categoria_atual = None
    medalha = None

    # Descobrir categoria baseada no XP total
    for c in CATEGORIAS_RANKING:
        if c["inicio"] <= score_total <= c["fim"]:
            categoria_atual = c["nome"]

            if c["bronze"][0] <= score_total <= c["bronze"][1]:
                medalha = "Bronze"
            elif c["prata"][0] <= score_total <= c["prata"][1]:
                medalha = "Prata"
            elif c["ouro"][0] <= score_total <= c["ouro"][1]:
                medalha = "Ouro"
            else:
                medalha = "Bronze"  # fallback de segurança
            break
            
    # Caso de borda: Se não encontrou (ex: XP negativo ou erro), retorna padrão
    if not categoria_atual:
         categoria_atual = "Leitor Leigo"
         medalha = "Bronze"

    return categoria_atual, medalha


def calcular_nivel(xp: int):
    if xp == 0:
        nivel = 1
        xp_base_nivel_atual = 0
        xp_limite_categoria = 1500
    else:
        if xp % 1500 == 0:
            nivel = (xp // 1500)
        else:
            nivel = (xp // 1500) + 1
        
        xp_base_nivel_atual = (nivel - 1) * 1500
        xp_limite_categoria = nivel * 1500
    
    xp_no_ciclo_atual = xp - xp_base_nivel_atual
    xp_total_do_ciclo = xp_limite_categoria - xp_base_nivel_atual
    
    if xp == xp_limite_categoria:
        xp_no_ciclo_atual = xp_total_do_ciclo
    
    progresso_percentual = int((xp_no_ciclo_atual / xp_total_do_ciclo) * 100) if xp_total_do_ciclo > 0 else 0
    
    return {
        "nivel": nivel,
        "progresso_xp_texto": f"{xp_no_ciclo_atual} / {xp_total_do_ciclo}", 
        "progresso_xp_total_texto": f"{xp} / {xp_limite_categoria}", 
        "progresso_percentual": progresso_percentual,
        "xp_proximo_limite": xp_limite_categoria
    }

# ===============================================
# FUNÇÕES DE SERVIÇO (ORQUESTRAÇÃO DA LÓGICA)
# ===============================================

def get_user_data(user_id):
    """Busca dados do utilizador e suas medalhas."""
    return get_user_data_from_db(user_id)

def adicionar_xp_jc(user_id, xp_ganho=0, jc_ganho=0):
    """Adiciona XP e/ou JC Points a um utilizador."""
    return update_xp_jc_in_db(user_id, xp_ganho, jc_ganho)


def check_and_award_medals(user_id, user_data): 
    if not user_data:
        print(f"Erro: check_and_award_medals recebeu user_data vazio para {user_id}.")
        return []

    medalhas_ja_conquistadas = set(user_data.get('medalhas_conquistadas', []))
    medalhas_novas = [] 

    for nome_medalha, regra in MEDALHAS.items():
        if nome_medalha in medalhas_ja_conquistadas:
            continue
        
        try:
            if regra["check"](user_data):
                print(f"✅ Medalha '{nome_medalha}' atingida pelo usuário {user_id} — registrando no DB...")
                ganhou = insert_medal_in_db(user_id, nome_medalha)
                if ganhou:
                    if regra["jc_points"] > 0:
                        update_xp_jc_in_db(user_id, jc_ganho=regra["jc_points"])
                    medalhas_novas.append({
                        "medalha": nome_medalha,
                        "jc_points": regra["jc_points"]
                    })
        except Exception as e:
            print(f"❌ Erro ao checar medalha '{nome_medalha}' para user {user_id}: {e}")

    return medalhas_novas

def get_completed_daily_missions(user_id, conn):
    """Busca as missões diárias já completadas pelo usuário HOJE."""
    return get_completed_missions_from_db(user_id, conn)

def mark_daily_mission_complete(user_id, missao_nome, conn):
    """Marca uma missão diária como completa para o usuário HOJE."""
    return insert_daily_mission_in_db(user_id, missao_nome, conn)

def check_and_award_daily_missions(user_id, user_data, conn):
    """
    Verifica TODAS as missões diárias e concede recompensas (Lógica de Negócio).
    Inclui registro de OFENSIVA (streak) na primeira missão do dia.
    """
    if not conn:
        print("Erro Crítico: Conexão com DB é necessária para check_and_award_daily_missions")
        return [] 

    completed_today = get_completed_daily_missions(user_id, conn)
    newly_completed_missions = [] 
    
    # Flag para registrar a ofensiva
    missoes_concluidas_agora = False 

    try:
        for nome_missao, dados_missao in MISSOES_DIARIAS.items():
            
            if nome_missao not in completed_today and dados_missao['check'](user_data):
                
                print(f"Tentando completar missão '{nome_missao}' para {user_id}...")
                
                # Tenta marcar no DB (SEM COMMIT)
                if mark_daily_mission_complete(user_id, nome_missao, conn):
                    
                    missoes_concluidas_agora = True 
                    
                    # Adiciona recompensas (função interna abre/fecha própria conexão, seguro aqui)
                    adicionar_xp_jc(user_id, xp_ganho=dados_missao['xp'], jc_ganho=dados_missao['jc_points'])
                    
                    print(f"✅ Missão Diária '{nome_missao}' completada E recompensada para {user_id}!")
                    newly_completed_missions.append({
                        "nome": nome_missao,
                        "xp": dados_missao['xp'],
                        "jc_points": dados_missao['jc_points'],
                        "raridade": dados_missao.get('raridade', 'comum')
                    })
                    completed_today.add(nome_missao)
                
                else:
                    print(f"⚠️ Alerta: Falha ao MARCAR missão '{nome_missao}' (provavelmente já existia) para {user_id}.")

        # --- LÓGICA DA OFENSIVA ---
        if missoes_concluidas_agora:
            print(f"🔥 Registrando dia de ofensiva para o usuário {user_id}...")
            registrar_dia_com_missao(user_id, conn)
        
        # COMMIT CENTRALIZADO
        conn.commit()
        print("Transação de missões e ofensiva comitada com sucesso.")

    except Exception as e:
        print(f"❌ Erro Crítico na transação de missões: {e}. Fazendo rollback...")
        if conn:
            conn.rollback()
            
    user_data['missoes_completas_hoje_count'] = len(completed_today)
    return newly_completed_missions

def get_leaderboard(limit=10, order_by="xps"):
    ranking = get_leaderboard_from_db(limit=limit, order_by=order_by)
    if not ranking:
        print("⚠️ Nenhum dado de ranking encontrado.")
        return []
    
    for r in ranking:
        categoria, medalha = calcular_categoria_e_medalha(r["xps"])
        r["categoria"] = categoria
        r["medalha"] = medalha
    return ranking

# 🚀 ATUALIZADO: CORREÇÃO DE BUG (TARGET VISUAL)
def get_user_rank(user_id, order_by="xps"):
    dados = get_user_rank_from_db(user_id, order_by=order_by)
    if not dados:
        print(f"⚠️ Usuário {user_id} não encontrado no ranking.")
        return None
    
    xp_atual = dados["xps"]

    # 1. Calcula o Status Atual
    categoria, medalha = calcular_categoria_e_medalha(xp_atual)
    dados["categoria"] = categoria
    dados["medalha"] = medalha

    # 2. Lógica para descobrir a "Próxima Medalha" (Target Visual)
    limite_da_categoria_atual = 1500 # fallback padrão
    
    for c in CATEGORIAS_RANKING:
        if c["inicio"] <= xp_atual <= c["fim"]:
            limite_da_categoria_atual = c["fim"]
            break
    
    # Simula o usuário tendo 1 XP a mais que o limite atual
    # Isso força o cálculo a pegar a medalha "Bronze" da próxima categoria
    prox_cat, prox_med = calcular_categoria_e_medalha(limite_da_categoria_atual + 1)
    
    dados["proxima_categoria_nome"] = prox_cat
    dados["proxima_medalha_tipo"] = prox_med 

    return dados

def get_user_streak(user_id):
    """
    Busca o número de dias consecutivos de ofensiva (streak).
    """
    print(f"Buscando streak para usuário {user_id}...")
    try:
        dias = get_user_streak_from_db(user_id)
        print(f"Usuário {user_id} tem {dias} dias de ofensiva.")
        return {
            "sucesso": True,
            "dias_consecutivos": dias
        }
    except Exception as e:
        print(f"Erro ao buscar ofensiva (camada de lógica) para {user_id}: {e}")
        return {"sucesso": False, "dias_consecutivos": 0}

def registrar_dia_com_missao(usuario_id, conn):
    """
    Registra o dia atual na tabela 'ofensiva_usuario'.
    Usa 'INSERT IGNORE' para garantir que só há um registro por dia.
    (Esta função não faz commit, é parte da transação maior)
    """
    cursor = conn.cursor()
    hoje = date.today()
    try:
        cursor.execute("""
            INSERT IGNORE INTO ofensiva_usuario (usuario_id, data_registro)
            VALUES (%s, %s)
        """, (usuario_id, hoje))
        print(f"Registro de ofensiva para {usuario_id} em {hoje} preparado (pendente de commit).")
    except Exception as e:
        print(f"Erro ao registrar dia de missão (antes do commit): {e}")
    finally:
        cursor.close()