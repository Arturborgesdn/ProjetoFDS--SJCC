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
    let tempoOnlineIntervalId = null; 

    function iniciarContadorTempoOnline() {
        const usuarioId = getUsuarioId(); // Pega o ID (de utils.js)
        if (!usuarioId) {
            console.log("Utilizador não logado. Timer de tempo online desativado.");
            return; 
        }

        if (tempoOnlineIntervalId) clearInterval(tempoOnlineIntervalId); // Limpa timer anterior

        console.log("Iniciando timer 'Fica de olho, visse?' (1 ping/minuto)...");

        // Envia o primeiro ping imediatamente para registrar o início da sessão
        enviarPingTempo(usuarioId); 

        // Configura o envio periódico a cada 60 segundos
        tempoOnlineIntervalId = setInterval(() => {
            enviarPingTempo(usuarioId);
        }, 60000); // 60 segundos
    }

    async function enviarPingTempo(usuarioId) {
         try {
            // Chama a rota /ping_tempo
            const response = await fetch(`${API_USUARIO}/${usuarioId}/ping_tempo`, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' } 
            });
            const result = await response.json();

            if (result.sucesso) {
                console.log(`Ping tempo OK. Minutos hoje: ${result.tempo_hoje_minutos}.`);
                // Verifica se a missão "Fica de olho" (ou outra) foi completada
                if (result.novas_missoes_diarias && result.novas_missoes_diarias.length > 0) {
                    result.novas_missoes_diarias.forEach(missao => {
                        console.log(`🎉 Missão Diária Completada: ${missao.nome}! Recompensas: +${missao.xp} XP, +${missao.jc_points} JC Points`);
                        // Aqui você chamaria uma função para mostrar um alerta/toast visualmente
                        alert(`🎉 Missão Diária Completada: ${missao.nome}! +${missao.xp} XP, +${missao.jc_points} JC Points`); 
                    });
                }
            } else {
                console.error("Erro retornado pela API de ping:", result.mensagem);
            }
        } catch (error) {
            console.error("Falha de rede ao enviar ping de tempo:", error);
        }
    }
    // --- FIM DO NOVO CÓDIGO ---

    // --- CHAMADA PARA INICIAR O CONTADOR ---
    iniciarContadorTempoOnline(); // Inicia o timer assim que o DOM carrega
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