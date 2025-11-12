from datetime import datetime, timedelta
from modules.db_services import get_db_connection  # já usado em seu projeto

# ======================================================
# 🎁 Definição dos Benefícios Fixos
# ======================================================

BENEFITS = {
    "Acesso antecipado a notícias": {"custo": 250, "duracao": "por matéria"},
    "Enviar perguntas a jornalistas": {"custo": 400, "duracao": "por envio aprovado"},
    "Resumo Inteligente": {"custo": 150, "duracao": "por notícia"},
    "Notas extras de colunistas": {"custo": 300, "duracao": "acesso individual"},
    "Citação na newsletter 'Leitores em Destaque'": {"custo": 800, "duracao": "mensal"},
    "Teste Beta de novos recursos": {"custo": 1000, "duracao": "por ciclo de teste"},
    "Avatar customizado": {"custo": 100, "duracao": "permanente"},
    "Moldura de perfil": {"custo": 150, "duracao": "permanente"},
    "Selo de reconhecimento (Check azul)": {"custo": 500, "duracao": "permanente"},
    "Moldura temática": {"custo": 200, "duracao": "por temporada"},
    "Descontos culturais": {"custo": 700, "duracao": "por cupom"},
    "Participação em eventos": {"custo": 1200, "duracao": "por evento"},
}

# ======================================================
# ⚡ Definição dos Multiplicadores
# ======================================================

XP_MULTIPLIERS = {
    "Pequeno": {"bonus": 1.25, "duracao_horas": 24, "custo": 300},
    "Médio": {"bonus": 1.50, "duracao_horas": 24, "custo": 500},
    "Grande": {"bonus": 2.00, "duracao_horas": 24, "custo": 800},
    "Épico": {"bonus": 2.50, "duracao_horas": 24, "custo": 1200},
}

JC_MULTIPLIERS = {
    "Pequeno": {"bonus": 1.10, "duracao_horas": 12, "custo": 250},
    "Médio": {"bonus": 1.20, "duracao_horas": 24, "custo": 400},
    "Grande": {"bonus": 1.50, "duracao_horas": 24, "custo": 700},
    "Épico": {"bonus": 2.00, "duracao_horas": 48, "custo": 1000},
}

# ======================================================
# 🧩 Funções Auxiliares de Banco
# ======================================================

def get_user_points(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT jc_points FROM gamificacao WHERE usuario_id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row["jc_points"] if row else 0


def update_user_points(user_id, new_points):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE gamificacao SET jc_points = %s WHERE usuario_id = %s", (new_points, user_id))
    conn.commit()
    cursor.close()
    conn.close()


def save_benefit_log(user_id, nome_beneficio, expiracao=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO beneficios_resgatados (usuario_id, nome_beneficio, data_resgate, data_expiracao)
        VALUES (%s, %s, %s, %s)
    """, (user_id, nome_beneficio, datetime.now(), expiracao))
    conn.commit()
    cursor.close()
    conn.close()


# ======================================================
# 🏆 Resgatar Benefício
# ======================================================

def redeem_benefit(user_id, nome_beneficio):
    """
    Verifica se o usuário tem JC Points suficientes e resgata o benefício.
    """
    if nome_beneficio not in BENEFITS:
        return {"erro": "Benefício não encontrado."}

    beneficio = BENEFITS[nome_beneficio]
    custo = beneficio["custo"]
    pontos_atuais = get_user_points(user_id)

    if pontos_atuais < custo:
        return {"erro": "Pontos insuficientes."}

    # Debita pontos
    novo_saldo = pontos_atuais - custo
    update_user_points(user_id, novo_saldo)

    # Define data de expiração
    expiracao = None
    dur = beneficio["duracao"]
    if dur == "mensal":
        expiracao = datetime.now() + timedelta(days=30)
    elif dur in ["por temporada", "por ciclo de teste"]:
        expiracao = datetime.now() + timedelta(days=15)
    elif dur in ["por evento", "por cupom", "por envio aprovado", "por notícia", "por matéria"]:
        expiracao = datetime.now() + timedelta(days=7)

    save_benefit_log(user_id, nome_beneficio, expiracao)

    return {
        "mensagem": f"🎁 Benefício '{nome_beneficio}' resgatado com sucesso!",
        "saldo_atual": novo_saldo,
        "expira_em": expiracao.strftime('%d/%m/%Y %H:%M') if expiracao else "permanente"
    }


# ======================================================
# ⚙ Ativar Multiplicador (XP ou JC)
# ======================================================

def activate_multiplier(user_id, tipo, nivel):
    tipo = tipo.lower()
    if tipo == "xp":
        tabela = XP_MULTIPLIERS
    elif tipo == "jc":
        tabela = JC_MULTIPLIERS
    else:
        return {"erro": "Tipo inválido. Use 'xp' ou 'jc'."}

    if nivel not in tabela:
        return {"erro": "Nível inválido."}

    mult = tabela[nivel]
    custo = mult["custo"]
    duracao = mult["duracao_horas"]
    bonus = mult["bonus"]

    pontos_atuais = get_user_points(user_id)
    if pontos_atuais < custo:
        return {"erro": "Pontos insuficientes."}

    novo_saldo = pontos_atuais - custo
    update_user_points(user_id, novo_saldo)

    expiracao = datetime.now() + timedelta(hours=duracao)
    save_benefit_log(user_id, f"Multiplicador {tipo.upper()} - {nivel}", expiracao)

    return {
        "mensagem": f"⚡ Multiplicador {tipo.upper()} ({nivel}) ativado! +{int((bonus-1)*100)}% por {duracao}h.",
        "expira_em": expiracao.strftime('%d/%m/%Y %H:%M'),
        "saldo_atual": novo_saldo
}