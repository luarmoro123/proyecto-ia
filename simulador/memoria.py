"""
Memoización de rutas: el sistema "recuerda" rutas que ya calculó.

¿Cuándo RAZONA y cuándo APRENDE?

* RAZONA cuando no tiene la respuesta guardada: ejecuta un algoritmo de
  búsqueda y explora el mapa celda por celda (gasta tiempo y nodos).
* APRENDE / RECUERDA cuando guarda ese resultado y, la próxima vez que le
  piden lo mismo (mismo mapa, mismo inicio, mismo algoritmo), contesta de
  inmediato sin explorar nada (0 nodos expandidos).

Además, para A* y UCS (que dan rutas ÓPTIMAS) se aprovecha el principio de
optimalidad: si la ruta óptima de A a la salida pasa por B, entonces el tramo
B -> salida también es óptimo para B. Por eso, al calcular una ruta, se
guardan también todas sus sub-rutas. Así, una persona que empiece en
cualquier celda de esa ruta obtiene su respuesta "aprendida" sin buscar.

La clave incluye una huella del mapa: si se cambia una sola celda del mapa,
las rutas viejas ya no aplican y se vuelve a razonar.

Las rutas se guardan en un archivo JSON, así que la memoria sobrevive entre
ejecuciones del programa.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .algoritmos import ALGORITMOS, Resultado
from .cuadricula import Cuadricula, Posicion

ARCHIVO_POR_DEFECTO = Path(__file__).resolve().parent.parent / "resultados" / "memoria_rutas.json"

# Solo estos algoritmos garantizan rutas óptimas, así que sus sub-rutas también lo son.
ALGORITMOS_OPTIMOS = {"A*", "UCS"}


class MemoriaRutas:
    def __init__(self, archivo: Path | str | None = ARCHIVO_POR_DEFECTO) -> None:
        """Si `archivo` es None la memoria vive solo en RAM (útil para pruebas)."""
        self.archivo = Path(archivo) if archivo else None
        self.rutas: dict[str, dict] = {}
        self.aciertos = 0  # veces que respondió desde memoria
        self.fallos = 0    # veces que tuvo que razonar
        if self.archivo and self.archivo.exists():
            try:
                self.rutas = json.loads(self.archivo.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self.rutas = {}

    # --- Claves ---------------------------------------------------------------
    @staticmethod
    def _id_mapa(mapa: Cuadricula) -> str:
        return hashlib.sha1(mapa.huella().encode()).hexdigest()[:12]

    def _clave(self, mapa: Cuadricula, algoritmo: str, inicio: Posicion) -> str:
        return f"{self._id_mapa(mapa)}|{algoritmo}|{inicio[0]},{inicio[1]}"

    # --- Operaciones ----------------------------------------------------------
    def consultar(self, mapa: Cuadricula, algoritmo: str, inicio: Posicion) -> Resultado | None:
        dato = self.rutas.get(self._clave(mapa, algoritmo, inicio))
        return Resultado.desde_dict(dato) if dato else None

    def guardar(self, mapa: Cuadricula, algoritmo: str, inicio: Posicion, resultado: Resultado) -> int:
        """Guarda el resultado (y sus sub-rutas si es óptimo). Devuelve cuántas entradas nuevas añadió."""
        nuevas = 0
        clave = self._clave(mapa, algoritmo, inicio)
        if clave not in self.rutas:
            nuevas += 1
        self.rutas[clave] = resultado.a_dict()

        if resultado.exito and algoritmo in ALGORITMOS_OPTIMOS:
            for i in range(1, len(resultado.ruta) - 1):
                sub_inicio = resultado.ruta[i]
                sub_clave = self._clave(mapa, algoritmo, sub_inicio)
                if sub_clave in self.rutas:
                    continue
                sub_ruta = resultado.ruta[i:]
                derivado = Resultado(
                    algoritmo=algoritmo,
                    exito=True,
                    ruta=sub_ruta,
                    costo=mapa.costo_ruta(sub_ruta),
                    mensaje=f"Aprendida como sub-ruta de la búsqueda desde {inicio}.",
                )
                self.rutas[sub_clave] = derivado.a_dict()
                nuevas += 1
        self._persistir()
        return nuevas

    def resolver(self, mapa: Cuadricula, algoritmo: str, inicio: Posicion) -> tuple[Resultado, bool]:
        """
        Devuelve (resultado, vino_de_memoria).
        Si ya lo sabe lo recuerda; si no, razona con el algoritmo y lo aprende.
        """
        recordado = self.consultar(mapa, algoritmo, inicio)
        if recordado is not None:
            self.aciertos += 1
            return recordado, True
        self.fallos += 1
        resultado = ALGORITMOS[algoritmo](mapa, inicio)
        self.guardar(mapa, algoritmo, inicio, resultado)
        return resultado, False

    def olvidar(self) -> None:
        self.rutas.clear()
        self.aciertos = self.fallos = 0
        self._persistir()

    def celdas_conocidas(self, mapa: Cuadricula, algoritmo: str) -> list[Posicion]:
        """Celdas desde las que ya se conoce una ruta (para dibujarlas en la interfaz)."""
        prefijo = f"{self._id_mapa(mapa)}|{algoritmo}|"
        celdas = []
        for clave in self.rutas:
            if clave.startswith(prefijo):
                f, c = clave[len(prefijo):].split(",")
                celdas.append((int(f), int(c)))
        return celdas

    def __len__(self) -> int:
        return len(self.rutas)

    def _persistir(self) -> None:
        if self.archivo is None:
            return
        self.archivo.parent.mkdir(parents=True, exist_ok=True)
        self.archivo.write_text(json.dumps(self.rutas), encoding="utf-8")
