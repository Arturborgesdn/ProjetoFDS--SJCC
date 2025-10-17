
// CÓDIGO JAVASCRIPT ATUALIZADO: Integração com Back-End e MySQL 
// Conceito Geral: Este JS envia dados para o Python (incluindo usuario_id),
// recebe a resposta do banco de dados e exibe os resultados.
// Mudanças: Adicionamos usuario_id no fetch e usamos a resposta para alertas dinâmicos.
// Passos: Espera cliques, envia fetch, processa resposta, e atualiza o usuário.

document.addEventListener('DOMContentLoaded', function() {
    
    // Elementos dos botões (igual ao seu código original).
    const btnComoGastar = document.querySelector('.jcpoints');
    const lupaBtn = document.querySelector('.lupa-btn');
    
    // URL para conectar com o Python (Flask em localhost:5000).
    const API_URL = 'http://localhost:5000/api/conectar';
    
    // Exemplo de usuario_id: Para teste, use um valor fixo. No futuro, pegue de um login ou API.
    const USUARIO_ID = 'seu_usuario_id_aqui';  // Substitua por um ID real (ex: de um campo de login).
    
    // Função para testar a conexão com Python.
    function testarConexao(acao) {
        console.log('Tentando conectar com Python para ação:', acao);  // Log para depuração.
        
        fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'  // Define o tipo de dados como JSON.
            },
            body: JSON.stringify({
                acao: acao,  // Envia a ação (ex: 'gastar').
                usuario_id: USUARIO_ID  // Nova: Envia o ID do usuário para o Python atualizar o DB.
            })
        })
        .then(response => response.json())  // Converte a resposta em objeto JSON.
        .then(data => {
            if (data.sucesso) {
                console.log('Conexão com Python OK:', data.mensagem);  // Log de sucesso.
                // Nova: Usa a mensagem e os dados retornados do Python para o alerta.
                alert(data.mensagem + ' Seus JC Points agora são: ' + data.jc_points);
                // Conceito: Isso torna o alerta dinâmico, baseado no que o back-end retornou.
            } else {
                console.log('Erro na resposta do Python:', data.mensagem);  // Log de erro.
                alert('Erro: ' + data.mensagem);  // Fallback com a mensagem do erro.
            }
        })
        .catch(error => {
            console.error('Falha na conexão com Python:', error);  // Log de erro de rede.
            alert('Sem conexão com o servidor. Tente novamente.');  // Fallback simples.
        });
    }

    // Event Listeners (mantidos, mas com a nova função).
    if (btnComoGastar) {
        btnComoGastar.addEventListener('click', function(event) {
            event.preventDefault();  // Impede o comportamento padrão.
            testarConexao('gastar');  // Chama com a ação 'gastar' e usuario_id.
        });
    }

    if (lupaBtn) {
        lupaBtn.addEventListener('click', function(event) {
            event.preventDefault();
            testarConexao('busca');  // Chama com a ação 'busca' e usuario_id.
        });
    }

    console.log('JS atualizado: Pronto para conectar com Python e banco de dados!');
});

