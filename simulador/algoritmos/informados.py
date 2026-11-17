"""
Búsqueda INFORMADA: usa la heurística h(n) = distancia Manhattan a la
salida más cercana para decidir qué explorar primero.

    A*  - mira f(n) = g(n) + h(n)      (óptima con h admisible)
"""

from __future__ import annotations

import heapq
from itertools import count

from ..cuadricula import Cuadricula, Posicion
from .base import Resultado, resultado_exitoso, validar_inicio


def a_estrella(mapa: Cuadricula, inicio: Posicion) -> Resultado:
    """
    A* (algoritmo principal del proyecto).

    Ordena la frontera por f(n) = g(n) + h(n):
      g(n) = costo real desde el inicio (cuenta el humo como 5),
      h(n) = Manhattan a la salida más cercana (estimación optimista).

    Como h nunca sobreestima (admisible) y es consistente, la primera salida
    que se expande es la de menor costo, explorando solo
    las celdas hacia donde h "empuja" la búsqueda (hacia las salidas).
    En empate de f se prefiere la celda con menor h (la más cercana a salir).

    Completa: sí.  Óptima en costo: sí.
    """
    nombre = "A*"
    if error := validar_inicio(mapa, inicio):
        return Resultado(nombre, False, mensaje=error)

    desempate = count()
    h0 = mapa.heuristica(inicio)
    frontera = [(h0, h0, next(desempate), inicio)]  # (f, h, orden de llegada, celda)
    g: dict[Posicion, int] = {inicio: 0}
    padres: dict[Posicion, Posicion | None] = {inicio: None}
    cerrados: set[Posicion] = set()
    expandidos = generados = 0
    max_frontera = 1
    orden: list[Posicion] = []

    while frontera:
        _, _, _, actual = heapq.heappop(frontera)
        if actual in cerrados:
            continue
        cerrados.add(actual)
        expandidos += 1
        orden.append(actual)

        if mapa.es_salida(actual):
            return resultado_exitoso(nombre, mapa, padres, actual, expandidos, generados, max_frontera, orden)

        for vecino in mapa.vecinos(actual):
            nuevo_g = g[actual] + mapa.costo(vecino)
            if vecino not in cerrados and nuevo_g < g.get(vecino, float("inf")):
                g[vecino] = nuevo_g
                padres[vecino] = actual
                h = mapa.heuristica(vecino)
                heapq.heappush(frontera, (nuevo_g + h, h, next(desempate), vecino))
                generados += 1
        max_frontera = max(max_frontera, len(frontera))

    return Resultado(nombre, False, nodos_expandidos=expandidos, nodos_generados=generados,
                     max_frontera=max_frontera, orden_expansion=orden, mensaje="No hay salida alcanzable.")


