import os
import json
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Configuración de rutas
CARPETA_IMAGENES = "smart_cropped_recipes"
ARCHIVO_JSON = "recetas_completas_database.json"
PUERTO = 8080

if not os.path.exists(CARPETA_IMAGENES):
    print(f"Error: No se encuentra la carpeta '{CARPETA_IMAGENES}'")
    exit()

# 1. Cargar o inicializar la Base de Datos
if os.path.exists(ARCHIVO_JSON):
    with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
        database = json.load(f)
else:
    database = {}

# 2. Sincronizar imágenes con el JSON (Proceso Batch)
todas_las_fotos = sorted([f for f in os.listdir(CARPETA_IMAGENES) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

cambios_batch = False
for foto in todas_las_fotos:
    if foto not in database:
        titulo_limpio = os.path.splitext(foto)[0].replace('_', ' ')
        database[foto] = {
            "archivo": foto,
            "titulo": titulo_limpio,
            "categoria": "",
            "palabras_clave": []
        }
        cambios_batch = True

if cambios_batch:
    with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=4)

class ManejadorCaptura(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith(f"/{CARPETA_IMAGENES}/"):
            return SimpleHTTPRequestHandler.do_GET(self)
            
        url_decodificada = urlparse(self.path)
        params = parse_qs(url_decodificada.query)
        
        # Actualizar la lista de fotos vivas en el JSON (por si se acaban de borrar algunas)
        fotos_vivas = sorted([f for f in todas_las_fotos if f in database])
        
        # Si ya no quedan tarjetas en la base de datos
        if not fotos_vivas:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            html_vacio = "<html><body style='font-family:sans-serif; background:#111; color:#fff; text-align:center; padding-top:100px;'><h1>No hay tarjetas en el JSON.</h1></body></html>"
            self.wfile.write(html_vacio.encode('utf-8'))
            return
        
        # Ruta Principal de la Interfaz
        if url_decodificada.path == "/" or url_decodificada.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            
            idx_actual = int(params.get('idx', [0])[0])
            
            # Si entramos de cero, buscar la primera sin categoría
            if 'idx' not in params:
                for i, foto in enumerate(fotos_vivas):
                    if database[foto]["categoria"] == "":
                        idx_actual = i
                        break
            
            if idx_actual >= len(fotos_vivas):
                idx_actual = len(fotos_vivas) - 1
            if idx_actual < 0:
                idx_actual = 0
                
            foto_actual = fotos_vivas[idx_actual]
            datos_receta = database[foto_actual]
            
            titulo_val = datos_receta["titulo"]
            categoria_val = datos_receta["categoria"]
            tags_val = ", ".join(datos_receta["palabras_clave"])
            total = len(fotos_vivas)
            
            html_captura = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Asistente de Indexación y Edición</title>
                <style>
                    body {{ font-family: 'Segoe UI', sans-serif; background: #1a1a1a; color: #e0e0e0; margin: 0; display: flex; height: 100vh; overflow: hidden; }}
                    .panel-izq {{ width: 60%; height: 100%; display: flex; justify-content: center; align-items: center; background: #111; padding: 20px; }}
                    .panel-izq img {{ max-width: 100%; max-height: 100%; object-fit: contain; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border-radius: 6px; }}
                    .panel-der {{ width: 40%; height: 100%; background: #262626; padding: 40px; display: flex; flex-direction: column; justify-content: space-between; border-left: 1px solid #3c3c3c; }}
                    h2 {{ color: #f1c40f; margin-top: 0; margin-bottom: 5px; }}
                    .archivo-nombre {{ font-size: 0.85rem; color: #888; margin-bottom: 15px; font-family: monospace; }}
                    .progreso {{ font-size: 0.9rem; color: #aaa; margin-bottom: 20px; }}
                    label {{ display: block; font-weight: bold; margin-bottom: 5px; color: #ccc; }}
                    input[type="text"] {{ width: 100%; padding: 12px; background: #1a1a1a; border: 1px solid #444; border-radius: 6px; color: #fff; font-size: 1rem; margin-bottom: 20px; }}
                    input[type="text"]:focus {{ border-color: #f1c40f; outline: none; }}
                    
                    .nav-buttons {{ display: flex; gap: 10px; margin-bottom: 20px; }}
                    .btn-nav {{ flex: 1; padding: 10px; background: #3a3a3a; border: 1px solid #555; color: white; border-radius: 6px; cursor: pointer; font-weight: bold; }}
                    .btn-nav:hover {{ background: #4a4a4a; }}
                    .btn-nav:disabled {{ background: #222; color: #555; cursor: not-allowed; border-color: #333; }}
                    
                    .actions-container {{ display: flex; flex-direction: column; gap: 10px; }}
                    .btn-guardar {{ background: #27ae60; color: white; border: none; padding: 15px; border-radius: 6px; font-size: 1.1rem; font-weight: bold; cursor: pointer; width: 100%; transition: background 0.2s; }}
                    .btn-guardar:hover {{ background: #2ecc71; }}
                    
                    .btn-eliminar {{ background: #c0392b; color: white; border: none; padding: 10px; border-radius: 6px; font-size: 0.9rem; font-weight: bold; cursor: pointer; width: 100%; transition: background 0.2s; margin-top: 10px; }}
                    .btn-eliminar:hover {{ background: #e74c3c; }}
                    
                    .instrucciones {{ background: #333; padding: 12px; border-radius: 6px; font-size: 0.85rem; color: #ccc; border-left: 4px solid #f1c40f; }}
                </style>
                <script>
                    function confirmarEliminacion(archivo, idx) {{
                        if (confirm("¿Seguro que deseas eliminar esta tarjeta del JSON?")) {{
                            location.href = "/eliminar?archivo=" + encodeURIComponent(archivo) + "&idx=" + idx;
                        }}
                    }}
                </script>
            </head>
            <body>
                <div class="panel-izq">
                    <img src="/{CARPETA_IMAGENES}/{foto_actual}" alt="Tarjeta Actual">
                </div>
                <div class="panel-der">
                    <div>
                        <h2>Indexación / Edición</h2>
                        <div class="archivo-nombre">Archivo: {foto_actual}</div>
                        
                        <div class="progreso">
                            Tarjeta <strong>{idx_actual + 1}</strong> de {total}
                        </div>
                        
                        <div class="nav-buttons">
                            <button class="btn-nav" type="button" onclick="location.href='/?idx={idx_actual - 1}'" {"disabled" if idx_actual == 0 else ""}>◀ Anterior</button>
                            <button class="btn-nav" type="button" onclick="location.href='/?idx={idx_actual + 1}'" {"disabled" if idx_actual == total - 1 else ""}>Siguiente ▶</button>
                        </div>
                        
                        <form action="/guardar" method="GET">
                            <input type="hidden" name="idx" value="{idx_actual}">
                            <input type="hidden" name="archivo" value="{foto_actual}">
                            
                            <label>Título de la Receta:</label>
                            <input type="text" name="titulo" id="titulo" required autofocus value="{titulo_val}">
                            
                            <label>Categoría:</label>
                            <input type="text" name="categoria" value="{categoria_val}" placeholder="Ej. Pasteles, Galletas, Sopas">
                            
                            <label>Palabras Clave (separadas por comas):</label>
                            <input type="text" name="tags" value="{tags_val}" placeholder="Ej. chocolate, dulce, horno">
                            
                            <div class="actions-container">
                                <button type="submit" class="btn-guardar">Guardar Cambios (Enter)</button>
                                <button type="button" class="btn-eliminar" onclick="confirmarEliminacion('{foto_actual}', {idx_actual})">🗑 Eliminar Tarjeta del JSON</button>
                            </div>
                        </form>
                    </div>
                    
                    <div class="instrucciones">
                        <strong>💡 Gestión de Datos:</strong> El botón rojo eliminará la receta únicamente de tu índice JSON. Útil para descartar fotos duplicadas o archivos de desecho durante la indexación.
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_captura.encode('utf-8'))
            
        # Ruta para procesar el guardado
        elif url_decodificada.path == "/guardar":
            archivo = params['archivo'][0]
            idx_actual = int(params['idx'][0])
            titulo = params['titulo'][0].strip()
            categoria = params.get('categoria', ['Otros'])[0].strip() or "Otros"
            tags_raw = params.get('tags', [''])[0]
            
            palabras_clave = [t.strip().lower() for t in tags_raw.split(',') if t.strip()]
            
            database[archivo] = {
                "archivo": archivo,
                "titulo": titulo,
                "categoria": categoria,
                "palabras_clave": palabras_clave
            }
            
            with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
                json.dump(database, f, ensure_ascii=False, indent=4)
                
            self.send_response(303)
            self.send_header("Location", f"/?idx={idx_actual + 1}")
            self.end_headers()

        # NUEVA RUTA: Procesar la eliminación de una tarjeta
        elif url_decodificada.path == "/eliminar":
            archivo = params['archivo'][0]
            idx_actual = int(params['idx'][0])
            
            if archivo in database:
                del database[archivo]
                with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
                    json.dump(database, f, ensure_ascii=False, indent=4)
                print(f" -> Tarjeta eliminada del JSON: {archivo}")
            
            # Redirigir al mismo índice (que ahora apuntará al elemento que tomó su lugar)
            self.send_response(303)
            self.send_header("Location", f"/?idx={idx_actual}")
            self.end_headers()

def iniciar_servidor():
    server = HTTPServer(('localhost', PUERTO), ManejadorCaptura)
    print(f"=========================================================")
    print(f" Asistente con función BORRAR corriendo en http://localhost:{PUERTO}")
    print(f"=========================================================")
    webbrowser.open(f"http://localhost:{PUERTO}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido con éxito.")

if __name__ == '__main__':
    iniciar_servidor()
