const wrapper = document.querySelector(".carrossel-wrapper");
const dotsContainer = document.querySelector(".carrossel-dots");
const cards = document.querySelectorAll(".carrossel-card");

let index = 0;

// Criar dots
cards.forEach((c, i) => {
  const dot = document.createElement("div");
  if (i === 0) dot.classList.add("active");
  dotsContainer.appendChild(dot);
});

const dots = document.querySelectorAll(".carrossel-dots div");

// Atualizar dots
function updateDots(pos) {
  dots.forEach((d, i) => d.classList.toggle("active", i === pos));
}

document.querySelector(".carrossel-btn-right").addEventListener("click", () => {
  index = Math.min(index + 1, cards.length - 1);
  wrapper.scrollTo({ left: cards[index].offsetLeft - 10, behavior: "smooth" });
  updateDots(index);
});

document.querySelector(".carrossel-btn-left").addEventListener("click", () => {
  index = Math.max(index - 1, 0);
  wrapper.scrollTo({ left: cards[index].offsetLeft - 10, behavior: "smooth" });
  updateDots(index);
});

// Captura scroll manual
wrapper.addEventListener("scroll", () => {
  let closest = 0;
  let minDist = Infinity;
  cards.forEach((card, i) => {
    const dist = Math.abs(card.offsetLeft - wrapper.scrollLeft);
    if (dist < minDist) {
      minDist = dist;
      closest = i;
    }
  });
  index = closest;
  updateDots(index);
});