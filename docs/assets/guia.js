// Oracle — la guía como juego. Vuelve interactivos los bloques `<!-- juego {...} -->` que
// `tools/sitio.py` deja en la página: misiones, predicciones, preguntas, el tablero y la cacería
// de mutantes. Sin dependencias.
//
// Lo que el juego afirma sobre Oracle no se escribe acá: el `donde` del tablero es la forma
// canónica de la medida real, y qué caso mata a qué mutante lo calculó `nucleo.mutacion` al generar
// la página. Este archivo sólo lo muestra y lleva el puntaje.
(() => {
  "use strict";

  const CLAVE = "oracle-de-cero-v1";
  const reducido = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const RANGOS = [[0, "Grumete"], [150, "Marinero"], [350, "Cabo"], [600, "Sargento"],
                  [900, "Teniente"], [1200, "Capitán"]];
  const LOGROS = {
    enrolado:     ["Enrolado", "Instalaste Oracle y viste tu primer SIN MEDICIÓN.", "ancla"],
    cronista:     ["Cronista", "Distinguiste un hecho de una opinión.", "hoja"],
    primer_rojo:  ["Primer rojo", "Escribiste el caso rojo antes que la regla.", "bandera"],
    cartografo:   ["Cartógrafo", "Pusiste la regla roja por sus cuatro bordes.", "barco"],
    cazamutantes: ["Cazamutantes", "No dejaste vivo ni un mutante de la regla del tablero.", "mutante"],
    flota:        ["Once reglas", "Cada regla del juego tiene casos que la pueden romper.", "barco"],
    juez:         ["Juez de partidas", "Juzgaste una partida de verdad y leíste lo que no se miró.", "ojo"],
    disenador:    ["Diseñador de reglas", "Pensaste una regla que el juego todavía no tiene.", "hoja"],
    oraculo:      ["Oráculo", "Predijiste todas las salidas al primer intento.", "ojo"],
    almirante:    ["Almirante", "Terminaste las nueve misiones.", "trofeo"],
  };

  // ---------------------------------------------------------------- estado (sólo en este navegador)
  function nuevo() { return { puntos: {}, logros: {}, predicciones: {} }; }
  function cargar() {
    try {
      const e = JSON.parse(localStorage.getItem(CLAVE));
      return e && typeof e === "object" && e.puntos ? e : nuevo();
    } catch (_) { return nuevo(); }
  }
  function guardar() { try { localStorage.setItem(CLAVE, JSON.stringify(estado)); } catch (_) { /* sin almacenamiento */ } }
  let estado = cargar();
  const xp = () => Object.values(estado.puntos).reduce((a, b) => a + b, 0);

  // Cada acción suma una sola vez: repetirla no infla el puntaje.
  function sumar(id, puntos) {
    if (id in estado.puntos) return false;
    estado.puntos[id] = puntos;
    guardar();
    actualizar();
    if (puntos) aviso(`+${puntos} XP`, null);
    return true;
  }
  function otorgar(id) {
    if (!LOGROS[id] || estado.logros[id]) return;
    estado.logros[id] = true;
    guardar();
    actualizar();
    aviso(`Logro: ${LOGROS[id][0]}`, LOGROS[id][2], LOGROS[id][1]);
  }

  // ---------------------------------------------------------------- pixel art
  const SPRITES = {
    ancla: ["...kk...", "..k..k..", "...kk...", "kkkkkkkk", "...kk...", "k..kk..k", ".k.kk.k.", "..kkkk.."],
    hoja: ["kkkkkk..", "kwwwwkk.", "kwllwwk.", "kwwwwwk.", "kwlllwk.", "kwwwwwk.", "kwllwwk.", "kkkkkkk."],
    bandera: ["kr......", "krrr....", "krrrrr..", "krrrrrrr", "krrrr...", "kr......", "k.......", "k......."],
    barco: ["...k....", "...kr...", "...krr..", "...k....", "kkkkkkkk", ".kiiiik.", "..kkkk..", "bbbbbbbb"],
    mutante: [".v....v.", "..vvvv..", ".vkvvkv.", "vvvvvvvv", "v.vvvv.v", "..v..v..", ".v....v.", "........"],
    ojo: ["..kkkk..", ".kwwwwk.", "kwwiiwwk", "kwikkiwk", "kwikkiwk", "kwwiiwwk", ".kwwwwk.", "..kkkk.."],
    trofeo: ["aaaaaaaa", "a.aaaa.a", "a.aaaa.a", ".aaaaaa.", "..aaaa..", "...aa...", "..aaaa..", ".kkkkkk."],
    muerto: ["........", ".k....k.", "..k..k..", "...kk...", "...kk...", "..k..k..", ".k....k.", "........"],
  };
  function paleta() {
    const s = getComputedStyle(document.documentElement);
    const v = (n) => s.getPropertyValue(n).trim();
    return { k: v("--tinta"), w: v("--papel"), l: v("--linea"), i: v("--acento"), r: v("--rojo"),
             v: v("--verde"), a: v("--ambar"), b: v("--acento-suave"), g: v("--gris") };
  }
  function sprite(nombre, escala = 4, colores = null) {
    const filas = SPRITES[nombre] || SPRITES.ancla;
    const c = document.createElement("canvas");
    c.width = filas[0].length; c.height = filas.length;
    c.className = "sprite";
    c.style.width = `${c.width * escala}px`; c.style.height = `${c.height * escala}px`;
    c.setAttribute("aria-hidden", "true");
    const ctx = c.getContext("2d");
    const p = { ...paleta(), ...(colores || {}) };
    filas.forEach((fila, y) => [...fila].forEach((ch, x) => {
      if (ch === ".") return;
      ctx.fillStyle = p[ch] || p.k;
      ctx.fillRect(x, y, 1, 1);
    }));
    return c;
  }
  // Cada mutante tiene su cara: el color sale del nombre, así un mismo mutante se reconoce siempre.
  function colorDe(texto) {
    let h = 0;
    for (const ch of texto) h = (h * 31 + ch.codePointAt(0)) >>> 0;
    return `hsl(${h % 360} 62% 52%)`;
  }

  // ---------------------------------------------------------------- utilidades de DOM
  function el(etiqueta, clase, texto) {
    const e = document.createElement(etiqueta);
    if (clase) e.className = clase;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }
  // `código` en los textos del juego, como en el resto de la página.
  function conCodigo(nodo, texto) {
    texto.split(/(`[^`]+`)/).forEach((parte) => {
      if (parte.startsWith("`") && parte.endsWith("`") && parte.length > 1) nodo.append(el("code", "", parte.slice(1, -1)));
      else if (parte) nodo.append(document.createTextNode(parte));
    });
    return nodo;
  }
  function boton(texto, clase, accion) {
    const b = el("button", clase, texto);
    b.type = "button";
    b.addEventListener("click", accion);
    return b;
  }

  // ---------------------------------------------------------------- avisos
  const zonaAvisos = el("div", "avisos");
  zonaAvisos.setAttribute("aria-live", "polite");
  function aviso(titulo, nombreSprite, texto) {
    const a = el("div", "aviso");
    // El aviso es oscuro: el sprite se dibuja con el color del papel para que se vea.
    if (nombreSprite) a.append(sprite(nombreSprite, 4, { k: paleta().w }));
    while (zonaAvisos.children.length >= 3) zonaAvisos.firstElementChild.remove();
    const cuerpo = el("div");
    cuerpo.append(el("strong", "pixel", titulo));
    if (texto) cuerpo.append(el("span", "", texto));
    a.append(cuerpo);
    zonaAvisos.append(a);
    setTimeout(() => a.classList.add("sale"), reducido ? 3000 : 2600);
    setTimeout(() => a.remove(), 3400);
  }

  // ---------------------------------------------------------------- bitácora
  const misiones = [];
  const bitacora = el("aside", "bitacora");
  bitacora.setAttribute("aria-label", "Tu progreso en la guía");
  const pastilla = el("button", "bitacora-pastilla");
  pastilla.type = "button";
  pastilla.setAttribute("aria-expanded", "false");
  const panel = el("div", "bitacora-panel");
  panel.hidden = true;
  pastilla.addEventListener("click", () => {
    panel.hidden = !panel.hidden;
    pastilla.setAttribute("aria-expanded", String(!panel.hidden));
  });
  bitacora.append(panel, pastilla);

  function rango() {
    const hechas = misiones.filter((m) => estado.puntos[`mision-${m.n}`] !== undefined).length;
    if (misiones.length && hechas === misiones.length) return ["Almirante", null, hechas];
    const puntos = xp();
    let actual = RANGOS[0], siguiente = null;
    for (const r of RANGOS) { if (puntos >= r[0]) actual = r; else { siguiente = r; break; } }
    return [actual[1], siguiente, hechas];
  }

  function actualizar() {
    const [nombre, siguiente, hechas] = rango();
    const puntos = xp();
    pastilla.replaceChildren(sprite("ancla", 3),
      el("span", "pixel", `${puntos} XP · ${nombre} · ${hechas}/${misiones.length}`));

    panel.replaceChildren();
    panel.append(el("p", "pixel bitacora-titulo", "Bitácora"));
    panel.append(el("p", "bitacora-rango", nombre));
    const barra = el("div", "barra-xp");
    const base = RANGOS.filter((r) => r[0] <= puntos).pop()[0];
    const tope = siguiente ? siguiente[0] : Math.max(puntos, 1);
    const relleno = el("span");
    relleno.style.width = `${Math.min(100, ((puntos - base) / Math.max(1, tope - base)) * 100)}%`;
    barra.append(relleno);
    barra.setAttribute("role", "img");
    barra.setAttribute("aria-label", siguiente ? `${puntos} de ${siguiente[0]} XP para ${siguiente[1]}` : `${puntos} XP`);
    panel.append(barra);
    panel.append(el("p", "bitacora-sub", siguiente ? `${siguiente[0] - puntos} XP para ${siguiente[1]}` : "Rango máximo por puntaje"));

    const banderas = el("ol", "banderas");
    for (const m of misiones) {
      const li = el("li");
      const hecha = estado.puntos[`mision-${m.n}`] !== undefined;
      li.className = hecha ? "hecha" : "";
      const a = el("a", "", String(m.n));
      a.href = `#${m.ancla}`;
      a.title = `Misión ${m.n}: ${m.titulo}${hecha ? " (cumplida)" : ""}`;
      li.append(a);
      banderas.append(li);
    }
    panel.append(el("p", "pixel bitacora-titulo", "Misiones"), banderas);

    const logros = el("ul", "logros");
    for (const [id, [nombreLogro, texto, spr]] of Object.entries(LOGROS)) {
      const li = el("li", estado.logros[id] ? "tiene" : "");
      li.append(sprite(estado.logros[id] ? spr : "ancla", 3, estado.logros[id] ? null : { k: paleta().l }));
      li.append(el("span", "", estado.logros[id] ? nombreLogro : "???"));
      li.title = estado.logros[id] ? texto : "Todavía no";
      logros.append(li);
    }
    panel.append(el("p", "pixel bitacora-titulo", `Logros ${Object.keys(estado.logros).length}/${Object.keys(LOGROS).length}`), logros);

    let armado = false;
    const reiniciar = boton("Empezar de nuevo", "enlace-boton", () => {
      if (!armado) { armado = true; reiniciar.textContent = "¿Seguro? Tocá otra vez"; return; }
      estado = nuevo(); guardar(); location.reload();
    });
    panel.append(reiniciar);
    document.querySelectorAll(".mision-cumplida").forEach((b) => b.dispatchEvent(new Event("refrescar")));
  }

  // ---------------------------------------------------------------- misiones
  function mision(nodo, d) {
    const h2 = nodo.previousElementSibling;
    if (!h2 || h2.tagName !== "H2") return;
    const titulo = h2.textContent.replace(/#$/, "").replace(/^Paso \d+ · /, "");
    misiones.push({ n: d.n, titulo, ancla: h2.id });
    h2.classList.add("mision-h2");
    const cinta = el("div", "mision-cinta");
    cinta.append(sprite(d.sprite || "bandera", 4), el("span", "pixel", `Misión ${d.n}`),
                 el("span", "mision-xp pixel", `+${d.xp} XP`));
    h2.before(cinta);
    const objetivo = el("p", "mision-objetivo");
    objetivo.append(el("strong", "pixel", "Objetivo "), document.createTextNode(d.objetivo));
    nodo.replaceWith(objetivo);

    // El botón va al final de la sección: después de hacer, no antes.
    let fin = objetivo.nextElementSibling;
    while (fin && fin.tagName !== "H2" && !fin.classList.contains("fuente")) fin = fin.nextElementSibling;
    const b = boton("", "mision-cumplida", () => {
      if (sumar(`mision-${d.n}`, d.xp)) {
        if (d.logro) otorgar(d.logro);
        if (misiones.every((m) => estado.puntos[`mision-${m.n}`] !== undefined)) otorgar("almirante");
      }
    });
    b.addEventListener("refrescar", () => {
      const hecha = estado.puntos[`mision-${d.n}`] !== undefined;
      b.textContent = hecha ? `✔ Misión ${d.n} cumplida` : `Lo hice en mi terminal: misión cumplida (+${d.xp} XP)`;
      b.disabled = hecha;
    });
    const envoltura = el("div", "mision-fin");
    envoltura.append(b);
    if (fin) fin.before(envoltura); else objetivo.parentElement.append(envoltura);
    b.dispatchEvent(new Event("refrescar"));
  }

  // ---------------------------------------------------------------- predecir la salida
  function predecir(nodo, d) {
    const salida = nodo.nextElementSibling;
    if (!salida || !salida.matches("pre.salida")) return;
    const caja = el("div", "prediccion");
    caja.append(el("p", "pixel prediccion-titulo", "Predecí la salida"));
    caja.append(conCodigo(el("p", "prediccion-pregunta"), d.pregunta));
    const opciones = el("div", "opciones");
    const resultado = el("p", "prediccion-resultado");
    resultado.setAttribute("aria-live", "polite");
    const previa = estado.predicciones[d.id];
    const revelar = () => { salida.classList.remove("velada"); salida.removeAttribute("aria-hidden"); ver.remove(); };
    const ver = boton("Mostrar sin predecir", "enlace-boton", revelar);
    for (const op of d.opciones) {
      const b = boton(op, `opcion lampara ${claseDe(op)}`, () => {
        const acierto = op === d.correcta;
        if (!(d.id in estado.predicciones)) {
          estado.predicciones[d.id] = acierto;
          guardar();
          if (acierto) sumar(`prediccion-${d.id}`, 25);
          comprobarOraculo();
        }
        opciones.querySelectorAll("button").forEach((x) => {
          x.disabled = true;
          if (x.textContent === d.correcta) x.classList.add("correcta");
        });
        if (!acierto) b.classList.add("errada");
        resultado.replaceChildren();
        conCodigo(resultado, acierto ? `¡Acertaste! ${d.explica || ""}` : `Salió ${d.correcta}. ${d.explica || ""}`);
        revelar();
      });
      opciones.append(b);
    }
    caja.append(opciones, resultado, ver);
    nodo.replaceWith(caja);
    if (previa === undefined) {
      salida.classList.add("velada");
      salida.setAttribute("aria-hidden", "true");
    } else {
      opciones.querySelectorAll("button").forEach((x) => { x.disabled = true; if (x.textContent === d.correcta) x.classList.add("correcta"); });
      resultado.textContent = previa ? "Lo predijiste bien." : `Salió ${d.correcta}.`;
      ver.remove();
    }
  }
  function claseDe(op) {
    if (/^VERDE/i.test(op)) return "verde";
    if (/^ROJO/i.test(op)) return "rojo";
    return "ambar";
  }
  let predicciones = [];
  function comprobarOraculo() {
    if (predicciones.length && predicciones.every((id) => estado.predicciones[id] === true)) otorgar("oraculo");
  }

  // ---------------------------------------------------------------- elegir (pregunta cerrada)
  function elegir(nodo, d) {
    const caja = el("div", "prediccion elegir");
    caja.append(el("p", "pixel prediccion-titulo", d.titulo || "Elegí"));
    caja.append(conCodigo(el("p", "prediccion-pregunta"), d.pregunta));
    const opciones = el("div", "opciones columna");
    const resultado = el("p", "prediccion-resultado");
    resultado.setAttribute("aria-live", "polite");
    d.opciones.forEach((op) => {
      const b = boton("", "opcion-larga", () => {
        b.classList.add(op.ok ? "correcta" : "errada");
        resultado.replaceChildren(); conCodigo(resultado, op.porque);
        if (op.ok) {
          opciones.querySelectorAll("button").forEach((x) => { x.disabled = true; });
          sumar(`elegir-${d.id}`, d.xp || 20);
          if (d.logro) otorgar(d.logro);
        }
      });
      if (op.codigo) b.append(el("code", "", op.texto)); else b.textContent = op.texto;
      opciones.append(b);
    });
    caja.append(opciones, resultado);
    nodo.replaceWith(caja);
  }

  // ---------------------------------------------------------------- el álgebra mínima del tablero
  // Evalúa la forma canónica tal como la escribió Oracle. Sólo lo que aparece en un `donde` de
  // comparaciones: si la medida usara otra cosa, el tablero lo dice en vez de adivinar.
  function evaluar(expr, fila) {
    if (!Array.isArray(expr)) return expr;
    const [op, ...args] = expr;
    const val = (x) => evaluar(x, fila);
    switch (op) {
      case "campo": return fila[args[1]];
      case "o": return args.map(val).some(Boolean);
      case "y": return args.map(val).every(Boolean);
      case "no": return !val(args[0]);
      case "<": return val(args[0]) < val(args[1]);
      case "<=": return val(args[0]) <= val(args[1]);
      case ">": return val(args[0]) > val(args[1]);
      case ">=": return val(args[0]) >= val(args[1]);
      case "==": return val(args[0]) === val(args[1]);
      case "!=": return val(args[0]) !== val(args[1]);
      default: throw new Error(`operador no soportado en el tablero: ${op}`);
    }
  }
  function texto(expr) {
    if (!Array.isArray(expr)) return JSON.stringify(expr);
    const [op, ...args] = expr;
    if (op === "campo") return `${args[0]}.${args[1]}`;
    if (op === "o" || op === "y") return args.map(texto).join(` ${op} `);
    if (op === "no") return `no (${texto(args[0])})`;
    return `${texto(args[0])} ${op} ${texto(args[1])}`;
  }

  // ---------------------------------------------------------------- tablero: rompé la regla
  function tablero(nodo, d) {
    const ramas = d.donde[0] === "o" ? d.donde.slice(1) : [d.donde];
    const ocupadas = new Map(d.inicial.map(([f, c]) => [`${f},${c}`, [f, c]]));
    const encontradas = new Set(estado.puntos[`tablero-${d.id}`] !== undefined ? ramas.map((_, i) => i) : []);
    const caja = el("div", "minijuego tablero-juego");
    caja.append(el("p", "pixel prediccion-titulo", d.titulo || "Rompé la regla"));
    caja.append(conCodigo(el("p", "prediccion-pregunta"), d.consigna));
    const rejilla = el("div", "rejilla");
    rejilla.setAttribute("role", "grid");
    rejilla.setAttribute("aria-label", "Tablero de 10 por 10 con un borde de casillas que no existen");
    const lado = el("div", "tablero-lado");
    const regla = el("pre", "regla-mini");
    regla.textContent = `ninguno ${d.medida}:\n    de ${d.relacion} ${d.alias}\n    donde ${texto(d.donde)}\n    umbral ${d.umbral[0]} ${d.umbral[1]}`;
    const evidencia = el("pre", "evidencia-mini");
    const veredicto = el("pre", "veredicto-mini");
    veredicto.setAttribute("aria-live", "polite");
    const retos = el("ul", "retos");
    const botones = el("div", "fila-botones");
    botones.append(boton("Vaciar el tablero", "enlace-boton", () => { ocupadas.clear(); pintar(); }),
                   boton("Volver al caso 005", "enlace-boton", () => {
                     ocupadas.clear(); d.inicial.forEach(([f, c]) => ocupadas.set(`${f},${c}`, [f, c])); pintar(); }));
    lado.append(el("p", "pixel etiqueta-mini", "la regla"), regla,
                el("p", "pixel etiqueta-mini", `la evidencia (${d.relacion})`), evidencia,
                el("p", "pixel etiqueta-mini", "lo que diría oracle juzgar"), veredicto);

    for (let f = -1; f <= 10; f++) {
      for (let c = -1; c <= 10; c++) {
        const fuera = f < 0 || f > 9 || c < 0 || c > 9;
        const celda = el("button", `celda${fuera ? " fuera" : ""}`);
        celda.type = "button";
        celda.dataset.f = f; celda.dataset.c = c;
        celda.setAttribute("aria-label", `fila ${f}, columna ${c}${fuera ? ", fuera del tablero" : ""}`);
        celda.addEventListener("click", () => {
          const k = `${f},${c}`;
          if (ocupadas.has(k)) ocupadas.delete(k); else ocupadas.set(k, [f, c]);
          pintar();
        });
        rejilla.append(celda);
      }
    }

    function pintar() {
      const filas = [...ocupadas.values()].sort((a, b) => a[0] - b[0] || a[1] - b[1])
        .map(([f, c], i) => ({ id: `c${i + 1}`, fila: f, columna: c }));
      rejilla.querySelectorAll(".celda").forEach((x) => {
        const on = ocupadas.has(`${x.dataset.f},${x.dataset.c}`);
        x.classList.toggle("barco", on);
        x.setAttribute("aria-pressed", String(on));
      });
      evidencia.textContent = filas.length
        ? `${d.relacion}: id, fila, columna\n` + filas.map((r) => `    "${r.id}", ${r.fila}, ${r.columna}`).join("\n")
        : `${d.relacion}: (ninguna fila)`;
      let testigos;
      try {
        testigos = filas.filter((r) => evaluar(d.donde, r) === true);
      } catch (e) { veredicto.textContent = String(e.message); return; }
      testigos.forEach((t) => ramas.forEach((r, i) => { if (evaluar(r, t) === true) encontradas.add(i); }));
      const n = testigos.length;
      const ok = n <= d.umbral[1];
      if (!filas.length && d.requiere.includes(d.relacion)) {
        veredicto.textContent = `⊘ ${d.medida}  SIN EVIDENCIA («${d.relacion}» vacía; no se midió)`;
        veredicto.className = "veredicto-mini ambar";
      } else {
        veredicto.textContent = `${ok ? "✓" : "✗"} ${d.medida}  ${n} (${d.umbral[0]} ${d.umbral[1]})` +
          testigos.map((t) => `\n      → ${d.alias}={'id': '${t.id}', 'fila': ${t.fila}, 'columna': ${t.columna}}`).join("") +
          (!filas.length ? `\n\nVerde con cero casillas: esta regla es «ninguno» a secas. Por eso\nlas reglas que miran un universo usan la variante -requiere.` : "");
        veredicto.className = `veredicto-mini ${ok ? "verde" : "rojo"}`;
      }
      retos.replaceChildren(...ramas.map((r, i) => {
        const li = el("li", encontradas.has(i) ? "hecho" : "");
        li.append(el("span", "pixel", encontradas.has(i) ? "✔" : "·"), el("code", "", texto(r)));
        return li;
      }));
      if (encontradas.size === ramas.length && sumar(`tablero-${d.id}`, d.xp || 60)) otorgar(d.logro);
    }

    const cuerpo = el("div", "tablero-cuerpo");
    const izquierda = el("div");
    izquierda.append(rejilla, botones, el("p", "pixel etiqueta-mini", "reto: poné la regla roja con cada condición"), retos);
    cuerpo.append(izquierda, lado);
    caja.append(cuerpo, conCodigo(el("p", "nota-mini"), "Esta simulación corre en tu navegador sobre la forma canónica de la medida real. El veredicto que vale es el de `oracle juzgar`."));
    nodo.replaceWith(caja);
    pintar();
  }

  // ---------------------------------------------------------------- cacería de mutantes
  function cazamutantes(nodo, d) {
    const activos = new Set(d.activos);
    const caja = el("div", "minijuego caza");
    caja.append(el("p", "pixel prediccion-titulo", d.titulo || "Cacería de mutantes"));
    caja.append(conCodigo(el("p", "prediccion-pregunta"), d.consigna));
    const regla = el("pre", "regla-mini");
    regla.textContent = d.regla.join("\n");
    const marcador = el("p", "marcador pixel");
    marcador.setAttribute("aria-live", "polite");
    const casos = el("ul", "casos-caza");
    const grilla = el("ul", "mutantes");

    d.casos.forEach((c) => {
      const li = el("li");
      const id = `caso-${d.id}-${c.id}`;
      const input = el("input");
      input.type = "checkbox"; input.id = id; input.checked = activos.has(c.id);
      input.disabled = d.activos.includes(c.id) && d.fijos !== false;
      input.addEventListener("change", () => { if (input.checked) activos.add(c.id); else activos.delete(c.id); pintar(); });
      const label = el("label");
      label.htmlFor = id;
      const esperado = c.etiqueta === "verde_correcto" ? "verde" : "rojo";
      label.append(el("span", `lampara ${esperado}`, esperado), el("strong", "", c.id.slice(0, 3)),
                   document.createTextNode(` ${c.titulo}`));
      const filas = Object.entries(c.evidencia).map(([rel, fs]) => fs.filter((f) => !Array.isArray(f))
        .map((f) => `${rel}: fila ${f.fila}, columna ${f.columna}`).join(" · ")).join(" · ");
      li.append(input, label, el("small", "", filas));
      casos.append(li);
    });

    function pintar() {
      let vivos = 0;
      grilla.replaceChildren(...d.mutantes.map((m) => {
        const asesinos = m.muere_con.filter((c) => activos.has(c));
        const vivo = asesinos.length === 0;
        if (vivo) vivos += 1;
        const li = el("li", vivo ? "vivo" : "muerto");
        li.append(sprite(vivo ? "mutante" : "muerto", 4, vivo ? { v: colorDe(m.id) } : { k: paleta().g }));
        const info = el("div");
        info.append(el("span", "pixel nombre-mutante", m.id.replace(/^expresion:|^agregado:|^campo:/, "").replace(/@[\d.]+:/, " ").replace(/_/g, " ")));
        const linea = m.cambia.length ? m.cambia.join(" · ") : `sin «${m.quita.join(" · ")}»`;
        info.append(el("code", "", linea));
        const pista = vivo
          ? (m.muere_con.length ? `lo mataría ${m.muere_con.map((c) => c.slice(0, 3)).join(" o ")}` : "ningún caso de esta lista lo mata")
          : `lo mató ${asesinos.map((c) => c.slice(0, 3)).join(", ")}`;
        info.append(el("small", "", pista));
        li.append(info);
        return li;
      }));
      marcador.textContent = vivos ? `${vivos} de ${d.mutantes.length} mutantes vivos` : `¡Los ${d.mutantes.length} mutantes murieron!`;
      marcador.className = `marcador pixel ${vivos ? "rojo" : "verde"}`;
      if (!vivos && sumar(`caza-${d.id}`, d.xp || 80)) otorgar(d.logro);
    }

    const cuerpo = el("div", "caza-cuerpo");
    const izq = el("div");
    izq.append(el("p", "pixel etiqueta-mini", "la regla"), regla, el("p", "pixel etiqueta-mini", "tus casos"), casos);
    const der = el("div");
    der.append(marcador, grilla);
    cuerpo.append(izq, der);
    caja.append(cuerpo, el("p", "nota-mini", "Los mutantes y quién mata a quién los calculó Oracle al generar esta página, con los casos reales del ejemplo."));
    nodo.replaceWith(caja);
    pintar();
  }

  // ---------------------------------------------------------------- cierre
  function cierre(nodo) {
    const caja = el("div", "minijuego cierre");
    const pintar = () => {
      const [nombre, , hechas] = rango();
      caja.replaceChildren(sprite(hechas === misiones.length ? "trofeo" : "ancla", 8),
        el("p", "pixel prediccion-titulo", "Fin de la travesía"),
        el("p", "cierre-rango", nombre),
        el("p", "", `${xp()} XP · ${hechas} de ${misiones.length} misiones · ${Object.keys(estado.logros).length} logros`));
    };
    nodo.replaceWith(caja);
    pintar();
    caja.addEventListener("refrescar", pintar);
    new MutationObserver(pintar).observe(pastilla, { childList: true });
  }

  // ---------------------------------------------------------------- las preguntas «Pensalo»
  function pensalo() {
    document.querySelectorAll(".prosa p.pregunta").forEach((p, i) => {
      const detalles = p.nextElementSibling;
      if (!detalles || detalles.tagName !== "DETAILS") return;
      p.prepend(sprite("ojo", 3));
      detalles.addEventListener("toggle", () => { if (detalles.open) sumar(`pensalo-${i}`, 10); });
    });
  }

  // ---------------------------------------------------------------- arranque
  const PIEZAS = { mision, predecir, elegir, tablero, cazamutantes, cierre };
  function arrancar() {
    const nodos = [...document.querySelectorAll(".juego[data-juego]")];
    if (!nodos.length) return;
    document.body.classList.add("con-juego");
    document.body.append(bitacora, zonaAvisos);
    predicciones = nodos.map((n) => JSON.parse(n.dataset.juego)).filter((d) => d.tipo === "predecir").map((d) => d.id);
    for (const n of nodos) {
      const d = JSON.parse(n.dataset.juego);
      try { PIEZAS[d.tipo](n, d); } catch (e) { console.error("[guia]", d.tipo, e); }
    }
    pensalo();
    actualizar();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", arrancar);
  else arrancar();
})();
