// ============================================
// Módulo: Utils (Funções e Constantes Globais)
//
// Responsabilidades:
// 1. Gerenciamento de Sessão (Login/Logout)
// 2. Definição de URLs da API
// 3. Mapeamento de Categorias/Medalhas para caminhos de imagem
// ============================================

// --- URLs da API (Constantes) ---
const API_REGISTRAR = '/api/registrar';
const API_LOGIN = '/api/login';
const API_USUARIO = '/api/usuario'; // Rota para /api/usuario/<id>


// --- Gerenciamento de Sessão ---

/**
 * Salva o ID e nome do utilizador no Local Storage após o login.
 * @param {object} userData - Deve conter usuario_id e nome.
 */
function salvarSessao(userData) { 
    const sessionData = { id: userData.usuario_id, nome: userData.nome };
    localStorage.setItem('usuario_sjcc', JSON.stringify(sessionData)); 
}

/**
 * Obtém os dados de sessão (ID e Nome) do Local Storage.
 * @returns {object|null} Dados do utilizador ou null se não houver.
 */
function getSessaoUsuario() { 
    const session = localStorage.getItem('usuario_sjcc');
    return session ? JSON.parse(session) : null;
}

/**
 * Obtém apenas o ID do utilizador logado.
 * @returns {string|null} ID do utilizador.
 */
function getUsuarioId() {
    const session = getSessaoUsuario();
    return session ? session.id : null;
}

/**
 * Limpa a sessão e redireciona para a página de login.
 */
function limparSessao() { 
    localStorage.removeItem('usuario_sjcc'); 
    window.location.href = '/login.html'; 
}


// --- Mapeamento e Path de Emblemas ---

const EMBLEM_MAP = {
    // CATEGORIA_MEDALHA: Nome do arquivo exato na pasta assets (sem extensão se for .png)
    
    // 1. LEITOR LEIGO
    // ⚠️ Atenção: O arquivo 'Bronze' está escrito 'Leito' (sem R) na pasta.
    'Leitor Leigo_Bronze': 'Leito_Leigo_Bronze-removebg-preview', 
    'Leitor Leigo_Prata': 'Leitor_Leigo_Prata-removebg-preview',
    'Leitor Leigo_Ouro': 'Leitor_Leigo_Ouro-removebg-preview',
    
    // 2. LEITOR MASSA
    'Leitor Massa_Bronze': 'Leitor_Massa_Bronze-removebg-preview',
    'Leitor Massa_Prata': 'Leitor_Massa_Prata-removebg-preview',
    'Leitor Massa_Ouro': 'Leitor_Massa_Ouro-removebg-preview',
    
    // 3. LEITOR ENGAJADO
    'Leitor Engajado_Bronze': 'Leitor_Engajado_Bronze-removebg-preview',
    'Leitor Engajado_Prata': 'Leitor_Engajado_Prata-removebg-preview',
    'Leitor Engajado_Ouro': 'Leitor_Engajado_Ouro-removebg-preview',
    
    // 4. LEITOR ARRETADO
    'Leitor Arretado_Bronze': 'Leitor_Arretado_Bronze-removebg-preview',
    'Leitor Arretado_Prata': 'Leitor_Arretado_Prata-removebg-preview',
    'Leitor Arretado_Ouro': 'Leitor_Arretado_Ouro-removebg-preview',
    
    // 5. LEITOR DESENROLADO (Sem o sufixo -removebg-preview na pasta)
    'Leitor Desenrolado_Bronze': 'Leitor_Desenrolado_Bronze',
    'Leitor Desenrolado_Prata': 'Leitor_Desenrolado_Prata',
    'Leitor Desenrolado_Ouro': 'Leitor_Desenrolado_Ouro',
    
    // 6. LEITOR TOPADO
    // ⚠️ Atenção: O arquivo 'Bronze' está com 'topado' minúsculo na pasta, os outros maiúsculos.
    'Leitor Topado_Bronze': 'Leitor_topado_Bronze', 
    'Leitor Topado_Prata': 'Leitor_Topado_Prata',
    'Leitor Topado_Ouro': 'Leitor_Topado_Ouro',
};

