document.addEventListener('DOMContentLoaded', function() {
    // Seleciona os formulários e botões
    const formCadastro = document.querySelector('#formCadastro');
    const formLogin = document.querySelector('#formLogin');
    const btnComoGastar = document.querySelector('.jcpoints');
    const lupaBtn = document.querySelector('.lupa-btn');
    
    // Define os URLs da API
    const API_REGISTRAR = '/api/registrar';
    const API_LOGIN = '/api/login';
    
    
    function salvarSessao(usuarioId) {
        localStorage.setItem('usuario_id_sjcc', usuarioId);
    }

    function getUsuarioId() {
        return localStorage.getItem('usuario_id_sjcc');
    }

   
    function cadastrarUsuario() {
       
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
    
   
    function mostrarAlertaMVP(acao) {
        console.log('Ação de placeholder acionada:', acao);
        
        
        if (acao === 'gastar') {
            alert('Calma! Em breve incluiremos a página de recompensas no MVP.');
        } else if (acao === 'busca') {
            alert('A funcionalidade de busca ainda será implementada. Aguarde!');
        } else {
            
            alert('Esta funcionalidade ainda não está disponível.');
        }
    }
    
    
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
    
    
    if (btnComoGastar) {
        btnComoGastar.addEventListener('click', function(event) {
            event.preventDefault();
            mostrarAlertaMVP('gastar'); 
        });
    }
    
    if (lupaBtn) {
        lupaBtn.addEventListener('click', function(event) {
            event.preventDefault();
            mostrarAlertaMVP('busca'); 
        });
    }
    
    console.log('JS inicializado e pronto para navegação!');
});