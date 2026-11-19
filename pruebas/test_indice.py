import json
import tempfile
import unittest
from pathlib import Path

from rag.generacion import SIN_EVIDENCIA, generar
from rag.indice import indexar, recuperar

RAIZ = Path(__file__).resolve().parents[1]


class PruebaIndice(unittest.TestCase):
    def test_consultas_y_actualizacion(self):
        datos = json.loads((RAIZ / "datos/python.json").read_text(encoding="utf-8"))
        casos = json.loads((RAIZ / "pruebas/consultas.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "prueba.sqlite3"
            indexar(ruta, datos)
            for pregunta, esperado in casos:
                with self.subTest(pregunta=pregunta):
                    filas = recuperar(ruta, pregunta)
                    self.assertEqual(filas[0]["id"] if filas else None, esperado)
            indexar(ruta, datos[:1])
            self.assertEqual(recuperar(ruta, "diccionario"), [])
            self.assertEqual(generar("¿Marte?", []), SIN_EVIDENCIA)
