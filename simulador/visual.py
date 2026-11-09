"""
Dibujo del mapa y de las gráficas comparativas con matplotlib.
Lo usan tanto la interfaz de Streamlit como el script de experimentos.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # sin ventana: solo genera imágenes

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

from .cuadricula import FUEGO, HUMO, LIBRE, MURO, SALIDA, Cuadricula, Posicion

# Orden de los códigos numéricos que usa el mapa de color.
CODIGOS = {LIBRE: 0, MURO: 1, FUEGO: 2, HUMO: 3, SALIDA: 4}
COLORES = ["#f4f1ea", "#3a3a3a", "#e4572e", "#a9a9b8", "#2e9e5b"]
NOMBRES = ["Libre (1)", "Muro", "Fuego", "Humo (5)", "Salida"]

COLOR_ALGORITMO = {
    "A*": "#1f6feb",
    "BFS": "#8250df",
    "DFS": "#bf8700",
    "UCS": "#1a7f37",
    "Greedy": "#cf222e",
    "Hill Climbing": "#57606a",
}


def dibujar_mapa(
    mapa: Cuadricula,
    inicio: Posicion | None = None,
    ruta: list[Posicion] | None = None,
    expandidos: list[Posicion] | None = None,
    conocidas: list[Posicion] | None = None,
    titulo: str = "",
    color_ruta: str = "#1f6feb",
    tamano: float = 6.0,
):
    """Devuelve una figura con el edificio, las celdas exploradas y la ruta."""
    datos = np.array([[CODIGOS[s] for s in fila] for fila in mapa.celdas])
    fig, ax = plt.subplots(figsize=(tamano, tamano))
    ax.imshow(datos, cmap=ListedColormap(COLORES), vmin=0, vmax=4)

    if conocidas:
        ys, xs = zip(*[(f, c) for f, c in conocidas])
        ax.scatter(xs, ys, marker="s", s=(tamano * 14) ** 2 / 400, color="#ffd33d", alpha=0.45, linewidths=0)

    if expandidos:
        ys, xs = zip(*expandidos)
        ax.scatter(xs, ys, marker="o", s=18, color=color_ruta, alpha=0.25, linewidths=0)

    if ruta and len(ruta) > 1:
        ys, xs = zip(*ruta)
        ax.plot(xs, ys, color=color_ruta, linewidth=2.6, solid_capstyle="round")

    if inicio is not None:
        ax.scatter([inicio[1]], [inicio[0]], marker="*", s=260, color="#ffd33d",
                   edgecolors="black", linewidths=0.8, zorder=5)

    ax.set_xticks(np.arange(-0.5, mapa.columnas, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, mapa.filas, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.5)
    ax.set_xticks(range(0, mapa.columnas, 2))
    ax.set_yticks(range(0, mapa.filas, 2))
    ax.tick_params(which="both", length=0, labelsize=7)
    if titulo:
        ax.set_title(titulo, fontsize=11)
    fig.tight_layout()
    return fig


def leyenda_mapa():
    """Figura pequeña solo con la leyenda de colores."""
    fig, ax = plt.subplots(figsize=(6, 0.5))
    ax.axis("off")
    manijas = [Patch(color=c, label=n) for c, n in zip(COLORES, NOMBRES)]
    ax.legend(handles=manijas, loc="center", ncol=5, frameon=False, fontsize=8)
    return fig


def grafica_barras(valores: dict[str, float], titulo: str, eje_y: str, escala_log: bool = False):
    """Barras por algoritmo (un valor por algoritmo)."""
    nombres = list(valores)
    fig, ax = plt.subplots(figsize=(6, 3.4))
    barras = ax.bar(nombres, [valores[n] if valores[n] is not None else 0 for n in nombres],
                    color=[COLOR_ALGORITMO.get(n, "#888") for n in nombres])
    for barra, n in zip(barras, nombres):
        v = valores[n]
        texto = "—" if v is None else (f"{v:.0f}" if v >= 10 else f"{v:.2f}")
        ax.annotate(texto, (barra.get_x() + barra.get_width() / 2, barra.get_height()),
                    ha="center", va="bottom", fontsize=8)
    if escala_log:
        ax.set_yscale("log")
    ax.set_title(titulo, fontsize=11)
    ax.set_ylabel(eje_y)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=8)
    fig.tight_layout()
    return fig
