# Alfonso Vision — Clasificador de imágenes por visión artificial

Clasificador de imágenes **zero-shot** con [CLIP](https://openai.com/research/clip)
(modelo `openai/clip-vit-large-patch14`) vía Hugging Face `transformers`.
No requiere entrenamiento: tú defines las categorías (en texto) y el modelo
decide cuál describe mejor la imagen.

Incluye tres formas de usarlo:

- 🌐 **Interfaz web** "Alfonso Vision" (`servidor.py` + `index.html`) — diseño elegante, arrastrar y soltar.
- 🖥️ **Interfaz de escritorio** (`app.py`) — ventana Tkinter, sin dependencias extra.
- ⌨️ **Línea de comandos** (`classifier.py`).

Todas comparten el mismo motor (`motor.py`) y el mismo registro de perfiles (`clasificadores.py`).

---

## Instalación

```bash
# 1. Clonar
git clone <url-del-repo>
cd "Ingia ia imagenes"

# 2. Crear entorno virtual e instalar dependencias
python -m venv alfonso
alfonso\Scripts\activate            # Windows
pip install -r requirements.txt
```

> **Nota (Windows / Smart App Control):** si al importar `torch` aparece
> `WinError 4551 - Una directiva de Control de aplicaciones bloqueó este archivo`,
> es Smart App Control bloqueando los DLL (sin firmar) de PyTorch. Solución:
> *Seguridad de Windows → Control de aplicaciones y del explorador →
> Configuración de Control inteligente de aplicaciones → Desactivado*, y reiniciar.

---

## Uso

### Interfaz web (recomendada)
```bash
python servidor.py
```
Abre el navegador en `http://localhost:8000`. En Windows puedes usar el
lanzador **`Abrir Alfonso Vision.bat`** (doble clic).

### Interfaz de escritorio
```bash
python app.py
```
O el lanzador **`Abrir UI.bat`**.

### Línea de comandos
```bash
python classifier.py --image perro1.png --clasificador animales
python classifier.py --listar                       # ver perfiles
python classifier.py --image foto.jpg --labels "gato,perro,auto"
```

---

## Agregar un clasificador nuevo

Todo el catálogo de categorías vive en [`clasificadores.py`](clasificadores.py).
Para añadir un perfil (p. ej. vehículos) basta con **una entrada** en el
diccionario `CLASIFICADORES`; aparecerá automáticamente en la web, la interfaz
de escritorio y la CLI:

```python
"vehiculos": Clasificador(
    id="vehiculos",
    nombre="Vehiculos",
    etiquetas=["un carro", "una moto", "un camion", "un bus",
               "una bicicleta", "un avion", "un barco", "un tren"],
),
```

---

## Estructura

| Archivo | Rol |
|---|---|
| `clasificadores.py` | Registro de perfiles (categorías) |
| `motor.py` | Motor CLIP (carga con caché, clasificación) |
| `servidor.py` | Servidor web local (solo librería estándar) |
| `index.html` | Interfaz web Alfonso Vision |
| `app.py` | Interfaz de escritorio (Tkinter) |
| `classifier.py` | Interfaz de línea de comandos |

## Licencia

MIT
