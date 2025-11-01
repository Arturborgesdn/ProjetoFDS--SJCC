//deixei esse para fazer os checks de missoes
document.addEventListener("DOMContentLoaded", () => {
    // Cria o container para os alertas (caso não exista)
    let toastContainer = document.querySelector(".toast-container");
    if (!toastContainer) {
      toastContainer = document.createElement("div");
      toastContainer.classList.add("toast-container");
      document.body.appendChild(toastContainer);
    }
  
    // Lista de conquistas simuladas
    const conquistas = [
      {
        nome: "Leitura massa",
        pontos: 10,
        icone: "fa-book-open",
        tipo: "comum"
      },
      {
        nome: "Fica de olho, visse?",
        pontos: 20,
        icone: "fa-fire",
        tipo: "rara"
      },
      {
        nome: "Noticia bunitinha",
        pontos: 10,
        icone: "fa-calendar",
        tipo: "epica"
      },
      {
        nome: "Compartilha ai, na moral",
        pontos: 75,
        icone: "fa-share-alt",
        tipo: "epica"
      },
      {
        nome: "Destaque massa",
        pontos: 20,
        icone: "fa-star",
        tipo: "epica"
      }
    ];
  
    // Função para exibir um alerta
    function mostrarAlerta(conquista) {
      const toast = document.createElement("div");
      toast.classList.add("toast");
  
      toast.innerHTML = `
        <i class="fas ${conquista.icone}"></i>
        <div class="toast-content">
          <strong>${conquista.nome}</strong>
          <span>⭐ +${conquista.pontos} JC Points</span>
        </div>
      `;
  
      toastContainer.appendChild(toast);
  
      // Remove o alerta depois de 4 segundos
      setTimeout(() => {
        toast.classList.add("hide");
        setTimeout(() => toast.remove(), 400);
      }, 4000);
    }
  
    // Simula conquistas automáticas (1 a cada 3 segundos)
    let index = 0;
    const intervalo = setInterval(() => {
      if (index < conquistas.length) {
        mostrarAlerta(conquistas[index]);
        index++;
      } else {
        clearInterval(intervalo);
      }
    }, 2000);
  });