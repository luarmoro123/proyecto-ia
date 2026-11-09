"""
Piezas comunes a todos los algoritmos de búsqueda.

Convenciones que siguen los 6 algoritmos (para que la comparación sea justa):

* La prueba de objetivo se hace al EXPANDIR un nodo (al sacarlo de la frontera),
  no al generarlo. Así "nodos expandidos" significa lo mismo en todos.
* Los vecinos se generan siempre en el mismo orden: arriba, abajo, izquierda, derecha.
* Los empates en colas de prioridad se rompen por orden de llegada (FIFO),
  usando un contador incremental.
* Todos son búsqueda en GRAFO: recuerdan qué celdas ya visitaron para no
  repetirlas (salvo Hill Climbing, que no guarda historial).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..cuadricula import Cuadricula, Posicion


@dataclass
class Resultado:
    """Lo que devuelve cualquier algoritmo de búsqueda."""

    algoritmo: str
    exito: bool
    ruta: list[Posicion] = field(default_factory=list)
    costo: int = 0
    nodos_expandidos: int = 0
    nodos_generados: int = 0
    max_frontera: int = 0
    # Orden en el que se expandieron las celdas (para dibujarlas en la interfaz).
    orden_expansion: list[Posicion] = field(default_factory=list)
    mensaje: str = ""

    @property
    def pasos(self) -> int:
        """Número de movimientos de la ruta (celdas - 1)."""
        return max(len(self.ruta) - 1, 0)

    def a_dict(self) -> dict:
        """Versión serializable (se usa en la caché JSON)."""
        return {
            "algoritmo": self.algoritmo,
            "exito": self.exito,
            "ruta": [list(p) for p in self.ruta],
            "costo": self.costo,
            "nodos_expandidos": self.nodos_expandidos,
            "nodos_generados": self.nodos_generados,
            "max_frontera": self.max_frontera,
            "orden_expansion": [list(p) for p in self.orden_expansion],
            "mensaje": self.mensaje,
        }

    @classmethod
    def desde_dict(cls, d: dict) -> "Resultado":
        return cls(
            algoritmo=d["algoritmo"],
            exito=d["exito"],
            ruta=[tuple(p) for p in d["ruta"]],
            costo=d["costo"],
            nodos_expandidos=d["nodos_expandidos"],
            nodos_generados=d["nodos_generados"],
            max_frontera=d["max_frontera"],
            orden_expansion=[tuple(p) for p in d["orden_expansion"]],
            mensaje=d.get("mensaje", ""),
        )


def reconstruir_ruta(padres: dict[Posicion, Posicion | None], meta: Posicion) -> list[Posicion]:
    """Sigue los punteros a padre desde la meta hasta el inicio y voltea la lista."""
    ruta = []
    actual: Posicion | None = meta
    while actual is not None:
        ruta.append(actual)
        actual = padres[actual]
    ruta.reverse()
    return ruta


def resultado_exitoso(
    nombre: str,
    mapa: Cuadricula,
    padres: dict[Posicion, Posicion | None],
    meta: Posicion,
    expandidos: int,
    generados: int,
    max_frontera: int,
    orden: list[Posicion],
) -> Resultado:
    ruta = reconstruir_ruta(padres, meta)
    return Resultado(
        algoritmo=nombre,
        exito=True,
        ruta=ruta,
        costo=mapa.costo_ruta(ruta),
        nodos_expandidos=expandidos,
        nodos_generados=generados,
        max_frontera=max_frontera,
        orden_expansion=orden,
        mensaje=f"Llegó a la salida {meta}.",
    )


def validar_inicio(mapa: Cuadricula, inicio: Posicion) -> str | None:
    """Devuelve un mensaje de error si el inicio no sirve, o None si está bien."""
    if not mapa.dentro(inicio):
        return "El inicio está fuera del mapa."
    if not mapa.transitable(inicio):
        return "El inicio está sobre un muro o fuego."
    if not mapa.salidas:
        return "El mapa no tiene salidas."
    return None
