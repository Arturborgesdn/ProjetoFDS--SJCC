// src/scripts/script.js (Updated for new programa_Fidelidade.html)

document.addEventListener('DOMContentLoaded', function() {

    // --- Seleção de Elementos ---
    const formCadastro = document.querySelector('#formCadastro'); // For cadastro.html
    const formLogin = document.querySelector('#formLogin'); // For login.html
    
    // Elementos da página de Fidelidade (Use selectors from the new HTML)
    const profileCard = document.querySelector('.card.profile'); 
    const profileImages = document.querySelectorAll('.profile-img'); // Selects both header and card image
    const profileName = document.querySelector('.card.profile h2');
    const profileCategory = document.querySelector('.card.profile .titulo');
    const xpBarFill = document.querySelector('.card.profile .xp-bar .fill');
    const xpBarText = document.querySelector('.card.profile .container-xp-logo p');
    const xpBarEmblems = document.querySelectorAll('.card.profile .xp-bar .emblema_Barra img'); // Selects both images in the bar
    const jcPointsValue = document.querySelector('.cardjc .container-jc h2'); // Updated selector
    const headerEmblem = document.querySelector('.header-right .level-circle'); // Emblem next to profile pic in header

    // Botões for MVP alerts (if needed, otherwise remove)
    // Note: The cards are now links. If you want actions on specific elements inside, select them here.
    const lupaBtn = document.querySelector('.lupa-btn'); 

    // --- URLs da API ---
    const API_REGISTRAR = '/api/registrar';
    const API_LOGIN = '/api/login';
    const API_USUARIO = '/api/usuario'; 

    // --- Lógica de Memória (Sessão) ---
    function salvarSessao(usuarioId) { localStorage.setItem('usuario_id_sjcc', usuarioId); }
    function getUsuarioId() { return localStorage.getItem('usuario_id_sjcc'); }
    function limparSessao() { localStorage.removeItem('usuario_id_sjcc'); } 

    // --- Funções de Login/Registo (Keep your existing functions here) ---
    function cadastrarUsuario() {
        // Your existing cadastrarUsuario function code...
         const dados = {
            nome: document.querySelector('#nome').value,
            data_nascimento: document.querySelector('#data').value, // Formato DD/MM/YYYY
            email: document.querySelector('#email').value,
            senha: document.querySelector('#senha').value
        };
        fetch(API_REGISTRAR, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                // Keep alert for registration feedback or change as needed
                alert(data.mensagem); 
                window.location.href = '/login.html';
            } else {
                alert('Erro: ' + data.mensagem); 
            }
        }).catch(error => alert('Erro no registo: ' + error)); 
    }
    
    function fazerLogin() {
        // Your existing fazerLogin function code...
        const dados = {
            email: document.querySelector('#login-email').value,
            senha: document.querySelector('#login-senha').value
        };
        fetch(API_LOGIN, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                console.log(data.mensagem); // Log success instead of alert
                salvarSessao(data.usuario_id); 
                window.location.href = '/programa_Fidelidade.html';  
            } else {
                console.error('Erro de login (API): ' + data.mensagem); 
            }
        }).catch(error => {
            console.error('Erro na requisição de login (fetch):', error); 
        });
    }

    // --- FUNÇÃO PARA CARREGAR E MOSTRAR DADOS NA PÁGINA DE FIDELIDADE ---
    async function carregarDadosDeFidelidade() {
        const usuarioId = getUsuarioId(); 
        if (!usuarioId) {
            console.error("ID do utilizador não encontrado. Redirecionando para login.");
            window.location.href = '/login.html'; 
            return; 
        }
        console.log(`Buscando dados para o utilizador ID: ${usuarioId}`);
        try {
            const response = await fetch(`${API_USUARIO}/${usuarioId}`); 
            const result = await response.json();

            if (result.sucesso && result.dados) {
                const dados = result.dados; 
                console.log("Dados recebidos:", dados);
                
                // --- ATUALIZA O HTML ---
                if (profileName) profileName.textContent = dados.nome;
                if (profileCategory) profileCategory.textContent = dados.categoria; // Use categoria name from API
                if (xpBarFill) xpBarFill.style.width = `${dados.progresso_percentual}%`;
                if (xpBarText) xpBarText.textContent = `${dados.progresso_xp_texto} `; 
                if (jcPointsValue) jcPointsValue.textContent = dados.jc_points; // Update points

                // Update profile images (example, assumes a generic image for now)
                profileImages.forEach(img => img.src = '/assets/unnamed.png'); // Update with actual user image if available

                // Update XP bar emblems (Needs logic based on categoria/medalha)
                // Example: Determine image names based on 'dados.categoria' and 'dados.medalha'
                // For now, setting generic alt text
                if (xpBarEmblems.length >= 2) {
                    xpBarEmblems[0].alt = `${dados.categoria} ${dados.medalha}`;
                    xpBarEmblems[1].alt = `Próximo Nível`; 
                    // To change the image source dynamically:
                    // xpBarEmblems[0].src = `/assets/${dados.categoria}_${dados.medalha}.png`; // Adjust naming convention
                    // xpBarEmblems[1].src = `/assets/NextLevelEmblem.png`; // Placeholder for next level
                }

                // Update header emblem (Needs logic based on categoria/medalha)
                if (headerEmblem) {
                    headerEmblem.alt = `${dados.categoria} ${dados.medalha}`;
                    // To change the image source dynamically:
                    // headerEmblem.src = `/assets/${dados.categoria}_${dados.medalha}-removebg-preview.png`; // Adjust naming
                }

                console.log("Página de fidelidade atualizada!");

            } else {
                throw new Error(result.mensagem || "Resposta da API inválida ao buscar dados do utilizador");
            }
        } catch (error) {
            console.error("Erro CRÍTICO ao carregar/processar dados de fidelidade:", error);
            alert("Ocorreu um erro inesperado ao carregar os seus dados. Por favor, tente fazer o login novamente.");
            limparSessao();
            window.location.href = '/login.html';
        }
    }

    // --- LÓGICA DE ROTEAMENTO E EVENT LISTENERS ---
    
    // Identifica em qual página estamos e o que fazer
    if (formCadastro) {
        formCadastro.addEventListener('submit', function(event) {
            event.preventDefault();
            cadastrarUsuario(); 
        });
        console.log("Página de Registo pronta.");

    } else if (formLogin) {
        formLogin.addEventListener('submit', function(event) {
            event.preventDefault();
            fazerLogin(); 
        });
        console.log("Página de Login pronta.");

    } else if (profileCard) { // Check if the main profile card exists to know we are on the fidelity page
        carregarDadosDeFidelidade(); // Chama a função para buscar e mostrar os dados!
        
        // Remove alert placeholders - Clicks on card links will navigate
        if (lupaBtn) {
            lupaBtn.addEventListener('click', function(event) {
                event.preventDefault(); 
                console.log("Botão 'Busca' clicado - Nenhuma ação definida (MVP).");
                // alert('A funcionalidade de busca ainda será implementada. Aguarde!'); // Placeholder if needed
            });
        }
        console.log("Página de Fidelidade pronta.");
        
    } else {
        console.log("Script.js carregado numa página não reconhecida.");
    }

    // Add Logout functionality if needed (requires a logout button in HTML)
    const logoutButton = document.getElementById('logout-btn'); 
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            limparSessao();
            window.location.href = '/login.html';
        });
    }
});