# 🔥 Simulador de escape de incendios (#33)

Simulador de evacuación de un edificio en llamas. El edificio es una cuadrícula de 20 × 20
con muros, fuego, humo y varias salidas, y una persona busca la mejor ruta para escapar.

Se usa **A\*** como algoritmo principal y se compara con **BFS, DFS, UCS, Greedy Best-First
y Hill Climbing** para ver cuál llega con **menor costo** y **menos cálculo**. Todos los
algoritmos están programados a mano, sin librerías de búsqueda.

---

## 📋 Requisitos

- **Python 3.10 o más reciente** (se probó con Python 3.14 en Windows 11).
  Para revisar tu versión:

  ```bash
  python --version
  ```

  Si no lo tienes, descárgalo de <https://www.python.org/downloads/>. Al instalarlo en
  Windows, marca la casilla **"Add Python to PATH"**.

- Conexión a internet solo la primera vez, para instalar las dependencias.

---

## 🚀 Cómo correr el programa (paso a paso)

### 1. Abrir una terminal en la carpeta del proyecto

En VS Code: **Archivo → Abrir carpeta → `proyecto_ia`** y luego **Terminal → Nueva terminal**.

También puedes hacerlo desde cualquier terminal:

```bash
cd "ruta/a/proyecto_ia"
```

### 2. Crear el entorno virtual (solo la primera vez)

El entorno virtual es una carpeta `.venv` donde se instalan las librerías del proyecto, sin
afectar el resto de tu computadora.

```bash
python -m venv .venv
```

### 3. Instalar las dependencias (solo la primera vez)

**Windows (PowerShell / CMD):**

```bash
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Windows (Git Bash):**

```bash
./.venv/Scripts/python.exe -m pip install -r requirements.txt
```

**macOS / Linux:**

```bash
.venv/bin/python -m pip install -r requirements.txt
```

### 4. Abrir la interfaz visual

**Windows (PowerShell / CMD):**

```bash
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**Windows (Git Bash):**

```bash
./.venv/Scripts/python.exe -m streamlit run app.py
```

**macOS / Linux:**

```bash
.venv/bin/python -m streamlit run app.py
```

El navegador se abre solo en **<http://localhost:8501>**. Si no se abre, copia esa dirección
en el navegador.

Para **cerrar** el programa, regresa a la terminal y presiona **Ctrl + C**.

> 💡 **Opcional: activar el entorno.** Si activas el entorno, puedes escribir `python` y
> `streamlit` sin poner la ruta `.venv\Scripts\` antes:
>
> - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
> - Windows (CMD): `.venv\Scripts\activate.bat`
> - macOS / Linux: `source .venv/bin/activate`
>
> Después de activarlo basta con escribir `streamlit run app.py`.

---

## 🖥️ Cómo usar la interfaz

En la **barra lateral** eliges el **mapa** (Oficina, Escuela o Bodega) y el **punto de
inicio**: uno de los 5 predefinidos o uno personalizado.

| Pestaña | Qué hace |
|---|---|
| 🗺️ **Simulador** | Elige un algoritmo y verás la ruta, las celdas exploradas y sus métricas. Puedes **pintar celdas** (muro, fuego, humo, salida, libre) o editar todo el edificio como tabla. |
| 📊 **Comparar algoritmos** | Corre los 6 algoritmos sobre el mismo mapa e inicio: tabla, gráficas y la ruta de cada uno. |
| 🧪 **Experimento completo** | Corre las 90 pruebas (3 mapas × 5 inicios × 6 algoritmos), muestra los promedios y permite descargar el CSV. |
| 🧠 **Memoria** | Muestra cuándo el sistema **razona** (busca la ruta) y cuándo **recuerda** una ruta ya aprendida. |

El botón **"Restaurar mapa original"** deshace los cambios que hayas hecho al edificio.

---

## 🧪 Correr el experimento completo sin interfaz

Genera la tabla y las gráficas comparativas en la carpeta `resultados/`:

```bash
.venv\Scripts\python experimentos.py
```

| Archivo generado | Contenido |
|---|---|
| `resultados/resultados.csv` | Las 90 corridas, una fila por corrida |
| `resultados/resumen.csv` | Promedios por algoritmo |
| `resultados/grafica_*.png` | Gráficas de costo, nodos expandidos, tiempo, memoria, éxito y exceso de costo |
| `resultados/mapa_*.png` | Cada mapa con las rutas de A* |
| `resultados/memoizacion.txt` | Demostración de razonar contra recordar |

---

## ✅ Correr las pruebas automáticas

```bash
.venv\Scripts\python -m pytest -v
```

Deben pasar las **135 pruebas**.

---

## 🛠️ Problemas comunes

| Problema | Solución |
|---|---|
| `python` no se reconoce como comando | Reinstala Python marcando **"Add Python to PATH"**, o prueba con `py` en lugar de `python`. |
| PowerShell no deja activar el entorno ("la ejecución de scripts está deshabilitada") | No necesitas activarlo: usa los comandos con `.venv\Scripts\python ...` como aparecen arriba. |
| `No module named streamlit` | No se instalaron las dependencias, o estás usando el Python equivocado. Repite el paso 3 y usa `.venv\Scripts\python`. |
| El puerto 8501 está ocupado | Ya hay otra copia abierta. Ciérrala con Ctrl + C o usa otro puerto: `.venv\Scripts\python -m streamlit run app.py --server.port 8502` |
| La carpeta está en OneDrive y va lento | Es normal la primera vez, mientras OneDrive sincroniza la carpeta `.venv`. |

---

## 📐 Reglas del modelo

| Celda | Símbolo | Costo |
|---|---|---|
| Libre | `.` | 1 |
| Humo | `H` | 5 |
| Salida | `S` | 1 (objetivo) |
| Muro | `#` | bloqueada |
| Fuego | `F` | bloqueada (no se propaga) |

- La persona se mueve arriba, abajo, izquierda o derecha.
- Heurística: distancia Manhattan a la salida más cercana.
- Se usan 3 mapas con 5 puntos de inicio cada uno.

---

## 📁 Estructura del proyecto

```
proyecto_ia/
├── app.py                     Interfaz Streamlit (4 pestañas)
├── experimentos.py            Corre las 90 pruebas y genera la tabla y las gráficas
├── requirements.txt           Dependencias
├── simulador/
│   ├── cuadricula.py          Representación del edificio, costos y heurística
│   ├── mapas.py               Los 3 mapas y sus 5 puntos de inicio
│   ├── algoritmos/
│   │   ├── base.py            Resultado común y reconstrucción de rutas
│   │   ├── no_informados.py   BFS, DFS y UCS
│   │   └── informados.py      Greedy, A* y Hill Climbing
│   ├── metricas.py            Tiempo, memoria y experimento completo
│   ├── memoria.py             Memoización de rutas (razonar contra aprender)
│   └── visual.py              Dibujo del mapa y gráficas
├── tests/test_simulador.py    135 pruebas automáticas
├── resultados/                CSV, gráficas y demostración de memoización
└── docs/manual_tecnico.md     Manual técnico (borrador)
```

Más detalle sobre los algoritmos y los resultados: [docs/manual_tecnico.md](docs/manual_tecnico.md).

---

## 👥 Equipo

| Parte | Responsable |
|---|---|
| 1. Mapas, representación de la cuadrícula y estructura | ____ |
| 2. BFS, DFS y UCS | ____ |
| 3. Greedy, A* y Hill Climbing | ____ |
| 4. Métricas, gráficas e interfaz | ____ |
