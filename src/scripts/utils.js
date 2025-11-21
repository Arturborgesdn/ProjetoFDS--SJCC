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


// --- Gerenciamento de Sessão (Extraído do antigo script.js) ---

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


// --- Mapeamento e Path de Emblemas (Novo) ---

// --- Mapeamento e Path de Emblemas (CORRIGIDO) ---

const EMBLEM_MAP = {
    // CATEGORIA_MEDALHA: Nome do arquivo exato na pasta assets
    
    // 🔴 CORRIGIDO AQUI (Estava 'Leito_Leigo')
    'Leitor Leigo_Bronze': 'Leitor_Leigo_Bronze-removebg-preview', 
    'Leitor Leigo_Prata': 'Leitor_Leigo_Prata-removebg-preview',
    'Leitor Leigo_Ouro': 'Leitor_Leigo_Ouro-removebg-preview',
    
    'Leitor Massa_Bronze': 'Leitor_Massa_Bronze-removebg-preview',
    'Leitor Massa_Prata': 'Leitor_Massa_Prata-removebg-preview',
    'Leitor Massa_Ouro': 'Leitor_Massa_Ouro-removebg-preview',
    
    'Leitor Engajado_Bronze': 'Leitor_Engajado_Bronze-removebg-preview',
    'Leitor Engajado_Prata': 'Leitor_Engajado_Prata-removebg-preview',
    'Leitor Engajado_Ouro': 'Leitor_Engajado_Ouro-removebg-preview',
    
    'Leitor Arretado_Bronze': 'Leitor_Arretado_Bronze-removebg-preview',
    'Leitor Arretado_Prata': 'Leitor_Arretado_Prata-removebg-preview',
    'Leitor Arretado_Ouro': 'Leitor_Arretado_Ouro-removebg-preview',
    
    'Leitor Desenrolado_Bronze': 'Leitor_Desenrolado_Bronze',
    'Leitor Desenrolado_Prata': 'Leitor_Desenrolado_Prata',
    'Leitor Desenrolado_Ouro': 'Leitor_Desenrolado_Ouro',
    
    // 🔴 Padronizei 'topado' para 'Topado' (verifique se seu arquivo é maiúsculo ou minúsculo)
    'Leitor Topado_Bronze': 'Leitor_Topado_Bronze', 
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
    return '/assets/unnamed.png'; // Fallback genérico
}


// aqui tem a função para o header dinâmico em todas as páginas, de acordo com o usuario id.
async function updateHeader() {
    const usuarioId = getUsuarioId();
    // Seleção dos elementos do Header (IDs ou classes universais)
    const headerProfileImg = document.querySelector('.header-right .profile-img');
    const headerEmblem = document.querySelector('.header-right .level-circle'); 

    if (!usuarioId) {
        // Se não estiver logado, não faz nada (mantém os ícones de login)
        return;
    }

    try {
        const response = await fetch(`${API_USUARIO}/${usuarioId}`);
        const result = await response.json();

        if (result.sucesso && result.dados) {
            const dados = result.dados;
            
            const categoria = dados.categoria;
            const medalha = dados.medalha;
            const emblemaPath = getEmblemPath(categoria, medalha); // Usa o mapeamento já definido
            
            // 1. Atualiza a foto do Perfil (assumindo que o src é 'unnamed.png' se não houver um dado real)
            if (headerProfileImg) headerProfileImg.src = dados.foto_url || '/assets/unnamed.png'; 

            // 2. Atualiza o Emblema (Status/Categoria) no Header
            if (headerEmblem) headerEmblem.src = emblemaPath;
        }
    } catch (error) {
        console.error("Falha ao carregar dados do header:", error);
    }
}

// ... (final do arquivo utils.js, depois de updateHeader)

/**
 * MOSTRA UM ALERTA (TOAST) E ATUALIZA A UI EM TEMPO REAL.
 * Esta função agora é global.
 * @param {object} item - O objeto da missão ou medalha (deve ter .nome, .xp, .jc_points)
 * @param {string} tipo - 'missao' ou 'medalha'
 */
function mostrarAlertaFeedback(item, tipo) {
    // 1. Cria o container de toasts (se ainda não existir)
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.classList.add('toast-container');
        document.body.appendChild(container);
    }

    // 2. Define o conteúdo do toast
    const eMedalha = (tipo === 'medalha');
    const icone = eMedalha ? 'fa-medal' : 'fa-check-circle';
    const corClasse = eMedalha ? 'medalha' : 'missao';
    const titulo = eMedalha ? 'Medalha Conquistada!' : 'Missão Cumprida!';
    const recompensa = eMedalha ? `+${item.jc_points} JC Points` : `+${item.xp} XP, +${item.jc_points} JC Points`;

    // 3. Cria o elemento do toast
    const toast = document.createElement('div');
    toast.classList.add('toast'); // Adiciona a classe base

    if (eMedalha) {
        toast.classList.add('medalha');
    } else {
        // É uma missão
        toast.classList.add('missao');
        if (item.raridade) {
            toast.classList.add(item.raridade); // Adiciona 'comum', 'rara', ou 'epica'
        }
    }
    toast.innerHTML = `
        <i class="fas ${icone}"></i>
        <div class="toast-content">
            <strong>${titulo}</strong>
            <span>${item.nome} (${recompensa})</span>
        </div>
    `;

    // 4. Adiciona o toast ao container
    container.appendChild(toast);

    // 5. Remove o toast após 5 segundos
    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 400);
    }, 5000);

    // 6. ATUALIZAÇÃO DA UI EM TEMPO REAL (Sua solicitação)
    atualizarUIemRealTime(item, tipo);
}

/**
 * Função auxiliar para encontrar e atualizar o item na página ATUAL.
 */
function atualizarUIemRealTime(item, tipo) {
    // Escopo de segurança: só faz algo se o item tiver um nome
    if (!item || !item.nome) return;

    // Tenta "adivinhar" o seletor baseado no nome (escapando caracteres)
    const nomeFormatado = item.nome.replace(/"/g, '\\"');
    
    if (tipo === 'missao') {
        // Procura pela missão na página de missões
        const elementoMissao = document.querySelector(`.goal-item[data-nome="${nomeFormatado}"]`);
        if (elementoMissao) {
            console.log(`Atualizando UI para missão: ${item.nome}`);
            elementoMissao.classList.remove('pendente');
            elementoMissao.classList.add('concluida');
            // A regra de CSS que adicionamos (passo 1) vai esconder a barra automaticamente
        }
    } 
    else if (tipo === 'medalha') {
        // Procura pela medalha na página de medalhas
        const elementoMedalha = document.querySelector(`.medalha[data-nome="${nomeFormatado}"]`);
        if (elementoMedalha) {
            console.log(`Atualizando UI para medalha: ${item.nome}`);
            elementoMedalha.classList.remove('pendente');
            elementoMedalha.classList.add('concluida');
        }
    }
    
    // ATUALIZAR O HEADER (XP/JC Points)
    // A função updateHeader() busca o total. Vamos chamá-la após um pequeno delay
    // para dar tempo do DB processar a recompensa antes da nova busca.
    setTimeout(updateHeader, 1000); 
}