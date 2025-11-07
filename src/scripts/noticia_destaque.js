// ============================================
// Módulo: Notícia DESTAQUE (Lógica para noticia_destaque.html)
//
// Esta é uma cópia de noticia.js, mas chama a API /ler_noticia_destaque
// para ativar a missão "Destaque massa".
// ============================================

// --- T1UH15: LÓGICA DE COMPARTILHAR ---
// (Esta função é idêntica à de noticia.js)
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
                
                // --- SUBSTITUIR ALERTA AQUI ---
                if (result.novas_missoes_diarias && result.novas_missoes_diarias.length > 0) {
                    result.novas_missoes_diarias.forEach(missao => {
                        mostrarAlertaFeedback(missao, 'missao'); // <-- CORRIGIDO
                    });
                } else {
                    // alert("Obrigado por compartilhar!"); // (Removido - ou pode criar um toast de "info")
                }
                if (result.novas_medalhas && result.novas_medalhas.length > 0) {
                    result.novas_medalhas.forEach(m => {
                        // Padroniza o objeto que vem do backend
                        const medalhaObj = { nome: m.medalha, jc_points: m.jc_points };
                        mostrarAlertaFeedback(medalhaObj, 'medalha');
                    });
                }
                // --- FIM DA SUBSTITUIÇÃO ---
                updateHeader(); 
            } else {
                throw new Error(result.mensagem || "Erro ao registrar compartilhamento.");
            }
        } catch (error) {
            console.error("Falha na API de compartilhamento:", error);
            alert("Ocorreu um erro ao tentar compartilhar. Tente novamente.");
        }
    });
}

// --- T1UH14 / T2UH09: LÓGICA DE VERIFICAÇÃO DE LEITURA (DESTAQUE) ---
const TEMPO_MINIMO = 60000; // 60 segundos
let tempoLido = 0;
let atingiuTempo = false;
let atingiuScroll = false;
let leituraConcluida = false;
let barraLeitura = null;

async function apiNoticiaDestaqueLida() { // <--- NOME DA FUNÇÃO MUDADO
    const usuarioId = getUsuarioId();
    if (!usuarioId) {
        console.warn("Leitura concluída (destaque), mas usuário não logado.");
        return;
    }
    console.log("Verificação de leitura DESTAQUE completa. Enviando para API...");

    try {
        // --- ALTERAÇÃO CRÍTICA AQUI ---
        // Chama a nova rota da API
        const response = await fetch(`${API_USUARIO}/${usuarioId}/ler_noticia_destaque`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        // --- FIM DA ALTERAÇÃO ---

        const result = await response.json();
        if (result.sucesso) {
            const xpGanho = 25; // XP base pela leitura
            mostrarParabens(xpGanho); 
            updateHeader();

            // Alerta sobre novas medalhas
            if (result.novas_medalhas && result.novas_medalhas.length > 0) {
                result.novas_medalhas.forEach(m => {
                    // Padronizando o objeto que o backend envia (m.medalha)
                    const medalhaObj = { nome: m.medalha, jc_points: m.jc_points };
                    mostrarAlertaFeedback(medalhaObj, 'medalha'); // <--- MUDANÇA AQUI
                });
            }
            // Alerta sobre novas missões (incluindo "Destaque massa")
            if (result.novas_missoes_diarias && result.novas_missoes_diarias.length > 0) {
                 result.novas_missoes_diarias.forEach(missao => {
                 mostrarAlertaFeedback(missao, 'missao');             
            });
            }
        } else {
            throw new Error(result.mensagem || "Erro ao registrar leitura de destaque.");
        }
    } catch (error) {
        console.error("Falha na API de ler_noticia_destaque:", error);
    }
}

function verificarConclusaoLeituraDestaque() { // <--- NOME DA FUNÇÃO MUDADO
    if (atingiuTempo && atingiuScroll && !leituraConcluida) {
        leituraConcluida = true;
        clearInterval(cronometroLeitura);
        
        if (barraLeitura) {
            barraLeitura.style.width = "100%";
            barraLeitura.classList.add("completo");
            setTimeout(() => { barraLeitura.style.opacity = 0; }, 1200);
        }
        
        apiNoticiaDestaqueLida(); // <--- CHAMA A FUNÇÃO DE DESTAQUE
    }
}

// ... (Copie as funções criarBarraProgresso, atualizarBarraScroll, mostrarAvisoMissao, e mostrarParabens
//      exatamente como estão em 'noticia.js') ...

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
    }
}

function mostrarAvisoMissao(xp) {
    const aviso = document.createElement("div");
    aviso.classList.add("card-missao");
    aviso.innerHTML = `
        <div class="icone-missao"><i class="fas fa-star"></i></div>
        <div class="conteudo-missao">
            <strong>Missão Destaque!</strong>
            <p>Leia até o fim para ganhar <span>+${xp} XP</span> e bônus!</p>
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
    const aviso = document.querySelector('.card-parabens');
    if (!aviso) return;
    const xpSpan = aviso.querySelector('.conteudo-parabens span');
    if (xpSpan) xpSpan.textContent = `+${xp} XP`;
    aviso.style.display = 'flex';
    aviso.classList.add("mostrar");
}

// --- INICIALIZAÇÃO DA PÁGINA DE NOTÍCIA DE DESTAQUE ---

//setupShareButton();
criarBarraProgresso();
mostrarAvisoMissao(100); // Mostra o aviso (100XP é da missão)
window.addEventListener("scroll", atualizarBarraScroll);

const cronometroLeitura = setInterval(() => {
    tempoLido += 1000;
    if (tempoLido >= TEMPO_MINIMO) {
        atingiuTempo = true;
        verificarConclusaoLeituraDestaque(); // <--- CHAMA A FUNÇÃO DE DESTAQUE
        clearInterval(cronometroLeitura);
    }
}, 1000);