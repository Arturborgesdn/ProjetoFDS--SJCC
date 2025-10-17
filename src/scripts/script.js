
// Espera o DOM carregar .
document.addEventListener('DOMContentLoaded', function() {
    
    // Elementos dos botões .
    const btnComoGastar = document.querySelector('.jcpoints');
    const lupaBtn = document.querySelector('.lupa-btn');
    
    // URL para conectar com o Python (Flask em localhost:5000).
    const API_URL = 'http://localhost:5000/api/conectar';
    
    // Testa a conexão com Python (fetch).
    // Envia POST para o Python, espera resposta, depois mostra alerta.
    function testarConexao(acao) {
        // Log para debug: Confirma que a função rodou.
        console.log('Tentando conectar com Python para ação:', acao);
        
        fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                acao: acao  // Envia o tipo de ação (ex: 'gastar').
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                // Sucesso: Log no console e mostra alerta normal.
                console.log('Conexão com Python OK:', data.mensagem);
                alertOriginal(acao);  // Chama o alerta antigo.
            } else {
                // Erro raro no Python.
                console.log('Erro na resposta do Python:', data.mensagem);
                alertOriginal(acao);  // Fallback para alerta.
            }
        })
        .catch(error => {
            // Erro de conexão (ex: Python off): Log e fallback.
            console.error('Falha na conexão com Python:', error);
            alertOriginal(acao);  // Mostra alerta mesmo assim.
        });
    }
    
    // Função para Alertas Originais.
    function alertOriginal(acao) {
        if (acao === 'gastar') {
            alert('Calma! jaja incluiremos essa pagina no MVP');
        } else if (acao === 'busca') {
            alert('Ainda estamos implementando isso espera mais um pouco');
        }
    }

    // Event Listeners.
    if (btnComoGastar) {
        btnComoGastar.addEventListener('click', function(event) {
            event.preventDefault();
            // Chama a conexão em vez de alert direto.
            testarConexao('gastar');
        });
    }

    if (lupaBtn) {
        lupaBtn.addEventListener('click', function(event) {
            event.preventDefault();
            // Chama a conexão.
            testarConexao('busca');
        });
    }

    // Console Log para confirmar que o código atualizado carregou.
    console.log('JS atualizado: Pronto para conectar com Python!');
});

