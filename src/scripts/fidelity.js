// ============================================
// Módulo: Fidelidade (Lógica para programa_Fidelidade.html)
//
// Depende de: utils.js (para getEmblemPath, getUsuarioId, API_USUARIO, etc.)
// Nota: Este arquivo deve ser carregado DEPOIS de utils.js.
// ============================================

// --- FUNÇÃO PARA ANIMAÇÃO DA BARRA DE PROGRESSO (usando requestAnimationFrame) ---

/**
 * Anima a barra de XP de 0% até o progresso final.
 * @param {number} targetPercent - Porcentagem final de XP (ex: 80).
 * @param {string} targetText - Texto final de XP (ex: "4000 / 4500 JC").
 * @param {HTMLElement} xpBarFill - Elemento HTML da barra de preenchimento.
 * @param {HTMLElement} xpBarText - Elemento HTML do texto de XP.
 */
function animateProgress(targetPercent, targetText, xpBarFill, xpBarText) {
    const duration = 1500; // 1.5 segundos para a animação
    const startTime = performance.now();
    
    // Configura o texto final imediatamente (XP Total / Limite da Categoria)
    if (xpBarText) xpBarText.textContent = targetText; 

    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        let progress = Math.min(elapsed / duration, 1); // Progresso de 0 a 1

        // Easing: Desaceleração suave no final (visual mais agradável)
        const easeOut = 1 - Math.pow(1 - progress, 3);
        
        // Calcula a porcentagem atual da animação
        const currentPercent = targetPercent * easeOut;
        
        // Atualiza a largura no DOM
        if (xpBarFill) xpBarFill.style.width = `${currentPercent}%`;
        
        // Continua o loop de animação
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            // Garante o valor final exato
            if (xpBarFill) xpBarFill.style.width = `${targetPercent}%`;
        }
    }
    
    // Inicia o loop de animação
    requestAnimationFrame(animate);
}

