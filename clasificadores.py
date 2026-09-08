"""
clasificadores.py — Registro de "perfiles" de clasificacion para CLIP zero-shot.

Un clasificador aqui es simplemente:
  - un nombre visible (para la interfaz),
  - una lista de etiquetas (las categorias posibles),
  - una plantilla de prompt (como se le describe cada etiqueta al modelo),
  - el modelo CLIP a usar.

=====================================================================
PARA AGREGAR UN NUEVO CLASIFICADOR (p. ej. "instrumentos", "vehiculos"):
solo agrega una entrada al diccionario CLASIFICADORES de mas abajo.
No necesitas tocar el motor (motor.py) ni la interfaz (app.py); el nuevo
perfil aparece automaticamente en la CLI y en el menu de la UI.
=====================================================================
"""

from dataclasses import dataclass


# Modelo por defecto compartido. Cambiarlo aqui afecta a todos los
# clasificadores que no definan uno propio.
MODELO_DEFAULT = "openai/clip-vit-large-patch14"


@dataclass(frozen=True)
class Clasificador:
    """Un perfil de clasificacion zero-shot."""
    id: str                       # identificador corto, sin espacios (para la CLI)
    nombre: str                   # nombre visible en la interfaz
    etiquetas: list[str]          # categorias posibles
    plantilla: str = "una foto de {label}"   # como se arma el prompt de cada etiqueta
    modelo: str = MODELO_DEFAULT  # modelo CLIP a usar


CLASIFICADORES: dict[str, Clasificador] = {
    "general": Clasificador(
        id="general",
        nombre="General (objetos comunes)",
        etiquetas=[
            "un gato", "un perro", "un auto", "un avion", "una persona",
            "un edificio", "comida", "un paisaje natural", "un animal salvaje",
            "un objeto tecnologico",
        ],
    ),
    "animales": Clasificador(
        id="animales",
        nombre="Animales",
        etiquetas=[
            # domesticos y de granja
            "un perro", "un gato", "un caballo", "una vaca", "una oveja",
            "un cerdo", "una gallina", "un pato", "un conejo", "un raton",
            # salvajes
            "un leon", "un tigre", "un oso", "un elefante", "una jirafa",
            "un mono", "un venado", "un lobo", "un zorro", "una cebra",
            # aves
            "un aguila", "un buho", "un loro", "una paloma",
            # reptiles / anfibios
            "una serpiente", "una tortuga", "una rana", "un lagarto",
            # acuaticos
            "un pez", "un tiburon", "un delfin", "una ballena",
            # insectos / otros
            "una mariposa", "una abeja", "una arana", "un cangrejo",
        ],
    ),
    "frutas": Clasificador(
        id="frutas",
        nombre="Frutas",
        etiquetas=[
            "una manzana", "un banano", "una naranja", "una fresa",
            "una uva", "una sandia", "un melon", "una piña", "un mango",
            "una papaya", "un durazno", "una pera", "una cereza",
            "un limon", "una lima", "un kiwi", "una granada",
            "un coco", "un aguacate", "unos arandanos", "una frambuesa",
            "unas moras", "un higo", "un maracuya",
        ],
    ),
    "verduras": Clasificador(
        id="verduras",
        nombre="Verduras / Vegetales",
        etiquetas=[
            "una zanahoria", "un tomate", "una lechuga", "un brocoli",
            "una coliflor", "una papa", "una cebolla", "un ajo",
            "un pimiento", "un chile", "un pepino", "una berenjena",
            "un calabacin", "una calabaza", "un elote", "unos frijoles",
            "unos guisantes", "una espinaca", "un rabano", "una remolacha",
            "un apio", "un champiñon", "un repollo", "un camote",
        ],
    ),
}


def obtener(id_clasificador: str) -> Clasificador:
    """Devuelve el clasificador por id, o lanza KeyError con las opciones validas."""
    if id_clasificador not in CLASIFICADORES:
        opciones = ", ".join(CLASIFICADORES)
        raise KeyError(f"Clasificador '{id_clasificador}' no existe. Opciones: {opciones}")
    return CLASIFICADORES[id_clasificador]
