// Oracle — escenas en pixel art. Cada escena es una función (ctx, t) que dibuja un cuadro del tiempo t
// sobre un lienzo lógico chico, que CSS agranda sin suavizar. Sin dependencias.
//
// Con `prefers-reduced-motion` se dibuja sólo el cuadro final de cada escena, que es el que cuenta
// la idea completa. Una escena fuera de pantalla no se anima.
(() => {
  "use strict";

  const reducido = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------------------------------------------------------------- paleta (sigue el tema)
  function paleta() {
    const s = getComputedStyle(document.documentElement);
    const v = (n) => s.getPropertyValue(n).trim();
    return {
      ".": null, k: v("--tinta"), w: v("--papel"), p: v("--papel-2"), l: v("--linea"),
      g: v("--gris"), i: v("--acento"), r: v("--rojo"), R: v("--rojo-suave"), v: v("--verde"),
      V: v("--verde-suave"), a: v("--ambar"), A: v("--ambar-suave"), c: v("--codigo-fondo"),
      t: v("--codigo-tinta"), K: v("--codigo-clave"),
    };
  }

  // ---------------------------------------------------------------- sprites
  const SPRITES = {
    ojo: [
      ".....kkkkkk.....",
      "...kkwwwwwwkk...",
      "..kwwwwiiwwwwk..",
      ".kwwwiiiiiiwwwk.",
      "kwwwiiikkiiiwwwk",
      "kwwiiikkkkiiiwwk",
      "kwwiiikkkkiiiwwk",
      "kwwwiiikkiiiwwwk",
      ".kwwwiiiiiiwwwk.",
      "..kwwwwiiwwwwk..",
      "...kkwwwwwwkk...",
      ".....kkkkkk.....",
    ],
    ojoCerrado: [
      "................",
      "................",
      "................",
      "................",
      "................",
      "kkkkkkkkkkkkkkkk",
      ".kkwwwwwwwwwwkk.",
      "...kkkkkkkkkk...",
      "................",
      "................",
      "................",
      "................",
    ],
    hoja: [
      "kkkkkkkk.",
      "kwwwwwwkk",
      "kwllllwwk",
      "kwwwwwwwk",
      "kwlllllwk",
      "kwwwwwwwk",
      "kwllllwwk",
      "kwwwwwwwk",
      "kkkkkkkkk",
    ],
    bicho: [
      ".k....k.",
      "..k..k..",
      ".kaaaak.",
      "kaawwaak",
      "kaakkaak",
      ".kaaaak.",
      "k.k..k.k",
    ],
    bichoB: [
      ".k....k.",
      "..k..k..",
      ".kaaaak.",
      "kaawwaak",
      "kaakkaak",
      ".kaaaak.",
      ".k.kk.k.",
    ],
    robot: [
      "...kk...",
      "...ki...",
      "kkkkkkkk",
      "kppppppk",
      "kpkppkpk",
      "kppppppk",
      "kpkkkkpk",
      "kkkkkkkk",
      ".kk..kk.",
    ],
    chispa: [
      "i...i",
      ".i.i.",
      "..i..",
      ".i.i.",
      "i...i",
    ],
  };

  function sprite(ctx, pal, nombre, x, y, sustituir) {
    const filas = SPRITES[nombre];
    for (let j = 0; j < filas.length; j++) {
      for (let k = 0; k < filas[j].length; k++) {
        let c = filas[j][k];
        if (sustituir && c in sustituir) c = sustituir[c];
        const color = pal[c];
        if (color) { ctx.fillStyle = color; ctx.fillRect(x + k, y + j, 1, 1); }
      }
    }
  }

  const caja = (ctx, color, x, y, w, h) => { ctx.fillStyle = color; ctx.fillRect(x, y, w, h); };
  function borde(ctx, color, x, y, w, h) {
    caja(ctx, color, x, y, w, 1); caja(ctx, color, x, y + h - 1, w, 1);
    caja(ctx, color, x, y, 1, h); caja(ctx, color, x + w - 1, y, 1, h);
  }
  function texto(ctx, color, s, x, y, alineado = "left") {
    ctx.fillStyle = color; ctx.font = '8px "Silkscreen", monospace';
    ctx.textAlign = alineado; ctx.textBaseline = "top"; ctx.fillText(s, x, y);
  }
  const fase = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)));

  // ---------------------------------------------------------------- escenas
  // 1. La medida recorre las filas y señala las que ofenden: el veredicto trae sus testigos.
  const NOMBRES = ["acorazado  2,1", "acorazado  2,2", "destructor 9,5", "destructor 10,5", "fragata    4,7", "fragata    4,8"];
  const MALAS = new Set([3]);
  const testigos = {
    duracion: 9000,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.w, 0, 0, 192, 108);
      texto(ctx, pal.g, "celda_ocupada", 8, 6);
      const paso = 900, inicio = 500;
      const barrida = Math.min(NOMBRES.length, Math.floor((t - inicio) / paso));
      let rojos = 0;
      NOMBRES.forEach((n, j) => {
        const y = 18 + j * 14;
        const visto = j < barrida;
        const mala = MALAS.has(j) && visto;
        if (mala) rojos++;
        if (mala) caja(ctx, pal.R, 6, y - 2, 104, 13);
        sprite(ctx, pal, "hoja", 8, y, mala ? { l: "r" } : null);
        texto(ctx, mala ? pal.r : visto ? pal.k : pal.g, n, 21, y + 1);
        if (visto && !mala) caja(ctx, pal.v, 104, y + 3, 3, 3);
      });
      if (t > inicio && barrida < NOMBRES.length) {
        const y = 16 + ((t - inicio) % paso) / paso * 14 + barrida * 14;
        caja(ctx, pal.i, 4, Math.floor(y), 108, 1);
      }
      // panel del veredicto
      const x0 = 122;
      borde(ctx, pal.l, x0, 14, 64, 86);
      texto(ctx, pal.g, "valor", x0 + 5, 19);
      texto(ctx, rojos ? pal.r : pal.k, String(rojos), x0 + 5, 29);
      texto(ctx, pal.g, "umbral", x0 + 5, 39);
      texto(ctx, pal.k, "<= 0", x0 + 5, 47);
      const fin = barrida >= NOMBRES.length;
      if (fin) {
        caja(ctx, pal.R, x0 + 4, 58, 56, 12);
        texto(ctx, pal.r, "ROJO", x0 + 32, 60, "center");
        texto(ctx, pal.g, "testigo", x0 + 5, 75);
        texto(ctx, pal.r, "fila 10", x0 + 5, 85);
      } else {
        texto(ctx, pal.g, "midiendo", x0 + 5, 60);
      }
    },
  };

  // 2. Un mutante debilita la medida; el corpus lo atrapa y muere.
  const mutante = {
    duracion: 8000,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.w, 0, 0, 192, 108);
      // la medida
      caja(ctx, pal.c, 8, 10, 104, 44);
      texto(ctx, pal.K, "medida", 13, 14);
      texto(ctx, pal.t, "donde c.fila > 9", 13, 24);
      texto(ctx, pal.K, "umbral", 13, 36);
      const mutado = t > 2600 && t < 6200;
      const parpadea = t > 2200 && t < 2600 && Math.floor(t / 80) % 2;
      texto(ctx, mutado || parpadea ? pal.a : pal.t, mutado ? "<= 1" : "<= 0", 62, 36);
      // el bicho camina hasta el umbral
      const llegada = fase(t, 600, 2200);
      const bx = Math.round(170 - llegada * 94), by = 42;
      const muerto = t > 5400;
      if (!muerto) sprite(ctx, pal, Math.floor(t / 180) % 2 ? "bicho" : "bichoB", bx, by);
      // el caso del corpus
      caja(ctx, pal.p, 8, 64, 176, 36);
      texto(ctx, pal.g, "caso - falso_verde", 13, 68);
      texto(ctx, pal.k, "destructor en fila 10", 13, 78);
      if (t > 3400) {
        const espera = "espera ROJO";
        texto(ctx, pal.g, espera, 13, 88);
        if (t > 4200) {
          const da = mutado ? "da VERDE" : "da ROJO";
          texto(ctx, mutado ? pal.a : pal.r, da, 100, 88);
        }
      }
      if (t > 4800 && t <= 5400) {
        sprite(ctx, pal, "chispa", bx + 1, by - 2);
        texto(ctx, pal.r, "no coincide", 120, 50);
      }
      if (muerto) {
        caja(ctx, pal.V, 120, 10, 64, 30);
        texto(ctx, pal.v, "MUTANTE", 152, 15, "center");
        texto(ctx, pal.v, "MUERTO", 152, 26, "center");
      }
    },
  };

  // 3. La sombra perdona hasta su cota; por encima, el rojo vuelve.
  const sombra = {
    duracion: 7500,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.w, 0, 0, 192, 108);
      const valor = t < 3500 ? Math.floor(fase(t, 400, 3000) * 3) : 3 + Math.floor(fase(t, 4000, 5600) * 3);
      texto(ctx, pal.g, "deuda medida", 10, 8);
      const x0 = 10, y0 = 26, paso = 26;
      for (let j = 0; j < 8; j++) borde(ctx, pal.l, x0 + j * 21, y0, 19, 24);
      for (let j = 0; j < valor; j++) caja(ctx, j < 4 ? pal.a : pal.r, x0 + j * 21 + 2, y0 + 2, 15, 20);
      const cx = x0 + 4 * 21 - 1;
      caja(ctx, pal.k, cx, y0 - 6, 1, 36);
      texto(ctx, pal.k, "cota 4", cx + 3, y0 - 8);
      if (valor <= 4) {
        caja(ctx, pal.A, 10, 64, 172, 32);
        texto(ctx, pal.a, "EN SOMBRA", 16, 69);
        texto(ctx, pal.k, `${valor} de 4: perdonada`, 16, 81);
      } else {
        caja(ctx, pal.R, 10, 64, 172, 32);
        texto(ctx, pal.r, "SUPERA SU COTA", 16, 69);
        texto(ctx, pal.k, `${valor} > 4: vuelve el rojo`, 16, 81);
      }
      void paso;
    },
  };

  // 4. El agente escribe; Oracle juzga; el agente corrige con los testigos.
  const agente = {
    duracion: 10000,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.w, 0, 0, 192, 108);
      sprite(ctx, pal, "robot", 12, 14);
      texto(ctx, pal.g, "agente", 6, 26);
      const parpadeo = Math.floor(t / 1400) % 5 === 0 && (t % 1400) < 140;
      sprite(ctx, pal, parpadeo ? "ojoCerrado" : "ojo", 166, 12);
      texto(ctx, pal.g, "oracle", 158, 26);
      const lineas = Math.min(4, Math.floor(fase(t, 500, 2600) * 4.99));
      caja(ctx, pal.c, 36, 10, 118, 50);
      for (let j = 0; j < lineas; j++) caja(ctx, j === 2 && t < 7200 ? pal.a : pal.t, 42, 16 + j * 10, 60 + ((j * 23) % 40), 3);
      if (t > 7200) caja(ctx, pal.v, 42, 36, 30, 3);
      let msg, color, fondo;
      if (t < 3000) { msg = "escribe"; color = pal.g; fondo = pal.p; }
      else if (t < 4800) { msg = "juzga..."; color = pal.i; fondo = pal.p; }
      else if (t < 6800) { msg = "ROJO: linea 3"; color = pal.r; fondo = pal.R; }
      else if (t < 8200) { msg = "corrige linea 3"; color = pal.a; fondo = pal.A; }
      else { msg = "VERDE"; color = pal.v; fondo = pal.V; }
      caja(ctx, fondo, 36, 70, 118, 20);
      texto(ctx, color, msg, 95, 76, "center");
      if (t > 3000 && t < 4800) {
        const x = 150 - fase(t, 3000, 4800) * 110;
        caja(ctx, pal.i, Math.round(x), 30, 12, 1);
      }
    },
  };

  const ESCENAS = { testigos, mutante, sombra, agente };

  // ---------------------------------------------------------------- motor
  function montar(canvas) {
    const escena = ESCENAS[canvas.dataset.escena];
    if (!escena) return;
    canvas.width = 192; canvas.height = 108;
    const ctx = canvas.getContext("2d");
    let pal = paleta(), activo = false, t0 = performance.now(), cuadro = null;
    const pintar = (t) => escena.dibujar(ctx, pal, t);
    pintar(escena.duracion - 1);  // el cuadro final: la página se entiende en reposo
    if (reducido) return;
    const bucle = (ahora) => {
      pintar((ahora - t0) % escena.duracion);
      cuadro = activo ? requestAnimationFrame(bucle) : null;
    };
    new IntersectionObserver(([e]) => {
      activo = e.isIntersecting;
      if (activo && !cuadro) { t0 = performance.now(); cuadro = requestAnimationFrame(bucle); }
    }).observe(canvas);
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { pal = paleta(); });
    new MutationObserver(() => { pal = paleta(); })
      .observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  }

  const arrancar = () => document.querySelectorAll("canvas[data-escena]").forEach(montar);
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(arrancar);
})();
