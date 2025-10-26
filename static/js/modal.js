const modalCreaRepo = document.getElementById('modal-crea-repo');
const abrirModalCreaRepo = document.getElementById('abrir-modal-crea-repo');
const cerrarModalCreaRepo = document.getElementById('cerrar-modal-crea-repo');

abrirModalCreaRepo.addEventListener("click", () => {
    modalCreaRepo.style.display = 'flex';
});

cerrarModalCreaRepo.addEventListener('click', () => {
    modalCreaRepo.style.display = 'none';
});

modalCreaRepo.addEventListener('click', (e) => {
    if (e.target === modalCreaRepo) {
        modalCreaRepo.style.display = 'none';
    }
});


const modalClonaRepos = document.getElementById('modal-clona-repos');
const abrirModalClonaRepos = document.getElementById('abrir-modal-clona-repos');
const cerrarModalClonaRepos = document.getElementById('cerrar-modal-clona-repos');
const botonCerrarModalClonaRepos = document.getElementById('boton-cerrar-modal-clona-repos');

abrirModalClonaRepos.addEventListener("click", () => {
    modalClonaRepos.style.display = 'flex';
});

botonCerrarModalClonaRepos.addEventListener("click", () => {
    modalClonaRepos.style.display = 'none';
});

cerrarModalClonaRepos.addEventListener('click', () => {
    modalClonaRepos.style.display = 'none';
});

modalClonaRepos.addEventListener('click', (e) => {
    if (e.target === modalClonaRepos) {
        modalClonaRepos.style.display = 'none';
    }
});

const botonesActualizaRepo = document.querySelectorAll(".boton-actualizar");
const modalActualizaRepo = document.getElementById('modal-actualiza-repo');

botonesActualizaRepo.forEach(boton => {
    boton.addEventListener("click", async () => {
        const nombre = boton.getAttribute("data-nombre");
        const visibilidad = boton.getAttribute("data-visibilidad");

        fetch(`/estado_repo/${visibilidad}/${nombre}`)
            .then(respuesta => respuesta.json())
            .then(datos => {
                const lista = document.getElementById("lista-archivos");
                lista.textContent = "";

                if (datos.archivos.length === 0) {
                    const elemento = document.createElement("li");
                    elemento.classList.add("elemento")
                    elemento.textContent = "No hay cambios pendientes";
                    lista.appendChild(elemento);
                } else {
                    datos.archivos.forEach(element => {
                        const elemento = document.createElement("li");
                        elemento.classList.add("elemento");

                        const inputSelecciona = document.createElement("input");
                        inputSelecciona.type = "checkbox";
                        inputSelecciona.value = element.archivo;
                        inputSelecciona.checked = true;
                        inputSelecciona.name = "archivos";
                        inputSelecciona.id = "archivos";
                        elemento.appendChild(inputSelecciona);

                        const estado = document.createElement("strong");
                        estado.textContent = element.estado;
                        elemento.appendChild(estado);

                        const archivo = document.createElement("span");
                        archivo.textContent = element.archivo;
                        elemento.appendChild(archivo);

                        lista.appendChild(elemento);
                    });
                }

                modalActualizaRepo.style.display = 'flex';
            });
    });
});

const cerrarModalActualizaRepo = document.getElementById('cerrar-modal-actualiza-repo');
cerrarModalActualizaRepo.addEventListener('click', () => {
    modalActualizaRepo.style.display = 'none';
});