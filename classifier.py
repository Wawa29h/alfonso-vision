#!/usr/bin/env python3
"""
classifier.py — Clasificador de imagenes zero-shot con CLIP (linea de comandos).

Uso:
    python classifier.py --image perro1.png
    python classifier.py --image foto.jpg --clasificador frutas
    python classifier.py --image foto.jpg --clasificador animales --top 8
    python classifier.py --image foto.jpg --labels "gato,perro,auto"   # etiquetas manuales
    python classifier.py --listar                                      # ver perfiles

Los perfiles se definen en clasificadores.py.
La logica de clasificacion vive en motor.py (compartida con la UI: app.py).
"""

import argparse
import sys
from pathlib import Path

import clasificadores
from clasificadores import Clasificador
from motor import ErrorModelo, clasificar


def _construir_perfil(args) -> Clasificador:
    """Decide que clasificador usar segun los argumentos de la CLI."""
    if args.labels:
        etiquetas = [l.strip() for l in args.labels.split(",") if l.strip()]
        return Clasificador(
            id="manual", nombre="Manual", etiquetas=etiquetas,
            modelo=args.model or clasificadores.MODELO_DEFAULT,
        )

    base = clasificadores.obtener(args.clasificador)  # puede lanzar KeyError
    if not args.model:
        return base
    # Permitir sobre-escribir el modelo desde la CLI, conservando el resto.
    return Clasificador(
        id=base.id, nombre=base.nombre, etiquetas=base.etiquetas,
        plantilla=base.plantilla, modelo=args.model,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Clasificador de imagenes zero-shot con CLIP (CLI)"
    )
    parser.add_argument("--image", "-i", help="Ruta a la imagen a clasificar")
    parser.add_argument("--clasificador", "-c", default="general",
                        help="Perfil a usar (general, animales, frutas, verduras, ...)")
    parser.add_argument("--labels", "-l",
                        help="Etiquetas manuales separadas por coma (ignora --clasificador)")
    parser.add_argument("--model", "-m", help="Modelo CLIP a usar (opcional)")
    parser.add_argument("--top", "-k", type=int, default=5, help="Cuantos resultados mostrar")
    parser.add_argument("--listar", action="store_true",
                        help="Lista los clasificadores disponibles y sale")
    args = parser.parse_args()

    if args.listar:
        print("Clasificadores disponibles:")
        for c in clasificadores.CLASIFICADORES.values():
            print(f"  {c.id:12s} {c.nombre}  ({len(c.etiquetas)} etiquetas)")
        return

    if not args.image:
        parser.error("se requiere --image (o usa --listar para ver los perfiles)")

    if not Path(args.image).exists():
        print(f"Error: no se encontro la imagen '{args.image}'", file=sys.stderr)
        sys.exit(1)

    try:
        perfil = _construir_perfil(args)
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        resultados = clasificar(args.image, perfil)
    except ErrorModelo as e:
        print(f"\n[ERROR]\n{e}", file=sys.stderr)
        sys.exit(2)

    print(f"\nResultados para '{args.image}' [{perfil.nombre}]:\n")
    for etiqueta, prob in resultados[: args.top]:
        bar = "#" * int(prob * 40)
        print(f"  {etiqueta:25s} {prob*100:6.2f}%  {bar}")


if __name__ == "__main__":
    main()
