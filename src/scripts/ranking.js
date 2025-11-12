// src/scripts/ranking.js

/**
 * Função principal para carregar os dados do ranking.
 */
async function carregarDadosDeRanking() {
    console.log("Módulo Ranking: Carregando dados...");
    
    const usuarioId = getUsuarioId();
    if (!usuarioId) {
        limparSessao();
        return;
    }

    // Seletores dos elementos da página
    const podiumContainer = document.querySelector('.podium-grid');
    const listContainer = document.querySelector('.full-ranking');
    const userHighlightContainer = document.querySelector('#user-rank-highlight');

    // Seletores para os totais de jogadores
    const totalPlayersElement = document.querySelector('.total-players .count');

    if (!podiumContainer || !listContainer || !userHighlightContainer || !totalPlayersElement) {
        console.error("Erro: Elementos da UI de ranking não encontrados.");
        return;
    }

    // Mensagem de carregamento no card do usuário
    const userRankName = userHighlightContainer.querySelector('.rank-name');
    if (userRankName) userRankName.textContent = "Carregando...";

    try {
        // 1. Chamar a nova API (com a URL CORRIGIDA)
        // A constante API_USUARIO foi removida daqui
        const response = await fetch(`/api/ranking/${usuarioId}`);
        const result = await response.json();

        if (result.sucesso) {
            const leaderboard = result.leaderboard;
            const userRank = result.user_rank;

            // 2. Atualizar total de jogadores
            if (totalPlayersElement) {
                totalPlayersElement.textContent = leaderboard.length > 0 ? leaderboard.length : '...';
            }

            // 3. Popular o Pódio (Top 3)
            popularPodium(leaderboard.slice(0, 3));

            // 4. Popular a Lista (Ranks 4-10)
            popularLista(leaderboard.slice(3), listContainer, usuarioId);
            
            // 5. Popular o card do usuário logado
            popularUsuarioAtual(userRank);

            console.log("Módulo Ranking: Dados carregados e renderizados.");
        } else {
            throw new Error(result.mensagem || "Resposta da API inválida.");
        }

    } catch (error) {
        console.error("Erro ao carregar dados do ranking:", error);
        if (userRankName) userRankName.textContent = "Erro ao carregar";
        listContainer.innerHTML += '<p style="color: red; text-align: center;">Erro ao carregar ranking.</p>';
    }
}

/**
 * Atualiza os 3 cards do pódio.
 * @param {Array} top3 - Array com os 3 primeiros usuários.
 */
function popularPodium(top3) {
    const podiumItems = {
        1: document.querySelector('.podium-item.first'),
        2: document.querySelector('.podium-item.second'),
        3: document.querySelector('.podium-item.third')
    };

    top3.forEach((user, index) => {
        const position = index + 1;
        const item = podiumItems[position];
        if (!item) return;

        const emblemaPath = getEmblemPath(user.categoria, user.medalha);

        // Atualiza os campos
        // (Usando fotos genéricas como fallback, mas o ideal seria ter 'foto_url' no DB)
        const userPhotos = ['assets/Ana_Perfil.png', 'assets/Carlos_Perfil.png', 'assets/Marina_Perfil.png'];
        item.querySelector('.podium-avatar').src = user.foto_url || userPhotos[index]; 
        item.querySelector('.name').textContent = user.nome.split(' ')[0]; // Só o primeiro nome
        item.querySelector('.rank-level').textContent = user.xps;
        item.querySelector('.emblema_top3').src = emblemaPath;
    });
}

/**
 * Gera e insere o HTML para os ranks 4-10.
 * @param {Array} rankingList - Usuários do rank 4 em diante.
 * @param {HTMLElement} listContainer - O elemento .full-ranking.
 * @param {string} usuarioId - O ID do usuário logado (para não se duplicar).
 */
function popularLista(rankingList, listContainer, usuarioId) {
    let htmlLista = '';
    
    // Fotos genéricas para a lista
    const genericPhotos = [
        'assets/Julia_Ribeiro_Perfil.png',
        'assets/Pedro_Lima_Perfil.png',
        'assets/Beatriz_Souza_Perfil.png',
        'assets/Felipe_Perfil.png',
        'assets/Camila_Perfil.png',
        'assets/Rafael_Perfil.png',
        'assets/unnamed.png' // Fallback
    ];

    rankingList.forEach((user, index) => {
        if (user.usuario_id === usuarioId) {
            return;
        }

        const position = index + 4; // Começa da posição 4
        const emblemaPath = getEmblemPath(user.categoria, user.medalha);
        const foto = user.foto_url || genericPhotos[index % genericPhotos.length];

        htmlLista += `
            <div class="ranking-item">
                <div class="position-circle">${position}</div>
                <img src="${foto}" alt="${user.nome}" class="rank-avatar">
                <div class="user-details">
                    <p class="rank-name">${user.nome}</p>
                    <div class="pontos_XP_user">
                        <p style="font-size: 20px; color: #333;" class="rank-level">${user.xps}</p> 
                        <img style="margin-right: 17px;" class="emblema-xp" src="assets/XP_JC.png" alt="XP">
                    </div>
                </div>
                <div class="rank-score">
                    <img style="margin-right: 10px; width: 50px;" class="emblema" src="${emblemaPath}" alt="${user.categoria}">
                </div>
            </div>
        `;
    });

    // Insere a lista gerada (esta linha estava errada antes, agora é '+=' no container)
    // Encontra o card do usuário e insere a lista DEPOIS dele
    const userCard = listContainer.querySelector('#user-rank-highlight');
    if (userCard) {
        userCard.insertAdjacentHTML('afterend', htmlLista);
    } else {
        listContainer.innerHTML += htmlLista; // Fallback
    }
}

/**
 * Atualiza o card destacado do usuário logado.
 * @param {object} userRank - Objeto com os dados do usuário logado.
 */
function popularUsuarioAtual(userRank) {
    const item = document.querySelector('#user-rank-highlight');
    if (!item) return;
    
    const emblemaPath = getEmblemPath(userRank.categoria, userRank.medalha);

    item.querySelector('.position-circle').textContent = userRank.posicao;
    item.querySelector('.rank-avatar').src = userRank.foto_url || `assets/unnamed.png`;
    item.querySelector('.rank-name').textContent = userRank.nome + " (Você)";
    item.querySelector('.rank-level').textContent = userRank.xps;
    item.querySelector('.emblema').src = emblemaPath;
}