// src/scripts/main.js
// Ponto de entrada do Frontend. Gerencia o roteamento de scripts para cada página.

document.addEventListener('DOMContentLoaded', function() {
    
    updateHeader(); // Chama a função de atualização do header (de utils.js)
    
    // --- Seleção de Elementos de Roteamento ---
    const formCadastro = document.querySelector('#formCadastro'); 
    const formLogin = document.querySelector('#formLogin');       
    const profileCard = document.querySelector('.card.profile'); 
    const medalhasSection = document.querySelector('#titulo-pagina-medalhas');
    const missoesSection = document.querySelector('#titulo-pagina-missoes');
    const cardParabens = document.querySelector('.card-parabens'); 
    
    
    // Elementos globais
    const lupaBtn = document.querySelector('.lupa-btn');
    const logoutButton = document.getElementById('logout-btn');
    let tempoOnlineIntervalId = null; 

    // --- LÓGICA DO TIMER "Fica de olho, visse?" ---

    function iniciarContadorTempoOnline() {
        const usuarioId = getUsuarioId(); // Pega o ID (de utils.js)
        if (!usuarioId) {
            console.log("Utilizador não logado. Timer de tempo online desativado.");
            return; 
        }

        if (tempoOnlineIntervalId) clearInterval(tempoOnlineIntervalId); 

        console.log("Iniciando timer 'Fica de olho, visse?' (1 ping/minuto)...");

        // Envia o primeiro ping imediatamente
        enviarPingTempo(usuarioId); 

        // Configura o envio periódico a cada 60 segundos
        tempoOnlineIntervalId = setInterval(() => {
            enviarPingTempo(usuarioId);
        }, 60000); // 60 segundos
    }

    async function enviarPingTempo(usuarioId) {
         try {
            const response = await fetch(`${API_USUARIO}/${usuarioId}/ping_tempo`, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' } 
            });

            // --- CORREÇÃO DE BUG CRÍTICO ---
            // Se a sessão for inválida (Utilizador Não Encontrado), o ping falhará.
            if (response.status === 404 || response.status === 401) {
                console.error("Erro de Ping: Sessão inválida (404/401). Forçando logout.");
                clearInterval(tempoOnlineIntervalId); // 1. Para o timer
                limparSessao(); // 2. Força o logout e redireciona (de utils.js)
                return; // 3. Para a execução desta função
            }
            // --- FIM DA CORREÇÃO ---

            const result = await response.json();

            if (result.sucesso) {
                console.log(`Ping tempo OK. Minutos hoje: ${result.tempo_hoje_minutos}.`);
                // Verifica se a missão foi completada
                if (result.novas_missoes_diarias && result.novas_missoes_diarias.length > 0) {
                    result.novas_missoes_diarias.forEach(missao => {
                        console.log(`🎉 Missão Diária Completada: ${missao.nome}! Recompensas: +${missao.xp} XP, +${missao.jc_points} JC Points`);
                        mostrarAlertaFeedback(missao, 'missao');
                    });
                }
                if (result.novas_medalhas && result.novas_medalhas.length > 0) {
                    result.novas_medalhas.forEach(m => {
                        // Padroniza o objeto que vem do backend
                        const medalhaObj = { nome: m.medalha, jc_points: m.jc_points };
                        mostrarAlertaFeedback(medalhaObj, 'medalha');
                    });
                }
            } else {
                console.error("Erro retornado pela API de ping (Sucesso=false):", result.mensagem);
                clearInterval(tempoOnlineIntervalId); // Para o timer se a API der erro
            }
        } catch (error) {
            console.error("Falha de rede ao enviar ping de tempo:", error);
            clearInterval(tempoOnlineIntervalId); // Para o timer se a rede cair
        }
    }

    // --- CHAMADA PARA INICIAR O CONTADOR ---
    iniciarContadorTempoOnline(); // Inicia o timer assim que o DOM carrega
    
    // --- LÓGICA DE ROTEAMENTO PRINCIPAL ---
    // (Esta parte identifica qual página está ativa e chama o script correto)

    if (formCadastro) {
        formCadastro.addEventListener('submit', function(event) {
            event.preventDefault();
            cadastrarUsuario(); 
        });
        console.log("Módulo: Registo. Event Listener ativado.");

    } else if (formLogin) {
        formLogin.addEventListener('submit', function(event) {
            event.preventDefault();
            fazerLogin(); 
        });
        console.log("Módulo: Login. Event Listener ativado.");

    } else if (profileCard) { 
        carregarDadosDeFidelidade(); 
        console.log("Módulo: Fidelidade. Carregamento de dados iniciado.");
    
    } else if (medalhasSection) {
         carregarDadosDeMedalhas(); 
        console.log("Módulo: Medalhas. Carregamento de dados será iniciado.");
    
    } else if (missoesSection) { 
        carregarDadosDeMissoes();
        console.log("Módulo: Missões. Carregamento de dados iniciado.");

    } else if (cardParabens) { // <-- ADICIONE ESTE BLOCO
        // Estamos em uma página de notícia (comum ou destaque)
        setupShareButton();
        console.log("Módulo: Notícia. Botão de compartilhar ativado.");
    }
    
    // --- LÓGICA GLOBAL (Eventos Comuns) ---

    if (lupaBtn) {
        lupaBtn.addEventListener('click', function(event) {
            event.preventDefault();
            alert('A funcionalidade de busca ainda será implementada. Aguarde!'); 
        });
    }

    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            limparSessao(); 
        });
    }

    console.log("main.js carregado. Roteamento concluído.");
});