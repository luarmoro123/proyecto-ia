"""
Representación del edificio como una cuadrícula.

Cada celda guarda un símbolo:

    '.'  libre   -> se puede pisar, costo 1
    'H'  humo    -> se puede pisar, costo 5
    'S'  salida  -> se puede pisar, costo 1 (es el objetivo)
    '#'  muro    -> bloqueada
    'F'  fuego   -> bloqueada (el fuego no se propaga durante la simulación)

Una posición es una tupla (fila, columna) con origen arriba a la izquierda.
La persona se mueve solo en 4 direcciones: arriba, abajo, izquierda, derecha.

El costo de un movimiento es el costo de la celda a la que se ENTRA.
La celda de inicio no se cobra.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --- Símbolos -----------------------------------------------------------------
LIBRE = "."
HUMO = "H"
SALIDA = "S"
MURO = "#"
FUEGO = "F"

SIMBOLOS_VALIDOS = {LIBRE, HUMO, SALIDA, MURO, FUEGO}
BLOQUEADAS = {MURO, FUEGO}

COSTOS = {LIBRE: 1, SALIDA: 1, HUMO: 5}

# Orden fijo de exploración de vecinos. Es importante que sea siempre el mismo
# para que todos los algoritmos sean deterministas y los resultados repetibles.
MOVIMIENTOS = (
    (-1, 0),  # arriba
    (1, 0),   # abajo
    (0, -1),  # izquierda
    (0, 1),   # derecha
)

Posicion = tuple[int, int]


@dataclass
class Cuadricula:
    """Edificio de `filas x columnas` celdas."""

    celdas: list[list[str]]
    filas: int = field(init=False)
    columnas: int = field(init=False)
    salidas: list[Posicion] = field(init=False)

    def __post_init__(self) -> None:
        if not self.celdas:
            raise ValueError("La cuadrícula está vacía.")
        self.filas = len(self.celdas)
        self.columnas = len(self.celdas[0])
        for i, fila in enumerate(self.celdas):
            if len(fila) != self.columnas:
                raise ValueError(f"La fila {i} mide {len(fila)} y debería medir {self.columnas}.")
            for j, s in enumerate(fila):
                if s not in SIMBOLOS_VALIDOS:
                    raise ValueError(f"Símbolo desconocido {s!r} en ({i}, {j}).")
        self.salidas = [
            (i, j)
            for i in range(self.filas)
            for j in range(self.columnas)
            if self.celdas[i][j] == SALIDA
        ]

    # --- Construcción ---------------------------------------------------------
    @classmethod
    def desde_texto(cls, texto: str | list[str]) -> "Cuadricula":
        """Crea la cuadrícula a partir de líneas de texto (una por fila)."""
        lineas = texto.strip().splitlines() if isinstance(texto, str) else texto
        return cls([list(linea.strip()) for linea in lineas if linea.strip()])

    def a_texto(self) -> str:
        return "\n".join("".join(fila) for fila in self.celdas)

    def huella(self) -> str:
        """Texto que identifica de forma única el contenido del mapa (se usa en la caché)."""
        return "".join("".join(fila) for fila in self.celdas)

    # --- Consultas básicas ----------------------------------------------------
    def dentro(self, pos: Posicion) -> bool:
        f, c = pos
        return 0 <= f < self.filas and 0 <= c < self.columnas

    def simbolo(self, pos: Posicion) -> str:
        return self.celdas[pos[0]][pos[1]]

    def transitable(self, pos: Posicion) -> bool:
        return self.dentro(pos) and self.simbolo(pos) not in BLOQUEADAS

    def es_salida(self, pos: Posicion) -> bool:
        return self.simbolo(pos) == SALIDA

    def costo(self, pos: Posicion) -> int:
        """Costo de ENTRAR a la celda `pos`."""
        return COSTOS[self.simbolo(pos)]

    def vecinos(self, pos: Posicion) -> list[Posicion]:
        """Celdas transitables alcanzables en un paso, en el orden de MOVIMIENTOS."""
        f, c = pos
        resultado = []
        for df, dc in MOVIMIENTOS:
            nueva = (f + df, c + dc)
            if self.transitable(nueva):
                resultado.append(nueva)
        return resultado

    # --- Heurística -----------------------------------------------------------
    def heuristica(self, pos: Posicion) -> int:
        """
        Distancia Manhattan a la salida MÁS CERCANA.

        Es admisible: cada paso cuesta al menos 1 y necesitamos al menos
        |df| + |dc| pasos para llegar a una salida, así que nunca sobreestima.
        También es consistente: al movernos un paso, h cambia como mucho en 1,
        y ese paso cuesta >= 1.
        """
        if not self.salidas:
            return 0
        f, c = pos
        return min(abs(f - sf) + abs(c - sc) for sf, sc in self.salidas)

    # --- Utilidades -----------------------------------------------------------
    def costo_ruta(self, ruta: list[Posicion]) -> int:
        """Suma de los costos de cada celda a la que se entra (sin contar el inicio)."""
        return sum(self.costo(p) for p in ruta[1:])

    def copia(self) -> "Cuadricula":
        return Cuadricula([fila[:] for fila in self.celdas])

    def con_celda(self, pos: Posicion, simbolo: str) -> "Cuadricula":
        """Devuelve una copia con una celda cambiada (útil para el editor)."""
        nueva = self.copia()
        nueva.celdas[pos[0]][pos[1]] = simbolo
        nueva.__post_init__()
        return nueva
