"""
Genera los diagramas del reporte técnico en `docs/diagramas/`:

    grafo_espacio_estados.png  El mapa Escuela modelado como grafo (sección 3.5)
    grafo_ejemplo_costos.png   Un fragmento pequeño con costos, g, h y f (sección 3.5 / 4.2)
    caso_de_uso.png            Diagrama de caso de uso (sección 2.3)
    componentes.png            Diagrama de componentes (sección 3.4)

Uso:
    python diagramas.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch

from simulador import mapas
from simulador.algoritmos import a_estrella
from simulador.cuadricula import HUMO, SALIDA, Cuadricula

CARPETA = Path(__file__).resolve().parent / "docs" / "diagramas"

C_LIBRE = "#9aa5b1"
C_HUMO = "#8a63d2"
C_SALIDA = "#2e9e5b"
C_INICIO = "#f2b705"
C_RUTA = "#1f6feb"
C_ARISTA = "#c9ced6"
C_ARISTA_HUMO = "#d9c7f5"


# =============================================================================
# 1. Grafo del espacio de estados (mapa completo)
# =============================================================================
def grafo_espacio_estados(nombre: str = "Escuela", indice_inicio: int = 0) -> Path:
    """
    Cada celda transitable es un NODO (estado). Cada par de celdas vecinas
    transitables forma una ARISTA (acción de moverse). El peso de la arista
    es el costo de la celda destino: 1 si es libre o salida, 5 si es humo.
    Muros y fuego no son nodos: el agente nunca puede estar ahí.
    """
    mapa, inicios = mapas.cargar(nombre)
    inicio = inicios[indice_inicio]
    ruta = a_estrella(mapa, inicio).ruta
    aristas_ruta = {frozenset(par) for par in zip(ruta, ruta[1:])}

    fig, ax = plt.subplots(figsize=(10, 10.6))
    nodos = [(f, c) for f in range(mapa.filas) for c in range(mapa.columnas) if mapa.transitable((f, c))]

    # Aristas (cada una se dibuja una vez: solo hacia abajo y hacia la derecha)
    n_aristas = 0
    for f, c in nodos:
        for vecino in ((f + 1, c), (f, c + 1)):
            if not mapa.transitable(vecino):
                continue
            n_aristas += 1
            en_ruta = frozenset(((f, c), vecino)) in aristas_ruta
            con_humo = HUMO in (mapa.simbolo((f, c)), mapa.simbolo(vecino))
            color = C_RUTA if en_ruta else (C_ARISTA_HUMO if con_humo else C_ARISTA)
            ax.plot([c, vecino[1]], [f, vecino[0]], color=color,
                    linewidth=3.2 if en_ruta else 1.2, zorder=3 if en_ruta else 1, solid_capstyle="round")

    # Nodos
    for f, c in nodos:
        s = mapa.simbolo((f, c))
        color, tam = C_LIBRE, 38
        if s == HUMO:
            color = C_HUMO
        if s == SALIDA:
            color, tam = C_SALIDA, 190
        if (f, c) == inicio:
            color, tam = C_INICIO, 220
        ax.scatter(c, f, s=tam, color=color, edgecolors="white", linewidths=0.8, zorder=4)

    ax.annotate("Inicio\n" + str(inicio), (inicio[1], inicio[0]), xytext=(inicio[1] + 2.2, inicio[0] - 1.6),
                fontsize=9, fontweight="bold", arrowprops=dict(arrowstyle="-", color="#555"), zorder=6)
    for sf, sc in mapa.salidas:
        if sc == 0:
            xy, ha, va = (sc + 0.1, sf - 0.55), "left", "bottom"
        elif sc == mapa.columnas - 1:
            xy, ha, va = (sc - 0.1, sf - 0.55), "right", "bottom"
        else:
            xy, ha, va = (sc + 0.55, sf + 0.05), "left", "center"
        ax.text(*xy, f"Salida ({sf}, {sc})", ha=ha, va=va, fontsize=9, fontweight="bold", color=C_SALIDA, zorder=6,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.8, alpha=0.9))

    ax.set_xlim(-1, mapa.columnas)
    ax.set_ylim(mapa.filas, -1.2)
    ax.set_aspect("equal")
    ax.set_xticks(range(0, mapa.columnas, 2))
    ax.set_yticks(range(0, mapa.filas, 2))
    ax.tick_params(labelsize=8, length=0)
    ax.set_xlabel("columna", fontsize=9)
    ax.set_ylabel("fila", fontsize=9)
    for borde in ax.spines.values():
        borde.set_visible(False)

    costo = mapa.costo_ruta(ruta)
    ax.set_title(f"Espacio de estados del mapa «{nombre}» como grafo\n"
                 f"{len(nodos)} nodos (estados) · {n_aristas} aristas (acciones) · "
                 f"ruta de A*: {len(ruta) - 1} pasos, costo {costo}", fontsize=12)
    leyenda = [
        Line2D([], [], marker="o", ls="", color=C_LIBRE, markersize=7, label="Nodo libre (costo de entrar = 1)"),
        Line2D([], [], marker="o", ls="", color=C_HUMO, markersize=7, label="Nodo con humo (costo de entrar = 5)"),
        Line2D([], [], marker="o", ls="", color=C_SALIDA, markersize=11, label="Nodo meta (salida)"),
        Line2D([], [], marker="o", ls="", color=C_INICIO, markersize=11, label="Estado inicial"),
        Line2D([], [], color=C_ARISTA, lw=2, label="Arista (moverse ↑ ↓ ← →)"),
        Line2D([], [], color=C_ARISTA_HUMO, lw=2, label="Arista que toca humo"),
        Line2D([], [], color=C_RUTA, lw=3.2, label="Ruta óptima encontrada por A*"),
    ]
    ax.legend(handles=leyenda, loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=3, fontsize=8.5, frameon=False)
    fig.text(0.5, 0.012, "Muros (#) y fuego (F) no son nodos: son estados inalcanzables. "
             "Los huecos del grafo corresponden a ellos.", ha="center", fontsize=8.5, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    destino = CARPETA / "grafo_espacio_estados.png"
    fig.savefig(destino, dpi=170)
    plt.close(fig)
    return destino


# =============================================================================
# 2. Fragmento pequeño con pesos, g, h y f
# =============================================================================
EJEMPLO = """
#######
#.HH.S#
#.###.#
#.....#
#######
"""


def grafo_ejemplo_costos() -> Path:
    """
    Grafo pequeño para explicar el modelo: aristas DIRIGIDAS con el costo de
    entrar a la celda destino, y en cada nodo los valores g, h y f = g + h que
    calcula A* desde el inicio. Las aristas hacia el humo cuestan 5.
    """
    mapa = Cuadricula.desde_texto(EJEMPLO)
    inicio = (1, 1)
    ruta = a_estrella(mapa, inicio).ruta
    en_ruta = set(zip(ruta, ruta[1:]))

    # g real (costo mínimo) de cada nodo, calculado con un Dijkstra simple
    import heapq
    g = {inicio: 0}
    cola = [(0, inicio)]
    while cola:
        d, n = heapq.heappop(cola)
        if d > g[n]:
            continue
        for v in mapa.vecinos(n):
            nd = d + mapa.costo(v)
            if nd < g.get(v, 1e9):
                g[v] = nd
                heapq.heappush(cola, (nd, v))

    escala = 2.4
    pos = {n: (n[1] * escala, -n[0] * escala) for n in g}
    fig, ax = plt.subplots(figsize=(11, 5.6))

    for n in g:
        for v in mapa.vecinos(n):
            (x1, y1), (x2, y2) = pos[n], pos[v]
            dx, dy = x2 - x1, y2 - y1
            largo = (dx * dx + dy * dy) ** 0.5
            ux, uy = dx / largo, dy / largo
            # cada sentido va desplazado a un lado para que ida y vuelta no se encimen
            ox, oy = -uy * 0.17, ux * 0.17
            recorte = 0.86 if dx else 0.72  # radio del nodo en esa dirección
            ruta_flecha = (n, v) in en_ruta
            costo = mapa.costo(v)
            color = C_RUTA if ruta_flecha else (C_HUMO if costo == 5 else "#8c8c8c")
            flecha = FancyArrowPatch((x1 + ux * recorte + ox, y1 + uy * recorte + oy),
                                     (x2 - ux * recorte + ox, y2 - uy * recorte + oy),
                                     arrowstyle="-|>", mutation_scale=13, color=color,
                                     linewidth=2.6 if ruta_flecha else 1.2, zorder=5)
            ax.add_patch(flecha)
            ax.text(x1 + dx * 0.5 + ox * 2.2, y1 + dy * 0.5 + oy * 2.2, str(costo), fontsize=8.5,
                    ha="center", va="center", color=color, fontweight="bold", zorder=6)

    for n, (x, y) in pos.items():
        s = mapa.simbolo(n)
        color = C_SALIDA if s == SALIDA else (C_HUMO if s == HUMO else ("#fff3c4" if n == inicio else "#eef1f4"))
        borde = C_INICIO if n == inicio else (C_RUTA if n in ruta else "#9aa5b1")
        ax.add_patch(Ellipse((x, y), 1.55, 1.25, facecolor=color, edgecolor=borde, linewidth=2.2, zorder=4))
        texto_color = "white" if s in (SALIDA, HUMO) else "#1f1f1f"
        h = mapa.heuristica(n)
        ax.text(x, y + 0.27, f"{n}", ha="center", va="center", fontsize=8.5, fontweight="bold", color=texto_color, zorder=5)
        ax.text(x, y - 0.22, f"g={g[n]} h={h}\nf={g[n] + h}", ha="center", va="center", fontsize=7, color=texto_color, zorder=5)

    ax.set_xlim(min(x for x, _ in pos.values()) - 1.4, max(x for x, _ in pos.values()) + 1.4)
    ax.set_ylim(min(y for _, y in pos.values()) - 1.2, max(y for _, y in pos.values()) + 1.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Fragmento del espacio de estados con costos de transición\n"
                 "Cada flecha lleva el costo de ENTRAR a la celda destino.\n"
                 "En cada nodo: g = costo real mínimo, h = Manhattan a la salida, f = g + h", fontsize=11)
    leyenda = [
        Line2D([], [], color="#8c8c8c", lw=1.5, label="Transición a celda libre o salida (costo 1)"),
        Line2D([], [], color=C_HUMO, lw=1.5, label="Transición a celda con humo (costo 5)"),
        Line2D([], [], color=C_RUTA, lw=2.4, label=f"Ruta óptima (costo {mapa.costo_ruta(ruta)})"),
    ]
    ax.legend(handles=leyenda, loc="lower center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=8.5, frameon=False)
    fig.tight_layout()
    destino = CARPETA / "grafo_ejemplo_costos.png"
    fig.savefig(destino, dpi=170, bbox_inches="tight")
    plt.close(fig)
    return destino


# =============================================================================
# 3. Diagrama de caso de uso (UML)
# =============================================================================
def _actor(ax, x, y, nombre):
    ax.add_patch(plt.Circle((x, y + 0.55), 0.18, fill=False, lw=1.6))
    ax.plot([x, x], [y + 0.37, y - 0.15], color="black", lw=1.6)
    ax.plot([x - 0.3, x + 0.3], [y + 0.18, y + 0.18], color="black", lw=1.6)
    ax.plot([x, x - 0.25], [y - 0.15, y - 0.55], color="black", lw=1.6)
    ax.plot([x, x + 0.25], [y - 0.15, y - 0.55], color="black", lw=1.6)
    ax.text(x, y - 0.8, nombre, ha="center", va="top", fontsize=9.5, fontweight="bold")


def _caso(ax, x, y, texto, ancho=3.3):
    ax.add_patch(Ellipse((x, y), ancho, 0.78, facecolor="#fdf1ec", edgecolor="#b23a1f", lw=1.4, zorder=2))
    ax.text(x, y, texto, ha="center", va="center", fontsize=8.6, zorder=3)


def _linea(ax, a, b, estilo="-", texto=None, flecha=False):
    if flecha:
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="->", mutation_scale=12, ls=estilo, color="#444", lw=1.1, zorder=1))
    else:
        ax.plot([a[0], b[0]], [a[1], b[1]], ls=estilo, color="#444", lw=1.1, zorder=1)
    if texto:
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 0.12, texto, fontsize=7.5, ha="center", color="#444",
                style="italic", bbox=dict(facecolor="white", edgecolor="none", pad=0.5))


def caso_de_uso() -> Path:
    fig, ax = plt.subplots(figsize=(12, 7.6))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((2.9, 0.6), 9.8, 8.8, boxstyle="round,pad=0.05", fill=False, lw=1.5))
    ax.text(7.8, 9.0, "Sistema: Simulador de escape de incendios", ha="center", fontsize=11, fontweight="bold")

    _actor(ax, 1.2, 5.6, "Usuario\n(estudiante/evaluador)")
    _actor(ax, 14.8, 5.6, "Agente evacuador\n(A* y otros 5)")

    casos = {
        "mapa": (5.2, 8.1, "Seleccionar mapa"),
        "editar": (5.2, 6.9, "Diseñar / editar el edificio\n(muro, fuego, humo, salida)"),
        "inicio": (5.2, 5.7, "Elegir punto de inicio"),
        "algoritmo": (5.2, 4.5, "Elegir algoritmo de búsqueda"),
        "ruta": (10.4, 7.6, "Calcular ruta de evacuación"),
        "ver": (10.4, 6.2, "Visualizar ruta y\nnodos expandidos"),
        "comparar": (5.2, 3.1, "Comparar los 6 algoritmos"),
        "experimento": (5.2, 1.6, "Ejecutar experimento\n(90 corridas)"),
        "metricas": (10.4, 3.1, "Calcular métricas\n(costo, nodos, tiempo, memoria)"),
        "memoria": (10.4, 4.7, "Consultar memoria de rutas\n(razonar / recordar)"),
        "exportar": (10.4, 1.4, "Descargar resultados (CSV)"),
    }
    R = 1.95  # medio ancho de cada elipse
    for x, y, t in casos.values():
        _caso(ax, x, y, t, ancho=2 * R)

    actor_u = (1.65, 5.6)
    for k in ("mapa", "editar", "inicio", "algoritmo", "comparar", "experimento"):
        x, y, _ = casos[k]
        _linea(ax, actor_u, (x - R, y))

    actor_a = (14.35, 5.6)
    for k in ("ruta", "memoria", "metricas"):
        x, y, _ = casos[k]
        _linea(ax, actor_a, (x + R, y))

    _linea(ax, (casos["algoritmo"][0] + R * 0.9, casos["algoritmo"][1] + 0.2), (casos["ruta"][0] - R * 0.9, casos["ruta"][1] - 0.2),
           "--", "«include»", flecha=True)
    _linea(ax, (casos["ruta"][0], casos["ruta"][1] - 0.39), (casos["ver"][0], casos["ver"][1] + 0.39), "--", "«include»", flecha=True)
    _linea(ax, (casos["memoria"][0], casos["memoria"][1] + 0.39), (casos["ver"][0], casos["ver"][1] - 0.39), "--", "«extend»", flecha=True)
    _linea(ax, (casos["comparar"][0] + R, casos["comparar"][1]), (casos["metricas"][0] - R, casos["metricas"][1]),
           "--", "«include»", flecha=True)
    _linea(ax, (casos["experimento"][0] + R * 0.9, casos["experimento"][1] + 0.2), (casos["metricas"][0] - R * 0.9, casos["metricas"][1] - 0.2),
           "--", "«include»", flecha=True)
    # Descargar CSV es opcional después de correr el experimento: «extend»
    _linea(ax, (casos["exportar"][0] - R, casos["exportar"][1]), (casos["experimento"][0] + R, casos["experimento"][1]),
           "--", "«extend»", flecha=True)

    ax.set_title("Diagrama de caso de uso", fontsize=13, fontweight="bold", pad=4)
    destino = CARPETA / "caso_de_uso.png"
    fig.savefig(destino, dpi=170, bbox_inches="tight")
    plt.close(fig)
    return destino


# =============================================================================
# 4. Diagrama de componentes (UML)
# =============================================================================
def _componente(ax, x, y, w, h, nombre, detalle, color="#eef4ff", borde="#1f6feb"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=color, edgecolor=borde, lw=1.5, zorder=2))
    # icono UML de componente
    ix, iy = x + w - 0.42, y + h - 0.38
    ax.add_patch(plt.Rectangle((ix, iy), 0.28, 0.24, fill=False, lw=1, zorder=3))
    ax.add_patch(plt.Rectangle((ix - 0.06, iy + 0.04), 0.12, 0.05, facecolor="white", edgecolor="black", lw=0.8, zorder=4))
    ax.add_patch(plt.Rectangle((ix - 0.06, iy + 0.14), 0.12, 0.05, facecolor="white", edgecolor="black", lw=0.8, zorder=4))
    ax.text(x + 0.15, y + h - 0.25, f"«component»\n{nombre}", fontsize=8.6, fontweight="bold", va="top", zorder=3)
    ax.text(x + 0.15, y + 0.12, detalle, fontsize=7.4, va="bottom", color="#333", zorder=3)
    return (x, y, w, h)


def _dep(ax, a, b, texto="", t=0.5):
    """Dependencia punteada de `a` hacia `b`; la etiqueta va en la fracción `t` del recorrido."""
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="->", mutation_scale=13, ls="--", color="#555", lw=1.1, zorder=1))
    if texto:
        ax.text(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, texto, fontsize=7, ha="center", va="center", color="#555",
                bbox=dict(facecolor="white", edgecolor="none", pad=0.6), zorder=2)


def componentes() -> Path:
    fig, ax = plt.subplots(figsize=(12.5, 8.2))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10.6)
    ax.axis("off")

    azul, verde, naranja, gris = ("#eef4ff", "#1f6feb"), ("#eaf7ee", "#1a7f37"), ("#fdf1ec", "#b23a1f"), ("#f3f3f3", "#6e7781")

    ui = _componente(ax, 0.5, 8.0, 5.6, 2.0, "Interfaz (app.py)", "Streamlit: 4 pestañas\nSimulador · Comparar · Experimento · Memoria", *naranja)
    exp = _componente(ax, 10.5, 8.0, 5.0, 2.0, "Experimentos (experimentos.py)", "Corrida por lotes de 90 casos\nGenera CSV y gráficas PNG", *naranja)

    mem = _componente(ax, 0.5, 4.9, 4.6, 2.2, "Memoria (memoria.py)", "MemoriaRutas: consultar(), guardar()\nresolver() · sub-rutas óptimas\nTabla hash + archivo JSON", *azul)
    met = _componente(ax, 5.7, 4.9, 4.6, 2.2, "Métricas (metricas.py)", "medir(), comparar()\nexperimento_completo()\ntime.perf_counter · tracemalloc", *azul)
    vis = _componente(ax, 10.9, 4.9, 4.6, 2.2, "Visualización (visual.py)", "dibujar_mapa()\ngrafica_barras()\nmatplotlib", *azul)

    alg = _componente(ax, 0.5, 1.6, 6.6, 2.5, "Algoritmos (simulador/algoritmos)",
                      "no_informados: bfs · dfs · ucs\ninformados: greedy · a_estrella · hill_climbing\n"
                      "base: Resultado · reconstruir_ruta()\nEstructuras: deque · pila · heapq · dict", *verde)
    cua = _componente(ax, 8.2, 1.6, 4.0, 2.5, "Entorno (cuadricula.py)",
                      "Cuadricula: vecinos()\ncosto() · heuristica()\nes_salida() · transitable()", *verde)
    mapas_c = _componente(ax, 13.0, 1.6, 2.5, 2.5, "Mapas\n(mapas.py)", "Oficina\nEscuela\nBodega\n5 inicios c/u", *verde)

    _componente(ax, 6.6, 8.0, 3.4, 2.0, "Pruebas (tests/)", "pytest: 135 pruebas\nprueba entorno,\nalgoritmos y memoria", *gris)

    _dep(ax, (2.8, 8.0), (2.8, 7.1), "usa")
    _dep(ax, (5.3, 8.0), (6.6, 7.1), "usa")
    _dep(ax, (6.0, 8.0), (11.4, 7.1), "usa", t=0.62)
    _dep(ax, (13.2, 8.0), (13.2, 7.1), "usa")
    _dep(ax, (10.8, 8.0), (9.6, 7.1), "usa", t=0.28)
    _dep(ax, (2.8, 4.9), (2.8, 4.1), "ejecuta")
    _dep(ax, (6.5, 4.9), (6.5, 4.1), "ejecuta")
    _dep(ax, (alg[0] + alg[2], 2.85), (cua[0], 2.85), "consulta\nsensores")
    _dep(ax, (mapas_c[0], 2.85), (cua[0] + cua[2], 2.85), "crea")
    _dep(ax, (11.6, 4.9), (11.2, 4.1), "dibuja")

    ax.text(0.5, 0.75, "Capa de presentación (naranja) → capa de servicios (azul) → capa del agente y su entorno (verde).  "
            "Las flechas punteadas son dependencias.", fontsize=8, color="#555")
    ax.set_title("Diagrama de componentes", fontsize=13, fontweight="bold")
    destino = CARPETA / "componentes.png"
    fig.savefig(destino, dpi=170, bbox_inches="tight")
    plt.close(fig)
    return destino


def main() -> None:
    CARPETA.mkdir(parents=True, exist_ok=True)
    for funcion in (grafo_espacio_estados, grafo_ejemplo_costos, caso_de_uso, componentes):
        print("Generado:", funcion())


if __name__ == "__main__":
    main()
