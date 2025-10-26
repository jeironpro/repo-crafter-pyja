"""
    Implementar eliminar todo, posiblemente actualizar todo.
    Para actualizar: mostrarme los archivos en el fronted que estan modificados para seleccionar y agregarlo. Pedirme un mensaje para el commit.
"""

import os
import secrets
import requests
import subprocess
from flask import Flask, render_template, redirect, flash, request
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

app.secret_key = secrets.token_hex(32)

load_dotenv()

GITHUB_USER = os.getenv("GITHUB_USER")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

API_GITHUB="https://api.github.com/user/repos"
CABECERAS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}
HOME = Path.home()
CARPETA_REPOS = HOME / "Documentos" / "repositorios"

# Año actual para la licencia
YEAR = datetime.now().year

# Plantilla mínima de README
README_TEMPLATE = """# {project_name}

## 📌 Descripción
Este proyecto forma parte de mi portafolio personal.  
El objetivo es demostrar buenas prácticas de programación, organización y documentación en GitHub.

## 📜 Licencia
Este proyecto está bajo la licencia **MIT**.  
Consulta el archivo [LICENSE](LICENSE) para más detalles.
"""

# Plantilla de licencia MIT
LICENSE_TEMPLATE = """MIT License

Copyright (c) {year} {user}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def auxiliar_crea_repo(nombre, visibilidad):
    sesion = requests.Session()
    sesion.auth = (GITHUB_USER, GITHUB_TOKEN)

    carpeta_repo = CARPETA_REPOS / ("privado" if visibilidad else "publico") / nombre

    if carpeta_repo.exists():
        return f"❌ La carpeta '{carpeta_repo}' ya existe localmente." 
    
    os.makedirs(carpeta_repo, exist_ok=True)

    ruta_readme = carpeta_repo / "README.md"
    with open(ruta_readme, "w", encoding="utf-8") as fitxer:
        fitxer.write(README_TEMPLATE.format(project_name=nombre))

    ruta_license = carpeta_repo / "LICENSE"
    with open(ruta_license, "w", encoding="utf-8") as fitxer:
        fitxer.write(LICENSE_TEMPLATE.format(year=YEAR, user=GITHUB_USER))

    subprocess.run(["git", "-C", str(carpeta_repo), "init"])
    subprocess.run(["git", "branch", "-M", "main"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Agregando README & LICENSE"], check=True, stderr=subprocess.DEVNULL)

    datos = {
        "name": nombre,
        "description": f"Proyecto {nombre} subido automáticamente.",
        "private": visibilidad
    }

    respuesta = sesion.post(API_GITHUB, json=datos)

    if respuesta.status_code in [201, 422]:
        subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL)
        subprocess.run(["git", "remote", "add", "origin", f"git@github.com:{GITHUB_USER}/{nombre}.git"])
        subprocess.run(["git", "push", "-u", "origin", "main", "--force"])
        return f"✅ Repositorio '{nombre}' creado y subido correctamente."
    else:
        return f"❌ Error creando repo en GitHub: {respuesta.status_code} {respuesta.text}"

def auxiliar_clona_repo(nombre, visibilidad):
    carpeta_repo = CARPETA_REPOS / visibilidad / nombre
    url_clona = f"git@github.com:{GITHUB_USER}/{nombre}.git"
    
    try:
        subprocess.run(["git", "clone", url_clona, carpeta_repo], check=True)
        return f"Repositorio '{nombre}' clonado en {carpeta_repo} ✅"
    except subprocess.CalledProcessError:
        return f"Error al clona '{nombre}' ❌"

def auxiliar_clona_repos():
    pagina = 1

    while True:
        enlace_clona = f"{API_GITHUB}?per_page=100&page={pagina}"

        respuesta = requests.get(enlace_clona, auth=(GITHUB_USER, GITHUB_TOKEN))

        if respuesta.status_code != 200:
            return f"Error: {respuesta.status_code}, {respuesta.text}", "error"

        repos = respuesta.json()

        if not repos:
            break

        for repo in repos:
            enlace_ssh = repo["ssh_url"]
            nombre = repo["name"]
            visibilidad = repo["private"]

            carpeta_repo = CARPETA_REPOS / ("privado" if visibilidad else "publico") / nombre

            if carpeta_repo.exists() and any(carpeta_repo.iterdir()):
                print(f"⚠️ El repo '{nombre}' ya existe, saltando.")
            else:
                subprocess.run(["git", "clone", enlace_ssh, str(carpeta_repo)], check=True)

        pagina += 1
    return f"Todos los repositorios han sido clonados en {CARPETA_REPOS} ✅"

@app.route('/', methods=["GET", "POST"])
def index():
    parametros = {"per_page": 100}
    repos = []
    pagina = 1

    while True:
        parametros["page"] = pagina
        respuesta = requests.get(API_GITHUB, headers=CABECERAS, params=parametros)
        datos = respuesta.json()

        if respuesta.status_code != 200:
            return f"Error {respuesta.status_code}: {datos.get('message', 'Error desconocido')}"

        if not datos:
            break

        repos.extend(datos)
        pagina += 1

    return render_template("index.html", repos=repos)

@app.route("/crea_repo", methods=["POST"])
def crea_repo():
    nombre = request.form.get("nombre")
    visibilidad = request.form.get("visibilidad") == "si"

    mensaje = auxiliar_crea_repo(nombre, visibilidad)
    flash(mensaje, "success" if "✅" in mensaje else "error")
    return redirect("/")

@app.route("/clona_repo/<nombre>/<visibilidad>", methods=["POST"])
def clona_repo(nombre, visibilidad):
    mensaje = auxiliar_clona_repo(nombre, visibilidad)
    flash(mensaje, "success" if "✅" in mensaje else "error")
    return redirect("/")

@app.route("/clona_repos", methods=["POST"])
def clona_repos():
    mensaje = auxiliar_clona_repos()
    flash(mensaje, "success" if "✅" in mensaje else "error")
    return redirect("/")

@app.route("/estado_repo/<visibilidad>/<nombre>", methods=["GET"])
def estado_repo(visibilidad, nombre):
    carpeta_repo = CARPETA_REPOS / ("privado" if visibilidad else "publico") / nombre

    if not carpeta_repo.exists():
        flash(f"El repositorio {carpeta_repo} no existe.", "error")
        return redirect("/")
    
    resultado = subprocess.run(
        ["git", "-C", str(carpeta_repo), "status", "--porcelain"],
        capture_output=True, text=True
    )

    archivos = []
    for linea in resultado.stdout.strip().split("\n"):
        if linea:
            estado = linea[:2].strip()
            archivo = linea[2:].strip()
            archivos.append({"estado": estado, "archivo": archivo})
    
    return {"archivos": archivos}


@app.route("/commit_repo/<visibilidad>/<nombre>", methods=["POST"])
def commit_repo(visibilidad, nombre):
        archivos = request.form.get("archivos")
        mensaje = request.form.get("mensaje-commit")

        if not archivos:
            flash("Debes seleccionar al menos un archivo", "error")
            return redirect("/")
        
        carpeta_repo = CARPETA_REPOS / ("privado" if visibilidad else "publico") / nombre

        subprocess.run(["git", "-C", str(carpeta_repo), "add", *archivos])

        subprocess.run(["git", "-C", str(carpeta_repo), "commit", "-m", mensaje])

        flash(f"Repositorio actualizado en {carpeta_repo} con {len(archivos)} archivo(s)", "success")
        return redirect("/")

@app.route('/elimina_repo/<nombre>', methods=["POST"])
def elimina_repo(nombre):
    url_elimina = f"https://api.github.com/repos/{GITHUB_USER}/{nombre}"
    respuesta = requests.delete(url_elimina, headers=CABECERAS)

    if respuesta.status_code != 204:
        flash(f"Error {respuesta.status_code}: {respuesta.json().get('message')}")
        return redirect("/")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)