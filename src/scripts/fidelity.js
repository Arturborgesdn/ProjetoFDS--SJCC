// ============================================
// Módulo: Fidelidade (Lógica para programa_Fidelidade.html)
//
// Depende de: utils.js (para getEmblemPath, getUsuarioId, API_USUARIO, etc.)
// Nota: Este arquivo deve ser carregado DEPOIS de utils.js.
// ============================================

// --- FUNÇÃO PARA ANIMAÇÃO DA BARRA DE PROGRESSO ---
function animateProgress(targetPercent, targetText, xpBarFill, xpBarText) {
    const duration = 1500; 
    const startTime = performance.now();
    
    if (xpBarText) xpBarText.textContent = targetText; 

    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        let progress = Math.min(elapsed / duration, 1); 
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const currentPercent = targetPercent * easeOut;
        
        if (xpBarFill) xpBarFill.style.width = `${currentPercent}%`;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            if (xpBarFill) xpBarFill.style.width = `${targetPercent}%`;
        }
    }
    requestAnimationFrame(animate);
}

// --- FUNÇÃO PRINCIPAL: CARREGAR DADOS ---
async function carregarDadosDeFidelidade() {
    // 1. Seleção de Elementos
    const profileName = document.querySelector('.card.profile h2');
    const profileCategory = document.querySelector('.card.profile .titulo');
    const xpBarFill = document.querySelector('.card.profile .xp-bar .fill');
    const xpBarText = document.querySelector('.card.profile .container-xp-logo p');
    const jcPointsValue = document.querySelector('.cardjc .container-jc h2');
    const xpBarEmblems = document.querySelectorAll('.card.profile .xp-bar .emblema_Barra img'); 
    const headerEmblem = document.querySelector('.header-right .level-circle'); 
    const profileImages = document.querySelectorAll('.profile-img'); 
    const medalListElement = document.querySelector('.card .list');
    
    // 2. Obter ID e Verificar Sessão
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
            
            // --- 🚨 ÁREA DE DEBUG DO HAL (Veja no Console F12) ---
            console.log("--- DEBUG FIDELIDADE ---");
            console.log("Nível Atual:", dados.categoria, dados.medalha);
            console.log("Próximo Nível (Python):", dados.proxima_categoria_nome, dados.proxima_medalha_tipo);
            // -----------------------------------------------------

            // --- 4. DEFINIÇÃO DE VARIÁVEIS ---
            const categoria_atual = dados.categoria;
            const medalha_atual = dados.medalha;
            
            // Lógica de Fallback: Se o Python não mandar o "próximo" (ex: nível máximo), usa o atual
            const categoria_proxima = dados.proxima_categoria_nome ? dados.proxima_categoria_nome : categoria_atual;
            const medalha_proxima = dados.proxima_medalha_tipo ? dados.proxima_medalha_tipo : medalha_atual;
            
            // Atualiza textos
            if (profileName) profileName.textContent = dados.nome;
            if (profileCategory) profileCategory.textContent = categoria_atual;
            if (jcPointsValue) jcPointsValue.textContent = dados.jc_points;

            // --- 5. ATUALIZAÇÃO DOS EMBLEMAS (Imagens) ---
            
            // Emblema da Esquerda (Onde estou)
            const emblemaPath = getEmblemPath(categoria_atual, medalha_atual);
            
            // Emblema da Direita (Para onde vou)
            const emblemaProximoPath = getEmblemPath(categoria_proxima, medalha_proxima);
            
            // Debug das URLs das imagens
            console.log("URL Imagem Atual:", emblemaPath);
            console.log("URL Imagem Próxima:", emblemaProximoPath);

            // Aplica as imagens no HTML
            if (xpBarEmblems.length === 2) {
                xpBarEmblems[0].src = emblemaPath;
                xpBarEmblems[1].src = emblemaProximoPath; // <--- AQUI MUDA O ÍCONE DA DIREITA
            }
            
            // Header sempre mostra o atual
            if (headerEmblem) headerEmblem.src = emblemaPath;
            
            // Foto de perfil
            profileImages.forEach(img => img.src = dados.foto_url || '/assets/unnamed.png');
            
            // --- 6. ANIMAÇÃO DA BARRA ---
            const targetPercent = dados.progresso_percentual;
            const targetText = dados.progresso_xp_texto; 
            animateProgress(targetPercent, targetText, xpBarFill, xpBarText); 
            
            // --- 7. LISTA DE MEDALHAS ---
            if (medalListElement) {
                const medalhasConquistadas = dados.medalhas_conquistadas || [];
                let htmlListaMedalhas = '';

                if (medalhasConquistadas.length > 0) {
                    const top3Medalhas = medalhasConquistadas.slice(0, 3);
                    
                    top3Medalhas.forEach(nomeMedalha => {
                        let icone = 'fa-medal';
                        // Mapeamento simples de ícones
                        if (nomeMedalha.toLowerCase().includes('folha')) icone = 'fa-book';
                        if (nomeMedalha.toLowerCase().includes('pegou ar')) icone = 'fa-fire';
                        if (nomeMedalha.toLowerCase().includes('mil conto')) icone = 'fa-coins';
                        if (nomeMedalha.toLowerCase().includes('sono')) icone = 'fa-clock';
                        if (nomeMedalha.toLowerCase().includes('virado')) icone = 'fa-trophy';

                        htmlListaMedalhas += `
                            <li>
                              <i class="fas ${icone}"></i>
                              <p>${nomeMedalha}</p>
                              <span class="badge green">Conquistada</span>
                            </li>
                        `;
                    });

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
                medalListElement.innerHTML = htmlListaMedalhas;
            }

        } else {
            throw new Error(result.mensagem || "Erro na resposta da API");
        }
    } catch (error) {
        console.error("Erro CRÍTICO no Fidelidade:", error);
    }
}

// --- FUNÇÃO PARA CARREGAR MINI RANKING ---
async function carregarMiniRanking() {
    const rankingListElement = document.querySelector('.card .ranking');
    if (!rankingListElement) return; 

    const usuarioId = getUsuarioId();
    if (!usuarioId) return; 

    try {
        const response = await fetch(`/api/ranking/${usuarioId}`);
        const result = await response.json();

        if (result.sucesso && result.leaderboard) {
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
            rankingListElement.innerHTML = htmlListaRanking;
        }
    } catch (error) {
        console.error("Erro ao carregar mini-ranking:", error);
        rankingListElement.innerHTML = '<p style="font-size: 14px; color: red;">Erro ao carregar ranking.</p>';
    }
}