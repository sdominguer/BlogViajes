// static/js/map.js
document.addEventListener('DOMContentLoaded', function() {
    const btnAddRecomendacion = document.getElementById('Addrecommendation');
    const btnGuardarJson = document.getElementById('CrearPost');
    const templateRecomendacion = document.getElementById('recommendation-template');
    const jsonResult = document.getElementById('recommendations_json');
    const contenedorRecomendaciones = document.getElementById('recommendation-container');
    const selectOptions = document.getElementById('selectOptions');

    const TYPES_RECOMMENDATION = [
        "Hotel",
        "Restaurante",
        "Lugar",
        "Actividad"
    ];
    let dataRecomendation = [];

    const addOption = () => {
          TYPES_RECOMMENDATION.forEach(TYPE =>{
            const newOption = document.createElement('option')
          newOption.value = TYPE;
        newOption.textContent = TYPE
              selectOptions.appendChild(newOption);
        })
    }
    const render = () => {
        limpiarHTML();
        dataRecomendation.forEach(element => {
            const html = templateRecomendacion.content.cloneNode(true);
            html.querySelector('span.text').textContent = "Tipo de Recomendacion: " + element.recommendation_type;
            html.querySelector('span.text').textContent = html.querySelector('span.text').textContent + " Comentario: " + element.comment;
            html.querySelector('span.text').textContent = html.querySelector('span.text').textContent + " Contacto: " + element.contact;
            html.querySelector('span.text').textContent = html.querySelector('span.text').textContent + " Ratting: " + element.rating;
              html.querySelector('span.text').textContent = html.querySelector('span.text').textContent + " Price: " + element.price;
            contenedorRecomendaciones.appendChild(html)
        })
    }
   
    const limpiarHTML = () => {
        while (contenedorRecomendaciones.firstChild) {
            contenedorRecomendaciones.removeChild(contenedorRecomendaciones.firstChild);
        }
    }
    const saveData = () => {
        jsonResult.value = JSON.stringify(dataRecomendation);
    }
         addOption();
    btnAddRecomendacion.addEventListener('click', (event) => {
        event.preventDefault();
        const recommendation_type = document.querySelector('#selectOptions').value;
        const comment = document.querySelector('#comment').value;
        const rating = document.querySelector('#rating').value;
        const contact = document.querySelector('#contact').value;
        const price = document.querySelector('#price').value;

        if (recommendation_type === "") {
            alert("El nombre del archivo es obligatorio")
            return;
        }
        if (comment === "") {
            alert("La descripción es obligatorio")
            return;
        }

        const recommendation = {
            recommendation_type,
            comment,
            rating,
            contact,
            price
        }
        dataRecomendation = [...dataRecomendation, recommendation];
        render()

    });
    btnGuardarJson.addEventListener('click', () => {
        saveData();
    });
});