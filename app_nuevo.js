const CARPETA_IMAGENES = "Fotos-recortadas_integrados;
const ARCHIVO_JSON = "recetas_completas_database.json";
let recetas = [];
let indiceActual = 0;

async function cargarRecetas() {
    try {
        const respuesta = await fetch(ARCHIVO_JSON);
        recetas = await respuesta.json();
        if (recetas.length > 0) {
            mostrarReceta(indiceActual);
            generarListaLateral();
        }
    } catch (error) {
        console.error("Error al cargar JSON:", error);
    }
}

function mostrarReceta(indice) {
    if (indice < 0 || indice >= recetas.length) return;
    indiceActual = indice;
    const receta = recetas[indice];
    
    // Extraemos el nombre base de la imagen quitando la ruta de GitHub y su extensión original
    const nombreBase = receta.archivo.split('/').pop().replace(/\.[^/.]+$/, "");
    const imgElement = document.getElementById("receta-img");
    
    if (imgElement) {
        // Lista de extensiones posibles que pudo haber guardado la Mac o el celular
        const extensiones = ['jpeg', 'jpg', 'JPEG', 'JPG'];
        let idxExt = 0;

        // Intentar cargar la primera extensión
        imgElement.src = `${CARPETA_IMAGENES}/${nombreBase}.${extensiones[idxExt]}`;
        imgElement.alt = receta.titulo;

        // Si falla la extensión actual, brinca automáticamente a la siguiente de la lista
        imgElement.onerror = function() {
            idxExt++;
            if (idxExt < extensiones.length) {
                this.src = `${CARPETA_IMAGENES}/${nombreBase}.${extensiones[idxExt]}`;
            } else {
                // Si de plano no existía en ningún formato, quita el error repetitivo
                this.onerror = null; 
                this.alt = "Imagen no encontrada";
            }
        };
    }

    // Actualizar selección visual en la lista lateral
    document.querySelectorAll(".receta-item").forEach((item, i) => {
        if (i === indice) item.classList.add("activo");
        else item.classList.remove("activo");
    });
}

function generarListaLateral() {
    const listaElement = document.getElementById("lista-recetas");
    if (!listaElement) return;
    listaElement.innerHTML = "";
    recetas.forEach((receta, indice) => {
        const item = document.createElement("div");
        item.className = "receta-item";
        item.innerText = receta.titulo || `Receta ${indice + 1}`;
        item.onclick = () => mostrarReceta(indice);
        listaElement.appendChild(item);
    });
}

window.onload = cargarRecetas;
