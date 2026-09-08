#!/usr/bin/env python3
"""
servidor.py — Sirve la interfaz web "Alfonso Vision" y la conecta al motor CLIP.

Usa SOLO la libreria estandar de Python (http.server): no hay que instalar nada.

Ejecutar:
    python servidor.py
Luego abre solo el navegador en http://localhost:8000

Endpoints:
    GET  /                 -> pagina web (index.html)
    GET  /clasificadores   -> perfiles disponibles (para el menu "Plantilla")
    POST /clasificar       -> JSON {image: dataURL/base64, labels: "a, b, c"}
                             devuelve {resultados: [{etiqueta, prob}, ...]}
"""
from __future__ import annotations

import base64
import io
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import clasificadores
from clasificadores import Clasificador
from motor import ErrorModelo, cargar_modelo, clasificar

AQUI = Path(__file__).resolve().parent
INDEX = AQUI / "index.html"
PUERTO = 8000


class Handler(BaseHTTPRequestHandler):
    # --- utilidades ---
    def _enviar(self, codigo, cuerpo, ctype="application/json; charset=utf-8"):
        if isinstance(cuerpo, (dict, list)):
            cuerpo = json.dumps(cuerpo, ensure_ascii=False)
        if isinstance(cuerpo, str):
            cuerpo = cuerpo.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, *args):
        pass  # silenciar el log de peticiones en consola

    # --- rutas ---
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._enviar(200, INDEX.read_text(encoding="utf-8"),
                         "text/html; charset=utf-8")
        elif self.path == "/clasificadores":
            data = [
                {"id": c.id, "nombre": c.nombre, "etiquetas": ", ".join(c.etiquetas)}
                for c in clasificadores.CLASIFICADORES.values()
            ]
            self._enviar(200, data)
        else:
            self._enviar(404, {"error": "no encontrado"})

    def do_POST(self):
        if self.path != "/clasificar":
            self._enviar(404, {"error": "no encontrado"})
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n) or b"{}")

            b64 = payload.get("image", "")
            if "," in b64:                       # quitar "data:image/...;base64,"
                b64 = b64.split(",", 1)[1]
            etiquetas = [e.strip() for e in payload.get("labels", "").split(",") if e.strip()]

            if not b64:
                self._enviar(400, {"error": "No se recibio ninguna imagen."})
                return
            if not etiquetas:
                self._enviar(400, {"error": "Escribe al menos una categoria."})
                return

            from PIL import Image
            imagen = Image.open(io.BytesIO(base64.b64decode(b64)))

            perfil = Clasificador(id="web", nombre="Web", etiquetas=etiquetas)
            resultados = clasificar(imagen, perfil, log=lambda m: None)

            self._enviar(200, {
                "resultados": [{"etiqueta": e, "prob": float(p)} for e, p in resultados]
            })
        except ErrorModelo as e:
            self._enviar(500, {"error": str(e)})
        except Exception as e:  # noqa: BLE001
            self._enviar(500, {"error": f"Error inesperado: {e}"})


def _precargar_modelo():
    """Carga el modelo en segundo plano al arrancar, para que la 1a clasificacion
    sea rapida. Si torch esta bloqueado, se ignora (el error saldra al clasificar)."""
    try:
        cargar_modelo(clasificadores.MODELO_DEFAULT, log=lambda m: print("[modelo]", m))
    except Exception as e:  # noqa: BLE001
        print("[modelo] No se pudo precargar todavia:", e)


def main():
    threading.Thread(target=_precargar_modelo, daemon=True).start()

    servidor = ThreadingHTTPServer(("127.0.0.1", PUERTO), Handler)
    url = f"http://localhost:{PUERTO}"
    print("=" * 60)
    print("  Alfonso Vision  —  servidor local")
    print(f"  Abierto en: {url}")
    print("  Cierra ESTA ventana para apagar la aplicacion.")
    print("=" * 60)

    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nApagando servidor...")
        servidor.shutdown()


if __name__ == "__main__":
    main()
