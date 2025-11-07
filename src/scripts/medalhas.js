// src/scripts/medalhas.js

/**
 * Função principal para carregar os dados das medalhas (a ser chamada pelo main.js).
 */
async function carregarDadosDeMedalhas() {
    console.log("Módulo Medalhas: Carregando dados...");
    
    const usuarioId = getUsuarioId(); // Pega ID de utils.js
    if (!usuarioId) {
        limparSessao(); // Se não está logado, volta para login
        return;
    }

    // Seletores dos elementos da página
    const listaMedalhasElement = document.querySelector('.card .list');
    const cardConquistadas = document.querySelector('.card-top.blue h2');
    const cardJcPointsGanhos = document.querySelector('.card-top.green h2');

    if (!listaMedalhasElement || !cardConquistadas || !cardJcPointsGanhos) {
        console.error("Erro: Elementos da UI de medalhas não encontrados.");
        return;
    }
    
    // Limpa a lista para mostrar o "loading" (opcional)
    listaMedalhasElement.innerHTML = '<p>Carregando medalhas...</p>';

    try {
        // 1. Chamar a nova API (que criamos no backend)
        const response = await fetch(`${API_USUARIO}/${usuarioId}/medalhas`);
        const result = await response.json();

        if (result.sucesso && result.medalhas) {
            
            // 2. Atualizar os Cards de Resumo (Topo)
            cardConquistadas.textContent = result.resumo.conquistadas_texto;
            cardJcPointsGanhos.textContent = result.resumo.jc_points_ganhos;
            
            // 3. Gerar o HTML da Lista (Já vem ordenada do backend)
            let htmlMedalhas = '';
            
            result.medalhas.forEach(medalha => {
                // Define as classes CSS com base no status (concluida ou pendente)
                const classeStatus = medalha.is_complete ? 'concluida' : 'pendente';
                const raridadeClass = medalha.raridade; // 'comum', 'rara', 'epica'
                
                // Gera o HTML para este <li>
                htmlMedalhas += `
                    <li class="medalha ${classeStatus} ${raridadeClass}" data-nome="${medalha.nome}">
                        <div class="icon"><i class="fas ${medalha.icone}"></i></div>
                        
                        <div class="info">
                            <div class="title-row">
                                <h3>${medalha.nome}</h3>
                            </div>
                            <p>${medalha.descricao}</p>
                            <div class="subinfo">
                                <span class="date"><i class="fas fa-calendar-alt"></i> Conquistada</span>
                                <span class="status">Em andamento</span>
                            </div>
                        </div>
                        
                        <div class="points">
                            <span>⭐ +${medalha.jc_points} JC Points</span>
                        </div>
                    </li>
                `;
            });

            // 4. Inserir o HTML na página
            listaMedalhasElement.innerHTML = htmlMedalhas;
            console.log("Módulo Medalhas: Dados carregados e renderizados.");

        } else {
            throw new Error(result.mensagem || "Resposta da API inválida.");
        }

    } catch (error) {
        console.error("Erro ao carregar dados das medalhas:", error);
        listaMedalhasElement.innerHTML = '<p style="color: red;">Erro ao carregar medalhas.</p>';
    }
}