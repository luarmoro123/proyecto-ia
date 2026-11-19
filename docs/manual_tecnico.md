# Manual técnico: Simulador de escape de incendios forestales

**Proyecto #33**: comparación de 3 algoritmos de búsqueda (A\*, BFS y DFS) para evacuar una
zona forestal en llamas.

| Parte | Responsable |
|---|---|
| 1. Mapa, representación de la cuadrícula y estructura | ____ |
| 2. Algoritmos (A\*, BFS y DFS) | ____ |
| 3. Interfaz y pruebas | ____ |

Fecha de entrega: ____ *(pendiente de confirmar con la profesora)*

---

## 1. Objetivo

Comparar y explicar 3 algoritmos de búsqueda que encuentran la ruta de evacuación de un bosque
con humo, fuego, rocas, ríos y varias zonas seguras. A\* es el algoritmo principal. La
comparación mide qué algoritmo llega con **menor costo** y con **menos cálculo**, y la
interfaz permite **ver cada búsqueda en vivo**, celda por celda.

## 2. Instalación

Requisitos: Python 3.10 o más reciente (se probó con 3.14 en Windows 11).

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

| Comando | Qué hace |
|---|---|
| `.venv\Scripts\python app.py` | Inicia el servidor; la página queda en `http://localhost:5000` |
| `.venv\Scripts\python -m pytest -v` | Corre las 37 pruebas automáticas |

Dependencias: `flask` (servidor) y `pytest` (pruebas). **Ninguna se usa para buscar rutas.**
Los algoritmos solo usan la biblioteca estándar: `collections.deque` (cola), `list` (pila) y
`heapq` (cola de prioridad). La página es HTML, CSS y JavaScript propios, sin frameworks.

## 3. Arquitectura

```
web/ (HTML + CSS + JS)
   │  fetch() a la API JSON
   ▼
app.py (servidor Flask)
   │
   ▼
simulador/metricas.py      mide tiempo y memoria
simulador/algoritmos/
  base.py                  Resultado común, reconstruir_ruta()
  no_informados.py         bfs(), dfs()
  informados.py            a_estrella()
   │
   ▼
simulador/cuadricula.py    Cuadricula: vecinos, costo, heurística
simulador/mapas.py         mapa "Pinar" + 5 inicios
```

Los 3 algoritmos tienen la misma firma, `funcion(mapa, inicio) -> Resultado`, y están
registrados en el diccionario `ALGORITMOS`.

`Resultado` guarda: `exito`, `ruta`, `costo`, `pasos`, `nodos_expandidos`,
`nodos_generados`, `max_frontera`, `orden_expansion` y un `mensaje`. El campo
`orden_expansion` es la lista de celdas en el orden en que se expandieron: la página lo usa
para reproducir la búsqueda en vivo.

### 3.1 Cómo funciona la ejecución en vivo

1. Al pulsar **Correr**, la página envía `POST /api/correr` con el algoritmo y el inicio.
2. El servidor ejecuta el algoritmo en Python (5 veces, para medir el tiempo con la mediana)
   y devuelve el `Resultado` completo.
3. La página dibuja una celda expandida cada fracción de segundo,
   marcando con un recuadro la celda que se está expandiendo. **Paso** avanza una sola celda.
4. Cuando se han mostrado todas las celdas, se dibuja la ruta y se agrega una fila a la tabla
   de resultados.

| Método | Ruta de la API | Qué hace |
|---|---|---|
| GET | `/api/mapa` | Celdas, 5 inicios, algoritmos y colores |
| POST | `/api/correr` | Corre un algoritmo desde un inicio |

## 4. Modelo del problema

| Elemento | Definición |
|---|---|
| Estado | Posición `(fila, columna)` de la persona en la cuadrícula de 20 × 20 |
| Estado inicial | Uno de los 5 puntos de inicio, o la celda que se elija con un clic |
| Acciones | Moverse arriba, abajo, izquierda o derecha (en ese orden) |
| Restricciones | No se puede entrar a rocas o ríos (`#`) ni a fuego (`F`); el fuego no se mueve |
| Costo de un paso | Costo de la celda a la que se **entra**: sendero o zona segura = 1, humo = 5 |
| Prueba de objetivo | La celda es una zona segura (`S`); sirve **cualquier** zona segura |
| Heurística h(n) | Distancia Manhattan a la zona segura más cercana |

### 4.1 ¿Por qué la heurística es admisible y consistente?

- **Admisible:** para llegar a una zona segura hacen falta al menos |Δfila| + |Δcolumna|
  pasos, y cada paso cuesta **como mínimo 1**. Por eso h(n) nunca supera el costo real.
- **Consistente:** al dar un paso, la distancia Manhattan cambia en a lo más 1, y ese paso
  cuesta ≥ 1. Entonces h(n) ≤ c(n, n') + h(n').
