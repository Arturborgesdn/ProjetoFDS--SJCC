// ============================================
// Módulo: Notícia (Lógica para noticia.html)
//
// Responsabilidades:
// 1. Lidar com o clique no botão "Compartilhar". (T1UH15)
// 2. Lidar com a detecção de rolagem/tempo para ganho de XP. (T1UH14)
//
// Depende de: utils.js (para getUsuarioId, API_USUARIO, updateHeader)
// ============================================

// --- T1UH15: LÓGICA DE COMPARTILHAR ---

/**
 * Configura o event listener para o botão de compartilhar.
 */
function setupShareButton() {
    const shareButton = document.querySelector('#share-button'); 
    if (!shareButton) {
        console.warn("Botão de compartilhar (#share-button) não encontrado.");
        return;
    }

    shareButton.addEventListener('click', async () => {
        console.log("Botão de compartilhar clicado!");
        const usuarioId = getUsuarioId();
        if (!usuarioId) {
            alert("Você precisa estar logado para compartilhar e ganhar recompensas!");
            window.location.href = '/login.html';
            return;
        }

        try {
            const response = await fetch(`${API_USUARIO}/${usuarioId}/share`, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();

            if (result.sucesso) {
                console.log(`Compartilhamento registrado. Total hoje: ${result.compartilhamentos_hoje}`);
                if (result.novas_missoes_diarias && result.novas_missoes_diarias.length > 0) {
                    result.novas_missoes_diarias.forEach(missao => {
                        alert(`🎉 Missão Diária Completada: ${missao.nome}!\n+${missao.xp} XP, +${missao.jc_points} JC Points`);
                    });
                } else {
                    alert("Obrigado por compartilhar!");
                }
                updateHeader(); // Atualiza o header (XP/JC)
            } else {
                throw new Error(result.mensagem || "Erro ao registrar compartilhamento.");
            }
        } catch (error) {
            console.error("Falha na API de compartilhamento:", error);
            alert("Ocorreu um erro ao tentar compartilhar. Tente novamente.");
        }
    });
}


// --- T1UH14: LÓGICA DE VERIFICAÇÃO DE LEITURA ---

// Constantes da lógica do seu parceiro
const TEMPO_MINIMO = 60000; // 60 segundos
let tempoLido = 0;
let atingiuTempo = false;
let atingiuScroll = false;
let leituraConcluida = false; // Trava para não chamar a API múltiplas vezes
let barraLeitura = null;

/**
 * Função principal que chama a API de leitura no back-end.
 */
async function apiNoticiaLida() {
    const usuarioId = getUsuarioId();
    if (!usuarioId) {
        console.warn("Leitura concluída, mas usuário não logado.");
        return;
    }

    console.log("Verificação de leitura completa. Enviando para API...");

    try {
        const response = await fetch(`${API_USUARIO}/${usuarioId}/ler_noticia`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const result = await response.json();

        if (result.sucesso) {
            // Sucesso! Mostra o pop-up de parabéns com o XP real ganho (do back-end)
            const xpGanho = result.xp_atual - (window.xpInicialUsuario || result.xp_atual); // Calcula o XP ganho
            mostrarParabens(xpGanho || 25); // Mostra 25 se for o primeiro acesso

            // Atualiza o header (utils.js) para refletir novo XP/JC
            updateHeader();

            // Alerta sobre novas medalhas
            if (result.novas_medalhas && result.novas_medalhas.length > 0) {
                result.novas_medalhas.forEach(m => {
                    alert(`🏅 Medalha Conquistada: ${m.medalha}!\n+${m.jc_points} JC Points!`);
                });
            }
            // Alerta sobre novas missões
            if (result.novas_missoes_diarias && result.novas_missoes_diarias.length > 0) {
                 result.novas_missoes_diarias.forEach(missao => {
                    alert(`🎉 Missão Diária Completada: ${missao.nome}!\n+${missao.xp} XP, +${missao.jc_points} JC Points`);
                });
            }

        } else {
            throw new Error(result.mensagem || "Erro ao registrar leitura.");
        }
    } catch (error) {
        console.error("Falha na API de ler_noticia:", error);
        // Não mostra alerta de erro para o usuário, para não poluir
    }
}

/**
 * Função de verificação (do seu parceiro), agora integrada com a API.
 */
function verificarConclusaoLeitura() {
    if (atingiuTempo && atingiuScroll && !leituraConcluida) {
        leituraConcluida = true; // Trava
        clearInterval(cronometroLeitura); // Para o timer
        
        // Animação da barra
        if (barraLeitura) {
            barraLeitura.style.width = "100%";
            barraLeitura.classList.add("completo");
            setTimeout(() => { barraLeitura.style.opacity = 0; }, 1200);
        }
        
        // CHAMA A API DO BACK-END
        apiNoticiaLida();
    }
}

// --- Funções de UI (Pop-ups e Barra) ---

function criarBarraProgresso() {
    barraLeitura = document.createElement("div");
    barraLeitura.classList.add("barra-leitura");
    document.body.appendChild(barraLeitura);
}

function atualizarBarraScroll() {
    if (!barraLeitura || leituraConcluida) return;

    const posicao = window.scrollY + window.innerHeight;
    const altura = document.documentElement.scrollHeight;
    const progresso = Math.min((posicao / altura) * 100, 100);

    barraLeitura.style.width = progresso + "%";

    if (progresso < 50) barraLeitura.style.backgroundColor = "#ffc107";
    else if (progresso < 80) barraLeitura.style.backgroundColor = "#fd7e14";
    else barraLeitura.style.backgroundColor = "#28a745";

    if (posicao >= altura * 0.95) {
        atingiuScroll = true;
        verificarConclusaoLeitura();
    }
}

function mostrarAvisoMissao(xp) {
    const aviso = document.createElement("div");
    aviso.classList.add("card-missao");
    aviso.innerHTML = `
        <div class="icone-missao"><i class="fas fa-hourglass-half"></i></div>
        <div class="conteudo-missao">
            <strong>Missão iniciada!</strong>
            <p>Leia até o fim para ganhar <span>+${xp} XP</span></p>
        </div>`;
    document.body.appendChild(aviso);
    aviso.classList.add("mostrar");
    setTimeout(() => {
        aviso.classList.remove("mostrar");
        aviso.classList.add("ocultar");
        setTimeout(() => aviso.remove(), 500);
    }, 4000);
}

function mostrarParabens(xp) {
    // Busca o card que já existe no HTML da notícia
    const aviso = document.querySelector('.card-parabens');
    if (!aviso) {
        console.warn("Card de Parabéns não encontrado no HTML.");
        // Se não encontrar o card (ex: HTML antigo), cria um dinâmico
        const avisoDinamico = document.createElement("div");
        avisoDinamico.classList.add("card-parabens-dinamico"); // Usar um estilo diferente se necessário
        avisoDinamico.innerHTML = `<strong>Parabéns!</strong> +${xp} XP pela leitura!`;
        document.body.appendChild(avisoDinamico);
        setTimeout(() => avisoDinamico.remove(), 5000);
        return;
    }

    // Atualiza o XP no card do HTML
    const xpSpan = aviso.querySelector('.conteudo-parabens span');
    if (xpSpan) xpSpan.textContent = `+${xp} XP`;
    
    // Mostra o card (que estava escondido)
    aviso.style.display = 'flex';
    aviso.classList.add("mostrar"); // Adiciona classe para animação
}

// --- INICIALIZAÇÃO DA PÁGINA DE NOTÍCIA ---

// Pega o XP inicial para calcular o ganho depois (opcional, mas legal)
// window.xpInicialUsuario = 0;
// if (getUsuarioId()) {
//     fetch(`${API_USUARIO}/${getUsuarioId()}`)
//         .then(res => res.json())
//         .then(data => { if(data.sucesso) window.xpInicialUsuario = data.dados.xps; });
// }

// 1. Configura o botão de compartilhar
setupShareButton();

// 2. Configura a verificação de leitura (T1UH14)
criarBarraProgresso();
mostrarAvisoMissao(25); // Mostra o aviso (o XP é 25, definido na API)
window.addEventListener("scroll", atualizarBarraScroll);

// 3. Inicia o timer de leitura
const cronometroLeitura = setInterval(() => {
    tempoLido += 1000;
    if (tempoLido >= TEMPO_MINIMO) {
        atingiuTempo = true;
        verificarConclusaoLeitura();
        clearInterval(cronometroLeitura); // Para o timer
    }
}, 1000);