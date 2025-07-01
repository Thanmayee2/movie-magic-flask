document.addEventListener('DOMContentLoaded', () => {
    const seats = document.querySelectorAll('.seat');
    const input = document.querySelector('input[name="seat"]');

    seats.forEach(seat => {
        seat.addEventListener('click', () => {
            // Deselect any previously selected seat
            document.querySelectorAll('.seat.selected').forEach(s => s.classList.remove('selected'));

            // Add selected class to clicked seat
            seat.classList.add('selected');

            // Trigger a fun animation
            seat.animate(
                [
                    { transform: 'scale(1.4)' },
                    { transform: 'scale(1.0)' }
                ],
                {
                    duration: 150,
                    easing: 'ease-out'
                }
            );

            // Set hidden input value if it exists
            if (input) {
                input.value = seat.dataset.seat;
            }
        });
    });
});
let currentSlide = 0;
const slides = document.querySelectorAll(".slide");

function showSlide(index) {
    slides.forEach((slide, i) => {
        slide.classList.toggle("active", i === index);
    });
}

function moveSlide(step) {
    currentSlide = (currentSlide + step + slides.length) % slides.length;
    showSlide(currentSlide);
}

setInterval(() => moveSlide(1), 5000); // Auto-slide every 5s
// Load confetti only once DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const bookBtn = document.querySelector('.btn');

    if (bookBtn) {
        bookBtn.addEventListener('click', (e) => {
            // Fire confetti at button
            const rect = bookBtn.getBoundingClientRect();
            confetti({
                particleCount: 80,
                spread: 70,
                origin: {
                    x: (rect.left + rect.width / 2) / window.innerWidth,
                    y: (rect.top + rect.height / 2) / window.innerHeight
                }
            });
        });
    }
});