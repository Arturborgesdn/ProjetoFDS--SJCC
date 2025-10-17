document.addEventListener('DOMContentLoaded', function() {
    const formCadastro = document.querySelector('#formCadastro');
    const formLogin = document.querySelector('#formLogin');
    const btnComoGastar = document.querySelector('.jcpoints');
    const lupaBtn = document.querySelector('.lupa-btn');
    
    const API_REGISTRAR = 'http://localhost:5000/api/registrar';
    const API_LOGIN = 'http://localhost:5000/api/login';
    const API_CONECTAR = 'http://localhost:5000/api/conectar';
    
    let USUARIO_ID = 'seu_usuario_id_aqui';
    
    function cadastrarUsuario() {
        const dados = {
            nome: document.querySelector('#nome').value,
            data_nascimento: document.querySelector('#data').value,
            email: document.querySelector('#email').value,
            senha: document.querySelector('#senha').value
        };
        
        fetch(API_REGISTRAR, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                alert(data.mensagem);
                USUARIO_ID = data.id;
                window.location.href = 'login.html';
            } else {
                alert('Erro: ' + data.mensagem);
            }
        })
        .catch(error => alert('Erro no cadastro: ' + error));
    }
    
    function fazerLogin() {
        const dados = {
            email: document.querySelector('#login-email').value,
            senha: document.querySelector('#login-senha').value
        };
        
        fetch(API_LOGIN, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                alert(data.mensagem);
                USUARIO_ID = data.usuario_id;
                window.location.href = 'index.html';
            } else {
                alert('Erro: ' + data.mensagem);
            }
        })
        .catch(error => alert('Erro no login: ' + error));
    }
    
    function testarConexao(acao) {
        console.log('Tentando conectar com Python para ação:', acao);
        
        fetch(API_CONECTAR, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                acao: acao,
                usuario_id: USUARIO_ID
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                console.log('Conexão OK:', data.mensagem);
                alert(data.mensagem + ' Seus JC Points: ' + data.jc_points);
            } else {
                console.log('Erro:', data.mensagem);
                alert('Erro: ' + data.mensagem);
            }
        })
        .catch(error => {
            console.error('Falha na conexão:', error);
            alert('Sem conexão. Tente novamente.');
        });
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
            testarConexao('gastar');
        });
    }
    
    if (lupaBtn) {
        lupaBtn.addEventListener('click', function(event) {
            event.preventDefault();
            testarConexao('busca');
        });
    }
    
    console.log('JS atualizado: Pronto para navegação e integração!');
});