- La prueba `test_heuristica_es_admisible` lo comprueba en **todas** las celdas libres del
  mapa, comparando h(n) con el costo óptimo real.

### 4.2 El mapa "Pinar"

Bosque abierto con 4 focos de fuego rodeados de humo, grupos de rocas y 4 zonas seguras
(una en cada borde). Puntos de inicio: (1, 1), (9, 9), (15, 10), (17, 3) y (11, 8).

## 5. Algoritmos

Reglas comunes para que la comparación sea justa:

1. La prueba de objetivo se hace al **expandir** (sacar de la frontera), no al generar.
2. Los vecinos siempre se generan en el orden arriba, abajo, izquierda y derecha.
3. Todos son búsqueda en **grafo**: no repiten celdas ya expandidas.

### 5.1 BFS: búsqueda en amplitud

- **Estructura:** cola FIFO (`deque`).
- **Idea:** explora por capas: primero todo lo que está a 1 paso, luego a 2, etc.
- **Garantía:** encuentra la ruta con **menos pasos**, pero ignora el costo del humo.
- **Completo:** sí. **Óptimo en costo:** no (solo si todos los pasos costaran igual).

### 5.2 DFS: búsqueda en profundidad

- **Estructura:** pila LIFO (`list`).
- **Idea:** sigue un camino hasta el fondo antes de probar otro.
- **Completo:** sí, en grafos finitos con control de visitados. **Óptimo:** no.
- **Comportamiento:** la ruta suele ser larga y serpenteante.

### 5.3 A\*: algoritmo principal

- **Estructura:** cola de prioridad (`heapq`) ordenada por **f(n) = g(n) + h(n)**. En empate
  de f se prefiere la menor h.
- **Idea:** combina lo que ya costó llegar (g) con una estimación de lo que falta (h).
- **Completo:** sí. **Óptimo:** sí, porque h es admisible y consistente (sección 4.1).

| Algoritmo | Usa costo g | Usa heurística h | Completo | Óptimo en costo |
|---|---|---|---|---|
| BFS | no | no | sí | no (sí en pasos) |
| DFS | no | no | sí | no |
| A\* | sí | sí | sí | **sí** |

## 6. Resultados en el mapa Pinar

Cada celda muestra **costo / pasos / nodos expandidos**.

| Inicio | A\* | BFS | DFS |
|---|---|---|---|
| (1, 1) | **12** / 12 / **13** | 12 / 12 / 73 | 134 / 102 / 125 |
| (9, 9) | **12** / 12 / **15** | 18 / **10** / 145 | 186 / 130 / 161 |
| (15, 10) | **11** / 11 / **41** | 21 / **5** / 42 | 169 / 117 / 145 |
| (17, 3) | **6** / 6 / **7** | 6 / 6 / 35 | 166 / 118 / 139 |
| (11, 8) | **11** / 11 / **12** | 11 / 11 / 177 | 93 / 73 / 103 |
| **Promedio** | **10.4** / 10.4 / **17.6** | 13.6 / **8.8** / 94.4 | 149.6 / 108.0 / 134.6 |

- **A\*** tiene siempre el costo mínimo y expande en promedio **81 % menos celdas que BFS**.
- **BFS** da las rutas con menos pasos, pero cruza el humo cuando eso acorta el camino. Desde
  (15, 10) llega en 5 pasos con costo 21; A\* da 11 pasos con costo 11.
- **DFS** es el peor en costo: sus rutas recorren medio bosque.

**Conclusión:** para evacuar, donde importa la ruta de menor costo (menos exposición al humo)
y que el cálculo sea poco, **A\*** es la mejor opción.

## 7. Pruebas

`tests/test_simulador.py` tiene **37 pruebas**:

| Grupo | Qué verifica |
|---|---|
| Mapa | Es 20 × 20, tiene zonas seguras y los 5 inicios son celdas válidas |
| Cuadrícula | Costos, orden de los vecinos, heurística y rechazo de mapas mal formados |
| Rutas válidas (15 casos) | Cada movimiento es de 1 celda, no pisa roca/río ni fuego, el costo es correcto y termina en una zona segura |
| A\* óptimo (5 casos) | A\* tiene el costo mínimo real (comparado con un Dijkstra de referencia) |
| BFS (5 casos) | BFS da la ruta con menos pasos |
| Heurística | h(n) ≤ costo óptimo en todas las celdas |
| Humo | En un mapa pequeño, BFS cruza el humo (costo 17) y A\* lo rodea (costo 9) |
| Casos límite | Sin zona segura alcanzable; inicio sobre roca |
| API | `/api/mapa`, `/api/correr` y rechazo de peticiones inválidas |

## 8. Limitaciones y trabajo futuro

- El fuego es estático. En un incendio forestal real avanza con el viento y la pendiente; con
  fuego que se propaga habría que volver a planear la ruta en cada paso.
- Solo se modela una persona y un mapa.
