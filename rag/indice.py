"""Índice de vectores TF-IDF con búsqueda por coseno en SQLite."""
import json
import math
import re
import sqlite3
import unicodedata
from collections import Counter

VACIAS = set("a al con como cual de del el en es la las lo los metodo permite me mi para por que se sin su un una y".split())


def palabras(texto):
    plano = unicodedata.normalize("NFKD", texto.lower())
    plano = "".join(c for c in plano if not unicodedata.combining(c))
    return [p for p in re.findall(r"[a-z0-9_]+", plano) if p not in VACIAS]


def vector(texto, pesos):
    conteo = Counter(palabras(texto))
    valores = {p: n * pesos[p] for p, n in conteo.items() if p in pesos}
    norma = math.sqrt(sum(x * x for x in valores.values()))
    return {p: x / norma for p, x in valores.items()}


def indexar(ruta, apuntes):
    if not apuntes:
        raise ValueError("Agrega al menos un fragmento al corpus.")
    textos = [a["tema"] + " " + a["texto"] for a in apuntes]
    frecuencia = Counter(p for t in textos for p in set(palabras(t)))
    pesos = {p: 1 + math.log((1 + len(textos)) / (1 + n)) for p, n in frecuencia.items()}
    db = sqlite3.connect(ruta)
    try:
        # Reemplazamos todo en una transacción para que un apunte borrado desaparezca también del índice.
        with db:
            db.execute("CREATE TABLE IF NOT EXISTS terminos (palabra TEXT PRIMARY KEY, peso REAL)")
            db.execute("CREATE TABLE IF NOT EXISTS apuntes (id INTEGER PRIMARY KEY, tema TEXT, texto TEXT, fuente TEXT, vector TEXT)")
            db.execute("DELETE FROM terminos")
            db.execute("DELETE FROM apuntes")
            db.executemany("INSERT INTO terminos VALUES (?, ?)", pesos.items())
            for i, (a, t) in enumerate(zip(apuntes, textos), 1):
                db.execute("INSERT INTO apuntes VALUES (?, ?, ?, ?, ?)",
                           (i, a["tema"], a["texto"], a["fuente"], json.dumps(vector(t, pesos))))
    finally:
        db.close()


def recuperar(ruta, pregunta, limite=3, umbral=0.20):
    db = sqlite3.connect(ruta)
    db.row_factory = sqlite3.Row
    try:
        db.execute("BEGIN")
        consulta = vector(pregunta, dict(db.execute("SELECT palabra, peso FROM terminos")))
        if not consulta:
            return []
        # Como ambos vectores ya tienen longitud uno, su producto punto es el coseno.
        def coseno(guardado):
            documento = json.loads(guardado)
            return sum(v * documento.get(p, 0) for p, v in consulta.items())

        db.create_function("coseno", 1, coseno)
        filas = db.execute("""
            SELECT id, tema, texto, fuente, coseno(vector) AS puntaje FROM apuntes
            WHERE coseno(vector) >= ? ORDER BY puntaje DESC, id LIMIT ?
        """, (umbral, limite))
        return [dict(fila) for fila in filas]
    finally:
        db.close()
