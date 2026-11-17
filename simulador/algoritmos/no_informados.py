"""
Búsquedas NO informadas: no usan ninguna pista sobre dónde está la salida.

    BFS  - Búsqueda en amplitud     (cola FIFO)
    DFS  - Búsqueda en profundidad  (pila LIFO)

Las dos buscan la salida MÁS CERCANA de entre todas las del mapa: cualquier
celda 'S' cumple la prueba de objetivo.
"""

from __future__ import annotations

from collections import deque

from ..cuadricula import Cuadricula, Posicion
from .base import Resultado, resultado_exitoso, validar_inicio


def bfs(mapa: Cuadricula, inicio: Posicion) -> Resultado:
    """
    Búsqueda en amplitud.

    Explora por "capas": primero todo lo que está a 1 paso, luego a 2, etc.
    Encuentra la ruta con MENOS PASOS, pero ignora el costo del humo, así que
    su ruta puede ser más cara que la de A*.

    Completa: sí.  Óptima en costo: solo si todos los pasos cuestan igual.
    """
    nombre = "BFS"
    if error := validar_inicio(mapa, inicio):
        return Resultado(nombre, False, mensaje=error)

    frontera = deque([inicio])
    padres: dict[Posicion, Posicion | None] = {inicio: None}  # también sirve de "visitados"
    expandidos = generados = 0
    max_frontera = 1
    orden: list[Posicion] = []

    while frontera:
        actual = frontera.popleft()
        expandidos += 1
        orden.append(actual)

        if mapa.es_salida(actual):
            return resultado_exitoso(nombre, mapa, padres, actual, expandidos, generados, max_frontera, orden)

        for vecino in mapa.vecinos(actual):
            if vecino not in padres:
                padres[vecino] = actual
                frontera.append(vecino)
                generados += 1
        max_frontera = max(max_frontera, len(frontera))

    return Resultado(nombre, False, nodos_expandidos=expandidos, nodos_generados=generados,
                     max_frontera=max_frontera, orden_expansion=orden, mensaje="No hay salida alcanzable.")


def dfs(mapa: Cuadricula, inicio: Posicion) -> Resultado:
    """
    Búsqueda en profundidad.

    Sigue un camino hasta el fondo antes de intentar otro. Usa poca memoria,
    pero la primera salida que encuentra suele dar una ruta larga y cara.
    Se marca "visitado" al expandir, como en la versión clásica con pila.

    Completa: sí (en grafos finitos con control de visitados).  Óptima: no.
    """
    nombre = "DFS"
    if error := validar_inicio(mapa, inicio):
        return Resultado(nombre, False, mensaje=error)

    pila: list[Posicion] = [inicio]
    padres: dict[Posicion, Posicion | None] = {inicio: None}
    visitados: set[Posicion] = set()
    expandidos = generados = 0
    max_frontera = 1
    orden: list[Posicion] = []

    while pila:
        actual = pila.pop()
        if actual in visitados:
            continue
        visitados.add(actual)
        expandidos += 1
        orden.append(actual)

        if mapa.es_salida(actual):
            return resultado_exitoso(nombre, mapa, padres, actual, expandidos, generados, max_frontera, orden)

        # Se apilan al revés para que el PRIMER vecino (arriba) sea el primero en salir.
        for vecino in reversed(mapa.vecinos(actual)):
            if vecino not in visitados:
                padres[vecino] = actual
                pila.append(vecino)
                generados += 1
        max_frontera = max(max_frontera, len(pila))

    return Resultado(nombre, False, nodos_expandidos=expandidos, nodos_generados=generados,
                     max_frontera=max_frontera, orden_expansion=orden, mensaje="No hay salida alcanzable.")

