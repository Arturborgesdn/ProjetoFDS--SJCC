// src/scripts/missoes.js

/**
 * Função principal para carregar os dados das missões diárias.
 */
async function carregarDadosDeMissoes() {
    console.log("Módulo Missões: Carregando dados...");

    const usuarioId = getUsuarioId(); // Função de utils.js
    if (!usuarioId) {
        limparSessao(); // Se não está logado, redireciona para login
        return;
    }

    // Seletores da interface
    const listaMissoesElement = document.querySelector('.daily-goals-list');
    const cardRealizadas = document.querySelector('.card-top.blue h2');
    const cardXp = document.querySelector('.card-top.green h2');
    const cardProgressoFill = document.querySelector('.card-top.blue .progress-fill');

    if (!listaMissoesElement || !cardRealizadas || !cardXp || !cardProgressoFill) {
        console.error("Erro: Elementos da UI de missões não encontrados.");
        return;
    }

    listaMissoesElement.innerHTML = '<p>Carregando missões...</p>';

    try {
        // Chama API das missões
        const response = await fetch(`${API_USUARIO}/${usuarioId}/missoes`);
        const result = await response.json();

        if (result.sucesso && result.missoes) {
            
            // Atualiza cards de resumo
            cardRealizadas.textContent = result.resumo.realizadas_texto;
            cardXp.textContent = result.resumo.xp_conquistado_texto;
            cardProgressoFill.style.width = result.resumo.progresso_percentual + '%';
            
            // Monta lista de missões
            let htmlMissoes = '';
            
            result.missoes.forEach(missao => {
                const classeStatus = missao.is_complete ? 'concluida' : 'pendente';
                const classeRaridade = missao.raridade; // comum, rara, epica
                
                htmlMissoes += `
                    <div class="goal-item ${classeStatus}" data-nome="${missao.nome}">
                        <div class="goal-icon-circle ${classeRaridade}">
                            <i class="fas ${missao.icone}"></i>
                        </div>
                        
                        <div class="goal-details">
                            <p class="goal-title">${missao.nome}</p>
                            <p class="goal-description">${missao.descricao}</p>
                            <div class="progress-bar-container">
                                <div class="progress-fill-mission" style="width: ${missao.progresso_percentual}%;"></div>
                            </div>
                            <p class="progress-text">${missao.progresso_atual} / ${missao.requisito}</p>
                        </div>
                        
                        <div style="display: flex; flex-direction: column; gap: 10px;"> 
                            <div style="color: #00b783;" class="goal-xp">+${missao.xp}XP</div>
                            <div class="goal-xp">+${missao.jc_points}JC</div>
                        </div>
                    </div>
                `;
            });

            listaMissoesElement.innerHTML = htmlMissoes;
            console.log("Módulo Missões: Dados carregados e renderizados.");

        } else {
            throw new Error(result.mensagem || "Resposta da API inválida.");
        }

    } catch (error) {
        console.error("Erro ao carregar dados das missões:", error);
        listaMissoesElement.innerHTML = '<p style="color: red;">Erro ao carregar missões.</p>';
    }
}

/**
 * Função para carregar e exibir a ofensiva (sequência de dias com missão concluída)
 */
// Versão NOVA e CORRETA (para missoes.js)
async function carregarOfensiva() {
    const usuarioId = getUsuarioId();
    if (!usuarioId) return;

    // 1. Ela procura o NOVO elemento (o <h2>)
    const streakElement = document.getElementById('streak-numero-dias');

    if (!streakElement) {
        // 2. O aviso (warning) aqui é diferente e correto
        console.warn("Elemento da ofensiva (streak-numero-dias) não encontrado.");
        return;
    }

    try {
        // 3. Ela busca o endpoint /ofensiva e preenche o número
        const response = await fetch(`${API_USUARIO}/${usuarioId}/ofensiva`); 
        const result = await response.json();

        if (result.sucesso) {
            const dias_completos = result.dias_consecutivos || 0;
            streakElement.textContent = dias_completos;
        } else {
            streakElement.textContent = '0';
        }
    } catch (error) {
        console.error("Erro ao carregar ofensiva:", error);
        streakElement.textContent = '0';
    }
}

