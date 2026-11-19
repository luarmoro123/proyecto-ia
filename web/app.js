/* Escape de incendio forestal — lógica de la página (JavaScript propio)
 *
 * 1. Pide el mapa al servidor (GET /api/mapa).
 * 2. Al correr un algoritmo, el servidor lo ejecuta (POST /api/correr) y
 *    devuelve el orden en que expandió las celdas y la ruta final.
 * 3. La página reproduce esa búsqueda en vivo, celda por celda.
 */

"use strict";

const CELDAS_POR_SEGUNDO = 30;
const COLOR_CELDA ={ ".": "var(--libre)", "#": "var(--roca)", "F": "var(--fuego)", "H": "var(--humo)", "S": "var(--salida)" };

const estado = {
  datos: null,        // respuesta de /api/mapa
  algoritmo: "A*",
  inicio: null,
  resultado: null,    // corrida actual (de /api/correr)
  paso: 0,            // cuántas celdas expandidas se muestran
  temporizador: null,
  tabla: {},          // algoritmo -> resultado, para el inicio actual
};

const $ = (id) => document.getElementById(id);
const mismaPos = (a, b) => a[0] === b[0] && a[1] === b[1];
const color = (alg) => estado.datos.colores[alg];

// ---------------------------------------------------------------- Dibujo
function dibujarMapa() {
  const celdas = estado.datos.celdas;
  const filas = celdas.length, cols = celdas[0].length, m = 0.9;
  const svg = $("mapa");
  svg.setAttribute("viewBox", `${-m} ${-m} ${cols + m} ${filas + m}`);
  let html = "";
  celdas.forEach((fila, f) => fila.forEach((s, c) => {
    html += `<rect x="${c}" y="${f}" width="1" height="1" fill="${COLOR_CELDA[s]}" stroke="var(--linea)" stroke-width=".06" data-f="${f}" data-c="${c}"/>`;
  }));
  for (let i = 0; i < cols; i += 2) html += `<text class="eje" x="${i + .5}" y="-.3" text-anchor="middle">${i}</text>`;
  for (let i = 0; i < filas; i += 2) html += `<text class="eje" x="-.3" y="${i + .65}" text-anchor="end">${i}</text>`;
  svg.innerHTML = html + '<g id="capa" pointer-events="none"></g>';
}

function dibujarCapa() {
  const r = estado.resultado;
  const col = color(estado.algoritmo);
  let html = "";
  if (r) {
    const vistos = r.orden_expansion.slice(0, estado.paso);
    html += vistos.map(([f, c]) => `<circle cx="${c + .5}" cy="${f + .5}" r=".2" fill="${col}"/>`).join("");
    const actual = vistos[vistos.length - 1];
    if (actual && !terminado()) {
      html += `<rect x="${actual[1] + .05}" y="${actual[0] + .05}" width=".9" height=".9" fill="none" stroke="#111" stroke-width=".1"/>`;
    }
    if (terminado() && r.ruta.length > 1) {
      const puntos = r.ruta.map(([f, c]) => `${c + .5},${f + .5}`).join(" ");
      html += `<polyline points="${puntos}" fill="none" stroke="#fff" stroke-width=".42" stroke-linecap="round" stroke-linejoin="round"/>`;
      html += `<polyline points="${puntos}" fill="none" stroke="${col}" stroke-width=".26" stroke-linecap="round" stroke-linejoin="round"/>`;
    }
  }
  const [f, c] = estado.inicio;
  html += `<circle cx="${c + .5}" cy="${f + .5}" r=".32" fill="var(--inicio)" stroke="#000" stroke-width=".05"/>`;
  $("capa").innerHTML = html;
}

// ---------------------------------------------------------------- Estado de la corrida
const total = () => (estado.resultado ? estado.resultado.orden_expansion.length : 0);
const terminado = () => estado.resultado !== null && estado.paso >= total();
const corriendo = () => estado.temporizador !== null;

function actualizarPantalla() {
  dibujarCapa();
  const r = estado.resultado;
  $("barra").style.width = r ? `${(100 * estado.paso) / total()}%` : "0";
  $("btnCorrer").textContent = corriendo() ? "⏸ Pausa" : terminado() ? "↺ Otra vez" : "▶ Correr";
  $("mExpandidos").textContent = r ? estado.paso : "—";

  const fin = terminado();
  $("mCosto").textContent = fin && r.exito ? r.costo : "—";
  $("mPasos").textContent = fin && r.exito ? r.pasos : "—";
  $("mTiempo").textContent = fin ? `${r.tiempo_ms.toFixed(2)} ms` : "—";

  if (!r) $("estado").textContent = "Elige un algoritmo y pulsa Correr.";
  else if (fin) $("estado").textContent = `${r.algoritmo}: ${r.mensaje.replace("salida", "zona segura")} Cruza ${r.celdas_humo} celda(s) con humo.`;
  else if (estado.paso === 0) $("estado").textContent = "Listo para empezar.";
  else {
    const [f, c] = r.orden_expansion[estado.paso - 1];
    $("estado").textContent = `Expandiendo (${f}, ${c}) — paso ${estado.paso} de ${total()}`;
  }
}

