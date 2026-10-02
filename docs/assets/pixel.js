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
    tilde: [
      ".....v",
      "....vv",
      "v..vv.",
      "vvvv..",
      ".vv...",
    ],
    parcial: [
      "..aaa..",
      ".aaaaa.",
      "aaaa..a",
      "aaaa..a",
      "aaaa..a",
      ".aaaaa.",
      "..aaa..",
    ],
    cruz: [
      "r.....r",
      ".r...r.",
      "..r.r..",
      "...r...",
      "..r.r..",
      ".r...r.",
      "r.....r",
    ],
    interrogacion: [
      "..ggg..",
      ".g...g.",
      "....gg.",
      "...gg..",
      "...gg..",
      ".......",
      "...gg..",
    ],
    centinela: [
      ".....kkkkkk.....",
      "...kkwwwwwwkk...",
      "..kwwwwrrwwwwk..",
      ".kwwwrrrrrrwwwk.",
      "kwwwrrkkkrrrwwwk",
      "kwwrrkkkkkkrrwwk",
      "kwwrrkkkkkkrrwwk",
      "kwwwrrkkkrrrwwwk",
      ".kwwwrrrrrrwwwk.",
      "..kwwwwrrwwwwk..",
      "...kkwwwwwwkk...",
      ".....kkkkkk.....",
    ],
    alerta: [
      "....r....",
      "...rrr...",
      "..rrkrr..",
      "..rrkrr..",
      ".rrrrrrr.",
      ".rrrkrrr.",
      "rrrrrrrrr",
    ],
    documento: [
      "kkkkkkk..",
      "kwwwwwkk.",
      "kwiiwwwk.",
      "kwwwwwwk.",
      "kwlllllwk",
      "kwwwwwwk.",
      "kwlllllwk",
      "kwwwwwwk.",
      "kwlllllwk",
      "kwwwwwwk.",
      "kkkkkkkk.",
    ],
    flechaDer: [
      "...k...",
      "....k..",
      "kkkkkkk",
      "....k..",
      "...k...",
    ],
    lupa: [
      "..kkkk...",
      ".kwwwwk..",
      "kwwwwwwk.",
      "kwwwwwwk.",
      ".kwwwwk..",
      "..kkkkk..",
      ".....kkk.",
      "......kkk",
      ".......kk",
    ],
    embudo: [
      "kkkkkkkkk",
      ".kaaaaak.",
      "..kaaak..",
      "...kak...",
      "...kak...",
      "...kak...",
      "...kak...",
      "...kkk...",
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

  const AVANCE = 6;

  function verificarTexto(s, x, maxW = null, alineado = "left") {
    const str = String(s);
    const w = str.length * AVANCE;
    let excede = false;
    let limite = 192;
    if (maxW != null) {
      limite = maxW;
      if (w > maxW) excede = true;
    } else {
      if (alineado === "left" && x + w > 192) excede = true;
      else if (alineado === "right" && x - w < 0) excede = true;
      else if (alineado === "center" && (x - w / 2 < 0 || x + w / 2 > 192)) excede = true;
    }
    if (excede) {
      console.warn(`[pixel.js] Texto "${str}" excede su caja (${w}px > ${limite}px)`);
    }
    return w;
  }

  const caja = (ctx, color, x, y, w, h) => { ctx.fillStyle = color; ctx.fillRect(x, y, w, h); };
  function borde(ctx, color, x, y, w, h) {
    caja(ctx, color, x, y, w, 1); caja(ctx, color, x, y + h - 1, w, 1);
    caja(ctx, color, x, y, 1, h); caja(ctx, color, x + w - 1, y, 1, h);
  }
  function texto(ctx, color, s, x, y, alineado = "left", maxW = null) {
    verificarTexto(s, x, maxW, alineado);
    ctx.fillStyle = color; ctx.font = '8px "Silkscreen", monospace';
    ctx.textAlign = alineado; ctx.textBaseline = "top"; ctx.fillText(s, x, y);
  }
  const fase = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)));

  // ---------------------------------------------------------------- escenas
  // 1. La medida recorre las filas y señala las que ofenden: el veredicto trae sus testigos.
  const NOMBRES = ["acorazado 2,1", "acorazado 2,2", "destruc. 9,5", "destruc. 10,5", "fragata 4,7", "fragata 4,8"];
  const MALAS = new Set([3]);
  const testigos = {
    duracion: 9000,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.w, 0, 0, 192, 108);
      texto(ctx, pal.g, "celda_ocupada", 8, 6, "left", 104);
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
        texto(ctx, mala ? pal.r : visto ? pal.k : pal.g, n, 21, y + 1, "left", 82);
        if (visto && !mala) caja(ctx, pal.v, 104, y + 3, 3, 3);
      });
      if (t > inicio && barrida < NOMBRES.length) {
        const y = 16 + ((t - inicio) % paso) / paso * 14 + barrida * 14;
        caja(ctx, pal.i, 4, Math.floor(y), 108, 1);
      }
      // panel del veredicto
      const x0 = 122;
      borde(ctx, pal.l, x0, 14, 64, 86);
      texto(ctx, pal.g, "valor", x0 + 5, 19, "left", 54);
      texto(ctx, rojos ? pal.r : pal.k, String(rojos), x0 + 5, 29, "left", 54);
      texto(ctx, pal.g, "umbral", x0 + 5, 39, "left", 54);
      texto(ctx, pal.k, "<= 0", x0 + 5, 47, "left", 54);
      const fin = barrida >= NOMBRES.length;
      if (fin) {
        caja(ctx, pal.R, x0 + 4, 58, 56, 12);
        texto(ctx, pal.r, "ROJO", x0 + 32, 60, "center", 56);
        texto(ctx, pal.g, "testigo", x0 + 5, 75, "left", 54);
        texto(ctx, pal.r, "fila 10", x0 + 5, 85, "left", 54);
      } else {
        texto(ctx, pal.g, "midiendo", x0 + 5, 60, "left", 54);
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
      texto(ctx, pal.K, "medida", 13, 14, "left", 94);
      texto(ctx, pal.t, "donde c.fila > 9", 13, 24, "left", 98);
      texto(ctx, pal.K, "umbral", 13, 36, "left", 48);
      const mutado = t > 2600 && t < 6200;
      const parpadea = t > 2200 && t < 2600 && Math.floor(t / 80) % 2;
      texto(ctx, mutado || parpadea ? pal.a : pal.t, mutado ? "<= 1" : "<= 0", 62, 36, "left", 46);
      // el bicho camina hasta el umbral
      const llegada = fase(t, 600, 2200);
      const bx = Math.round(170 - llegada * 94), by = 42;
      const muerto = t > 5400;
      if (!muerto) sprite(ctx, pal, Math.floor(t / 180) % 2 ? "bicho" : "bichoB", bx, by);
      // el caso del corpus
      caja(ctx, pal.p, 8, 64, 176, 36);
      texto(ctx, pal.g, "caso - falso_verde", 13, 68, "left", 166);
      texto(ctx, pal.k, "destructor en fila 10", 13, 78, "left", 166);
      if (t > 3400) {
        const espera = "espera ROJO";
        texto(ctx, pal.g, espera, 13, 88, "left", 80);
        if (t > 4200) {
          const da = mutado ? "da VERDE" : "da ROJO";
          texto(ctx, mutado ? pal.a : pal.r, da, 100, 88, "left", 80);
        }
      }
      if (t > 4800 && t <= 5400) {
        sprite(ctx, pal, "chispa", bx + 1, by - 2);
        texto(ctx, pal.r, "no coincide", 120, 50, "left", 70);
      }
      if (muerto) {
        caja(ctx, pal.V, 120, 10, 64, 30);
        texto(ctx, pal.v, "MUTANTE", 152, 15, "center", 64);
        texto(ctx, pal.v, "MUERTO", 152, 26, "center", 64);
      }
    },
  };

  // 3. La sombra perdona hasta su cota; por encima, el rojo vuelve.
  const sombra = {
    duracion: 7500,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.w, 0, 0, 192, 108);
      const valor = t < 3500 ? Math.floor(fase(t, 400, 3000) * 3) : 3 + Math.floor(fase(t, 4000, 5600) * 3);
      texto(ctx, pal.g, "deuda medida", 10, 8, "left", 100);
      const x0 = 10, y0 = 26, paso = 26;
      for (let j = 0; j < 8; j++) borde(ctx, pal.l, x0 + j * 21, y0, 19, 24);
      for (let j = 0; j < valor; j++) caja(ctx, j < 4 ? pal.a : pal.r, x0 + j * 21 + 2, y0 + 2, 15, 20);
      const cx = x0 + 4 * 21 - 1;
      caja(ctx, pal.k, cx, y0 - 6, 1, 36);
      texto(ctx, pal.k, "cota 4", cx + 3, y0 - 8, "left", 48);
      if (valor <= 4) {
        caja(ctx, pal.A, 10, 64, 172, 32);
        texto(ctx, pal.a, "EN SOMBRA", 16, 69, "left", 160);
        texto(ctx, pal.k, `${valor} de 4: perdonada`, 16, 81, "left", 160);
      } else {
        caja(ctx, pal.R, 10, 64, 172, 32);
        texto(ctx, pal.r, "SUPERA SU COTA", 16, 69, "left", 160);
        texto(ctx, pal.k, `${valor} > 4: vuelve el rojo`, 16, 81, "left", 160);
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
      texto(ctx, pal.g, "agente", 6, 26, "left", 40);
      const parpadeo = Math.floor(t / 1400) % 5 === 0 && (t % 1400) < 140;
      sprite(ctx, pal, parpadeo ? "ojoCerrado" : "ojo", 166, 12);
      texto(ctx, pal.g, "oracle", 174, 26, "center", 36);
      const lineas = Math.min(4, Math.floor(fase(t, 500, 2600) * 4.99));
      caja(ctx, pal.c, 36, 10, 118, 50);
      for (let j = 0; j < lineas; j++) caja(ctx, j === 2 && t < 7200 ? pal.a : pal.t, 42, 16 + j * 10, 60 + ((j * 23) % 40), 3);
      if (t > 7200) caja(ctx, pal.v, 42, 36, 30, 3);
      let msg, color, fondo;
      if (t < 3000) { msg = "escribe"; color = pal.g; fondo = pal.p; }
      else if (t < 4800) { msg = "juzga"; color = pal.i; fondo = pal.p; }
      else if (t < 6800) { msg = "ROJO: linea 3"; color = pal.r; fondo = pal.R; }
      else if (t < 8200) { msg = "corrige linea 3"; color = pal.a; fondo = pal.A; }
      else { msg = "VERDE"; color = pal.v; fondo = pal.V; }
      caja(ctx, fondo, 36, 70, 118, 20);
      texto(ctx, color, msg, 95, 76, "center", 118);
      if (t > 3000 && t < 4800) {
        const x = 150 - fase(t, 3000, 4800) * 110;
        caja(ctx, pal.i, Math.round(x), 30, 12, 1);
      }
    },
  };

  // 5. El generador busca discrepancia con el mutante y luego encoge la evidencia hasta matarlo.
  const generador = {
    duracion: 8500,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.w, 0, 0, 192, 108);
      texto(ctx, pal.g, "caso generar", 8, 6, "left", 106);

      const buscando = t < 2600;
      const encogiendo = t >= 2600 && t < 5400;
      const fin = t >= 5400;

      // Caja de evidencia a la izquierda
      const x0 = 8, y0 = 17, w0 = 106, h0 = 82;
      borde(ctx, pal.l, x0, y0, w0, h0);

      if (buscando) {
        caja(ctx, pal.p, x0 + 1, y0 + 1, w0 - 2, 14);
        sprite(ctx, pal, "lupa", x0 + 4, y0 + 3);
        texto(ctx, pal.i, "BUSCA CASO", x0 + 16, y0 + 4, "left", 84);
        const paso = Math.floor(t / 650);
        const candidatos = [
          ["fila 2", "igual"],
          ["fila 4", "igual"],
          ["fila 7", "igual"],
          ["fila 10", "DISCREPA"],
        ];
        const idx = Math.min(candidatos.length - 1, paso);
        for (let i = 0; i <= idx; i++) {
          const y = y0 + 19 + i * 14;
          const esUltimo = i === 3;
          if (esUltimo) caja(ctx, pal.V, x0 + 3, y - 1, w0 - 6, 12);
          texto(ctx, esUltimo ? pal.v : pal.k, candidatos[i][0], x0 + 5, y, "left", 48);
          texto(ctx, esUltimo ? pal.v : pal.g, candidatos[i][1], x0 + w0 - 6, y, "right", 54);
        }
      } else if (encogiendo) {
        caja(ctx, pal.A, x0 + 1, y0 + 1, w0 - 2, 14);
        sprite(ctx, pal, "embudo", x0 + 4, y0 + 3);
        texto(ctx, pal.a, "ENCOGE PODA", x0 + 16, y0 + 4, "left", 84);
        const pasoPoda = Math.floor((t - 2600) / 700);
        const filas = [
          { texto: "fila 2,1", tachar: pasoPoda >= 1 },
          { texto: "fila 4,7", tachar: pasoPoda >= 2 },
          { texto: "fila 6,3", tachar: pasoPoda >= 3 },
          { texto: "fila 10,5", tachar: false },
        ];
        filas.forEach((f, i) => {
          const y = y0 + 19 + i * 14;
          if (f.tachar) {
            caja(ctx, pal.R, x0 + 3, y - 1, w0 - 6, 12);
            texto(ctx, pal.r, f.texto, x0 + 5, y, "left", 50);
            caja(ctx, pal.r, x0 + 5, y + 4, 48, 1);
            texto(ctx, pal.r, "PODA", x0 + w0 - 6, y, "right", 30);
          } else {
            const queda = i === 3 && pasoPoda >= 3;
            if (queda) caja(ctx, pal.V, x0 + 3, y - 1, w0 - 6, 12);
            texto(ctx, queda ? pal.v : pal.k, f.texto, x0 + 5, y, "left", 54);
            if (queda) texto(ctx, pal.v, "QUEDA", x0 + w0 - 6, y, "right", 36);
          }
        });
      } else {
        // Cuadro final: caso mínimo irreducible
        caja(ctx, pal.V, x0 + 1, y0 + 1, w0 - 2, 14);
        texto(ctx, pal.v, "CASO MINIMO", x0 + 6, y0 + 4, "left", 92);

        caja(ctx, pal.c, x0 + 5, y0 + 19, w0 - 10, 36);
        texto(ctx, pal.K, "caso generado:", x0 + 8, y0 + 22, "left", 86);
        texto(ctx, pal.t, "destructor", x0 + 8, y0 + 32, "left", 86);
        texto(ctx, pal.t, "fila 10, col 5", x0 + 8, y0 + 42, "left", 86);

        caja(ctx, pal.p, x0 + 5, y0 + 58, w0 - 10, 19);
        texto(ctx, pal.g, "caso generado", x0 + 8, y0 + 60, "left", 86);
        texto(ctx, pal.v, "mata mutante", x0 + 8, y0 + 68, "left", 86);
      }

      // Panel derecho: el mutante
      const x1 = 120, y1 = 17, w1 = 64, h1 = 82;
      borde(ctx, pal.l, x1, y1, w1, h1);
      texto(ctx, pal.g, "mutante", x1 + 5, y1 + 5, "left", 54);
      texto(ctx, pal.k, "umbral 1", x1 + 5, y1 + 15, "left", 54);

      if (buscando) {
        sprite(ctx, pal, Math.floor(t / 180) % 2 ? "bicho" : "bichoB", x1 + 24, y1 + 30);
        caja(ctx, pal.A, x1 + 8, y1 + 48, w1 - 16, 12);
        texto(ctx, pal.a, "VIVO", x1 + 32, y1 + 50, "center", 48);
        texto(ctx, pal.g, "sin caso", x1 + 32, y1 + 64, "center", 48);
        texto(ctx, pal.g, "que mate", x1 + 32, y1 + 72, "center", 48);
      } else if (encogiendo) {
        sprite(ctx, pal, "bicho", x1 + 24, y1 + 28);
        sprite(ctx, pal, "chispa", x1 + 24, y1 + 22);
        caja(ctx, pal.R, x1 + 6, y1 + 44, w1 - 12, 13);
        texto(ctx, pal.r, "HALLADO", x1 + 32, y1 + 46, "center", 52);
        texto(ctx, pal.g, "podando", x1 + 32, y1 + 60, "center", 52);
        texto(ctx, pal.g, "sobrante", x1 + 32, y1 + 70, "center", 52);
      } else {
        sprite(ctx, pal, "chispa", x1 + 24, y1 + 26);
        caja(ctx, pal.V, x1 + 6, y1 + 34, w1 - 12, 22);
        texto(ctx, pal.v, "MUTANTE", x1 + 32, y1 + 37, "center", 52);
        texto(ctx, pal.v, "MUERTO", x1 + 32, y1 + 46, "center", 52);
        texto(ctx, pal.g, "muere con", x1 + 32, y1 + 62, "center", 60);
        texto(ctx, pal.v, "caso nuevo", x1 + 32, y1 + 71, "center", 60);
      }
    },
  };

  // 6. oracle cambios vigila catálogo, escalares y sensores: detecta cuando alguien afloja.
  const cambios = {
    duracion: 8500,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.w, 0, 0, 192, 108);
      texto(ctx, pal.g, "oracle cambios", 8, 6, "left", 106);

      const aflojando = t > 2000 && t < 4500;
      const atrapado = t >= 4500;

      // Código de la medida (izquierda arriba)
      caja(ctx, pal.c, 8, 17, 106, 44);
      texto(ctx, pal.K, "medida", 13, 21, "left", 40);
      texto(ctx, pal.t, "tablero", 56, 21, "left", 50);
      texto(ctx, pal.t, "donde c.fila > 9", 13, 31, "left", 98);
      texto(ctx, pal.K, "umbral", 13, 42, "left", 42);

      if (aflojando) {
        const parpadea = Math.floor(t / 90) % 2;
        texto(ctx, parpadea ? pal.a : pal.t, "<= 3", 58, 42, "left", 26);
        caja(ctx, pal.A, 86, 41, 22, 11);
        texto(ctx, pal.a, "ojo", 97, 42, "center", 22);
      } else if (atrapado) {
        caja(ctx, pal.R, 56, 40, 52, 13);
        texto(ctx, pal.r, "<= 3 MAL", 82, 42, "center", 50);
      } else {
        texto(ctx, pal.t, "<= 0", 58, 42, "left", 48);
      }

      // Sensores declarados (izquierda abajo)
      caja(ctx, pal.p, 8, 65, 106, 34);
      texto(ctx, pal.g, "sensor vigilado", 13, 69, "left", 98);
      texto(ctx, pal.k, "radar.py", 13, 79, "left", 98);
      if (atrapado) {
        caja(ctx, pal.R, 11, 88, 98, 10);
        texto(ctx, pal.r, "TOCADO EN RAMA", 13, 89, "left", 96);
      } else {
        texto(ctx, pal.g, "sin cambios", 13, 89, "left", 96);
      }

      // Panel de vigilancia a la derecha
      const x1 = 120, y1 = 17, w1 = 64, h1 = 82;
      borde(ctx, pal.l, x1, y1, w1, h1);

      // Centinela
      sprite(ctx, pal, "centinela", x1 + 24, y1 + 6);

      if (!atrapado) {
        const lx = Math.round(fase(t, 600, 2000) * 8);
        caja(ctx, pal.i, x1 + 4, y1 + 11, 16 - lx, 1);
        caja(ctx, pal.p, x1 + 4, y1 + 42, w1 - 8, 34);
        texto(ctx, pal.g, "vigila", x1 + 32, y1 + 48, "center", 56);
        texto(ctx, pal.i, "cambios", x1 + 32, y1 + 59, "center", 56);
      } else {
        // Alarma roja de atrapado
        caja(ctx, pal.R, x1 + 4, y1 + 36, w1 - 8, 41);
        borde(ctx, pal.r, x1 + 4, y1 + 36, w1 - 8, 41);
        sprite(ctx, pal, "alerta", x1 + 28, y1 + 40);
        texto(ctx, pal.r, "ATRAPADO", x1 + 32, y1 + 51, "center", 56);
        texto(ctx, pal.r, "error:", x1 + 32, y1 + 60, "center", 56);
        texto(ctx, pal.k, "aflojada", x1 + 32, y1 + 68, "center", 56);
      }
    },
  };

  // 7. oracle cobertura con veredicto: promesas evaluadas (✓, ◐, ✗, ?).
  const requisitos = {
    duracion: 8500,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.w, 0, 0, 192, 108);
      texto(ctx, pal.g, "oracle cobertura", 8, 6, "left", 108);

      const items = [
        { nombre: "auth.token", sim: "tilde", col: pal.v, fondo: pal.V, sub: "1 de 1 verde" },
        { nombre: "flota.tablero", sim: "parcial", col: pal.a, fondo: pal.A, sub: "sin_medir" },
        { nombre: "pago.monto", sim: "cruz", col: pal.r, fondo: pal.R, sub: "falla: fila 8" },
        { nombre: "sesion.limpia", sim: "interrogacion", col: pal.g, fondo: pal.p, sub: "sin evidencia" },
      ];

      const paso = 1100, inicio = 400;
      const revelados = Math.min(items.length, Math.floor((t - inicio) / paso));

      // Lista de requisitos a la izquierda
      items.forEach((item, j) => {
        const y = 17 + j * 21;
        const visto = j <= revelados;
        borde(ctx, pal.l, 8, y, 108, 19);
        if (visto) {
          caja(ctx, item.fondo, 9, y + 1, 106, 17);
          sprite(ctx, pal, item.sim, 12, y + 6);
          texto(ctx, pal.k, item.nombre, 24, y + 3, "left", 88);
          texto(ctx, item.col, item.sub, 24, y + 11, "left", 88);
        } else {
          texto(ctx, pal.g, item.nombre, 24, y + 6, "left", 88);
          texto(ctx, pal.g, "-", 14, y + 6, "left", 10);
        }
      });

      // Panel de resumen a la derecha
      const x1 = 120, y1 = 17, w1 = 66, h1 = 82;
      borde(ctx, pal.l, x1, y1, w1, h1);
      texto(ctx, pal.g, "veredicto", x1 + 5, y1 + 5, "left", 56);

      const yIconos = y1 + 17;
      sprite(ctx, pal, "tilde", x1 + 6, yIconos);
      texto(ctx, pal.k, "cumple", x1 + 17, yIconos, "left", 46);

      sprite(ctx, pal, "parcial", x1 + 6, yIconos + 11);
      texto(ctx, pal.k, "parcial", x1 + 17, yIconos + 11, "left", 46);

      sprite(ctx, pal, "cruz", x1 + 6, yIconos + 22);
      texto(ctx, pal.k, "falla", x1 + 17, yIconos + 22, "left", 46);

      sprite(ctx, pal, "interrogacion", x1 + 6, yIconos + 33);
      texto(ctx, pal.k, "sin dato", x1 + 17, yIconos + 33, "left", 48);

      const fin = revelados >= items.length - 1;
      if (fin) {
        caja(ctx, pal.R, x1 + 4, y1 + 62, w1 - 8, 16);
        texto(ctx, pal.r, "SALIDA 1", x1 + 29, y1 + 64, "center", 58);
        texto(ctx, pal.k, "1 en rojo", x1 + 29, y1 + 72, "center", 58);
      } else {
        texto(ctx, pal.g, "juzgando", x1 + 29, y1 + 67, "center", 58);
      }
    },
  };

  // 8. OpenSpec: una spec entra como Markdown y sale como requisitos sin medir; luego se enlaza la medida.
  const openspec = {
    duracion: 8000,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.w, 0, 0, 192, 108);
      texto(ctx, pal.g, "oracle requisito importar", 8, 6, "left", 180);

      const paso2 = t >= 4000;

      // Lado izquierdo: spec.md de OpenSpec
      const x0 = 6, y0 = 17, w0 = 82, h0 = 74;
      borde(ctx, pal.l, x0, y0, w0, h0);
      caja(ctx, pal.p, x0 + 1, y0 + 1, w0 - 2, 12);
      sprite(ctx, pal, "documento", x0 + 4, y0 + 2);
      texto(ctx, pal.k, "spec.md", x0 + 16, y0 + 3, "left", 60);

      texto(ctx, pal.i, "### Req:", x0 + 4, y0 + 16, "left", 72);
      texto(ctx, pal.k, "auth.expira", x0 + 4, y0 + 26, "left", 72);
      texto(ctx, pal.g, "SHALL exp.", x0 + 4, y0 + 37, "left", 72);
      texto(ctx, pal.i, "### Escen.:", x0 + 4, y0 + 49, "left", 72);
      texto(ctx, pal.g, "WHEN expira", x0 + 4, y0 + 59, "left", 72);

      // Centro: flecha de flujo
      const avance = (t % 1500) / 1500;
      sprite(ctx, pal, "flechaDer", 91, 48);
      caja(ctx, pal.i, 89 + Math.floor(avance * 12), 50, 2, 1);

      // Lado derecho: requisito de Oracle
      const x1 = 104, y1 = 17, w1 = 82, h1 = 74;
      borde(ctx, pal.l, x1, y1, w1, h1);
      caja(ctx, pal.c, x1 + 1, y1 + 1, w1 - 2, h1 - 2);

      texto(ctx, pal.K, "req auth:", x1 + 4, y1 + 4, "left", 72);
      texto(ctx, pal.t, "texto SHALL", x1 + 6, y1 + 14, "left", 70);
      texto(ctx, pal.t, "fuente spec", x1 + 6, y1 + 23, "left", 70);

      if (!paso2) {
        // Tiempo 1: el importador crea el requisito con SIN_MEDIR (sin medido_por)
        texto(ctx, pal.K, "sin_medir", x1 + 6, y1 + 35, "left", 70);
        caja(ctx, pal.A, x1 + 5, y1 + 45, w1 - 10, 23);
        texto(ctx, pal.a, "\"sin medida", x1 + 8, y1 + 48, "left", 68);
        texto(ctx, pal.a, " todavia\"", x1 + 8, y1 + 57, "left", 68);
      } else {
        // Tiempo 2: la persona enlaza la medida con oracle medida nueva
        texto(ctx, pal.K, "medido_por", x1 + 6, y1 + 33, "left", 70);
        caja(ctx, pal.V, x1 + 5, y1 + 42, w1 - 10, 11);
        texto(ctx, pal.v, "auth.expira", x1 + 8, y1 + 44, "left", 68);
        texto(ctx, pal.K, "sin_medir", x1 + 6, y1 + 55, "left", 70);
        texto(ctx, pal.v, "cubierto", x1 + 8, y1 + 64, "left", 68);
      }

      // Pie informativo que cambia con el tiempo
      if (!paso2) {
        caja(ctx, pal.A, 6, 94, 180, 11);
        texto(ctx, pal.a, "1. importar: nace SIN MEDIR", 96, 96, "center", 180);
      } else {
        caja(ctx, pal.V, 6, 94, 180, 11);
        texto(ctx, pal.v, "2. medida nueva: ya enlazada", 96, 96, "center", 180);
      }
    },
  };

  const ESCENAS = { testigos, mutante, generador, sombra, cambios, requisitos, openspec, agente };

  // ---------------------------------------------------------------- motor
  function montar(canvas) {
    const escena = ESCENAS[canvas.dataset.escena];
    if (!escena) return;
    canvas.width = 192; canvas.height = 108;
    const ctx = canvas.getContext("2d");
    let pal = paleta(), activo = false, t0 = performance.now(), cuadro = null;
    const pintar = (t) => escena.dibujar(ctx, pal, t);
    pintar(escena.duracion - 1);  // el cuadro final: la página se entiende en reposo
    const repintar = () => { pal = paleta(); pintar(escena.duracion - 1); };
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", repintar);
    new MutationObserver(repintar)
      .observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    if (reducido) return;
    const bucle = (ahora) => {
      pintar((ahora - t0) % escena.duracion);
      cuadro = activo ? requestAnimationFrame(bucle) : null;
    };
    new IntersectionObserver(([e]) => {
      activo = e.isIntersecting;
      if (activo && !cuadro) { t0 = performance.now(); cuadro = requestAnimationFrame(bucle); }
    }).observe(canvas);
  }

  const arrancar = () => document.querySelectorAll("canvas[data-escena]").forEach(montar);
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(arrancar);
})();
