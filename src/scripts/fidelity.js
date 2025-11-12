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
            

        } else {
            throw new Error(result.mensagem || "Resposta da API inválida ao buscar dados do utilizador");
        }
    } catch (error) {
        console.error("Erro CRÍTICO ao carregar dados de fidelidade:", error);
        alert("Ocorreu um erro ao carregar os seus dados. Por favor, faça login novamente.");
        limparSessao();
    }
}