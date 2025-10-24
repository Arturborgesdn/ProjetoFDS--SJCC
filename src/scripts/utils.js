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

const EMBLEM_MAP = {
    // CATEGORIA_MEDALHA: Nome do arquivo (sem a extensão .png/.webp, mas com -removebg-preview se existir)
    'Leitor Leigo_Bronze': 'Leito_Leigo_Bronze-removebg-preview',
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
    return '/assets/unnamed.png'; // Fallback genérico
}