# 🌲 Simulador de escape de incendios forestales (#33)

Una persona atrapada en un bosque en llamas busca la ruta más segura hasta una zona segura.
El bosque es una cuadrícula de 20 × 20 con rocas y ríos, focos de fuego, humo y 4 zonas
seguras.

Se comparan 3 algoritmos de búsqueda programados a mano, sin librerías de búsqueda:
**A\*** (el principal), **BFS** y **DFS**. En la página puedes ver cada uno **en vivo**,
expandiendo celda por celda hasta encontrar la ruta.

La interfaz es una sola página en **HTML, CSS y JavaScript propios** (sin frameworks),
servida por un pequeño servidor **Flask** que ejecuta los algoritmos en Python.

---

## 📋 Requisitos

- **Python 3.10 o más reciente** (se probó con Python 3.14 en Windows 11).
- Un navegador moderno (Chrome, Edge o Firefox).

---

## 🚀 Cómo correr el programa

### 1. Crear el entorno virtual e instalar dependencias (solo la primera vez)

```bash
python -m venv .venv
```

**Windows:**

```bash
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS / Linux:**

```bash
.venv/bin/python -m pip install -r requirements.txt
```

### 2. Iniciar el servidor

**Windows:**

```bash
.\.venv\Scripts\python.exe app.py
```

**macOS / Linux:**

```bash
.venv/bin/python app.py
```

Abre en el navegador **<http://localhost:5000>**. Para cerrar, presiona **Ctrl + C** en la
terminal.

---

## 🖥️ Cómo usar la página

1. **Algoritmo:** elige A\*, BFS o DFS.
2. **Inicio:** elige uno de los 5 puntos de inicio, o haz clic en cualquier celda libre del
   mapa.
3. **Ejecución:**
   - **▶ Correr** reproduce la búsqueda en vivo; el mismo botón la **pausa**.
   - **Paso** avanza una sola celda.
   - **Reiniciar** vuelve al principio.
   - **Velocidad** controla cuántas celdas por segundo se expanden.
4. Al terminar se dibuja la ruta, se muestran el costo, los pasos, las celdas expandidas y el
   tiempo, y el algoritmo se agrega a la tabla **Resultados desde este inicio** para
   compararlo con los demás.

---

## 📐 Reglas del modelo

| Celda | Símbolo | Costo |
|---|---|---|
| Sendero / pasto | `.` | 1 |
| Humo | `H` | 5 |
| Zona segura | `S` | 1 (objetivo) |
| Roca o río | `#` | bloqueada |
| Fuego | `F` | bloqueada (no se propaga) |

- La persona se mueve arriba, abajo, izquierda o derecha.
- Heurística de A\*: distancia Manhattan a la zona segura más cercana.

---

## ✅ Pruebas automáticas

```bash
.venv\Scripts\python -m pytest -v
```

Deben pasar las **37 pruebas**.

---

## 📁 Estructura del proyecto

```
proyecto_ia/
├── app.py                     Servidor Flask: sirve la página y la API JSON
├── web/
│   ├── index.html             La página
│   ├── estilos.css            Estilos propios
│   └── app.js                 Dibujo del mapa y reproducción en vivo
├── simulador/
│   ├── cuadricula.py          Representación del bosque, costos y heurística
│   ├── mapas.py               El mapa "Pinar" y sus 5 puntos de inicio
│   ├── metricas.py            Medición de tiempo y memoria
│   └── algoritmos/
│       ├── base.py            Resultado común y reconstrucción de rutas
│       ├── no_informados.py   BFS y DFS
│       └── informados.py      A*
├── tests/test_simulador.py    37 pruebas automáticas
├── requirements.txt           flask y pytest
└── docs/
    ├── manual_tecnico.md      Manual técnico
    ├── reporte_tecnico.docx   Reporte técnico (formato IEEE, editable)
    ├── reporte_tecnico.pdf    Reporte técnico (formato IEEE, PDF)
    └── diagramas/             Caso de uso, componentes y grafos de ejemplo
```

### API JSON

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/api/mapa` | Celdas, 5 inicios, algoritmos y colores |
| POST | `/api/correr` | Corre un algoritmo (`{"algoritmo": "A*", "inicio": [1, 1]}`) y devuelve el orden de expansión, la ruta y las métricas |

Más detalle: [docs/manual_tecnico.md](docs/manual_tecnico.md).
