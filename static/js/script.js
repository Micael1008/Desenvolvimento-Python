// static/js/script.js
// Script para o carrossel de imagens

let currentSlide = 0;
const slides = document.querySelectorAll(".carousel-slide");
const dots = document.querySelectorAll(".carousel-dots .dot");

/**
 * Exibe um slide específico e atualiza os indicadores (bolinhas).
 * @param {number} index O índice do slide a ser exibido.
 */
function showSlide(index) {
    // Remove a classe 'active' de todos os slides e bolinhas
    slides.forEach((slide) => {
        slide.classList.remove("active");
    });
    dots.forEach((dot) => {
        dot.classList.remove("active");
    });

    // Calcula o índice do slide, garantindo que ele esteja dentro dos limites
    currentSlide = (index + slides.length) % slides.length;

    // Adiciona a classe 'active' ao slide e à bolinha correspondente
    slides[currentSlide].classList.add("active");
    dots[currentSlide].classList.add("active");
}

/**
 * Move o carrossel para o próximo/anterior slide.
 * @param {number} direction A direção do movimento (-1 para anterior, 1 para próximo).
 */
function moveSlide(direction) {
    showSlide(currentSlide + direction);
}

/**
 * Navega para um slide específico através das bolinhas.
 * @param {number} index O índice do slide para o qual navegar.
 */
function goToSlide(index) {
    showSlide(index);
}

// Inicializa o carrossel exibindo o primeiro slide
document.addEventListener('DOMContentLoaded', () => {
    if (slides.length > 0) {
        showSlide(currentSlide);
    }
});


// Autoplay do carrossel
// Define um intervalo para trocar o slide automaticamente a cada 5 segundos
setInterval(() => {
    moveSlide(1);
}, 5000); // troca a cada 5 segundos
