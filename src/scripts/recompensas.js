// src/scripts/recompensas.js

let saldoAtualUsuario = 0;

// Mapeamento de ícones (Reutilizável)
function getAtributosVisuais(nome, raridade = 'raro', tipo = 'beneficio') {
    const nomeLower = nome.toLowerCase();
    
    let visual = {
        classeCard: 'card-raro',
        classeTag: 'tag-raro',
        classeFundoIcone: 'fundo-raro',
        icone: 'fa-gift'
    };

    if (raridade === 'epico') {
        visual.classeCard = 'card-epico';
        visual.classeTag = 'tag-epico';
        visual.classeFundoIcone = 'fundo-epico';
    } else if (raridade === 'lendario') {
        visual.classeCard = 'card-lendario';
        visual.classeTag = 'tag-lendario';
        visual.classeFundoIcone = 'fundo-lendario';
    }

    // Lógica de Ícones
    if (tipo === 'xp' || nomeLower.includes('xp')) visual.icone = 'fa-star';
    else if (tipo === 'jc' || nomeLower.includes('jc')) visual.icone = 'fa-gem';
    else if (nomeLower.includes('antecipado')) visual.icone = 'fa-hourglass-half';
    else if (nomeLower.includes('jornalistas')) visual.icone = 'fa-microphone';
    else if (nomeLower.includes('resumo')) visual.icone = 'fa-book-reader';
    else if (nomeLower.includes('colunistas')) visual.icone = 'fa-feather-alt';
    else if (nomeLower.includes('newsletter')) visual.icone = 'fa-envelope-open-text';
    else if (nomeLower.includes('beta')) visual.icone = 'fa-flask';
    else if (nomeLower.includes('avatar')) visual.icone = 'fa-user-circle';
    else if (nomeLower.includes('moldura')) visual.icone = 'fa-crop-alt';
    else if (nomeLower.includes('selo') || nomeLower.includes('check')) {
        visual.icone = 'fa-check-circle';
        visual.classeCard = 'card-lendario';
        visual.classeTag = 'tag-lendario';
    }
    else if (nomeLower.includes('culturais') || nomeLower.includes('eventos')) visual.icone = 'fa-ticket-alt';

    return visual;
}

/**
 * Função principal para carregar TUDO (Loja + Inventário).
 */
async function carregarLojaDeRecompensas() {
    console.log("Módulo Recompensas: Iniciando...");
    const usuarioId = getUsuarioId();
    if (!usuarioId) {
        limparSessao();
        return;
    }

    const saldoElement = document.getElementById('user-jc-points-saldo');
    const lojaContainer = document.getElementById('lista-loja-container');
    const contadorOfertas = document.getElementById('contador-ofertas-ativas');

    // Loading
    if(lojaContainer) lojaContainer.innerHTML = '<p style="text-align:center; padding:20px;">Carregando ofertas...</p>';

    try {
        // --- CORREÇÃO AQUI ---
        // Antes estava: ${API_USUARIO}/${usuarioId}/recompensas
        // O correto é bater direto em /api/recompensas/ID
        const responseLoja = await fetch(`/api/recompensas/${usuarioId}`); 
        // ---------------------
        
        const resultLoja = await responseLoja.json();

        if (resultLoja.sucesso) {
            saldoAtualUsuario = resultLoja.jc_points;
            if (saldoElement) saldoElement.textContent = saldoAtualUsuario;
            if (contadorOfertas) contadorOfertas.textContent = resultLoja.itens.length;
            
            renderizarLoja(resultLoja.itens, lojaContainer);
        } else {
            // Tratamento caso a API retorne sucesso: false
             if(lojaContainer) lojaContainer.innerHTML = `<p style="text-align:center;">${resultLoja.mensagem}</p>`;
        }

        // 2. Carrega o INVENTÁRIO (Meus Itens)
        // Nota: A rota de inventário no seu código já está correta (/api/recompensas/inventario/...)
        carregarInventario(usuarioId);

    } catch (error) {
        console.error("Erro ao carregar loja:", error);
        if(lojaContainer) lojaContainer.innerHTML = '<p style="color:red; text-align:center;">Erro ao carregar a loja.</p>';
    }
}

/**
 * Busca e renderiza os itens comprados.
 */
