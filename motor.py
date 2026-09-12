"""
motor.py — Motor de clasificacion CLIP (zero-shot), independiente de la interfaz.

Carga el modelo CLIP una sola vez por modelo (cache) y clasifica imagenes
contra el conjunto de etiquetas de un Clasificador. Lo usan tanto la CLI
(classifier.py) como la interfaz grafica (app.py).

torch/transformers se importan de forma PEREZOSA (solo al clasificar) para que
la interfaz pueda abrirse aunque el modelo aun no este disponible, y para poder
mostrar un mensaje claro si Windows (Smart App Control) esta bloqueando torch.
"""
from __future__ import annotations

from clasificadores import Clasificador


class ErrorModelo(RuntimeError):
    """Error legible para mostrar al usuario (dependencia faltante o torch bloqueado)."""


# Cache de modelos ya cargados: {nombre_modelo: (model, processor, device)}
_CACHE: dict[str, tuple] = {}

_ETIQUETAS_CLIP = {
    "un perro": "a dog", "un gato": "a cat", "un caballo": "a horse",
    "una vaca": "a cow", "una oveja": "a sheep", "un cerdo": "a pig",
    "una gallina": "a chicken", "un pato": "a duck", "un conejo": "a rabbit",
    "un raton": "a mouse", "un leon": "a lion", "un tigre": "a tiger",
    "un oso": "a bear", "un elefante": "an elephant", "una jirafa": "a giraffe",
    "un mono": "a monkey", "un venado": "a deer", "un lobo": "a wolf",
    "un zorro": "a fox", "una cebra": "a zebra", "un aguila": "an eagle",
    "un buho": "an owl", "un loro": "a parrot", "una paloma": "a pigeon",
    "una serpiente": "a snake", "una tortuga": "a turtle", "una rana": "a frog",
    "un lagarto": "a lizard", "un pez": "a fish", "un tiburon": "a shark",
    "un delfin": "a dolphin", "una ballena": "a whale", "una mariposa": "a butterfly",
    "una abeja": "a bee", "una arana": "a spider", "un cangrejo": "a crab",
    "un mapache": "a raccoon", "una llama": "a llama", "un leopardo": "a leopard",
    "un hipopotamo": "a hippopotamus", "un rinoceronte": "a rhinoceros",
    "un cocodrilo": "a crocodile", "un pinguino": "a penguin",
    "un flamenco": "a flamingo", "un avestruz": "an ostrich",
    "un murcielago": "a bat", "una ardilla": "a squirrel",
    "una nutria": "an otter", "un koala": "a koala", "un panda": "a panda",
    "un canguro": "a kangaroo", "un gorila": "a gorilla",
    "un chimpance": "a chimpanzee", "una foca": "a seal",
    "un pulpo": "an octopus", "una medusa": "a jellyfish",
    "una langosta": "a lobster", "un caracol": "a snail",
}

_DESCRIPCIONES_CLAVE = {
    "un mapache": "a masked mammal with a ringed tail",
    "un raton": "a tiny rodent with round ears and a thin tail",
    "un oso": "a large robust mammal with powerful paws",
    "un zorro": "a fox-like mammal with a pointed muzzle and bushy tail",
    "un lobo": "a large wild canine with a long muzzle and pointed ears",
    "un leopardo": "a large spotted muscular cat",
    "un tigre": "a large cat with dark stripes",
    "una llama": "a South American animal with a long neck and wool",
}

_VARIANTES_PROMPT = {
    "un mapache": [
        "a photo of a raccoon",
        "a close-up photo of a raccoon",
        "a raccoon with a black facial mask and ringed tail",
    ],
    "un raton": [
        "a photo of a mouse",
        "a close-up photo of a mouse",
        "a small mouse with round ears and a thin tail",
    ],
}


def _importar_torch():
    """Importa torch/transformers y traduce fallos comunes a ErrorModelo."""
    try:
        import torch
        from transformers import CLIPModel, CLIPProcessor
        return torch, CLIPModel, CLIPProcessor
    except OSError as e:
        # WinError 4551 = Smart App Control bloquea el DLL de PyTorch
        texto = str(e)
        if "4551" in texto or "Control de aplicaciones" in texto or "Application Control" in texto:
            raise ErrorModelo(
                "Windows (Smart App Control) esta bloqueando las librerias de PyTorch.\n\n"
                "Para solucionarlo:\n"
                "  1. Seguridad de Windows > Control de aplicaciones y del explorador\n"
                "  2. Configuracion de Control inteligente de aplicaciones > Desactivado\n"
                "  3. Reinicia la computadora."
            ) from e
        raise ErrorModelo(f"No se pudieron cargar las librerias del modelo:\n{e}") from e
    except ImportError as e:
        raise ErrorModelo(
            f"Falta una dependencia: {e}\n"
            "Instala con: pip install torch transformers pillow"
        ) from e


def cargar_modelo(nombre_modelo: str, log=print):
    """Carga (y cachea) un modelo CLIP. Devuelve (model, processor, device)."""
    if nombre_modelo in _CACHE:
        return _CACHE[nombre_modelo]

    torch, CLIPModel, CLIPProcessor = _importar_torch()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    log(f"Cargando modelo '{nombre_modelo}' en {device} ... (puede tardar la primera vez)")

    model = CLIPModel.from_pretrained(nombre_modelo, torch_dtype=dtype).to(device)
    processor = CLIPProcessor.from_pretrained(nombre_modelo)

    log("Modelo listo.")
    _CACHE[nombre_modelo] = (model, processor, device)
    return _CACHE[nombre_modelo]


def clasificar(imagen, clasificador: Clasificador, log=print):
    """Clasifica una imagen segun un perfil de Clasificador.

    'imagen' puede ser una ruta (str/Path) o una imagen PIL ya abierta
    (util para la version web, que recibe la imagen en memoria).

    Devuelve una lista [(etiqueta, probabilidad), ...] ordenada de mayor a menor.
    """
    from pathlib import Path
    from PIL import Image

    torch, _, _ = _importar_torch()   # ya cacheado por sys.modules tras la 1a vez

    model, processor, device = cargar_modelo(clasificador.modelo, log=log)

    if isinstance(imagen, (str, Path)):
        image = Image.open(imagen).convert("RGB")
    else:
        image = imagen.convert("RGB")   # ya es una imagen PIL
    grupos_prompts = []
    for etq in clasificador.etiquetas:
        etiqueta_clip = _ETIQUETAS_CLIP.get(etq)
        prompt = f"a photo of {etiqueta_clip}" if etiqueta_clip else clasificador.plantilla.format(label=etq)
        descripcion = _DESCRIPCIONES_CLAVE.get(etq)
        if descripcion:
            prompt += f", {descripcion}"
        grupos_prompts.append(_VARIANTES_PROMPT.get(etq, [prompt]))
    prompts = [prompt for grupo in grupos_prompts for prompt in grupo]

    inputs = processor(text=prompts, images=image, return_tensors="pt", padding=True).to(device)
    if device == "cuda":
        inputs["pixel_values"] = inputs["pixel_values"].to(torch.float16)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits_per_image[0]
        scores = []
        cursor = 0
        for grupo in grupos_prompts:
            cantidad = len(grupo)
            scores.append(logits[cursor:cursor + cantidad].mean())
            cursor += cantidad
        probs = torch.stack(scores).softmax(dim=0).cpu().numpy()

    return sorted(zip(clasificador.etiquetas, probs), key=lambda x: x[1], reverse=True)
