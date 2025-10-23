// src/scripts/script.js (Versão SEM Alertas de Placeholder)

document.addEventListener('DOMContentLoaded', function() {

    // --- Seleção de Elementos ---
    const formCadastro = document.querySelector('#formCadastro');
    const formLogin = document.querySelector('#formLogin');
    // Elementos da página de Fidelidade (só existem nessa página)
    const profileCard = document.querySelector('.card.profile');
    const btnComoGastar = document.querySelector('.jcpoints'); // Botão "COMO GASTAR?"
    const lupaBtn = document.querySelector('.lupa-btn'); // Botão da lupa no header

    // --- URLs da API ---
    const API_REGISTRAR = '/api/registrar';
    const API_LOGIN = '/api/login';
    const API_USUARIO = '/api/usuario'; // URL base para buscar dados do utilizador

    // --- Lógica de Memória (Sessão) ---
    function salvarSessao(usuarioId) { localStorage.setItem('usuario_id_sjcc', usuarioId); }
    function getUsuarioId() { return localStorage.getItem('usuario_id_sjcc'); }
    function limparSessao() { localStorage.removeItem('usuario_id_sjcc'); } // Para Logout futuro

    // --- Funções de Login/Registo (COPIE AS SUAS FUNÇÕES COMPLETAS AQUI, se não estiverem) ---
    function cadastrarUsuario() {
        // Cole aqui a sua função cadastrarUsuario completa
         const dados = {
            nome: document.querySelector('#nome').value,
            data_nascimento: document.querySelector('#data').value, // Formato DD/MM/YYYY
            email: document.querySelector('#email').value,
            senha: document.querySelector('#senha').value
        };
        fetch(API_REGISTRAR, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                alert(data.mensagem); // Mantemos o alerta de sucesso/erro do REGISTO
                window.location.href = '/login.html';
            } else {
                alert('Erro: ' + data.mensagem); // Mantemos o alerta de sucesso/erro do REGISTO
            }
        }).catch(error => alert('Erro no registo: ' + error)); // Mantemos o alerta de erro de rede
    }

   function fazerLogin() {
        const dados = {
            email: document.querySelector('#login-email').value,
            senha: document.querySelector('#login-senha').value
        };
        fetch(API_LOGIN, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                // Substituído alert por console.log para a mensagem de sucesso
                console.log(data.mensagem); // <--- ALTERAÇÃO AQUI
                salvarSessao(data.usuario_id); // Guarda o ID na memória!
                window.location.href = '/programa_Fidelidade.html';  
            } else {
                // Substituído alert por console.error para a mensagem de erro da API
                console.error('Erro de login (API): ' + data.mensagem); // <--- ALTERAÇÃO AQUI
                // Poderia também exibir o erro numa área da página HTML em vez de console
            }
        }).catch(error => {
            // Substituído alert por console.error para erros de rede/fetch
            console.error('Erro na requisição de login (fetch):', error); // <--- ALTERAÇÃO AQUI
        });
    }

    // --- FUNÇÃO PARA CARREGAR E MOSTRAR DADOS NA PÁGINA DE FIDELIDADE ---
    async function carregarDadosDeFidelidade() {
        const usuarioId = getUsuarioId();
        if (!usuarioId) {
            console.error("ID do utilizador não encontrado. Redirecionando para login.");
            window.location.href = '/login.html';
            return;
        }
        console.log(`Buscando dados para o utilizador ID: ${usuarioId}`);
        try {
            const response = await fetch(`${API_USUARIO}/${usuarioId}`);
            const result = await response.json();
            if (result.sucesso && result.dados) {
                const dados = result.dados;
                console.log("Dados recebidos:", dados);
                // Atualiza o HTML
                document.querySelector('.profile h2').textContent = dados.nome;
                document.querySelector('.profile .titulo').textContent = dados.categoria;
                document.querySelector('.profile .xp-bar .fill').style.width = `${dados.progresso_percentual}%`;
                document.querySelector('.profile .xp-bar + .container-xp-logo p').textContent = `${dados.progresso_xp_texto} `;
                document.querySelector('.cardjc h1').textContent = dados.jc_points;
                // (Opcional) Atualizações do header
                const headerXpFill = document.querySelector('.xp-bar-header .xp-fill');
                if (headerXpFill) headerXpFill.style.width = `${dados.progresso_percentual}%`;
                const headerEmblema = document.querySelector('.header-right .emblema');
                if(headerEmblema) headerEmblema.alt = dados.categoria;
                console.log("Página de fidelidade atualizada!");
            } else {
                throw new Error(result.mensagem || "Resposta da API inválida ao buscar dados do utilizador");
            }
        } catch (error) {
            console.error("Erro ao carregar dados de fidelidade:", error);
            // Removemos o alert daqui também para evitar pop-ups indesejados
            limparSessao();
            window.location.href = '/login.html';
        }
    }

    // --- LÓGICA DE ROTEAMENTO E EVENT LISTENERS ---
    if (formCadastro) {
        formCadastro.addEventListener('submit', function(event) {
            event.preventDefault();
            cadastrarUsuario();
        });
        console.log("Página de Registo pronta.");
    } else if (formLogin) {
        formLogin.addEventListener('submit', function(event) {
            event.preventDefault();
            fazerLogin();
        });
        console.log("Página de Login pronta.");
    } else if (profileCard) {
        // Estamos na página de fidelidade
        carregarDadosDeFidelidade(); // Busca e mostra os dados do utilizador

        // --- REMOÇÃO DOS ALERTAS ---
        // Agora, os botões simplesmente não fazem nada ao serem clicados.

        if (btnComoGastar) {
            btnComoGastar.addEventListener('click', function(event) {
                event.preventDefault(); // Impede qualquer ação padrão do botão
                console.log("Botão 'Como Gastar?' clicado - Nenhuma ação definida (MVP).");
                // NENHUM ALERT AQUI
            });
        }
        if (lupaBtn) {
            lupaBtn.addEventListener('click', function(event) {
                event.preventDefault(); // Impede qualquer ação padrão do botão
                console.log("Botão 'Busca' clicado - Nenhuma ação definida (MVP).");
                // NENHUM ALERT AQUI
            });
        }
        console.log("Página de Fidelidade pronta.");
    } else {
        console.log("Script.js carregado numa página não reconhecida.");
    }

    // Adiciona funcionalidade de Logout (se existir um botão)
    const logoutButton = document.getElementById('logout-btn'); // Crie um botão com este ID se quiser logout
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            limparSessao();
            // alert("Você saiu da sua conta."); // Alert de logout também pode ser removido
            window.location.href = '/login.html';
        });
    }
});