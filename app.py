"""
Interfaz visual del simulador de escape de incendios (Streamlit).

Ejecutar con:
    streamlit run app.py

Pestañas:
    1. Simulador   - editar el edificio, elegir inicio y algoritmo, ver la ruta.
    2. Comparar    - los 6 algoritmos sobre el mismo mapa e inicio.
    3. Experimento - las 90 corridas (3 mapas x 5 inicios x 6 algoritmos).
    4. Memoria     - cuándo el sistema razona y cuándo recuerda lo aprendido.
"""

from __future__ import annotations

import time

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from simulador import mapas
from simulador.algoritmos import ALGORITMOS
from simulador.cuadricula import BLOQUEADAS, SIMBOLOS_VALIDOS, Cuadricula
from simulador.memoria import MemoriaRutas
from simulador.metricas import agregar_optimalidad, comparar, experimento_completo, medir
from simulador.visual import COLOR_ALGORITMO, dibujar_mapa, grafica_barras, leyenda_mapa

st.set_page_config(page_title="Escape de incendios", page_icon="🔥", layout="wide")


# --- Estado de la sesión -------------------------------------------------------
def mostrar(fig) -> None:
    st.pyplot(fig, width="stretch")
    plt.close(fig)


@st.cache_resource
def obtener_memoria() -> MemoriaRutas:
    return MemoriaRutas()


def cargar_mapa_en_sesion(nombre: str) -> None:
    mapa, inicios = mapas.cargar(nombre)
    st.session_state.mapa_texto = mapa.a_texto()
    st.session_state.inicios = inicios
    st.session_state.mapa_nombre = nombre
    st.session_state.version_editor = st.session_state.get("version_editor", 0) + 1


if "mapa_texto" not in st.session_state:
    cargar_mapa_en_sesion(mapas.nombres()[0])


def mapa_actual() -> Cuadricula:
    return Cuadricula.desde_texto(st.session_state.mapa_texto)


# --- Barra lateral -------------------------------------------------------------
st.sidebar.title("🔥 Escape de incendios")

nombre = st.sidebar.selectbox("Mapa", mapas.nombres(),
                              index=mapas.nombres().index(st.session_state.mapa_nombre))
if nombre != st.session_state.mapa_nombre:
    cargar_mapa_en_sesion(nombre)
if st.sidebar.button("Restaurar mapa original"):
    cargar_mapa_en_sesion(nombre)

mapa = mapa_actual()

st.sidebar.subheader("Punto de inicio")
opciones_inicio = [f"Inicio {i + 1}: {p}" for i, p in enumerate(st.session_state.inicios)] + ["Personalizado"]
eleccion = st.sidebar.radio("Inicio", opciones_inicio, label_visibility="collapsed")
if eleccion == "Personalizado":
    c1, c2 = st.sidebar.columns(2)
    fila = c1.number_input("Fila", 0, mapa.filas - 1, 1)
    col = c2.number_input("Columna", 0, mapa.columnas - 1, 1)
    inicio = (int(fila), int(col))
else:
    inicio = st.session_state.inicios[opciones_inicio.index(eleccion)]

st.sidebar.caption(f"Celda de inicio: **{mapa.simbolo(inicio)}**  ·  h = {mapa.heuristica(inicio)}")
inicio_valido = mapa.transitable(inicio)
if not inicio_valido:
    st.sidebar.error("El inicio está sobre un muro o fuego. Elige otra celda.")

st.sidebar.markdown(
    "**Reglas**\n"
    "- Movimiento: ↑ ↓ ← →\n"
    "- Libre `.` cuesta 1 · Humo `H` cuesta 5\n"
    "- Muro `#` y fuego `F` bloquean\n"
    "- Heurística: Manhattan a la salida `S` más cercana"
)

tab_sim, tab_comp, tab_exp, tab_mem = st.tabs(
    ["🗺️ Simulador", "📊 Comparar algoritmos", "🧪 Experimento completo", "🧠 Memoria"]
)