/**
 * Retorna o caminho completo para o arquivo de imagem do emblema.
 * @param {string} categoria - Categoria do utilizador (ex: 'Leitor Massa').
 * @param {string} medalha - Nível da medalha (Bronze, Prata, Ouro).
 * @returns {string} Caminho completo (ex: /assets/Leitor_Massa_Prata-removebg-preview.png).
 */
function getEmblemPath(categoria, medalha) {
    const key = `${categoria}_${medalha}`;
    const fileName = EMBLEM_MAP[key];
    
    if (fileName) {
        // Assume .png como extensão padrão se não estiver no nome do arquivo
        const extension = fileName.endsWith('.png') || fileName.endsWith('.webp') ? '' : '.png';
        return `/assets/${fileName}${extension}`;
    }
    
    // Fallback: Retorna uma imagem padrão se não encontrar o emblema
    return '/assets/unnamed.png'; 
}


// --- Função para Header Dinâmico ---
async function updateHeader() {
    const usuarioId = getUsuarioId();
    // Seleção dos elementos do Header
    const headerProfileImg = document.querySelector('.header-right .profile-img');
    const headerEmblem = document.querySelector('.header-right .level-circle'); 

    if (!usuarioId) return;

    try {
        const response = await fetch(`${API_USUARIO}/${usuarioId}`);
        const result = await response.json();

        if (result.sucesso && result.dados) {
            const dados = result.dados;
            
            const categoria = dados.categoria;
            const medalha = dados.medalha;
            const emblemaPath = getEmblemPath(categoria, medalha);
            
            // 1. Atualiza a foto do Perfil
            if (headerProfileImg) headerProfileImg.src = dados.foto_url || '/assets/unnamed.png'; 

            // 2. Atualiza o Emblema no Header
            if (headerEmblem) headerEmblem.src = emblemaPath;
        }
    } catch (error) {
        console.error("Falha ao carregar dados do header:", error);
    }
}

// --- Sistema de Feedback Visual (Toasts) ---

/**
 * MOSTRA UM ALERTA (TOAST) E ATUALIZA A UI EM TEMPO REAL.
 * @param {object} item - O objeto da missão ou medalha.
 * @param {string} tipo - 'missao' ou 'medalha'.
 */
function mostrarAlertaFeedback(item, tipo) {
    // 1. Cria o container de toasts
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.classList.add('toast-container');
        document.body.appendChild(container);
    }

    // 2. Define o conteúdo
    const eMedalha = (tipo === 'medalha');
    const icone = eMedalha ? 'fa-medal' : 'fa-check-circle';
    const titulo = eMedalha ? 'Medalha Conquistada!' : 'Missão Cumprida!';
    const recompensa = eMedalha ? `+${item.jc_points} JC Points` : `+${item.xp} XP, +${item.jc_points} JC Points`;

    // 3. Cria o elemento
    const toast = document.createElement('div');
    toast.classList.add('toast'); 

    if (eMedalha) {
        toast.classList.add('medalha');
    } else {
        toast.classList.add('missao');
        if (item.raridade) toast.classList.add(item.raridade);
    }
    
    toast.innerHTML = `
        <i class="fas ${icone}"></i>
        <div class="toast-content">
            <strong>${titulo}</strong>
            <span>${item.nome} (${recompensa})</span>
        </div>
    `;

    // 4. Adiciona e remove após tempo
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 400);
    }, 5000);

    // 6. Atualiza a UI da página atual
    atualizarUIemRealTime(item, tipo);
}

/**
 * Função auxiliar para encontrar e atualizar o item na página ATUAL.
 */
function atualizarUIemRealTime(item, tipo) {
    if (!item || !item.nome) return;

    const nomeFormatado = item.nome.replace(/"/g, '\\"');
    
    if (tipo === 'missao') {
        const elementoMissao = document.querySelector(`.goal-item[data-nome="${nomeFormatado}"]`);
        if (elementoMissao) {
            elementoMissao.classList.remove('pendente');
            elementoMissao.classList.add('concluida');
        }
    } 
    else if (tipo === 'medalha') {
        const elementoMedalha = document.querySelector(`.medalha[data-nome="${nomeFormatado}"]`);
        if (elementoMedalha) {
            elementoMedalha.classList.remove('pendente');
            elementoMedalha.classList.add('concluida');
        }
    }
    
    // Atualiza o header após breve delay para sincronizar com DB
    setTimeout(updateHeader, 1000); 
}