function pausar() {
  clearInterval(estado.temporizador);
  estado.temporizador = null;
}

function olvidarCorrida() {
  pausar();
  estado.resultado = null;
  estado.paso = 0;
  actualizarPantalla();
}

async function cargarCorrida() {
  if (estado.resultado) return true;
  const resp = await fetch("/api/correr", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ algoritmo: estado.algoritmo, inicio: estado.inicio }),
  });
  const datos = await resp.json();
  if (!resp.ok) { $("estado").textContent = datos.error; return false; }
  estado.resultado = datos;
  estado.paso = 0;
  return true;
}

function avanzar() {
  if (terminado()) return;
  estado.paso += 1;
  if (terminado()) {
    pausar();
    estado.tabla[estado.algoritmo] = estado.resultado;
    pintarTabla();
  }
  actualizarPantalla();
}

function programar() {
  clearInterval(estado.temporizador);
  estado.temporizador = setInterval(avanzar, 1000 / CELDAS_POR_SEGUNDO);
}

// ---------------------------------------------------------------- Botones
async function correr() {
  if (corriendo()) { pausar(); actualizarPantalla(); return; }
  if (!(await cargarCorrida())) return;
  if (terminado()) estado.paso = 0;
  programar();
  actualizarPantalla();
}

async function paso() {
  pausar();
  if (!(await cargarCorrida())) return;
  avanzar();
  actualizarPantalla();
}

function reiniciar() {
  pausar();
  estado.paso = 0;
  actualizarPantalla();
}

// ---------------------------------------------------------------- Tabla de resultados
function pintarTabla() {
  const filas = estado.datos.algoritmos.filter((a) => estado.tabla[a]);
  $("tabla").innerHTML = filas.length
    ? filas.map((a) => {
        const r = estado.tabla[a];
        return `<tr><td class="alg" style="--c:${color(a)}">${a}</td><td>${r.exito ? r.costo : "—"}</td><td>${r.exito ? r.pasos : "—"}</td><td>${r.nodos_expandidos}</td><td>${r.tiempo_ms.toFixed(3)}</td></tr>`;
      }).join("")
    : '<tr><td colspan="5" class="nota">Aún no se ha corrido ningún algoritmo.</td></tr>';
}

// ---------------------------------------------------------------- Selección
function elegirAlgoritmo(alg) {
  estado.algoritmo = alg;
  document.querySelectorAll(".segmento").forEach((b) => b.classList.toggle("activo", b.dataset.alg === alg));
  olvidarCorrida();
}

function elegirInicio(pos) {
  estado.inicio = pos;
  const i = estado.datos.inicios.findIndex((p) => mismaPos(p, pos));
  $("inicio").value = i >= 0 ? String(i) : "otro";
  $("inicio").querySelector('option[value="otro"]').textContent = i >= 0 ? "Otro (clic en el mapa)" : `Otro: (${pos[0]}, ${pos[1]})`;
  estado.tabla = {};
  pintarTabla();
  olvidarCorrida();
}

// ---------------------------------------------------------------- Arranque
async function iniciar() {
  estado.datos = await (await fetch("/api/mapa")).json();
  const { inicios, algoritmos } = estado.datos;

  $("algoritmos").innerHTML = algoritmos
    .map((a) => `<button class="segmento" data-alg="${a}" style="--c:${color(a)}">${a}</button>`).join("");
  $("algoritmos").addEventListener("click", (e) => {
    const b = e.target.closest(".segmento");
    if (b) elegirAlgoritmo(b.dataset.alg);
  });

  $("inicio").innerHTML = inicios.map((p, i) => `<option value="${i}">Inicio ${i + 1}: (${p[0]}, ${p[1]})</option>`).join("")
    + '<option value="otro" disabled>Otro (clic en el mapa)</option>';
  $("inicio").addEventListener("change", (e) => elegirInicio(inicios[Number(e.target.value)]));

  $("mapa").addEventListener("click", (e) => {
    const celda = e.target.closest("rect[data-f]");
    if (!celda) return;
    const f = Number(celda.dataset.f), c = Number(celda.dataset.c);
    const s = estado.datos.celdas[f][c];
    if (s === "#" || s === "F") { $("estado").textContent = "No se puede iniciar sobre roca/río o fuego."; return; }
    elegirInicio([f, c]);
  });

  $("btnCorrer").addEventListener("click", correr);
  $("btnPaso").addEventListener("click", paso);
  $("btnReiniciar").addEventListener("click", reiniciar);

  dibujarMapa();
  elegirInicio(inicios[0]);
  elegirAlgoritmo(estado.algoritmo);
}

iniciar();
