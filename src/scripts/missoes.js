// src/scripts/missoes.js

/**
 * Função principal para carregar os dados das missões diárias.
 */
async function carregarDadosDeMissoes() {
    console.log("Módulo Missões: Carregando dados...");
    
    const usuarioId = getUsuarioId(); // Pega ID de utils.js
    if (!usuarioId) {
        limparSessao(); // Se não está logado, volta para login
        return;
    }

    // Seletores dos elementos da página
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
        // 1. Chamar a nova API
        const response = await fetch(`${API_USUARIO}/${usuarioId}/missoes`);
        const result = await response.json();

        if (result.sucesso && result.missoes) {
            
            // 2. Atualizar os Cards de Resumo (Topo)
            cardRealizadas.textContent = result.resumo.realizadas_texto;
            cardXp.textContent = result.resumo.xp_conquistado_texto;
            cardProgressoFill.style.width = result.resumo.progresso_percentual + '%';
            
            // 3. Gerar o HTML da Lista (Já vem ordenada do backend)
            let htmlMissoes = '';
            
            result.missoes.forEach(missao => {
                const classeStatus = missao.is_complete ? 'concluida' : 'pendente';
                const classeRaridade = missao.raridade; // 'comum', 'rara', 'epica'
                
                // Gera o HTML para este <li>
                htmlMissoes += `
                    <div class="goal-item ${classeStatus}"data-nome="${missao.nome}">
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
                        
                        <div style="display: flex;flex-direction: column;gap: 10px;"> 
                            <div style="color: #00b783;" class="goal-xp">+${missao.xp}XP</div>
                            <div class="goal-xp">+${missao.jc_points}JC</div>
                        </div>
                        
                        <div class="check-box"></div> 
                    </div>
                `;
            });

            // 4. Inserir o HTML na página
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