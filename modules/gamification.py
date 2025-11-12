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
    insert_daily_mission_in_db,
    get_leaderboard_from_db,
    get_user_rank_from_db,
)

# DEFINIÇÕES E REGRAS (LÓGICA PURA)
# --- Medalhas Definidas ---
# --- Medalhas Definidas (COM DESCRIÇÃO, ÍCONE E RARIDADE) ---
MEDALHAS = {
    "Novinho em folha": {
        "jc_points": 10, 
        "check": lambda u: u.get('noticias_completas_total', 0) >= 1,
        "descricao": "Leia sua primeira notícia completa",
        "raridade": "comum",
        "icone": "fa-book" # Ícone do Font Awesome
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
        "check": lambda u: u.get('missoes_completas_hoje_count', 0) >= len(MISSOES_DIARIAS), # Assumindo que MISSOES_DIARIAS existe
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
        "raridade": "comum", # Verde
        "icone": "fa-book-open"
    },
    "Fica de olho, visse?": {
        "descricao": "Passar 10 minutos no site",
        "xp": 100,
        "jc_points": 20,
        "metrica": "tempo_online_hoje_minutos", 
        "requisito": 10,
        "check": lambda u: u.get('tempo_online_hoje_minutos', 0) >= 10,
        "raridade": "comum", # Verde
        "icone": "fa-fire"
    },
    "Noticia Bunitinha": {
        "descricao": "Ler uma matéria publicada hoje", 
        "xp": 50,
        "jc_points": 10,
        "metrica": "noticias_lidas_hoje", 
        "requisito": 1,
        "check": lambda u: u.get('noticias_lidas_hoje', 0) >= 1, 
        "raridade": "comum", # Verde
        "icone": "fa-calendar"
    },
    "Compartilha ai, na moral": {
        "descricao": "Compartilhe uma notícia",
        "xp": 75,
        "jc_points": 75, 
        "metrica": "compartilhamentos_hoje",
        "requisito": 1,
        "check": lambda u: u.get('compartilhamentos_hoje', 0) >= 1,
        "raridade": "comum", # Verde
        "icone": "fa-share-alt"
    },
    "Destaque massa": {
        "descricao": "Leia uma matéria em destaque",
        "xp": 100,
        "jc_points": 20,
        "metrica": "noticias_destaque_lidas_hoje", # (Métrica futura)
        "requisito": 1,
        "check": lambda u: u.get('noticias_destaque_lidas_hoje', 0) >= 1, # (Lógica pendente)
        "raridade": "comum", # Verde
        "icone": "fa-star"
    },
    "Leitura Arretada": {
        "descricao": "Leia 5 matérias completas", 
        "xp": 150,      
        "jc_points": 30,
        "metrica": "noticias_lidas_hoje",
        "requisito": 5,
        "check": lambda u: u.get('noticias_lidas_hoje', 0) >= 5,
        "raridade": "rara", # Laranja
        "icone": "fa-book-open"
    },
    "Compartilhamento arretado": {
        "descricao": "Compartilhar 2 notícias",
        "xp": 250, 
        "jc_points": 60, 
        "metrica": "compartilhamentos_hoje",
        "requisito": 2,
        "check": lambda u: u.get('compartilhamentos_hoje', 0) >= 2,
        "raridade": "rara", # Laranja
        "icone": "fa-share-alt"
    },
    "Na resenha": { 
        "descricao": "Compartilhar 5 notícias",
        "xp": 400,
        "jc_points": 80,
        "metrica": "compartilhamentos_hoje",
        "requisito": 5,
        "check": lambda u: u.get('compartilhamentos_hoje', 0) >= 5,
        "raridade": "epica", # Vermelho
        "icone": "fa-crosshairs"
    }
}

# --- Funções de Cálculo (Lógica Pura) ---

