// ============================================
// Módulo: Utils (Funções e Constantes Globais)
// Arquivo: src/scripts/utils.js
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
    // CATEGORIA_MEDALHA: Nome do arquivo exato na pasta assets
    
    // 1. LEITOR LEIGO
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
    
    // 5. LEITOR DESENROLADO
    'Leitor Desenrolado_Bronze': 'Leitor_Desenrolado_Bronze',
    'Leitor Desenrolado_Prata': 'Leitor_Desenrolado_Prata',
    'Leitor Desenrolado_Ouro': 'Leitor_Desenrolado_Ouro',
    
    // 6. LEITOR TOPADO
    'Leitor Topado_Bronze': 'Leitor_topado_Bronze', 
    'Leitor Topado_Prata': 'Leitor_Topado_Prata',
    'Leitor Topado_Ouro': 'Leitor_Topado_Ouro',
};

/**
 * Retorna o caminho completo para o arquivo de imagem do emblema.
 * @param {string} categoria - Categoria do utilizador.
 * @param {string} medalha - Nível da medalha.
 */
function getEmblemPath(categoria, medalha) {
    const key = `${categoria}_${medalha}`;
    const fileName = EMBLEM_MAP[key];
    
    if (fileName) {
        const extension = fileName.endsWith('.png') || fileName.endsWith('.webp') ? '' : '.png';
        return `/assets/${fileName}${extension}`;
    }
    return '/assets/unnamed.png'; 
}

/**
 * Retorna o nome da PRÓXIMA medalha baseada na atual.
 * Útil para a barra de progresso (Ícone da Direita).
 * Ordem: Bronze -> Prata -> Ouro
 */
function getProximaMedalha(medalhaAtual) {
    const atual = medalhaAtual ? medalhaAtual.trim() : '';

    if (atual === 'Bronze') return 'Prata';
    if (atual === 'Prata') return 'Ouro';
    
    // Se for Ouro, o próximo continua sendo Ouro (nível máximo)
    return 'Ouro'; 
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


// --- LINK INTELIGENTE (Redirecionamento Condicional) ---

/**
 * Verifica se o usuário está logado e altera o destino de TODOS os links de fidelidade.
 * - Logado: Vai para "programa_Fidelidade.html" (Painel)
 * - Não Logado: Vai para "pagina_explicativa.html"
 * * Requer que os links no HTML tenham a classe: .link-fidelidade-dinamico
 */
function atualizarLinksFidelidade() {
    const usuarioId = getUsuarioId();
    
    // Seleciona TODOS os elementos com a classe definida no HTML
    const links = document.querySelectorAll('.link-fidelidade-dinamico');

    links.forEach(link => {
        if (usuarioId) {
            // Usuário Logado -> Acesso ao Painel/Programa
            link.href = "programa_Fidelidade.html";
            link.title = "Acessar meu Painel de Pontos";
        } else {
            // Usuário Não Logado -> Página Explicativa
            link.href = "pagina_explicativa.html";
            link.title = "Conheça nosso programa e cadastre-se!";
        }
    });
}


// --- Sistema de Feedback Visual (Toasts) ---

/**
 * MOSTRA UM ALERTA (TOAST) E ATUALIZA A UI EM TEMPO REAL.
 * @param {object} item - O objeto da missão ou medalha.
 * @param {string} tipo - 'missao' ou 'medalha'.
 */
function mostrarAlertaFeedback(item, tipo) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.classList.add('toast-container');
        document.body.appendChild(container);
    }

    const eMedalha = (tipo === 'medalha');
    const icone = eMedalha ? 'fa-medal' : 'fa-check-circle';
    const titulo = eMedalha ? 'Medalha Conquistada!' : 'Missão Cumprida!';
    const recompensa = eMedalha ? `+${item.jc_points} JC Points` : `+${item.xp} XP, +${item.jc_points} JC Points`;

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

    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 400);
    }, 5000);

    atualizarUIemRealTime(item, tipo);
}

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
    
    setTimeout(updateHeader, 1000); 
}

// --- Inicialização ---
// Executa assim que o HTML for carregado
document.addEventListener('DOMContentLoaded', () => {
    updateHeader();             // Atualiza avatar/emblema no topo se logado
    atualizarLinksFidelidade(); // Configura o destino dos links do troféu/banner
});