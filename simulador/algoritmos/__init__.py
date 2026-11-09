"""Los 6 algoritmos de búsqueda, programados a mano (sin librerías de búsqueda)."""

from .base import Resultado
from .informados import a_estrella, greedy, hill_climbing
from .no_informados import bfs, dfs, ucs

# Nombre visible -> función. A* va primero porque es el algoritmo principal.
ALGORITMOS = {
    "A*": a_estrella,
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
    "Greedy": greedy,
    "Hill Climbing": hill_climbing,
}

__all__ = ["ALGORITMOS", "Resultado", "a_estrella", "bfs", "dfs", "greedy", "hill_climbing", "ucs"]
