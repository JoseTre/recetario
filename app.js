let recetasGlobales = [];
let recetasFiltradas = [];
let indiceActual = 0;
const CARPETA_IMAGENES = "smart_cropped_recipes";

document.addEventListener("DOMContentLoaded", () => {
    fetch("recetas_completas_database.json")
        .then(response => {
            if (!response.ok) throw new Error("No se pudo cargar el archivo JSON");
            return response.json();
        })
        .then(data => {
            recetasGlobales = Object.values(data);
            recetasFiltradas = [...recetasGlobales];
            poblarCategorias();
            actualizarPantalla();
        })
        .catch(error => {
            console.error("Error inicializando la aplicación:", error);
            document.getElementById("tarjetaTitulo").innerText = "Error al cargar la base de datos";
        });
        
    document.addEventListener("keydown", (e) => {
        if (e.key === "ArrowLeft") navegar(-1);
        if (e.key === "ArrowRight") navegar(1);
    });
});

function poblarCategorias() {
    const selector = document.getElementById("filtroCategoria");
    const categorias = new Set();
    recetasGlobales.forEach(r => {
        if (r.categoria && r.categoria.trim() !== "") {
            categorias.add(r.categoria.trim());
        }
    });
    Array.from(categorias).sort().forEach(cat => {
        const opcion = document.createElement("option");
        opcion.value = cat;
        opcion.textContent = cat;
        selector.appendChild(opcion);
    });
}

function filtrarPorCategoria() {
    const categoriaSeleccionada = document.getElementById("filtroCategoria").value;
    if (categoriaSeleccionada === "TODAS") {
        recetasFiltradas = [...recetasGlobales];
    } else {
        recetasFiltradas = recetasGlobales.filter(r => r.categoria === categoriaSeleccionada);
    }
    indiceActual = 0;
    actualizarPantalla();
}

function navegar(direccion) {
    let nuevoIndice = indiceActual + direccion;
    if (nuevoIndice >= 0 && nuevoIndice < recetasFiltradas.length) {
        indiceActual = nuevoIndice;
        actualizarPantalla();
    }
}

function actualizarPantalla() {
    const total = recetasFiltradas.length;
    if (total === 0) {
        document.getElementById("tarjetaImagen").src = "";
        document.getElementById("tarjetaTitulo").innerText = "No hay recetas en esta sección";
        document.getElementById("tarjetaCategoria").innerText = "-";
        document.getElementById("tarjetaTags").innerHTML = "";
        document.getElementById("registroContador").innerText = "Tarjeta 0 de 0";
        document.getElementById("btnAnt").disabled = true;
        document.getElementById("btnSig").disabled = true;
        return;
    }
    
    const receta = recetasFiltradas[indiceActual];
    document.getElementById("tarjetaImagen").src = `${CARPETA_IMAGENES}/${receta.archivo}`;
    document.getElementById("tarjetaImagen").alt = receta.titulo;
    document.getElementById("tarjetaTitulo").innerText = receta.titulo;
    document.getElementById("tarjetaCategoria").innerText = receta.categoria || "Sin categoría";
    
    const contenedorTags = document.getElementById("tarjetaTags");
    contenedorTags.innerHTML = "";
    if (receta.palabras_clave && receta.palabras_clave.length > 0) {
        receta.palabras_clave.forEach(tag => {
            const span = document.createElement("span");
            span.className = "tag";
            span.innerText = tag;
            contenedorTags.appendChild(span);
        });
    } else {
        contenedorTags.innerHTML = "<span style='color:#666; font-style:italic;'>Ninguna</span>";
    }
    
    document.getElementById("registroContador").innerText = `Tarjeta ${indiceActual + 1} de ${total}`;
    document.getElementById("btnAnt").disabled = (indiceActual === 0);
    document.getElementById("btnSig").disabled = (indiceActual === total - 1);
}