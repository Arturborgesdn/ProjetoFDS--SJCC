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
async function carregarOfensiva() {
    const usuarioId = getUsuarioId();
    if (!usuarioId) return;

    try {
        const response = await fetch(`${API_USUARIO}/${usuarioId}/ofensiva`);
        const result = await response.json();

        if (result.sucesso) {
            const dias = result.dias_com_missao || 0;
            const container = document.querySelector('.weekly-streak-container .day-list');
            
            if (container) {
                // Atualiza visualmente o "weekly streak"
                atualizarWeeklyStreak(container, dias);
            } else {
                console.warn("Container do Weekly Streak não encontrado na página.");
            }
        }
    } catch (error) {
        console.error("Erro ao carregar ofensiva:", error);
    }
}

/**
 * Atualiza o componente visual de sequência semanal (weekly streak)
 * @param {HTMLElement} container - Contêiner da lista de dias
 * @param {number} diasCompletos - Quantos dias o usuário completou
 */
function atualizarWeeklyStreak(container, diasCompletos) {
    const diasSemana = ['S', 'T', 'Q', 'Q', 'S', 'S', 'D'];
    container.innerHTML = '';

    diasSemana.forEach((letra, index) => {
        let classe = '';
        if (index < diasCompletos) {
            classe = 'completed';
        } else if (index === diasCompletos) {
            classe = 'current';
        }

        container.innerHTML += `
            <div class="day-item ${classe}">
                ${letra} ${classe === 'completed' ? '<i class="fas fa-check-circle"></i>' : ''}
            </div>
        `;
    });
}

document.addEventListener('DOMContentLoaded', () => {
    carregarDadosDeMissoes();
    carregarOfensiva(); // Conectado ao Weekly Streak
});
