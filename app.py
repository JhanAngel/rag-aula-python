import argparse
import json
from pathlib import Path

from rag.generacion import generar
from rag.indice import indexar, recuperar

BASE = Path(__file__).resolve().parent
INDICE = BASE / "aula.sqlite3"


def main():
    parser = argparse.ArgumentParser(description="Consulta los apuntes del curso de Python.")
    parser.add_argument("pregunta", nargs="?")
    parser.add_argument("--indexar", action="store_true")
    parser.add_argument("--solo-fuentes", action="store_true")
    args = parser.parse_args()
    if args.indexar or not INDICE.exists():
        apuntes = json.loads((BASE / "datos/python.json").read_text(encoding="utf-8"))
        indexar(INDICE, apuntes)
        print(f"Índice listo con {len(apuntes)} fragmentos.")
    if args.indexar and not args.pregunta:
        return
    pregunta = args.pregunta or input("¿Qué quieres consultar? ")
    evidencia = recuperar(INDICE, pregunta)
    if not args.solo_fuentes:
        print(generar(pregunta, evidencia))
    if not evidencia:
        print("La búsqueda no recuperó fragmentos.")
    for f in evidencia:
        print(f'[{f["id"]}] {f["tema"]} · coseno {f["puntaje"]:.3f}\n{f["texto"]}\n{f["fuente"]}')


if __name__ == "__main__":
    main()
