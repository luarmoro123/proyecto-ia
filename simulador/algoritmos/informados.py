"""
Búsquedas INFORMADAS: usan la heurística h(n) = distancia Manhattan a la
salida más cercana para decidir qué explorar primero.

    Greedy Best-First - solo mira h(n)               (rápida, no óptima)
    A*                - mira f(n) = g(n) + h(n)      (óptima con h admisible)
    Hill Climbing     - se mueve al vecino con menor h, sin vuelta atrás
                        (puede quedarse atorada en un mínimo local)
"""

from __future__ import annotations

import heapq
from itertools import count

from ..cuadricula import Cuadricula, Posicion
from .base import Resultado, resultado_exitoso, validar_inicio


def greedy(mapa: Cuadricula, inicio: Posicion) -> Resultado:
    """
    Búsqueda voraz primero el mejor (Greedy Best-First).

    Expande la celda que "parece" más cerca de una salida según h(n), sin
    importar cuánto costó llegar ahí. Suele expandir muy pocos nodos, pero
    puede meterse en un callejón o atravesar humo y dar una ruta cara.

    Completa: sí (búsqueda en grafo finita).  Óptima: no.
    """
    nombre = "Greedy"
    if error := validar_inicio(mapa, inicio):
        return Resultado(nombre, False, mensaje=error)

    desempate = count()
    frontera = [(mapa.heuristica(inicio), next(desempate), inicio)]
    padres: dict[Posicion, Posicion | None] = {inicio: None}  # también marca "ya generado"
    cerrados: set[Posicion] = set()
    expandidos = generados = 0
    max_frontera = 1
    orden: list[Posicion] = []

    while frontera:
        _, _, actual = heapq.heappop(frontera)
        if actual in cerrados:
            continue
        cerrados.add(actual)
        expandidos += 1
        orden.append(actual)

        if mapa.es_salida(actual):
            return resultado_exitoso(nombre, mapa, padres, actual, expandidos, generados, max_frontera, orden)

        for vecino in mapa.vecinos(actual):
            if vecino not in padres:
                padres[vecino] = actual
                heapq.heappush(frontera, (mapa.heuristica(vecino), next(desempate), vecino))
                generados += 1
        max_frontera = max(max_frontera, len(frontera))

    return Resultado(nombre, False, nodos_expandidos=expandidos, nodos_generados=generados,
                     max_frontera=max_frontera, orden_expansion=orden, mensaje="No hay salida alcanzable.")


def a_estrella(mapa: Cuadricula, inicio: Posicion) -> Resultado:
    """
    A* (algoritmo principal del proyecto).

    Ordena la frontera por f(n) = g(n) + h(n):
      g(n) = costo real desde el inicio (cuenta el humo como 5),
      h(n) = Manhattan a la salida más cercana (estimación optimista).

    Como h nunca sobreestima (admisible) y es consistente, la primera salida
    que se expande es la de menor costo, igual que UCS, pero explorando
    menos celdas porque h "empuja" la búsqueda hacia las salidas.
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


def hill_climbing(mapa: Cuadricula, inicio: Posicion) -> Resultado:
    """
    Ascenso de colinas, versión de máxima pendiente (steepest ascent).

    Como queremos MINIMIZAR la distancia, "subir" significa bajar h(n):
    en cada paso mira a todos sus vecinos y se mueve al que tenga menor h,
    pero SOLO si es estrictamente mejor que la celda actual. Si ningún vecino
    mejora, se detiene: está en un mínimo local (por ejemplo, pegado a un muro
    detrás del cual está la salida) y reporta que NO llegó.

    No guarda frontera ni visitados: memoria casi nula, pero sin vuelta atrás.

    Completa: no.  Óptima: no.
    """
    nombre = "Hill Climbing"
    if error := validar_inicio(mapa, inicio):
        return Resultado(nombre, False, mensaje=error)

    actual = inicio
    ruta = [actual]
    expandidos = generados = 0
    orden: list[Posicion] = []

    while True:
        expandidos += 1
        orden.append(actual)
        if mapa.es_salida(actual):
            return Resultado(nombre, True, ruta=ruta, costo=mapa.costo_ruta(ruta),
                             nodos_expandidos=expandidos, nodos_generados=generados,
                             max_frontera=1, orden_expansion=orden,
                             mensaje=f"Llegó a la salida {actual}.")

        vecinos = mapa.vecinos(actual)
        generados += len(vecinos)
        if not vecinos:
            break
        # min() se queda con el primero en caso de empate (orden arriba, abajo, izq, der).
        mejor = min(vecinos, key=mapa.heuristica)
        if mapa.heuristica(mejor) >= mapa.heuristica(actual):
            break  # ningún vecino mejora: mínimo local o meseta
        actual = mejor
        ruta.append(actual)

    return Resultado(nombre, False, ruta=ruta, costo=mapa.costo_ruta(ruta),
                     nodos_expandidos=expandidos, nodos_generados=generados,
                     max_frontera=1, orden_expansion=orden,
                     mensaje=f"Se atoró en un mínimo local en {actual} (h = {mapa.heuristica(actual)}).")
