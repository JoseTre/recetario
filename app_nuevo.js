const CARPETA_IMAGENES = "Fotos-recortadas_integrados";
const ARCHIVO_JSON = "recetas_completas_database.json";

let recetas = [];
let indiceActual = 0;

async function cargarRecetas() {
    try {
        const respuesta = await fetch(
            `${ARCHIVO_JSON}?version=${Date.now()}`,
            { cache: "no-store" }
        );

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

    const nombreBase = receta.archivo
        .split("/")
        .pop()
        .replace(/\.[^/.]+$/, "");

    const imgElement = document.getElementById("receta-img");

    if (imgElement) {
        imgElement.src =
            `${CARPETA_IMAGENES}/${nombreBase}.jpg`;

        imgElement.alt =
            receta.titulo || "Receta";

        imgElement.onerror = function() {
            this.onerror = null;
            this.alt = "Imagen no encontrada";
            console.error("No se encontró:", this.src);
        };
    }

    document.querySelectorAll(".receta-item").forEach((item, i) => {
        if (i === indice) {
            item.classList.add("activo");
        } else {
            item.classList.remove("activo");
        }
    });
}

function generarListaLateral() {
    const listaElement =
        document.getElementById("lista-recetas");

    if (!listaElement) return;

    listaElement.innerHTML = "";

    recetas.forEach((receta, indice) => {
        const item = document.createElement("div");

        item.className = "receta-item";

        item.innerText =
            receta.titulo || `Receta ${indice + 1}`;

        item.onclick = () => mostrarReceta(indice);

        listaElement.appendChild(item);
    });
}

window.onload = cargarRecetas;