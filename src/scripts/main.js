// src/scripts/main.js
// Ponto de entrada do Frontend. Gerencia o roteamento de scripts para cada página.
// Funções como cadastrarUsuario(), fazerLogin(), carregarDadosDeFidelidade() e limparSessao()
// DEVEM ser definidas em arquivos carregados ANTES (ex: auth.js, fidelity.js, utils.js).

document.addEventListener('DOMContentLoaded', function() {
    
    updateHeader();//chama a funcção de atualização do header
    // --- Seleção de Elementos de Roteamento ---
    // Usamos estes elementos para identificar em qual página estamos.
    const formCadastro = document.querySelector('#formCadastro'); // Presente em cadastro.html
    const formLogin = document.querySelector('#formLogin');       // Presente em login.html
    const profileCard = document.querySelector('.card.profile'); // Presente em programa_Fidelidade.html
    const medalhasSection = document.querySelector('.medalhas-top-cards'); // Presente em medalhas.html
    
    // Elementos globais
    const lupaBtn = document.querySelector('.lupa-btn');
    const logoutButton = document.getElementById('logout-btn');

    // --- LÓGICA DE ROTEAMENTO PRINCIPAL ---

    // 1. Página de Cadastro
    if (formCadastro) {
        formCadastro.addEventListener('submit', function(event) {
            event.preventDefault();
            // Chama a função definida em auth.js
            cadastrarUsuario(); 
        });
        console.log("Módulo: Registo. Event Listener ativado.");

    // 2. Página de Login
    } else if (formLogin) {
        formLogin.addEventListener('submit', function(event) {
            event.preventDefault();
            // Chama a função definida em auth.js
            fazerLogin(); 
        });
        console.log("Módulo: Login. Event Listener ativado.");

    // 3. Página do Programa de Fidelidade
    } else if (profileCard) { 
        // Chama a função principal de carregamento de dados do fidelity.js
        carregarDadosDeFidelidade(); 
        console.log("Módulo: Fidelidade. Carregamento de dados iniciado.");
    
    // 4. Página de Medalhas
    } else if (medalhasSection) {
        // TODO: No próximo passo, criaremos essa função em medalhas.js
        // carregarDadosDeMedalhas(); 
        console.log("Módulo: Medalhas. Carregamento de dados será iniciado.");
    }
    
    // --- LÓGICA GLOBAL (Eventos Comuns) ---

    // Listener para o botão de busca (lupa)
    if (lupaBtn) {
        lupaBtn.addEventListener('click', function(event) {
            event.preventDefault();
            alert('A funcionalidade de busca ainda será implementada. Aguarde!'); 
        });
    }

    // Listener para o botão de Logout (se existir na página)
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            limparSessao(); // Chama a função de utils.js que limpa e redireciona
        });
    }

    console.log("main.js carregado. Roteamento concluído.");
});