// --- FUNÇÃO PARA CARREGAR E MOSTRAR DADOS NA PÁGINA DE FIDELIDADE ---
async function carregarDadosDeFidelidade() {
    // 1. Seleção de Elementos (Note a correção do seletor do header abaixo)
    const profileName = document.querySelector('.card.profile h2');
    const profileCategory = document.querySelector('.card.profile .titulo');
    const xpBarFill = document.querySelector('.card.profile .xp-bar .fill');
    const xpBarText = document.querySelector('.card.profile .container-xp-logo p');
    const jcPointsValue = document.querySelector('.cardjc .container-jc h2');
    const xpBarEmblems = document.querySelectorAll('.card.profile .xp-bar .emblema_Barra img'); 
    
    // CORREÇÃO AQUI: Seleciona a imagem dentro do span com a classe .level-circle do cabeçalho
    const headerEmblem = document.querySelector('.header-right .level-circle'); 

    const profileImages = document.querySelectorAll('.profile-img'); 
    const medalListElement = document.querySelector('.card .list');
    // 2. Obter ID e Verificar Sessão (Função de utils.js)
    const usuarioId = getUsuarioId(); 
    if (!usuarioId) {
        limparSessao(); 
        return; 
    }

    try {
        // 3. Chamar a API
        const response = await fetch(`${API_USUARIO}/${usuarioId}`); 
        const result = await response.json(); 

        if (result.sucesso && result.dados) {
            const dados = result.dados; 
            
            // --- 4. ATUALIZAÇÃO DOS ELEMENTOS ESTÁTICOS E EMBLEMAS ---
            const categoria_atual = dados.categoria;
            const medalha_atual = dados.medalha;
            
            // --- CORREÇÃO BUG EMBLEMA (Pente Fino) ---
            const categoria_proxima = dados.categoria_proxima;
            const medalha_proxima = dados.medalha_proxima;
            // --- FIM DA CORREÇÃO ---
            
            if (profileName) profileName.textContent = dados.nome;
            if (profileCategory) profileCategory.textContent = categoria_atual; // <-- Atualizado
            if (jcPointsValue) jcPointsValue.textContent = dados.jc_points;

            // Emblemas (Imagens Dinâmicas - usando getEmblemPath de utils.js)
            const emblemaPath = getEmblemPath(categoria_atual, medalha_atual);
            
            // --- CORREÇÃO BUG EMBLEMA (Pente Fino) ---
            const emblemaProximoPath = getEmblemPath(categoria_proxima, medalha_proxima);
            // --- FIM DA CORREÇÃO ---
            
            // Atualiza os emblemas no Card (Esquerdo e Direito)
            if (xpBarEmblems.length === 2) {
                xpBarEmblems[0].src = emblemaPath;
                xpBarEmblems[1].src = emblemaProximoPath; // <-- CORRIGIDO
            }
            
            // ATUALIZAÇÃO DO EMBLEMA DO HEADER (USANDO O SELETOR CORRIGIDO)
            if (headerEmblem) headerEmblem.src = emblemaPath;
            
            // Imagem de Perfil
            profileImages.forEach(img => img.src = dados.foto_url || '/assets/unnamed.png');
            
            // --- 5. ATUALIZAÇÃO ANIMADA DA BARRA XP ---
            const targetPercent = dados.progresso_percentual;
            const targetText = dados.progresso_xp_texto; // Ex: "4000 / 4500 JC"

            // Inicia a animação da barra de XP
            animateProgress(targetPercent, targetText, xpBarFill, xpBarText); 
            
            if (medalListElement) {
                const medalhasConquistadas = dados.medalhas_conquistadas || [];
                let htmlListaMedalhas = '';

                if (medalhasConquistadas.length > 0) {
                    // Pega apenas as 3 primeiras medalhas para o resumo
                    const top3Medalhas = medalhasConquistadas.slice(0, 3);
                    
                    top3Medalhas.forEach(nomeMedalha => {
                        // Define um ícone simples baseado no nome
                        let icone = 'fa-medal'; // Padrão
                        if (nomeMedalha.includes('folha')) icone = 'fa-book';
                        if (nomeMedalha.includes('Pegou ar')) icone = 'fa-fire';
                        if (nomeMedalha.includes('Mil Conto')) icone = 'fa-coins';
                        if (nomeMedalha.includes('sono')) icone = 'fa-clock';
                        if (nomeMedalha.includes('Bicho ta virado')) icone = 'fa-trophy';

                        htmlListaMedalhas += `
                            <li>
                              <i class="fas ${icone}"></i>
                              <p>${nomeMedalha}</p>
                              <span class="badge green">Conquistada</span>
                            </li>
                        `;
                    });

                    // Se houver mais de 3 medalhas, adiciona um "ver mais"
                    if (medalhasConquistadas.length > 3) {
                        htmlListaMedalhas += `
                            <li style="justify-content: center; font-weight: 600; color: #555; padding-top: 10px;">
                              <p>+${medalhasConquistadas.length - 3} medalhas...</p>
                            </li>
                        `;
                    }
                } else {
                    htmlListaMedalhas = '<p style="font-size: 14px; color: #777; text-align: left; padding: 10px 0;">Nenhuma medalha conquistada ainda.</p>';
                }

                // Insere o HTML na lista
                medalListElement.innerHTML = htmlListaMedalhas;
            }

        } else {
            throw new Error(result.mensagem || "Resposta da API inválida ao buscar dados do utilizador");
        }
    } catch (error) {
        console.error("Erro CRÍTICO ao carregar dados de fidelidade:", error);
        alert("Ocorreu um erro ao carregar os seus dados. Por favor, faça login novamente.");
        limparSessao();
    }
}
async function carregarMiniRanking() {
    const rankingListElement = document.querySelector('.card .ranking');
    if (!rankingListElement) return; // Não faz nada se a lista não existir

    const usuarioId = getUsuarioId();
    if (!usuarioId) return; // Precisa estar logado

    try {
        // 1. Chama a API de ranking que já criamos
        const response = await fetch(`/api/ranking/${usuarioId}`);
        const result = await response.json();

        if (result.sucesso && result.leaderboard) {
            // 2. Pega apenas os 4 primeiros
            const top4 = result.leaderboard.slice(0, 4);
            
            let htmlListaRanking = '';

            if (top4.length > 0) {
                top4.forEach((usuario, index) => {
                    htmlListaRanking += `
                        <li>
                            <span>${index + 1}</span>
                            ${usuario.nome}
                            <span class="points">${usuario.xps}</span>
                        </li>
                    `;
                });
            } else {
                htmlListaRanking = '<p style="font-size: 14px; color: #777;">Ainda não há ranking.</p>';
            }

            // 3. Insere o HTML na lista
            rankingListElement.innerHTML = htmlListaRanking;
        }

    } catch (error) {
        console.error("Erro ao carregar mini-ranking:", error);
        rankingListElement.innerHTML = '<p style="font-size: 14px; color: red;">Erro ao carregar ranking.</p>';
    }
}