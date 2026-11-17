"""
Medición de los algoritmos.

    tiempo_ms   mediana de varias repeticiones (reduce el ruido del sistema)
    memoria_kb  pico de memoria reservada durante la búsqueda (tracemalloc)

El tiempo y la memoria se miden por separado porque tracemalloc hace más
lento el código y alteraría el tiempo.
"""

from __future__ import annotations

import statistics
import time
import tracemalloc
from dataclasses import dataclass
from typing import Callable

from .algoritmos import Resultado
from .cuadricula import Cuadricula, Posicion

FuncionBusqueda = Callable[[Cuadricula, Posicion], Resultado]


@dataclass
class Medicion:
    resultado: Resultado
    tiempo_ms: float
    memoria_kb: float


def medir(funcion: FuncionBusqueda, mapa: Cuadricula, inicio: Posicion, repeticiones: int = 7) -> Medicion:
    """Ejecuta `funcion` varias veces y devuelve el resultado con su tiempo y memoria."""
    tiempos = []
    resultado = None
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        resultado = funcion(mapa, inicio)
        tiempos.append((time.perf_counter() - t0) * 1000)

    tracemalloc.start()
    tracemalloc.reset_peak()
    funcion(mapa, inicio)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return Medicion(resultado, statistics.median(tiempos), pico / 1024)