# =============================================================================
# 1. SIMULADOR
# =============================================================================
with tab_sim:
    izquierda, derecha = st.columns([3, 2])

    with derecha:
        algoritmo = st.selectbox("Algoritmo", list(ALGORITMOS), index=0)

        with st.expander("✏️ Pintar una celda", expanded=True):
            simbolos = {".": "Libre", "#": "Muro", "F": "Fuego", "H": "Humo", "S": "Salida"}
            herramienta = st.radio("Símbolo", list(simbolos), format_func=lambda s: f"{s}  {simbolos[s]}",
                                   horizontal=True)
            p1, p2, p3 = st.columns([1, 1, 1])
            pf = p1.number_input("Fila ", 0, mapa.filas - 1, 0, key="pinta_f")
            pc = p2.number_input("Col ", 0, mapa.columnas - 1, 0, key="pinta_c")
            p3.write("")
            if p3.button("Pintar", width="stretch"):
                st.session_state.mapa_texto = mapa.con_celda((int(pf), int(pc)), herramienta).a_texto()
                st.session_state.version_editor += 1
                st.rerun()

        with st.expander("🧱 Editar todo el edificio como tabla"):
            st.caption("Escribe un símbolo por celda: `.` `#` `F` `H` `S`")
            df = pd.DataFrame(mapa.celdas, columns=[str(c) for c in range(mapa.columnas)])
            editado = st.data_editor(df, key=f"editor_{st.session_state.version_editor}",
                                     width="stretch", height=400)
            if st.button("Aplicar cambios de la tabla"):
                filas = [[str(v).strip().upper()[:1] or "." for v in fila] for fila in editado.values.tolist()]
                malos = {s for fila in filas for s in fila} - SIMBOLOS_VALIDOS
                if malos:
                    st.error(f"Símbolos no válidos: {', '.join(sorted(malos))}")
                else:
                    st.session_state.mapa_texto = "\n".join("".join(f) for f in filas)
                    st.session_state.version_editor += 1
                    st.rerun()

        if inicio_valido:
            medicion = medir(ALGORITMOS[algoritmo], mapa, inicio, repeticiones=5)
            r = medicion.resultado
            (st.success if r.exito else st.warning)(r.mensaje)
            m1, m2, m3 = st.columns(3)
            m1.metric("Costo", r.costo)
            m2.metric("Pasos", r.pasos)
            m3.metric("Expandidos", r.nodos_expandidos)
            m4, m5, m6 = st.columns(3)
            m4.metric("Frontera máx.", r.max_frontera)
            m5.metric("Tiempo", f"{medicion.tiempo_ms:.2f} ms")
            m6.metric("Memoria", f"{medicion.memoria_kb:.1f} KB")
            humo = sum(1 for p in r.ruta[1:] if mapa.simbolo(p) == "H")
            st.caption(f"La ruta atraviesa {humo} celda(s) con humo.")

    with izquierda:
        if inicio_valido:
            ver_exp = st.checkbox("Mostrar celdas expandidas", value=True)
            fig = dibujar_mapa(mapa, inicio, r.ruta, r.orden_expansion if ver_exp else None,
                               titulo=f"{algoritmo} — {st.session_state.mapa_nombre}",
                               color_ruta=COLOR_ALGORITMO[algoritmo])
        else:
            fig = dibujar_mapa(mapa, inicio, titulo=st.session_state.mapa_nombre)
        mostrar(fig)
        mostrar(leyenda_mapa())

# =============================================================================
# 2. COMPARAR LOS 6 ALGORITMOS
# =============================================================================
with tab_comp:
    st.subheader("Los 6 algoritmos sobre el mismo mapa e inicio")
    if not inicio_valido:
        st.info("Elige un inicio válido en la barra lateral.")
    else:
        mediciones = comparar(mapa, inicio)
        filas = [m.fila(st.session_state.mapa_nombre, inicio) for m in mediciones.values()]
        filas = agregar_optimalidad(filas)
        tabla = pd.DataFrame(filas).drop(columns=["mapa", "inicio"]).set_index("algoritmo")
        st.dataframe(tabla, width="stretch")

        exitosos = [n for n, m in mediciones.items() if m.resultado.exito]
        if exitosos:
            mejor = min(exitosos, key=lambda n: (mediciones[n].resultado.costo, mediciones[n].resultado.nodos_expandidos))
            st.markdown(f"**Menor costo con menos cálculo:** {mejor} "
                        f"(costo {mediciones[mejor].resultado.costo}, "
                        f"{mediciones[mejor].resultado.nodos_expandidos} nodos expandidos).")
            st.caption("Ojo: solo A* y UCS GARANTIZAN la ruta de menor costo en cualquier mapa. "
                       "Si Greedy o BFS empatan en costo aquí, fue por este caso en particular.")

        g1, g2 = st.columns(2)
        with g1:
            mostrar(grafica_barras({n: m.resultado.costo if m.resultado.exito else None
                                    for n, m in mediciones.items()}, "Costo de la ruta", "costo"))
            mostrar(grafica_barras({n: m.tiempo_ms for n, m in mediciones.items()}, "Tiempo", "ms"))
        with g2:
            mostrar(grafica_barras({n: m.resultado.nodos_expandidos for n, m in mediciones.items()},
                                   "Nodos expandidos", "nodos"))
            mostrar(grafica_barras({n: m.memoria_kb for n, m in mediciones.items()}, "Memoria pico", "KB"))

        st.subheader("Rutas y celdas exploradas")
        columnas = st.columns(3)
        for i, (n, m) in enumerate(mediciones.items()):
            with columnas[i % 3]:
                estado = "[llegó]" if m.resultado.exito else "[no llegó]"
                mostrar(dibujar_mapa(mapa, inicio, m.resultado.ruta, m.resultado.orden_expansion,
                                     titulo=f"{estado} {n}  ·  costo {m.resultado.costo}",
                                     color_ruta=COLOR_ALGORITMO[n], tamano=4))

