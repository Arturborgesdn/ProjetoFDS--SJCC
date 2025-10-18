// src/scripts/script.js (Versão com Alertas de Placeholder)

document.addEventListener('DOMContentLoaded', function() {
    // Seleciona os formulários e botões
    const formCadastro = document.querySelector('#formCadastro');
    const formLogin = document.querySelector('#formLogin');
    const btnComoGastar = document.querySelector('.jcpoints');
    const lupaBtn = document.querySelector('.lupa-btn');
    
    // Define os URLs da API
    const API_REGISTRAR = '/api/registrar';
    const API_LOGIN = '/api/login';
    
    // --- LÓGICA DE MEMÓRIA (localStorage) ---
    function salvarSessao(usuarioId) {
        localStorage.setItem('usuario_id_sjcc', usuarioId);
    }

    function getUsuarioId() {
        return localStorage.getItem('usuario_id_sjcc');
    }

    // --- FUNÇÕES DE LOGIN/REGISTO (CONTINUAM IGUAIS) ---
    function cadastrarUsuario() {
        // ... (o seu código de registo continua aqui, sem alterações)
        const dados = {
            nome: document.querySelector('#nome').value,
            data_nascimento: document.querySelector('#data').value,
            email: document.querySelector('#email').value,
            senha: document.querySelector('#senha').value
        };
        fetch(API_REGISTRAR, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                alert(data.mensagem);
                window.location.href = '/login.html';
            } else {
                alert('Erro: ' + data.mensagem);
            }
        }).catch(error => alert('Erro no registo: ' + error));
    }
    
    function fazerLogin() {
        // ... (o seu código de login continua aqui, sem alterações)
        const dados = {
            email: document.querySelector('#login-email').value,
            senha: document.querySelector('#login-senha').value
        };
        fetch(API_LOGIN, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                alert(data.mensagem);
                salvarSessao(data.usuario_id);
                window.location.href = '/programa_Fidelidade.html';  
            } else {
                alert('Erro: ' + data.mensagem);
            }
        }).catch(error => alert('Erro no login: ' + error));
    }
    
    // --- FUNÇÃO DE ALERTA (A PARTE QUE VAMOS MUDAR) ---
    function mostrarAlertaMVP(acao) {
        console.log('Ação de placeholder acionada:', acao);
        
        // Mostra alertas de placeholder em vez de conectar ao backend
        if (acao === 'gastar') {
            alert('Calma! Em breve incluiremos a página de recompensas no MVP.');
        } else if (acao === 'busca') {
            alert('A funcionalidade de busca ainda será implementada. Aguarde!');
        } else {
            // Alerta genérico para qualquer outra ação
            alert('Esta funcionalidade ainda não está disponível.');
        }
    }
    
    // --- EVENT LISTENERS (Ligam os cliques às funções) ---
    if (formCadastro) {
        formCadastro.addEventListener('submit', function(event) {
            event.preventDefault();
            cadastrarUsuario();
        });
    }
    
    if (formLogin) {
        formLogin.addEventListener('submit', function(event) {
            event.preventDefault();
            fazerLogin();
        });
    }
    
    // Altera a ação dos botões para chamar a nova função de alerta
    if (btnComoGastar) {
        btnComoGastar.addEventListener('click', function(event) {
            event.preventDefault();
            mostrarAlertaMVP('gastar'); // Chama a função de alerta
        });
    }
    
    if (lupaBtn) {
        lupaBtn.addEventListener('click', function(event) {
            event.preventDefault();
            mostrarAlertaMVP('busca'); // Chama a função de alerta
        });
    }
    
    console.log('JS inicializado e pronto para navegação!');
});