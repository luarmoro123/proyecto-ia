"""
Pruebas del simulador. Ejecutar con:
    python -m pytest -v
"""

import pytest

from simulador import mapas
from simulador.algoritmos import ALGORITMOS, a_estrella, bfs, dfs, greedy, hill_climbing, ucs
from simulador.cuadricula import BLOQUEADAS, Cuadricula
from simulador.memoria import MemoriaRutas

CASOS = [(n, inicio) for n in mapas.nombres() for inicio in mapas.cargar(n)[1]]
IDS = [f"{n}-{i}" for n, i in CASOS]


# --- Mapas ---------------------------------------------------------------------
@pytest.mark.parametrize("nombre", mapas.nombres())
def test_mapas_son_20x20_con_5_inicios_validos(nombre):
    mapa, inicios = mapas.cargar(nombre)
    assert (mapa.filas, mapa.columnas) == (20, 20)
    assert len(inicios) == 5
    assert mapa.salidas, "cada mapa necesita al menos una salida"
    for inicio in inicios:
        assert mapa.transitable(inicio)
        assert not mapa.es_salida(inicio)


def test_costos_y_vecinos():
    mapa = Cuadricula.desde_texto("""
        #####
        #.H.S
        #F#.#
        #####
    """)
    assert mapa.costo((1, 1)) == 1
    assert mapa.costo((1, 2)) == 5
    assert mapa.costo((1, 4)) == 1
    # desde (1,1): arriba muro, abajo fuego, izquierda muro, derecha humo
    assert mapa.vecinos((1, 1)) == [(1, 2)]
    assert mapa.heuristica((1, 1)) == 3


def test_mapa_mal_formado_se_rechaza():
    with pytest.raises(ValueError):
        Cuadricula.desde_texto("...\n..")
    with pytest.raises(ValueError):
        Cuadricula.desde_texto("..X\n...")


# --- Validez de rutas ------------------------------------------------------------
def ruta_es_valida(mapa, inicio, r):
    assert r.ruta[0] == inicio
    for a, b in zip(r.ruta, r.ruta[1:]):
        assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1, "solo movimientos de 1 celda en 4 direcciones"
    for p in r.ruta:
        assert mapa.simbolo(p) not in BLOQUEADAS
    assert r.costo == mapa.costo_ruta(r.ruta)
    if r.exito:
        assert mapa.es_salida(r.ruta[-1])


@pytest.mark.parametrize("nombre,inicio", CASOS, ids=IDS)
@pytest.mark.parametrize("algoritmo", list(ALGORITMOS))
def test_todas_las_rutas_son_validas(nombre, inicio, algoritmo):
    mapa, _ = mapas.cargar(nombre)
    r = ALGORITMOS[algoritmo](mapa, inicio)
    ruta_es_valida(mapa, inicio, r)
    if algoritmo != "Hill Climbing":
        assert r.exito, "los algoritmos completos siempre encuentran salida en estos mapas"


# --- Propiedades teóricas --------------------------------------------------------
@pytest.mark.parametrize("nombre,inicio", CASOS, ids=IDS)
def test_a_estrella_es_optimo_y_expande_menos_que_ucs(nombre, inicio):
    mapa, _ = mapas.cargar(nombre)
    ra, ru = a_estrella(mapa, inicio), ucs(mapa, inicio)
    assert ra.costo == ru.costo
    assert ra.nodos_expandidos <= ru.nodos_expandidos
    for f in (bfs, dfs, greedy):
        assert f(mapa, inicio).costo >= ra.costo


@pytest.mark.parametrize("nombre,inicio", CASOS, ids=IDS)
def test_bfs_da_la_ruta_con_menos_pasos(nombre, inicio):
    mapa, _ = mapas.cargar(nombre)
    pasos_bfs = bfs(mapa, inicio).pasos
    for f in (dfs, ucs, greedy, a_estrella):
        assert f(mapa, inicio).pasos >= pasos_bfs


@pytest.mark.parametrize("nombre", mapas.nombres())
def test_heuristica_es_admisible(nombre):
    """h(n) nunca supera el costo real óptimo (calculado con UCS) desde ninguna celda."""
    mapa, _ = mapas.cargar(nombre)
    for f in range(mapa.filas):
        for c in range(mapa.columnas):
            if mapa.transitable((f, c)):
                r = ucs(mapa, (f, c))
                if r.exito:
                    assert mapa.heuristica((f, c)) <= r.costo


def test_ucs_y_a_estrella_rodean_el_humo_y_bfs_no():
    mapa = Cuadricula.desde_texto("""
        #######
        #.HHH.S
        #.###.#
        #.....#
        #######
    """)
    inicio = (1, 1)
    assert bfs(mapa, inicio).costo == 5 + 5 + 5 + 1 + 1   # cruza el humo: 5 pasos, costo 17
    assert ucs(mapa, inicio).costo == 9                    # rodea por abajo: 9 pasos, costo 9
    assert a_estrella(mapa, inicio).costo == 9
    assert bfs(mapa, inicio).pasos < a_estrella(mapa, inicio).pasos  # BFS: menos pasos, más caro


def test_hill_climbing_se_atora_en_minimo_local():
    # La salida está justo detrás del muro: acercarse en línea recta lleva a un callejón.
    mapa = Cuadricula.desde_texto("""
        #######
        #.....#
        #.###.#
        #.#.#.#
        #...#S#
        #######
    """)
    r = hill_climbing(mapa, (3, 3))
    assert not r.exito
    assert "mínimo local" in r.mensaje
    assert a_estrella(mapa, (3, 3)).exito


def test_sin_salida_alcanzable():
    mapa = Cuadricula.desde_texto("""
        #####
        #..F#
        #FFFS
        #####
    """)
    for f in ALGORITMOS.values():
        assert not f(mapa, (1, 1)).exito


def test_inicio_sobre_muro_es_error():
    mapa, _ = mapas.cargar("Oficina")
    for f in ALGORITMOS.values():
        r = f(mapa, (0, 0))
        assert not r.exito and "muro" in r.mensaje


# --- Memoización -----------------------------------------------------------------
def test_memoria_recuerda_y_aprende_subrutas():
    memoria = MemoriaRutas(archivo=None)
    mapa, inicios = mapas.cargar("Oficina")
    r1, recordado1 = memoria.resolver(mapa, "A*", inicios[0])
    r2, recordado2 = memoria.resolver(mapa, "A*", inicios[0])
    assert not recordado1 and recordado2
    assert r1.ruta == r2.ruta and r1.costo == r2.costo

    # Cualquier celda intermedia de la ruta ya tiene su respuesta aprendida y es óptima.
    intermedia = r1.ruta[len(r1.ruta) // 2]
    r3, recordado3 = memoria.resolver(mapa, "A*", intermedia)
    assert recordado3
    assert r3.costo == ucs(mapa, intermedia).costo


def test_memoria_se_invalida_si_cambia_el_mapa():
    memoria = MemoriaRutas(archivo=None)
    mapa, inicios = mapas.cargar("Escuela")
    memoria.resolver(mapa, "A*", inicios[0])
    otro = mapa.con_celda((1, 1), "#")
    _, recordado = memoria.resolver(otro, "A*", inicios[0])
    assert not recordado


def test_memoria_persiste_en_archivo(tmp_path):
    archivo = tmp_path / "memoria.json"
    mapa, inicios = mapas.cargar("Bodega")
    MemoriaRutas(archivo).resolver(mapa, "UCS", inicios[0])
    _, recordado = MemoriaRutas(archivo).resolver(mapa, "UCS", inicios[0])
    assert recordado
