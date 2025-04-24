document.addEventListener('DOMContentLoaded', () => {
    const recommendationContainer = document.getElementById('recommendation-container');
    const addBtn = document.getElementById('Addrecommendation');
    const recommendationsInput = document.getElementById('recommendations_json');
    const recommendationTemplate = document.getElementById('recommendation-template');

    addBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const clone = recommendationTemplate.content.cloneNode(true);
        const select = clone.querySelector('.recommendation-type');

        // Opciones fijas (puedes cambiarlas si quieres)
        const options = ["Plomero", "Cerrajero", "Electricista", "Veterinario"];
        options.forEach(opt => {
            const optionElement = document.createElement("option");
            optionElement.value = opt;
            optionElement.textContent = opt;
            select.appendChild(optionElement);
        });

        recommendationContainer.appendChild(clone);
    });

    const form = document.querySelector('form');
    form.addEventListener('submit', () => {
        const recommendations = [];
        const cards = recommendationContainer.querySelectorAll('.card');

        cards.forEach(card => {
            const type = card.querySelector('.recommendation-type').value;
            const comment = card.querySelector('.comment').value;
            const contact = card.querySelector('.contact').value;
            const price = card.querySelector('.price').value;
            const rating = parseInt(card.querySelector('.rating').value);

            if (type && comment && contact && price && rating >= 1 && rating <= 5) {
                recommendations.push({ type, comment, contact, price, rating });
            }
        });

        recommendationsInput.value = JSON.stringify(recommendations);
    });
});
