"""Los 3 algoritmos de búsqueda, programados a mano (sin librerías de búsqueda)."""

from .base import Resultado
from .informados import a_estrella
from .no_informados import bfs, dfs

# Nombre visible -> función. A* va primero porque es el algoritmo principal.
ALGORITMOS = {
    "A*": a_estrella,
    "BFS": bfs,
    "DFS": dfs,
}

__all__ = ["ALGORITMOS", "Resultado", "a_estrella", "bfs", "dfs"]