def calcular_categoria_e_medalha(xp: int):
    """Calcula Categoria e Medalha com base no XP, usando Níveis Cíclicos."""
    
    # 1. Encontrar o Nível (baseado em ciclos de 1500 XP)
    if xp == 0:
        nivel = 1
    elif xp % 1500 == 0:
        # Se XP = 3000, Nível é 2 (3000/1500), está no *fim* do Nível 2
        nivel = (xp // 1500)
    else:
        nivel = (xp // 1500) + 1
    
    # 2. Mapear Nível para Categoria
    if nivel == 1: categoria = "Leitor Leigo"
    elif nivel == 2: categoria = "Leitor Massa"
    elif nivel == 3: categoria = "Leitor Engajado"
    elif nivel == 4: categoria = "Leitor Arretado"
    elif nivel == 5: categoria = "Leitor Desenrolado"
    else: categoria = "Leitor Topado" # Nível 6+
        
    # 3. Calcular a Medalha (Bronze, Prata, Ouro)
    # (0-500 = Bronze, 501-1000 = Prata, 1001-1500 = Ouro)
    
    if xp == 0:
        xp_no_ciclo = 0
    elif xp % 1500 == 0:
        xp_no_ciclo = 1500 # Se for 1500, 3000, etc. (é o Ouro)
    else:
        xp_no_ciclo = xp % 1500
    
    if xp_no_ciclo <= 500: medalha = "Bronze"
    elif xp_no_ciclo <= 1000: medalha = "Prata"
    else: medalha = "Ouro" # 1001-1500
        
    return categoria, medalha


def calcular_nivel(xp: int):
    """Calcula o Nível e o Progresso da Barra de XP (XP Total / Limite Categoria)."""
    
    if xp == 0:
        nivel = 1
        xp_base_nivel_atual = 0
        xp_limite_categoria = 1500 # Limite do Nv 1
    else:
        # Calcula o nível atual
        if xp % 1500 == 0:
            nivel = (xp // 1500)
        else:
            nivel = (xp // 1500) + 1
        
        # Calcula os limites do nível
        xp_base_nivel_atual = (nivel - 1) * 1500
        xp_limite_categoria = nivel * 1500
    
    # XP atual dentro do ciclo de 1500
    xp_no_ciclo_atual = xp - xp_base_nivel_atual
    xp_total_do_ciclo = xp_limite_categoria - xp_base_nivel_atual # (Sempre 1500)
    
    # Se o usuário estiver exatamente no limite (ex: 3000 XP)
    if xp == xp_limite_categoria:
        xp_no_ciclo_atual = xp_total_do_ciclo
    
    progresso_percentual = int((xp_no_ciclo_atual / xp_total_do_ciclo) * 100) if xp_total_do_ciclo > 0 else 0
    
    return {
        "nivel": nivel,
        # Texto para a barra (ex: "1130 / 1500")
        "progresso_xp_texto": f"{xp_no_ciclo_atual} / {xp_total_do_ciclo}", 
        # Texto total (ex: "11630 / 12000")
        "progresso_xp_total_texto": f"{xp} / {xp_limite_categoria}", 
        "progresso_percentual": progresso_percentual,
        "xp_proximo_limite": xp_limite_categoria # (Ex: 12000)
    }

# ===============================================
# FUNÇÕES DE SERVIÇO (Orquestração da Lógica)
# ===============================================



def get_user_data(user_id):
    """Busca dados do utilizador e suas medalhas."""
    return get_user_data_from_db(user_id)

def adicionar_xp_jc(user_id, xp_ganho=0, jc_ganho=0):
    """Adiciona XP e/ou JC Points a um utilizador."""
    return update_xp_jc_in_db(user_id, xp_ganho, jc_ganho)

# --- FUNÇÃO ANTIGA REMOVIDA ---
# A função 'award_medal' foi removida
# pois a nova 'check_and_award_medals' é mais completa
# e lida com a lógica de adicionar pontos.

# --- NOVA FUNÇÃO (DO SEU AMIGO) ADICIONADA ---
def check_and_award_medals(user_id, user_data): # <--- MUDANÇA AQUI (recebe user_data)
    """
    Verifica todas as medalhas possíveis e marca no banco as que forem completadas.
    Retorna lista das medalhas recém-conquistadas.
    (Código da T1UH13 - Refatorado para desacoplamento)
    """
    # 1. (REMOVIDO) Não busca mais user_data, usa o que foi passado.
    if not user_data:
        print(f"Erro: check_and_award_medals recebeu user_data vazio para {user_id}.")
        return []

    medalhas_ja_conquistadas = set(user_data.get('medalhas_conquistadas', []))
    medalhas_novas = [] 

    # 2. Verifica cada medalha definida no dicionário MEDALHAS
    for nome_medalha, regra in MEDALHAS.items():

        if nome_medalha in medalhas_ja_conquistadas:
            continue
        
        # 3. VERIFICAÇÃO (AGORA CORRETA)
        # Esta verificação agora usa o user_data que veio da API,
        # que CONTERÁ a chave 'acessou_madrugada' se ela existir.
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
                        "jc_points": dados_missao['jc_points'],
                        "raridade": dados_missao.get('raridade', 'comum')
                    })
                    completed_today.add(nome_missao)
                else:
                    print(f"⚠️ Alerta: Falha ao conceder recompensa para missão '{nome_missao}' (já marcada como completa) para {user_id}.")
            else:
                 print(f"⚠️ Alerta: Falha ao MARCAR missão '{nome_missao}' como completa para {user_id}.")
    user_data['missoes_completas_hoje_count'] = len(completed_today)
    return newly_completed_missions

def get_leaderboard(limit=10, order_by="xps"):
    """
    Retorna o ranking dos leitores, ordenado por XP (padrão) ou JC Points.
    """
    ranking = get_leaderboard_from_db(limit=limit, order_by=order_by)
    if not ranking:
        print("⚠️ Nenhum dado de ranking encontrado.")
        return []
    
    # Adiciona categoria e medalha a cada jogador (usando sua função existente)
    for r in ranking:
        categoria, medalha = calcular_categoria_e_medalha(r["xps"])
        r["categoria"] = categoria
        r["medalha"] = medalha

    return ranking


def get_user_rank(user_id, order_by="xps"):
    """
    Retorna a posição e dados do usuário no ranking geral.
    """
    dados = get_user_rank_from_db(user_id, order_by=order_by)
    if not dados:
        print(f"⚠️ Usuário {user_id} não encontrado no ranking.")
        return None
    
    categoria, medalha = calcular_categoria_e_medalha(dados["xps"])
    dados["categoria"] = categoria
    dados["medalha"] = medalha

    return dados