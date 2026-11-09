"""
Los 3 mapas de prueba (20 x 20) y los 5 puntos de inicio de cada uno.

Leyenda:  '.' libre   'H' humo   'S' salida   '#' muro   'F' fuego

Cada mapa está pensado para poner a prueba algo distinto:

* Oficina  : cuartos con puertas y 3 salidas. Caso "normal".
* Escuela  : un pasillo central lleno de humo. Ir derecho es corto en pasos
             pero caro en costo; sirve para ver la diferencia entre BFS
             (menos pasos) y UCS/A* (menor costo).
* Bodega   : pasillos en espiral y callejones. La salida "parece" cerca
             pero hay que rodear; aquí Hill Climbing y Greedy se equivocan.
"""

from __future__ import annotations

from .cuadricula import Cuadricula, Posicion

OFICINA = """
#########S##########
#......#.....#.....#
#......#.....#.....#
#..HH..#..F..#..H..#
#..HH.........HHH..#
#......#.....#.....#
####.###.....####.##
#.........FF.......#
#..HHHH...FF...HHH.#
#.........FF.......#
##.####.######.#####
#....#.......#.....#
#....#..HHH..#..F..#
#....#..HHH..#.....#
#..F.....H.........S
#....#.......#.....#
######.#####.###.###
#.....H.....H......#
#..FF...HHHHH...F..#
#########S##########
"""

ESCUELA = """
####################
#.....#......#.....#
#.HH..#..HH..#..HH.#
#.HH..#..HH..#..HH.#
#.....#......#.....#
###.#####.######.###
S..HHHHHHHHHHHHHH..S
#..HHHHHFFFFHHHHH..#
###.#####FF#####.###
#.....#..FF..#.....#
#.....#......#.....#
#..F..#..HH..#..F..#
#.....#......#.....#
###.######.#######.#
#.....HHHHHHHHH....#
#.##########.#####.#
#.#........#.#...#.#
#.#..HHH...#.#.F.#.#
#....HHH.....#.....#
##########S#########
"""

BODEGA = """
####################
#..................S
#.##############.#.#
#.#............#.#.#
#.#.##########.#.#.#
#.#.#........#.#.#.#
#.#.#.######.#.#.#.#
#.#.#.#....#.#.#.#.#
#...#.#.FF.#.#...#.#
#####.#.FF.#.#####.#
#.....#....#.......#
#.#####HHHH#######.#
#.....HHHHHH.......#
#.###########.####.#
#.#.........#.#....#
#.#.FFF.HHH.#.#.##.#
#.#.........#.#..#.#
#.#####.#####.##.#.#
#.......H........#.S
####################
"""

# nombre -> (texto del mapa, lista de 5 puntos de inicio)
MAPAS: dict[str, tuple[str, list[Posicion]]] = {
    "Oficina": (OFICINA, [(1, 1), (8, 1), (12, 7), (17, 1), (5, 17)]),
    "Escuela": (ESCUELA, [(1, 9), (10, 1), (10, 10), (17, 9), (16, 15)]),
    "Bodega": (BODEGA, [(7, 8), (5, 9), (14, 5), (10, 1), (16, 16)]),
}


def cargar(nombre: str) -> tuple[Cuadricula, list[Posicion]]:
    """Devuelve la cuadrícula y los puntos de inicio del mapa `nombre`."""
    texto, inicios = MAPAS[nombre]
    return Cuadricula.desde_texto(texto), list(inicios)


def nombres() -> list[str]:
    return list(MAPAS)
