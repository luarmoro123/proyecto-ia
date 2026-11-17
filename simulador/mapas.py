"""
El mapa forestal de prueba (20 x 20) y sus 5 puntos de inicio.

Leyenda:  '.' sendero/pasto   'H' humo   'S' zona segura   '#' roca o río   'F' fuego

Pinar: bosque abierto con focos de fuego rodeados de humo y 4 zonas seguras.
"""

from __future__ import annotations

from .cuadricula import Cuadricula, Posicion

NOMBRE = "Pinar"

PINAR = """
##########S#########
#....##.......#....#
#.........HHH......#
#..##....HFFFH..##.#
#..##....HFFFH..##.#
#.........HHH......#
#....#.............S
#....##...##...##..#
#.........##...##..#
#..HHH.............#
#.HFFFH....##......#
#.HFFFH....##..HHH.#
#..HHH........HFFFH#
#.......##....HFFFH#
S.......##.....HHH.#
#...##.............#
#...##....HHHH.....#
#.........HFFH..##.#
#....###..HHHH..##.#
###########S########
"""

INICIOS: list[Posicion] = [(1, 1), (9, 9), (15, 10), (17, 3), (11, 8)]


def cargar() -> tuple[Cuadricula, list[Posicion]]:
    """Devuelve la cuadrícula y los puntos de inicio del mapa."""
    return Cuadricula.desde_texto(PINAR), list(INICIOS)
