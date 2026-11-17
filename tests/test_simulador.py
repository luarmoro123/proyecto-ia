"""
Pruebas del simulador. Ejecutar con:
    python -m pytest -v
"""

import heapq

import pytest

from app import app
from simulador import mapas
from simulador.algoritmos import ALGORITMOS, a_estrella, bfs, dfs
from simulador.cuadricula import BLOQUEADAS, Cuadricula

MAPA, INICIOS = mapas.cargar()


def costo_optimo(mapa, inicio):
    """Dijkstra de referencia (solo para las pruebas): costo mínimo a cualquier salida."""
    dist = {inicio: 0}
    cola = [(0, inicio)]
    while cola:
        d, p = heapq.heappop(cola)
        if d > dist[p]:
            continue
        if mapa.es_salida(p):
            return d
        for v in mapa.vecinos(p):
            nd = d + mapa.costo(v)
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(cola, (nd, v))
    return None


# --- Mapa ----------------------------------------------------------------------
def test_mapa_es_20x20_con_5_inicios_validos():
    assert (MAPA.filas, MAPA.columnas) == (20, 20)
    assert len(INICIOS) == 5
    assert MAPA.salidas, "el mapa necesita al menos una zona segura"
    for inicio in INICIOS:
        assert MAPA.transitable(inicio)
        assert not MAPA.es_salida(inicio)


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
    # desde (1,1): arriba roca, abajo fuego, izquierda roca, derecha humo
    assert mapa.vecinos((1, 1)) == [(1, 2)]
    assert mapa.heuristica((1, 1)) == 3


def test_mapa_mal_formado_se_rechaza():
    with pytest.raises(ValueError):
        Cuadricula.desde_texto("...\n..")
    with pytest.raises(ValueError):
        Cuadricula.desde_texto("..X\n...")


# --- Validez de rutas ------------------------------------------------------------
@pytest.mark.parametrize("inicio", INICIOS, ids=str)
@pytest.mark.parametrize("algoritmo", list(ALGORITMOS))
def test_todas_las_rutas_son_validas(inicio, algoritmo):
    r = ALGORITMOS[algoritmo](MAPA, inicio)
    assert r.exito
    assert r.ruta[0] == inicio
    for a, b in zip(r.ruta, r.ruta[1:]):
        assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1, "solo movimientos de 1 celda en 4 direcciones"
    for p in r.ruta:
        assert MAPA.simbolo(p) not in BLOQUEADAS
    assert r.costo == MAPA.costo_ruta(r.ruta)
    assert MAPA.es_salida(r.ruta[-1])
    assert r.orden_expansion[0] == inicio and r.orden_expansion[-1] == r.ruta[-1]


# --- Propiedades teóricas --------------------------------------------------------
@pytest.mark.parametrize("inicio", INICIOS, ids=str)
def test_a_estrella_es_optimo(inicio):
    costo_a = a_estrella(MAPA, inicio).costo
    assert costo_a == costo_optimo(MAPA, inicio)
    assert bfs(MAPA, inicio).costo >= costo_a
    assert dfs(MAPA, inicio).costo >= costo_a


@pytest.mark.parametrize("inicio", INICIOS, ids=str)
def test_bfs_da_la_ruta_con_menos_pasos(inicio):
    pasos_bfs = bfs(MAPA, inicio).pasos
    assert dfs(MAPA, inicio).pasos >= pasos_bfs
    assert a_estrella(MAPA, inicio).pasos >= pasos_bfs


def test_heuristica_es_admisible():
    """h(n) nunca supera el costo real óptimo desde ninguna celda."""
    for f in range(MAPA.filas):
        for c in range(MAPA.columnas):
            if MAPA.transitable((f, c)):
                optimo = costo_optimo(MAPA, (f, c))
                if optimo is not None:
                    assert MAPA.heuristica((f, c)) <= optimo


def test_a_estrella_rodea_el_humo_y_bfs_no():
    mapa = Cuadricula.desde_texto("""
        #######
        #.HHH.S
        #.###.#
        #.....#
        #######
    """)
    inicio = (1, 1)
    assert bfs(mapa, inicio).costo == 5 + 5 + 5 + 1 + 1   # cruza el humo: 5 pasos, costo 17
    assert a_estrella(mapa, inicio).costo == 9             # rodea por abajo: 9 pasos, costo 9
    assert bfs(mapa, inicio).pasos < a_estrella(mapa, inicio).pasos


def test_sin_salida_alcanzable():
    mapa = Cuadricula.desde_texto("""
        #####
        #..F#
        #FFFS
        #####
    """)
    for f in ALGORITMOS.values():
        assert not f(mapa, (1, 1)).exito


def test_inicio_sobre_roca_es_error():
    for f in ALGORITMOS.values():
        r = f(MAPA, (0, 0))
        assert not r.exito and "muro" in r.mensaje


# --- API -------------------------------------------------------------------------
@pytest.fixture
def cliente():
    return app.test_client()


def test_api_mapa(cliente):
    datos = cliente.get("/api/mapa").get_json()
    assert datos["algoritmos"] == ["A*", "BFS", "DFS"]
    assert len(datos["celdas"]) == 20 and len(datos["inicios"]) == 5


def test_api_correr(cliente):
    datos = cliente.post("/api/correr", json={"algoritmo": "A*", "inicio": list(INICIOS[0])}).get_json()
    assert datos["exito"] and datos["costo"] == costo_optimo(MAPA, INICIOS[0])
    assert len(datos["orden_expansion"]) == datos["nodos_expandidos"]


@pytest.mark.parametrize("cuerpo", [
    {"algoritmo": "UCS", "inicio": [1, 1]},
    {"algoritmo": "A*", "inicio": [0, 0]},
    {"algoritmo": "A*"},
])
def test_api_rechaza_peticiones_invalidas(cliente, cuerpo):
    assert cliente.post("/api/correr", json=cuerpo).status_code == 400
