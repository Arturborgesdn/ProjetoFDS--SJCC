// ============================================
// Lógica de Autenticação (Cadastro e Login)
// Assumimos que as funções e constantes abaixo são carregadas por utils.js:
// - salvarSessao(data)
// - API_REGISTRAR
// - API_LOGIN
// - API_USUARIO (não usada diretamente aqui, mas útil para o utils)
// ============================================

/**
 * Lida com o processo de cadastro do utilizador.
 */
function cadastrarUsuario() {
    // 1. Coleta de dados
    const formCadastro = document.querySelector('#formCadastro');
    if (!formCadastro) return; // Garante que a função só roda na página de cadastro

    const dados = {
        nome: document.querySelector('#nome').value,
        data_nascimento: document.querySelector('#data').value, 
        email: document.querySelector('#email').value,
        senha: document.querySelector('#senha').value
    };

    // 2. Validação básica (Opcional, a validação principal é no Flask)
    if (!dados.nome || !dados.email || !dados.senha) {
         alert('Por favor, preencha todos os campos obrigatórios.');
         return;
    }

    // 3. Chamada à API
    fetch(API_REGISTRAR, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            alert('Cadastro realizado com sucesso! Faça login para começar.'); 
            // Redireciona para a página de login
            window.location.href = '/login.html';
        } else {
            console.error('Erro de Cadastro (API):', data.mensagem);
            alert('Erro ao cadastrar: ' + data.mensagem); 
        }
    })
    .catch(error => {
        console.error('Erro na requisição de cadastro (fetch):', error); 
        alert('Erro de conexão com o servidor. Tente novamente mais tarde.');
    });
}


/**
 * Lida com o processo de login do utilizador.
 */
function fazerLogin() {
    // 1. Coleta de dados
    const formLogin = document.querySelector('#formLogin');
    if (!formLogin) return; // Garante que a função só roda na página de login
    
    const dados = {
        email: document.querySelector('#login-email').value,
        senha: document.querySelector('#login-senha').value
    };
    
    // 2. Chamada à API
    fetch(API_LOGIN, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            console.log(data.mensagem); 
            // 3. Salva os dados de sessão (ID e Nome) e redireciona
            salvarSessao(data); // Assume função de utils.js
            window.location.href = '/programa_Fidelidade.html';  
        } else {
            console.error('Erro de login (API): ' + data.mensagem); 
            alert('Email ou senha inválidos. Por favor, verifique suas credenciais.');
        }
    })
    .catch(error => {
        console.error('Erro na requisição de login (fetch):', error); 
        alert('Erro de conexão com o servidor. Verifique sua rede.');
    });
}