# =============================================================================
# 3. EXPERIMENTO COMPLETO
# =============================================================================
with tab_exp:
    st.subheader("3 mapas × 5 inicios × 6 algoritmos = 90 corridas")
    st.caption("Usa los mapas originales (no los editados). El tiempo es la mediana de 7 repeticiones.")
    if st.button("Correr experimento", type="primary"):
        with st.spinner("Corriendo..."):
            st.session_state.experimento = pd.DataFrame(agregar_optimalidad(experimento_completo()))

    if "experimento" in st.session_state:
        df = st.session_state.experimento
        resumen = df.groupby("algoritmo").agg(
            exito_pct=("exito", lambda s: 100 * s.mean()),
            costo_prom=("costo", "mean"),
            pasos_prom=("pasos", "mean"),
            exceso_costo_pct=("exceso_costo_%", "mean"),
            rutas_optimas=("exceso_costo_%", lambda s: int((s == 0).sum())),
            expandidos_prom=("nodos_expandidos", "mean"),
            tiempo_ms_prom=("tiempo_ms", "mean"),
            memoria_kb_prom=("memoria_kb", "mean"),
        ).reindex(list(ALGORITMOS)).round(2)
        st.markdown("**Promedios por algoritmo**")
        st.dataframe(resumen, width="stretch")

        def valores(col):
            return {a: (None if pd.isna(v) else float(v)) for a, v in resumen[col].items()}

        g1, g2, g3 = st.columns(3)
        with g1:
            mostrar(grafica_barras(valores("costo_prom"), "Costo promedio (exitosas)", "costo"))
            mostrar(grafica_barras(valores("exito_pct"), "Llegó a una salida", "%"))
        with g2:
            mostrar(grafica_barras(valores("expandidos_prom"), "Nodos expandidos promedio", "nodos"))
            mostrar(grafica_barras(valores("exceso_costo_pct"), "Exceso sobre el costo óptimo", "%"))
        with g3:
            mostrar(grafica_barras(valores("tiempo_ms_prom"), "Tiempo promedio", "ms"))
            mostrar(grafica_barras(valores("memoria_kb_prom"), "Memoria pico promedio", "KB"))

        with st.expander("Ver las 90 corridas"):
            st.dataframe(df, width="stretch")
        st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8-sig"),
                           "resultados.csv", "text/csv")

# =============================================================================
# 4. MEMORIA: RAZONAR vs. APRENDER
# =============================================================================
with tab_mem:
    memoria = obtener_memoria()
    st.subheader("¿Cuándo razona y cuándo aprende?")
    st.markdown(
        "- **Razona** cuando no conoce la respuesta: ejecuta el algoritmo y explora el mapa.\n"
        "- **Aprende** al guardar esa ruta. Si se le vuelve a pedir lo mismo, **recuerda** "
        "y contesta sin explorar (0 nodos expandidos).\n"
        "- Con A* y UCS (rutas óptimas) también aprende **cada sub-ruta**: cualquier celda "
        "de la ruta ya tiene su camino óptimo a la salida (principio de optimalidad).\n"
        "- Si cambias una celda del mapa, la huella del mapa cambia y vuelve a razonar."
    )
    alg_mem = st.radio("Algoritmo", ["A*", "UCS", "BFS", "Greedy"], horizontal=True)
    c1, c2 = st.columns([1, 1])
    resolver = c1.button("Buscar ruta (con memoria)", type="primary", disabled=not inicio_valido)
    if c2.button("Olvidar todo"):
        memoria.olvidar()
        st.session_state.pop("ultima_memoria", None)

    if resolver:
        t0 = time.perf_counter()
        r, recordado = memoria.resolver(mapa, alg_mem, inicio)
        ms = (time.perf_counter() - t0) * 1000
        st.session_state.ultima_memoria = (r, recordado, ms, inicio, alg_mem)

    k1, k2, k3 = st.columns(3)
    k1.metric("Rutas en memoria", len(memoria))
    k2.metric("Respondió de memoria", memoria.aciertos)
    k3.metric("Tuvo que razonar", memoria.fallos)

    izq, der = st.columns([3, 2])
    ultima = st.session_state.get("ultima_memoria")
    with der:
        if ultima:
            r, recordado, ms, ini, alg = ultima
            if recordado:
                st.success(f"🧠 RECORDÓ la ruta desde {ini} ({alg}). {r.mensaje}")
            else:
                st.info(f"🔎 RAZONÓ: buscó con {alg} desde {ini} y guardó el resultado.")
            st.metric("Costo", r.costo)
            st.metric("Nodos expandidos en esta consulta", 0 if recordado else r.nodos_expandidos)
            st.metric("Tiempo de respuesta", f"{ms:.3f} ms")
        st.caption("En amarillo: celdas desde las que ya se conoce una ruta para este mapa y algoritmo.")
    with izq:
        ruta = ultima[0].ruta if ultima and ultima[3] == inicio else None
        mostrar(dibujar_mapa(mapa, inicio, ruta, conocidas=memoria.celdas_conocidas(mapa, alg_mem),
                             titulo=f"Memoria de {alg_mem}", color_ruta=COLOR_ALGORITMO[alg_mem]))
