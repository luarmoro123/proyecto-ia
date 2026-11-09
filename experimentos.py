"""
Corre el experimento completo (3 mapas x 5 inicios x 6 algoritmos = 90 corridas)
y guarda en la carpeta `resultados/`:

    resultados.csv        una fila por corrida
    resumen.csv           promedios por algoritmo
    grafica_*.png         gráficas comparativas
    mapa_<nombre>.png     cada mapa con la ruta de A* desde cada inicio
    memoizacion.txt       demostración de razonar vs. recordar

Uso:
    python experimentos.py
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from simulador import mapas
from simulador.algoritmos import ALGORITMOS
from simulador.memoria import MemoriaRutas
from simulador.metricas import agregar_optimalidad, experimento_completo
from simulador.visual import COLOR_ALGORITMO, dibujar_mapa, grafica_barras

CARPETA = Path(__file__).resolve().parent / "resultados"
ORDEN = list(ALGORITMOS)


def resumir(df: pd.DataFrame) -> pd.DataFrame:
    resumen = df.groupby("algoritmo").agg(
        exito_pct=("exito", lambda s: 100 * s.mean()),
        costo_prom=("costo", "mean"),
        pasos_prom=("pasos", "mean"),
        exceso_costo_prom_pct=("exceso_costo_%", "mean"),
        rutas_optimas=("exceso_costo_%", lambda s: int((s == 0).sum())),
        expandidos_prom=("nodos_expandidos", "mean"),
        max_frontera_prom=("max_frontera", "mean"),
        tiempo_ms_prom=("tiempo_ms", "mean"),
        memoria_kb_prom=("memoria_kb", "mean"),
    )
    return resumen.reindex(ORDEN).round(2)


def guardar_graficas(resumen: pd.DataFrame) -> None:
    graficas = {
        "grafica_costo.png": ("costo_prom", "Costo promedio de la ruta (solo exitosas)", "costo"),
        "grafica_expandidos.png": ("expandidos_prom", "Nodos expandidos promedio", "nodos"),
        "grafica_tiempo.png": ("tiempo_ms_prom", "Tiempo promedio", "milisegundos"),
        "grafica_memoria.png": ("memoria_kb_prom", "Memoria pico promedio", "KB"),
        "grafica_exito.png": ("exito_pct", "Porcentaje de llegadas a una salida", "%"),
        "grafica_exceso_costo.png": ("exceso_costo_prom_pct", "Exceso de costo sobre la ruta óptima", "%"),
    }
    for archivo, (columna, titulo, eje) in graficas.items():
        valores = {a: (None if pd.isna(v) else float(v)) for a, v in resumen[columna].items()}
        fig = grafica_barras(valores, titulo, eje)
        fig.savefig(CARPETA / archivo, dpi=150)


def guardar_mapas() -> None:
    for nombre in mapas.nombres():
        mapa, inicios = mapas.cargar(nombre)
        expandidos, rutas = [], []
        for inicio in inicios:
            r = ALGORITMOS["A*"](mapa, inicio)
            rutas.append(r.ruta)
        fig = dibujar_mapa(mapa, titulo=f"{nombre}: rutas de A* desde los 5 inicios", tamano=6)
        ax = fig.axes[0]
        for inicio, ruta in zip(inicios, rutas):
            if len(ruta) > 1:
                ys, xs = zip(*ruta)
                ax.plot(xs, ys, color=COLOR_ALGORITMO["A*"], linewidth=2.2)
            ax.scatter([inicio[1]], [inicio[0]], marker="*", s=200, color="#ffd33d",
                       edgecolors="black", linewidths=0.8, zorder=5)
        fig.savefig(CARPETA / f"mapa_{nombre.lower()}.png", dpi=150)


def demostrar_memoizacion() -> str:
    """Resuelve todos los inicios dos veces con A*: la 1.ª razona, la 2.ª recuerda."""
    memoria = MemoriaRutas(archivo=None)  # en RAM, para no mezclar con la de la interfaz
    lineas = ["Demostración de memoización con A*", "=" * 40]
    for vuelta in (1, 2):
        lineas.append(f"\nVuelta {vuelta}:")
        for nombre in mapas.nombres():
            mapa, inicios = mapas.cargar(nombre)
            for inicio in inicios:
                t0 = time.perf_counter()
                r, recordado = memoria.resolver(mapa, "A*", inicio)
                ms = (time.perf_counter() - t0) * 1000
                modo = "RECUERDA" if recordado else "RAZONA  "
                expandidos = 0 if recordado else r.nodos_expandidos  # recordar no explora nada
                lineas.append(f"  {modo} {nombre:8s} {str(inicio):9s} costo={r.costo:3d} "
                              f"expandidos={expandidos:4d} tiempo={ms:.3f} ms")
    lineas.append(f"\nAciertos (de memoria): {memoria.aciertos}   Fallos (tuvo que buscar): {memoria.fallos}")
    lineas.append(f"Rutas guardadas (incluye sub-rutas aprendidas): {len(memoria)}")
    return "\n".join(lineas)


def main() -> None:
    CARPETA.mkdir(exist_ok=True)
    print("Corriendo 90 experimentos...")
    df = pd.DataFrame(agregar_optimalidad(experimento_completo()))
    df.to_csv(CARPETA / "resultados.csv", index=False, encoding="utf-8-sig")

    resumen = resumir(df)
    resumen.to_csv(CARPETA / "resumen.csv", encoding="utf-8-sig")
    print("\nResumen por algoritmo:\n")
    print(resumen.to_string())

    guardar_graficas(resumen)
    guardar_mapas()

    texto = demostrar_memoizacion()
    (CARPETA / "memoizacion.txt").write_text(texto, encoding="utf-8")
    print("\n" + texto.splitlines()[-2])
    print(texto.splitlines()[-1])
    print(f"\nArchivos guardados en {CARPETA}")


if __name__ == "__main__":
    main()
