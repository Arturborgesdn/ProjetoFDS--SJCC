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
        nome: "Novinho em Folha",
        pontos: 10,
        icone: "fa-book",
        tipo: "comum"
      },
      {
        nome: "Pegou Ar",
        pontos: 50,
        icone: "fa-fire",
        tipo: "rara"
      },
      {
        nome: "Sem leseira",
        pontos: 100,
        icone: "fa-star",
        tipo: "epica"
      },
      {
        nome: "Mil Conto",
        pontos: 80,
        icone: "fa-coins",
        tipo: "epica"
      },
      {
        nome: "Inimigo do sono",
        pontos: 100,
        icone: "fa-clock",
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
  