"""
Medición de los algoritmos y experimento completo.

Métricas por corrida:
    exito             ¿llegó a una salida?
    costo             suma de costos de la ruta (libre = 1, humo = 5)
    pasos             número de movimientos
    nodos_expandidos  celdas que sacó de la frontera y examinó
    nodos_generados   celdas que metió a la frontera
    max_frontera      tamaño máximo de la frontera (memoria "lógica")
    tiempo_ms         mediana de varias repeticiones (reduce el ruido del sistema)
    memoria_kb        pico de memoria reservada durante la búsqueda (tracemalloc)

El tiempo y la memoria se miden por separado porque tracemalloc hace más
lento el código y alteraría el tiempo.
"""

from __future__ import annotations

import statistics
import time
import tracemalloc
from dataclasses import dataclass
from typing import Callable

from .algoritmos import ALGORITMOS, Resultado
from .cuadricula import Cuadricula, Posicion
from . import mapas as catalogo

FuncionBusqueda = Callable[[Cuadricula, Posicion], Resultado]


@dataclass
class Medicion:
    resultado: Resultado
    tiempo_ms: float
    memoria_kb: float

    def fila(self, mapa: str = "", inicio: Posicion | None = None) -> dict:
        r = self.resultado
        return {
            "mapa": mapa,
            "inicio": str(inicio) if inicio is not None else "",
            "algoritmo": r.algoritmo,
            "exito": r.exito,
            "costo": r.costo if r.exito else None,
            "pasos": r.pasos if r.exito else None,
            "nodos_expandidos": r.nodos_expandidos,
            "nodos_generados": r.nodos_generados,
            "max_frontera": r.max_frontera,
            "tiempo_ms": round(self.tiempo_ms, 4),
            "memoria_kb": round(self.memoria_kb, 2),
            "mensaje": r.mensaje,
        }


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


def comparar(mapa: Cuadricula, inicio: Posicion, repeticiones: int = 7) -> dict[str, Medicion]:
    """Corre los 6 algoritmos sobre el mismo mapa e inicio."""
    return {nombre: medir(f, mapa, inicio, repeticiones) for nombre, f in ALGORITMOS.items()}


def experimento_completo(repeticiones: int = 7) -> list[dict]:
    """3 mapas x 5 inicios x 6 algoritmos = 90 corridas. Devuelve una fila por corrida."""
    filas = []
    for nombre_mapa in catalogo.nombres():
        mapa, inicios = catalogo.cargar(nombre_mapa)
        for inicio in inicios:
            for medicion in comparar(mapa, inicio, repeticiones).values():
                filas.append(medicion.fila(nombre_mapa, inicio))
    return filas


def agregar_optimalidad(filas: list[dict]) -> list[dict]:
    """
    Agrega la columna `exceso_costo_%`: cuánto más cara es cada ruta respecto
    a la óptima (la de UCS) en el mismo mapa e inicio. 0 % = ruta óptima.
    """
    optimos = {(f["mapa"], f["inicio"]): f["costo"] for f in filas if f["algoritmo"] == "UCS"}
    for f in filas:
        opt = optimos.get((f["mapa"], f["inicio"]))
        if f["exito"] and opt:
            f["exceso_costo_%"] = round(100 * (f["costo"] - opt) / opt, 1)
        else:
            f["exceso_costo_%"] = None
    return filas