async function carregarInventario(usuarioId) {
    const inventarioContainer = document.getElementById('lista-inventario');
    const secaoInventario = document.getElementById('secao-inventario');
    const contadorPossuidos = document.getElementById('contador-itens-possuidos');

    try {
        const response = await fetch(`/api/recompensas/inventario/${usuarioId}`);
        const result = await response.json();

        if (result.sucesso && result.inventario.length > 0) {
            // Mostra a seção e atualiza contador
            secaoInventario.style.display = 'block';
            contadorPossuidos.textContent = result.inventario.length;

            let htmlInv = '';
            result.inventario.forEach(item => {
                // Determina estilo baseado no nome (já que o DB de inventário não tem tipo/raridade salvos diretamente)
                // Uma melhoria futura seria salvar esses metadados no 'beneficios_resgatados'
                let raridadeEstimada = 'raro';
                if(item.nome_beneficio.includes('Épico') || item.nome_beneficio.includes('Beta')) raridadeEstimada = 'epico';
                if(item.nome_beneficio.includes('Lendário') || item.nome_beneficio.includes('Selo')) raridadeEstimada = 'lendario';

                const vis = getAtributosVisuais(item.nome_beneficio, raridadeEstimada);

                htmlInv += `
                    <div class="item-card ${vis.classeCard}" style="opacity: 0.9; border-style: dashed;">
                        <div class="icone-raridade ${vis.classeFundoIcone}">
                            <i class="fas ${vis.icone}"></i>
                        </div>
                        <span class="tag tag-limitado" style="background:#28a745;">ATIVO</span>
                        
                        <h3>${item.nome_beneficio}</h3>
                        <p style="font-size: 0.9em; margin-bottom: 5px;">
                            <i class="far fa-clock"></i> Expira: ${item.data_expiracao}
                        </p>
                        <p style="font-size: 0.8em; color:#777;">Resgatado em: ${item.data_resgate}</p>
                    </div>
                `;
            });
            inventarioContainer.innerHTML = htmlInv;
        } else {
            // Se não tiver itens, esconde a seção ou mostra zero
            secaoInventario.style.display = 'none';
            contadorPossuidos.textContent = '0';
        }
    } catch (error) {
        console.error("Erro ao carregar inventário:", error);
    }
}

/**
 * Renderiza a lista da loja.
 */
function renderizarLoja(itens, container) {
    let htmlItens = '<h2>Itens Disponíveis</h2>';
    
    if (itens.length === 0) {
        htmlItens += '<p>Nenhuma recompensa disponível no momento.</p>';
    } else {
        itens.forEach(item => {
            const vis = getAtributosVisuais(item.nome, item.raridade, item.tipo);
            
            const podeComprar = saldoAtualUsuario >= item.custo;
            const btnClass = podeComprar ? 'fundo-btn-laranja' : 'fundo-btn-cinza';
            const btnText = podeComprar ? 'Resgatar' : 'Faltam Pontos';
            const btnDisabled = podeComprar ? '' : 'disabled style="opacity: 0.5; cursor: not-allowed;"';

            let tipoDisplay = item.tipo === 'xp' ? 'Bônus XP' : (item.tipo === 'jc' ? 'Bônus JC' : 'Benefício');

            htmlItens += `
                <div class="item-card ${vis.classeCard}">
                    <div class="icone-raridade ${vis.classeFundoIcone}">
                        <i class="fas ${vis.icone}"></i>
                    </div>
                    
                    <span class="tag ${vis.classeTag}">${tipoDisplay}</span>
                    
                    <h3>${item.nome}</h3>
                    <p>${item.descricao}</p>
                    
                    <div class="compra-info">
                        <div class="custo">
                            <img src="assets/JC_Points_Novo.png" alt="JC" style="width: 20px; height: 20px; margin-right: 5px; vertical-align: middle;">
                            ${item.custo}
                        </div>
                        
                        <button class="btn-comprar ${btnClass}" 
                                onclick="comprarItem('${item.id}', '${item.tipo}', '${item.nivel || ''}', ${item.custo})"
                                ${btnDisabled}>
                            ${btnText}
                        </button>
                    </div>
                </div>
            `;
        });
    }
    container.innerHTML = htmlItens;
}

/**
 * Função de Compra.
 */
async function comprarItem(itemId, tipo, nivel, custo) {
    const usuarioId = getUsuarioId();
    if (!usuarioId) return;

    if (custo > saldoAtualUsuario) {
        alert("Saldo insuficiente!");
        return;
    }

    if (!confirm(`Confirmar resgate de "${itemId}" por ${custo} JC Points?`)) return;

    try {
        const response = await fetch('/api/recompensas/comprar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: usuarioId,
                item_id: itemId,
                tipo: tipo,
                nivel: nivel
            })
        });

        const result = await response.json();

        if (result.sucesso) {
            alert(result.mensagem);
            // Recarrega tudo para atualizar saldo e inventário
            carregarLojaDeRecompensas(); 
            updateHeader(); 
        } else {
            alert(result.mensagem || "Erro ao processar compra.");
        }
    } catch (error) {
        console.error(error);
        alert("Erro de conexão.");
    }
}