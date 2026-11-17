"""
Servidor web del simulador de escape de incendios forestales (Flask + API JSON).

Ejecutar con:
    python app.py
y abrir http://localhost:5000

La interfaz (HTML, CSS y JavaScript propios) vive en la carpeta `web/`.
Este archivo solo expone los algoritmos de `simulador/` como una API JSON:

    GET  /api/mapa      celdas, 5 puntos de inicio, algoritmos y colores
    POST /api/correr    corre un algoritmo desde un inicio y devuelve todo
                        lo necesario para reproducirlo paso a paso
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request

from simulador import mapas
from simulador.algoritmos import ALGORITMOS
from simulador.metricas import medir

CARPETA_WEB = Path(__file__).resolve().parent / "web"

COLOR_ALGORITMO = {"A*": "#1d4ed8", "BFS": "#9333ea", "DFS": "#ea580c"}

app = Flask(__name__, static_folder=str(CARPETA_WEB), static_url_path="")
MAPA, INICIOS = mapas.cargar()


@app.get("/")
def pagina():
    return app.send_static_file("index.html")


@app.get("/api/mapa")
def mapa():
    return jsonify({
        "nombre": mapas.NOMBRE,
        "celdas": MAPA.celdas,
        "inicios": [list(p) for p in INICIOS],
        "algoritmos": list(ALGORITMOS),
        "colores": COLOR_ALGORITMO,
    })


@app.post("/api/correr")
def correr():
    datos = request.get_json(silent=True) or {}
    algoritmo = datos.get("algoritmo")
    if algoritmo not in ALGORITMOS:
        return jsonify({"error": f"Algoritmo desconocido: {algoritmo!r}."}), 400
    try:
        f, c = datos["inicio"]
        inicio = (int(f), int(c))
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Inicio no válido: se esperaba [fila, columna]."}), 400
    if not MAPA.transitable(inicio):
        return jsonify({"error": "El inicio está sobre roca/río, fuego o fuera del mapa."}), 400

    m = medir(ALGORITMOS[algoritmo], MAPA, inicio, repeticiones=5)
    r = m.resultado
    return jsonify({
        **r.a_dict(),
        "pasos": r.pasos,
        "tiempo_ms": round(m.tiempo_ms, 4),
        "memoria_kb": round(m.memoria_kb, 2),
        "celdas_humo": sum(1 for p in r.ruta[1:] if MAPA.simbolo(p) == "H"),
    })


if __name__ == "__main__":
    print("Simulador de escape de incendios forestales en http://localhost:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
