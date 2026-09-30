// Oracle — pixel art en todas las páginas generadas de documentación.
// Provee:
//   1. Escenas animadas en la cabecera por sección (Empezar, Entender, Herramientas, Referencia, Decisiones).
//   2. Sprites individuales de 14x14 dibujados a mano en el título <h1> de cada página.
//   3. Divisores pixelados con olas marinas y motivo náutico.
//   4. Pie de página decorativo con escena marina completa (barco y faro).
// Sigue la paleta de tokens CSS de sitio.css y responde a temas claro y oscuro.
// Respeta `prefers-reduced-motion` mostrando sólo el fotograma estático/final.
// Sin dependencias externas ni CDN.
(() => {
  "use strict";

  const reducido = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------------------------------------------------------------- paleta (tokens CSS de sitio.css)
  function paleta() {
    const s = getComputedStyle(document.documentElement);
    const v = (n) => s.getPropertyValue(n).trim();
    return {
      ".": null,
      k: v("--tinta"),
      w: v("--papel"),
      p: v("--papel-2"),
      l: v("--linea"),
      g: v("--gris"),
      i: v("--acento"),
      b: v("--acento-suave"),
      r: v("--rojo"),
      R: v("--rojo-suave"),
      v: v("--verde"),
      V: v("--verde-suave"),
      a: v("--ambar"),
      A: v("--ambar-suave"),
      c: v("--codigo-fondo"),
      t: v("--codigo-tinta"),
      K: v("--codigo-clave"),
    };
  }

  // ---------------------------------------------------------------- sprites manuales
  const SPRITES = {
    // Sprites de 14x14 para los títulos <h1> de cada página:
    timon: [
      "....k....k....",
      "....k....k....",
      "..kkkkaaakkk..",
      "...kaakkkaak..",
      ".kkakkk..kkakk",
      "..kakk....kakk",
      "kaaak.ii.kaaak",
      "kaaak.ii.kaaak",
      "..kakk....kakk",
      ".kkakkk..kkakk",
      "...kaakkkaak..",
      "..kkkkaaakkk..",
      "....k....k....",
      "....k....k....",
    ],
    mapa: [
      ".kkkkkkkkkkkk.",
      "kwwwwwwwwwwpkk",
      "kw.a.a....wwpk",
      "kwa.a.....rwpk",
      "kw...a....rwpk",
      "kw....a...rrpk",
      "kw...r.a..rrpk",
      "kw..rrr.a.wwpk",
      "kw...r...a.wpk",
      "kw.......aawpk",
      "kw........awpk",
      "kppppppppppwwk",
      ".kkkkkkkkkkkk.",
      "..............",
    ],
    bandera_roja: [
      "..kr..........",
      "..krrrr.......",
      "..krrrrrrr....",
      "..krrrrrrrrr..",
      "..krrrrrrrrrr.",
      "..krrrrrrrrr..",
      "..krrrrrrr....",
      "..krrrr.......",
      "..kr..........",
      "..k...........",
      "..k...........",
      "..k...........",
      ".kkk..........",
      "kkkkk.........",
    ],
    pluma: [
      "..........iiii",
      ".........iiiii",
      "........iiiiki",
      ".......iiiikii",
      "......iiiiikii",
      ".....iiiikiiii",
      "....iiiikiiiii",
      "...iiikiiiiii.",
      "..iiikiiii....",
      ".iiikii.......",
      ".iik..........",
      ".ik...........",
      ".k............",
      "k.............",
    ],
    tacometro: [
      "....kkkkkk....",
      "..kkwwwwwwkk..",
      ".kwwwwwwvwwwk.",
      "kwwwwwwvvwwwwk",
      "kwwwwwvvwwwwwk",
      "kwwwwvvwwwwwwk",
      "kwwwwiiwwwwwwk",
      "kwwwwiiwwwwwwk",
      "kwwwwwwwwwwwwk",
      ".kwwwwwwwwwwk.",
      "..kkaa..aakk..",
      "....kkkkkk....",
      "..............",
      "..............",
    ],
    engranajes: [
      "...kk....kk...",
      "..kiiik.kiiik.",
      ".kkiiik.kiiikk",
      ".kiiiii.iiiiik",
      "..kiiii.iiiik.",
      "kkkiikiikiikkk",
      "kkkiiikiikikkk",
      "..kiiii.iiiik.",
      ".kiiiii.iiiiik",
      ".kkiiik.kiiikk",
      "..kiiik.kiiik.",
      "...kk....kk...",
      "..............",
      "..............",
    ],
    mutante_cazado: [
      ".r....vv....r.",
      "..r..vvvv..r..",
      "...rvkvvkvvr..",
      "...vvvvvvvv...",
      ".r.v.vvvv.v.r.",
      "..r..v..v..r..",
      ".r....vv....r.",
      "...r..rr..r...",
      "....rrrrrr....",
      "....rrrrrr....",
      "...r..rr..r...",
      "..r........r..",
      ".r..........r.",
      "..............",
    ],
    conector: [
      "..kk......kk..",
      "..kik....kik..",
      "..kiik..kiik..",
      "..kiiikkkiiik.",
      "..kiiiiiiiiik.",
      "..kiiivvviik..",
      "..kiiivvviik..",
      "..kiiivvviik..",
      "..kiiiiiiiiik.",
      "..kiiikkkiiik.",
      "..kiik..kiik..",
      "..kik....kik..",
      "..kk......kk..",
      "..............",
    ],
    martillo: [
      ".......kkkkkk.",
      "......kggggggk",
      ".....kgggggggk",
      "....kggggggggk",
      ".....kggggggk.",
      "......kkkakkk.",
      ".......kaak...",
      "......kaak....",
      ".....kaak.....",
      "....kaak......",
      "...kaak.......",
      "..kaak........",
      ".kaak.........",
      ".kk...........",
    ],
    matraz: [
      ".....kkkk.....",
      ".....kwwk.....",
      ".....kwwk.....",
      "....kkwwkk....",
      "...kwwwwwwk...",
      "..kwwwwwwwwk..",
      ".kwwwaawwwwwk.",
      "kwwwaaaaawwwwk",
      "kwwaaaaaaawwwk",
      "kwaaavaaaaawkk",
      "kwaavvvvaaawkk",
      "kwaaavaaaaawk.",
      ".kkkkkkkkkkk..",
      "..............",
    ],
    sensor_ojo: [
      "....kkkkkk....",
      "...kki..iikk..",
      "..kkiikkiikk..",
      ".kkiikkkkiikk.",
      "kkiikkkkkkiikk",
      "kiiwwkkkkwwiik",
      "kiiwwkkkkwwiik",
      "kkiikkkkkkiikk",
      ".kkiikkkkiikk.",
      "..kkiikkiikk..",
      "...kki..iikk..",
      "....kkkkkk....",
      ".....kiiik....",
      "....kkiiii....",
    ],
    llave_tuerca: [
      "......kkkkk...",
      ".....kiiiiik..",
      "....kiikkkiik.",
      "....kiik.kiik.",
      ".....kiikkii..",
      "......kiiik...",
      ".....kiikii...",
      "....kiik.ii...",
      "...kiik.......",
      "..kiik........",
      ".kiik.........",
      ".kkk..........",
      "..............",
      "..............",
    ],
    servidor_antena: [
      "......kk......",
      "....k.ii.k....",
      "...k..ii..k...",
      "..k...ii...k..",
      "......ii......",
      "...kkkkkkkk...",
      "...kppppppk...",
      "...kpipipik...",
      "...kppppppk...",
      "...kkkkkkkk...",
      "...kppppppk...",
      "...kpipipik...",
      "...kppppppk...",
      "...kkkkkkkk...",
    ],
    chip_memoria: [
      ".k.k.k..k.k.k.",
      "kkkkkkkkkkkkkk",
      "kcccccccccccck",
      "kc.K.K..K.K.ck",
      "kckkkkkkkkkkck",
      "kckt.t..t.tkck",
      "kckkkkkkkkkkck",
      "kckt.t..t.tkck",
      "kckkkkkkkkkkck",
      "kc.K.K..K.K.ck",
      "kcccccccccccck",
      "kkkkkkkkkkkkkk",
      ".k.k.k..k.k.k.",
      "..............",
    ],
    boya_campana: [
      "......kk......",
      ".....kwwk.....",
      "....kwwwwk....",
      "....kkkkkk....",
      "......kk......",
      "...kkkaakkk...",
      "..kaaaaaaaak..",
      ".kaaaaaaaaaak.",
      ".krrrrrrrrrrk.",
      "..krrrrrrrrk..",
      "...kkkkkkkk...",
      "....kbbbbk....",
      "...kbbbbbbk...",
      "..kbbbbbbbbk..",
    ],
    pergamino_sello: [
      ".kkkkkkkkkk...",
      "kwwwwwwwwwwk..",
      "kwllllllllwk..",
      "kwllllllllwk..",
      "kwllllllllwk..",
      "kwllllllllwk..",
      "kwllll..llwk..",
      "kwlll.rr.lwk..",
      "kwlllrrrrrwk..",
      "kwlllrrrrrwk..",
      "kwlll.rr.lwk..",
      "kwwwwwwwwwwk..",
      ".kkkkkkkkkkk..",
      "..............",
    ],
    encrucijada: [
      "......kk......",
      "..kkkkkkk.....",
      "..kiiiiiik....",
      "..kkkkkkk.....",
      "......kk......",
      ".....kkkkkkk..",
      "....kiiiiiik..",
      ".....kkkkkkk..",
      "......kk......",
      "......kk......",
      "......kk......",
      "......kk......",
      "....kkkkkk....",
      "...kppppppk...",
    ],
    faro_destello: [
      "a.....kk.....a",
      ".a...kwwk...a.",
      "..a.kaaaak.a..",
      "...kaaaaaak...",
      "....kkkkkk....",
      "....krrrrk....",
      "....kwwwwk....",
      "....krrrrk....",
      "....kwwwwk....",
      "...krrrrrrk...",
      "...kwwwwwwk...",
      "..krrrrrrrrk..",
      "..kwwwwwwwwk..",
      ".kkkkkkkkkkkk.",
    ],
    ancla_antigua: [
      ".....kkkk.....",
      "....kwwwwk....",
      "....kwwwwk....",
      ".....kkkk.....",
      "......kk......",
      "...kkkkkkkk...",
      "......kk......",
      "......kk......",
      "k.....kk.....k",
      "kk....kk....kk",
      ".kk...kk...kk.",
      "..kkk.kk.kkk..",
      "...kkkkkkkk...",
      ".....kkkk.....",
    ],
    brujula: [
      "....kkkkkk....",
      "..kkwwwwwwkk..",
      ".kwwwwrwwwwwk.",
      "kwwwwrrrwwwwwk",
      "kwwwwrrrwwwwwk",
      "kwwwrriiiwwwwk",
      "kwwrrriiiiwwwk",
      "kwwwiiiwwiwwwk",
      "kwwwwwiiwwwwwk",
      "kwwwwwiiwwwwwk",
      ".kwwwwwiwwwwk.",
      "..kkwwwwwwkk..",
      "....kkkkkk....",
      "..............",
    ],

    // Sprites auxiliares para escenas y pie:
    barco_bandera_roja: [
      ".........krrrrrr......",
      ".........krrrrrr......",
      ".........krrrr........",
      ".........k............",
      ".......wwk............",
      "......wwwk.wwww.......",
      ".....wwwwk.wwwww......",
      "....wwwwwk.wwwwww.....",
      "...wwwwwwk.wwwwwww....",
      "..wwwwwwwk.wwwwwwww...",
      ".wwwwwwwwk.wwwwwwwww..",
      "wwwwwwwwwk.wwwwwwwwww.",
      "....l....k....l.......",
      ".........k............",
      "kkkkkkkkkkkkkkkkkkkkkk",
      ".kaaaaaaaaaaaaaaaaaak.",
      "..kaaaaaaaaaaaaaaaak..",
      "...kaaaaaaaaaaaaaak...",
      "....kkkkkkkkkkkkkk....",
    ],
    bicho_mutante: [
      "...k....k...",
      "....k..k....",
      "...kvvvvk...",
      "..kvvwwvvk..",
      "..kvvkkvvk..",
      "..kvvvvvvk..",
      ".kkk.vv.kkk.",
      "k.k.kvvk.k.k",
      "...k....k...",
      "..k......k..",
    ],
    bicho_mutante_muerto: [
      "..k......k..",
      "...k....k...",
      "k.k.krrk.k.k",
      ".kkk.rr.kkk.",
      "..kggggggk..",
      "..kggwwggk..",
      "..kggkkggk..",
      "...kggggk...",
      "....k..k....",
      "...k....k...",
    ],
    faro_vigilante: [
      ".....kkkk.....",
      "....kwwwwk....",
      "....kaaaak....",
      ".....kkkk.....",
      "....kkkkkk....",
      "....krrrrk....",
      "....krrrrk....",
      "....kwwwwk....",
      "....kwwwwk....",
      "....krrrrk....",
      "....krrrrk....",
      "....kwwwwk....",
      "....kwwwwk....",
      "...krrrrrrk...",
      "...krrrrrrk...",
      "...kwwwwwwk...",
      "...kwwwwwwk...",
      "...krrrrrrk...",
      "...krrrrrrk...",
      "..kwwwwwwwwk..",
      "..kwwwwwwwwk..",
      "..krrrrrrrrk..",
      "..krrrrrrrrk..",
      ".kkkkkkkkkkkk.",
      ".kggggggggggk.",
      ".kggggggggggk.",
      "kkkkkkkkkkkkkk",
      "kkkkkkkkkkkkkk",
    ],
    boya_vigilante: [
      ".....rr.....",
      ".....rr.....",
      "....k..k....",
      "....k..k....",
      "...kaaaak...",
      "...kaaaak...",
      "..k......k..",
      ".kkkkkkkkkk.",
      ".krrrrrrrrk.",
      ".krrrrrrrrk.",
      ".kwwwwwwwwk.",
      ".kwwwwwwwwk.",
      ".krrrrrrrrk.",
      "..kaaaaaak..",
      "...kkkkkk...",
      "....kbbk....",
      "....kbbk....",
      "....kkkk....",
    ],
    cartografo_figura: [
      "......kkkk..........",
      ".....kiiikk.........",
      ".....kAAAAk.........",
      ".....kAAAAk.........",
      ".....kkkkkk.........",
      "....kkiwwiikk.......",
      "...kiiiwwiiiikk.....",
      "..kiiiiwwiiiiiik....",
      ".kiiiiaaaaiiiiiik...",
      ".kiiiiaaaaiiiiiik...",
      "..kiiiaaaaiiiiik....",
      "...kkiwwiikkkk......",
      "....kkAAkk.kaak.....",
      "....kAAAAk..kaak....",
      "....kk..kk...kaak...",
      "..............kaak..",
      "...............kak..",
      "................kk..",
      "....................",
      "....................",
    ],
    sello_lacre: [
      "....kkrrrrkk....",
      "..kkrrrrrrrrkk..",
      ".krrrrrrrrrrrrk.",
      ".krrrrRRRRrrrrk.",
      "krrrrRrrrrRrrrrk",
      "krrrrRrrrrRrrrrk",
      "krrrrRrrrrRrrrrk",
      "krrrrRRRRrrrrrrk",
      ".krrrrrrrrrrrrk.",
      "..kkrrrrrrrrkk..",
      "....kkrrrrkk....",
      ".....kr..rk.....",
      ".....kr..rk.....",
      ".....kr..rk.....",
      "....kkr..rkk....",
      "................",
    ],
    barco_chico: [
      "....k.......",
      "....kr......",
      "....krr.....",
      "....k.......",
      "kkkkkkkkkkkk",
      ".kaaaaaaaak.",
      "..kaaaaaak..",
      "...kkkkkk...",
    ],
    faro_chico: [
      "...kkkk...",
      "..kwwwwk..",
      "..kaaaak..",
      "...kkkk...",
      "...krrk...",
      "...kwwk...",
      "...krrk...",
      "...kwwk...",
      "..krrrrk..",
      "..kwwwwk..",
      "..krrrrk..",
      "..kwwwwk..",
      ".krrrrrrk.",
      ".kwwwwwwk.",
      ".krrrrrrk.",
      "kkkkkkkkkk",
      "kggggggggk",
      "kkkkkkkkkk",
    ],
    boya_chica: [
      "..kk..",
      ".kwwk.",
      "..kk..",
      ".kaak.",
      "kaaaak",
      "krrrrk",
      ".kkkk.",
      "..kk..",
    ],
    bicho_chico: [
      ".k....k.",
      "..k..k..",
      ".kvvvvk.",
      "kvvwwvvk",
      "kvvkkvvk",
      ".kvvvvk.",
      "k.k..k.k",
    ],
    bicho_muerto: [
      "k.k..k.k",
      ".kggggk.",
      "kggkkggk",
      "kggwwggk",
      ".kggggk.",
      "..k..k..",
      ".k....k.",
    ],
    robot_chico: [
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

  // ---------------------------------------------------------------- utilidades de dibujo
  function dibujarSprite(ctx, pal, nombre, x, y, sustituir = null) {
    const filas = SPRITES[nombre];
    if (!filas) return;
    for (let j = 0; j < filas.length; j++) {
      for (let k = 0; k < filas[j].length; k++) {
        let ch = filas[j][k];
        if (sustituir && ch in sustituir) ch = sustituir[ch];
        const color = pal[ch];
        if (color) {
          ctx.fillStyle = color;
          ctx.fillRect(Math.floor(x + k), Math.floor(y + j), 1, 1);
        }
      }
    }
  }

  const caja = (ctx, color, x, y, w, h) => {
    if (!color) return;
    ctx.fillStyle = color;
    ctx.fillRect(Math.floor(x), Math.floor(y), Math.floor(w), Math.floor(h));
  };

  function borde(ctx, color, x, y, w, h) {
    caja(ctx, color, x, y, w, 1);
    caja(ctx, color, x, y + h - 1, w, 1);
    caja(ctx, color, x, y, 1, h);
    caja(ctx, color, x + w - 1, y, 1, h);
  }

  function texto(ctx, color, s, x, y, alineado = "left") {
    ctx.fillStyle = color;
    ctx.font = '8px "Silkscreen", monospace';
    ctx.textAlign = alineado;
    ctx.textBaseline = "top";
    ctx.fillText(s, Math.floor(x), Math.floor(y));
  }

  const fase = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)));

  // ---------------------------------------------------------------- escenas de cabecera de sección (320 x 64)
  // 1. Empezar: Un barco saliendo del puerto con una bandera roja (el primer rojo).
  const escenaEmpezar = {
    ancho: 320, alto: 64, duracion: 8000,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.p, 0, 0, 320, 42);
      borde(ctx, pal.l, 0, 0, 320, 64);

      // Nubes distantes en el cielo
      caja(ctx, pal.w, 130, 8, 26, 4);
      caja(ctx, pal.w, 134, 6, 18, 2);
      caja(ctx, pal.w, 235, 12, 32, 4);
      caja(ctx, pal.w, 241, 10, 20, 2);

      // Gaviota sobrevolando el puerto
      caja(ctx, pal.k, 82, 14, 1, 1);
      caja(ctx, pal.w, 83, 13, 2, 1);
      caja(ctx, pal.k, 85, 14, 1, 1);

      // Agua del mar (capas y oleaje rítmico)
      caja(ctx, pal.b, 64, 42, 256, 22);
      caja(ctx, pal.i, 64, 52, 256, 12);
      for (let x = 64; x < 320; x += 14) {
        const off = (Math.floor(t / 200) + Math.floor(x / 14) * 3) % 7;
        caja(ctx, pal.w, x + off, 43, 3, 1);
        caja(ctx, pal.l, x + ((off + 4) % 7), 47, 4, 1);
        caja(ctx, pal.w, x + off, 53, 3, 1);
      }

      // Muelle de piedra del puerto a la izquierda (x: 0 a 74)
      caja(ctx, pal.g, 0, 36, 74, 28);
      caja(ctx, pal.k, 0, 36, 74, 2);
      for (let y = 40; y < 64; y += 4) {
        caja(ctx, pal.l, 0, y, 74, 1);
      }
      for (let x = 8; x < 74; x += 12) {
        caja(ctx, pal.k, x, 36, 1, 28);
      }
      // Pilotes de madera en el agua al borde del muelle
      caja(ctx, pal.a, 70, 38, 4, 26);
      caja(ctx, pal.k, 70, 38, 1, 26);
      caja(ctx, pal.k, 74, 38, 1, 26);

      // Bolardo con cabo desamarrado hacia el agua
      caja(ctx, pal.k, 64, 30, 4, 6);
      caja(ctx, pal.k, 63, 30, 6, 2);
      caja(ctx, pal.l, 66, 36, 1, 8);

      // Almacén y farola del puerto
      caja(ctx, pal.w, 0, 16, 36, 20);
      borde(ctx, pal.k, 0, 16, 36, 20);
      caja(ctx, pal.r, 0, 10, 38, 6);
      caja(ctx, pal.R, 2, 12, 34, 2);
      caja(ctx, pal.k, 12, 24, 10, 12);
      caja(ctx, pal.a, 26, 20, 6, 6);
      caja(ctx, pal.k, 48, 18, 2, 18);
      caja(ctx, pal.a, 46, 14, 6, 4);
      caja(ctx, pal.k, 45, 13, 8, 2);
      caja(ctx, pal.A, 42, 12, 14, 8);

      // Barco zarpando con la bandera roja ondeando
      const progreso = fase(t, 200, 7500);
      const bx = Math.round(76 + progreso * 160);
      const by = 24 + Math.round(Math.sin((t / 600) * Math.PI) * 1.5);
      // Estela de espuma tras la popa
      caja(ctx, pal.w, bx - 6, by + 18, 6, 1);
      caja(ctx, pal.w, bx - 12, by + 19, 4, 1);
      dibujarSprite(ctx, pal, "barco_bandera_roja", bx, by);

      // Baliza / arrecife lejano en el horizonte
      caja(ctx, pal.k, 300, 38, 8, 5);
      caja(ctx, pal.r, 303, 34, 2, 4);
    },
  };

  // 2. Entender: Mutantes que caen al pasar por una medida.
  const escenaEntender = {
    ancho: 320, alto: 64, duracion: 8000,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.p, 0, 0, 320, 64);
      borde(ctx, pal.l, 0, 0, 320, 64);

      // Viga y cables superiores de la estación
      caja(ctx, pal.l, 0, 4, 320, 3);
      caja(ctx, pal.g, 0, 7, 320, 1);

      // Plataforma izquierda (x: 0 a 142)
      caja(ctx, pal.g, 0, 44, 142, 20);
      caja(ctx, pal.k, 0, 44, 142, 2);
      caja(ctx, pal.a, 134, 46, 8, 2);

      // Plataforma derecha (x: 184 a 320)
      caja(ctx, pal.g, 184, 44, 136, 20);
      caja(ctx, pal.k, 184, 44, 136, 2);

      // Foso de caída entre plataformas (x: 142 a 184)
      caja(ctx, pal.c, 142, 44, 42, 20);
      caja(ctx, pal.k, 142, 60, 42, 4);
      // Mutantes derrotados acumulados en el fondo
      dibujarSprite(ctx, pal, "bicho_mutante_muerto", 146, 52);
      dibujarSprite(ctx, pal, "bicho_mutante_muerto", 164, 52);

      // El pórtico de "La Medida" (x: 138 a 188)
      caja(ctx, pal.k, 138, 8, 4, 36);
      caja(ctx, pal.i, 140, 12, 1, 30);
      caja(ctx, pal.k, 184, 8, 4, 36);
      caja(ctx, pal.i, 184, 12, 1, 30);
      // Consola emisora superior
      caja(ctx, pal.k, 134, 6, 58, 10);
      borde(ctx, pal.l, 134, 6, 58, 10);
      caja(ctx, pal.i, 138, 9, 3, 4);
      caja(ctx, pal.i, 144, 9, 3, 4);

      // Haz vertical de escaneo de la medida
      ctx.save();
      ctx.fillStyle = pal.A || "rgba(246, 232, 200, 0.4)";
      ctx.globalAlpha = 0.35;
      ctx.fillRect(146, 16, 34, 34);
      ctx.restore();
      const scanY = 16 + (Math.floor(t / 80) % 32);
      caja(ctx, pal.i, 146, scanY, 34, 2);

      // Mutante que marcha y cae al cruzar la medida
      const ciclo = t % 4000;
      if (ciclo < 2200) {
        const mx = Math.round(30 + (ciclo / 2200) * 114);
        dibujarSprite(ctx, pal, "bicho_mutante", mx, 34);
      } else if (ciclo < 2800) {
        // Al tocar el haz: la medida lo caza -> chispas de fallo y veredicto
        caja(ctx, pal.r, 160, 8, 6, 6);
        dibujarSprite(ctx, pal, "chispa", 150, 26);
        dibujarSprite(ctx, pal, "chispa", 168, 30);
        dibujarSprite(ctx, pal, "bicho_mutante_muerto", 154, 36);
      } else {
        // Cae abatido al foso
        const caida = (ciclo - 2800) / 1200;
        const my = Math.round(36 + caida * 18);
        dibujarSprite(ctx, pal, "bicho_mutante_muerto", 154, my);
      }

      // Segundo mutante avanzando en la fila
      const mx2 = Math.round(10 + (((t + 2000) % 4000) / 4000) * 60);
      dibujarSprite(ctx, pal, "bicho_mutante", mx2, 34);

      // Baliza de zona limpia a la derecha
      caja(ctx, pal.k, 250, 36, 4, 8);
      caja(ctx, pal.v, 248, 32, 8, 4);
      caja(ctx, pal.V, 246, 30, 12, 2);
    },
  };

  // 3. Herramientas: Un faro que vigila (los sensores) y una boya.
  const escenaHerramientas = {
    ancho: 320, alto: 64, duracion: 8000,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.p, 0, 0, 320, 38);
      borde(ctx, pal.l, 0, 0, 320, 64);

      // Estrellas en el cielo nocturno
      const estrellas = [[20, 6], [55, 12], [90, 5], [140, 9], [180, 4], [225, 8]];
      estrellas.forEach(([ex, ey], idx) => {
        const brilla = ((t + idx * 700) % 1400) > 350;
        caja(ctx, brilla ? pal.a : pal.l, ex, ey, 1, 1);
      });

      // Mar con oleaje animado
      caja(ctx, pal.b, 0, 38, 250, 26);
      caja(ctx, pal.i, 0, 50, 250, 14);
      for (let x = 0; x < 250; x += 14) {
        const off = (Math.floor(t / 220) + Math.floor(x / 14) * 3) % 7;
        caja(ctx, pal.w, x + off, 39, 3, 1);
        caja(ctx, pal.l, x + ((off + 4) % 7), 43, 4, 1);
        caja(ctx, pal.w, x + off, 51, 3, 1);
      }

      // Acantilado y faro que vigila a la derecha (x: 245 a 310)
      caja(ctx, pal.k, 245, 52, 75, 12);
      caja(ctx, pal.g, 250, 36, 70, 16);
      caja(ctx, pal.k, 254, 34, 66, 2);
      dibujarSprite(ctx, pal, "faro_vigilante", 268, 6);

      // Haz luminoso del faro barriendo el mar
      const sweep = (t % 4000) / 4000;
      const hazX = 275 - Math.round(sweep * 220);
      ctx.save();
      ctx.fillStyle = pal.A || "rgba(246, 232, 200, 0.4)";
      ctx.globalAlpha = 0.45;
      ctx.beginPath();
      ctx.moveTo(275, 12);
      ctx.lineTo(hazX, 22);
      ctx.lineTo(hazX, 48);
      ctx.closePath();
      ctx.fill();
      ctx.restore();

      // Boya sensora meciéndose en el oleaje
      const buoyY = 32 + Math.round(Math.sin((t / 700) * Math.PI) * 2);
      dibujarSprite(ctx, pal, "boya_vigilante", 95, buoyY);

      // Ondas de telemetría de la boya hacia el faro
      const onda = (t % 1500) / 1500;
      const rad = 6 + onda * 36;
      ctx.save();
      ctx.strokeStyle = pal.i;
      ctx.lineWidth = 1;
      ctx.globalAlpha = 1 - onda;
      ctx.beginPath();
      ctx.arc(101, buoyY + 2, rad, -0.6 * Math.PI, 0.1 * Math.PI);
      ctx.stroke();
      ctx.restore();

      // Sonda sensora en el agua
      caja(ctx, pal.k, 175, 42, 6, 8);
      caja(ctx, pal.v, 177, 39, 2, 3);
    },
  };

  // 4. Referencia: Un cartógrafo con el mapa y el sello.
  const escenaReferencia = {
    ancho: 320, alto: 64, duracion: 8000,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.p, 0, 0, 320, 64);
      borde(ctx, pal.l, 0, 0, 320, 64);

      // Estantería con cartas y bitácoras a la izquierda
      caja(ctx, pal.k, 4, 6, 32, 28);
      caja(ctx, pal.a, 6, 8, 4, 10);
      caja(ctx, pal.r, 11, 8, 5, 10);
      caja(ctx, pal.i, 17, 8, 4, 10);
      caja(ctx, pal.w, 22, 10, 12, 8);
      caja(ctx, pal.l, 6, 19, 28, 1);
      caja(ctx, pal.i, 6, 21, 6, 11);
      caja(ctx, pal.a, 13, 21, 5, 11);
      caja(ctx, pal.g, 19, 21, 6, 11);

      // Lámpara náutica colgante y halo cálido
      caja(ctx, pal.k, 160, 0, 1, 6);
      caja(ctx, pal.a, 158, 6, 5, 5);
      caja(ctx, pal.A, 146, 11, 29, 14);

      // Mesa de cartografía de roble
      caja(ctx, pal.a, 20, 34, 280, 30);
      caja(ctx, pal.k, 20, 34, 280, 2);
      caja(ctx, pal.l, 20, 44, 280, 1);
      caja(ctx, pal.l, 20, 54, 280, 1);

      // Gran mapa de navegación extendido sobre la mesa
      caja(ctx, pal.w, 74, 18, 152, 32);
      borde(ctx, pal.k, 74, 18, 152, 32);
      caja(ctx, pal.p, 74, 18, 6, 32);
      caja(ctx, pal.p, 220, 18, 6, 32);
      // Costas y derrota en el mapa
      caja(ctx, pal.l, 90, 24, 20, 1);
      caja(ctx, pal.l, 110, 25, 15, 1);
      caja(ctx, pal.l, 125, 27, 25, 1);
      caja(ctx, pal.l, 86, 32, 30, 1);
      caja(ctx, pal.i, 115, 28, 40, 1);
      caja(ctx, pal.i, 135, 22, 1, 16);
      caja(ctx, pal.a, 134, 27, 3, 3);

      // El sello de lacre rojo en la esquina del mapa
      dibujarSprite(ctx, pal, "sello_lacre", 196, 26);
      // Cuño de bronce del cartógrafo sobre la mesa
      caja(ctx, pal.k, 232, 28, 4, 14);
      caja(ctx, pal.a, 230, 26, 8, 4);

      // Tintero con pluma y catalejo
      caja(ctx, pal.k, 246, 32, 6, 6);
      caja(ctx, pal.w, 248, 24, 2, 8);
      caja(ctx, pal.a, 262, 38, 22, 4);
      caja(ctx, pal.k, 266, 37, 2, 6);

      // La figura del cartógrafo trabajando sobre el mapa
      dibujarSprite(ctx, pal, "cartografo_figura", 44, 14);
      // Compás de navegación en su mano midiendo rumbos
      caja(ctx, pal.a, 62, 26, 12, 1);
      caja(ctx, pal.a, 73, 27, 1, 4);
      caja(ctx, pal.a, 70, 27, 1, 4);
    },
  };

  // 5. Decisiones: El rumbo fijado en las decisiones de diseño.
  const escenaDecisiones = {
    ancho: 320, alto: 64, duracion: 8000,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.p, 0, 0, 320, 64);
      borde(ctx, pal.l, 0, 0, 320, 64);

      // Timón de maniobra a la izquierda
      caja(ctx, pal.a, 36, 10, 4, 48);
      caja(ctx, pal.a, 14, 32, 48, 4);
      caja(ctx, pal.k, 34, 30, 8, 8);
      caja(ctx, pal.a, 36, 32, 4, 4);
      borde(ctx, pal.k, 22, 18, 32, 32);

      // Carta de derrota en el centro
      caja(ctx, pal.w, 80, 16, 130, 38);
      borde(ctx, pal.l, 80, 16, 130, 38);
      dibujarSprite(ctx, pal, "brujula", 86, 22);

      // Puntos de decisión y trayectorias conectadas
      const puntos = [[120, 38], [145, 28], [170, 36], [195, 24]];
      for (let j = 0; j < puntos.length; j++) {
        const [px, py] = puntos[j];
        caja(ctx, pal.i, px - 2, py - 2, 5, 5);
        caja(ctx, pal.r, px - 1, py - 1, 3, 3);
        if (j < puntos.length - 1) {
          const [nx, ny] = puntos[j + 1];
          ctx.save();
          ctx.strokeStyle = pal.i;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(px, py);
          ctx.lineTo(nx, ny);
          ctx.stroke();
          ctx.restore();
        }
      }

      // Libro de bitácora con registro sellado a la derecha
      caja(ctx, pal.a, 224, 16, 82, 38);
      caja(ctx, pal.w, 226, 18, 38, 34);
      caja(ctx, pal.w, 266, 18, 38, 34);
      caja(ctx, pal.k, 264, 16, 2, 38);
      for (let y = 22; y < 48; y += 5) {
        caja(ctx, pal.l, 230, y, 30, 1);
        caja(ctx, pal.l, 270, y, 30, 1);
      }
      caja(ctx, pal.r, 264, 30, 2, 26);
      caja(ctx, pal.r, 288, 36, 8, 8);
    },
  };

  const ESCENAS_SECCION = {
    empezar: escenaEmpezar,
    entender: escenaEntender,
    herramientas: escenaHerramientas,
    referencia: escenaReferencia,
    decisiones: escenaDecisiones,
  };

  // ---------------------------------------------------------------- escena marina del pie (320 x 56)
  const escenaMarinaPie = {
    ancho: 320, alto: 56, duracion: 8000,
    dibujar(ctx, pal, t) {
      caja(ctx, pal.w, 0, 0, 320, 34);

      // Estrellas en el cielo
      const estrellas = [
        [24, 6], [58, 10], [92, 4], [130, 8], [174, 5], [215, 9], [250, 6],
      ];
      estrellas.forEach(([ex, ey], idx) => {
        const brilla = ((t + idx * 800) % 1600) > 400;
        caja(ctx, brilla ? pal.a : pal.l, ex, ey, 1, 1);
      });

      // Luna creciente
      caja(ctx, pal.A, 36, 6, 6, 6);
      caja(ctx, pal.w, 38, 6, 4, 6);

      // Faro a la derecha sobre rocas
      caja(ctx, pal.k, 260, 42, 60, 14);
      caja(ctx, pal.g, 265, 38, 55, 6);
      dibujarSprite(ctx, pal, "faro_chico", 280, 20);

      // Haz luminoso del faro
      const giro = (t % 4000) / 4000;
      const hazX = 282 - Math.round(giro * 220);
      ctx.save();
      ctx.fillStyle = pal.A || "rgba(246, 232, 200, 0.35)";
      ctx.globalAlpha = 0.45;
      ctx.beginPath();
      ctx.moveTo(284, 22);
      ctx.lineTo(hazX, 26);
      ctx.lineTo(hazX, 44);
      ctx.closePath();
      ctx.fill();
      ctx.restore();

      // Agua del mar (capas de olas)
      caja(ctx, pal.b, 0, 34, 265, 12);
      caja(ctx, pal.i, 0, 42, 320, 14);
      for (let x = 0; x < 265; x += 14) {
        const offset = Math.floor(t / 250) % 7;
        caja(ctx, pal.w, x + offset, 34, 3, 1);
        caja(ctx, pal.l, x + ((offset + 4) % 7), 38, 4, 1);
        caja(ctx, pal.w, x + offset, 44, 3, 1);
      }

      // Boya meciéndose en el agua
      const buoyY = 32 + Math.round(Math.sin((t / 600) * Math.PI) * 1.5);
      dibujarSprite(ctx, pal, "boya_chica", 135, buoyY);

      // Barco navegando suavemente
      const by = 22 + Math.round(Math.sin((t / 800) * Math.PI) * 1.5);
      const bx = 45 + Math.round(((t / 8000) * 160) % 180);
      dibujarSprite(ctx, pal, "barco_chico", bx, by);
    },
  };

  // ---------------------------------------------------------------- divisores pixelados
  function pintarDivisor(canvas, pal) {
    const w = canvas.width, h = canvas.height;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, w, h);

    const cy = 4;
    // Base de agua continua
    caja(ctx, pal.i, 0, cy + 2, w, 1);

    // Olas rítmicas de 2-3 píxeles de alto
    for (let x = 0; x < w; x += 16) {
      caja(ctx, pal.i, x + 2, cy + 1, 4, 1);
      caja(ctx, pal.i, x + 3, cy, 2, 1);
      caja(ctx, pal.i, x + 10, cy + 1, 4, 1);
      caja(ctx, pal.i, x + 11, cy, 2, 1);
    }

    // Fila de boyas náuticas cada 32 píxeles
    for (let bx = 0; bx <= w; bx += 32) {
      caja(ctx, pal.r, bx, cy - 1, 1, 1);
      caja(ctx, pal.r, bx - 1, cy, 3, 1);
      caja(ctx, pal.a, bx - 1, cy + 1, 3, 1);
      caja(ctx, pal.k, bx, cy + 2, 1, 1);
    }
  }

  // ---------------------------------------------------------------- montaje y ciclo de vida
  function montarSprite(canvas) {
    const nombre = canvas.dataset.sprite;
    if (!nombre || !SPRITES[nombre]) return;
    const filas = SPRITES[nombre];
    canvas.width = filas[0].length;
    canvas.height = filas.length;
    const ctx = canvas.getContext("2d");
    const repintar = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      dibujarSprite(ctx, paleta(), nombre, 0, 0);
    };
    repintar();
    canvas._repintar = repintar;
  }

  function montarEscena(canvas, escena) {
    if (!escena) return;
    canvas.width = escena.ancho;
    canvas.height = escena.alto;
    const ctx = canvas.getContext("2d");
    let pal = paleta(), activo = false, t0 = performance.now(), cuadro = null;

    const pintar = (t) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      escena.dibujar(ctx, pal, t);
    };

    // Cuadro final: siempre visible en reposo y para usuarios con prefers-reduced-motion
    pintar(escena.duracion - 1);
    canvas._repintar = () => { pal = paleta(); pintar(escena.duracion - 1); };

    if (reducido) return;

    const bucle = (ahora) => {
      pintar((ahora - t0) % escena.duracion);
      cuadro = activo ? requestAnimationFrame(bucle) : null;
    };

    new IntersectionObserver(([e]) => {
      activo = e.isIntersecting;
      if (activo && !cuadro) {
        t0 = performance.now();
        cuadro = requestAnimationFrame(bucle);
      }
    }).observe(canvas);
  }

  function montarDivisores() {
    document.querySelectorAll("hr.divisor-pixel").forEach((hr) => {
      if (hr.querySelector("canvas")) return;
      const c = document.createElement("canvas");
      c.width = 320;
      c.height = 10;
      c.setAttribute("aria-hidden", "true");
      c.className = "divisor-canvas";
      hr.replaceChildren(c);
      const repintar = () => pintarDivisor(c, paleta());
      repintar();
      c._repintar = repintar;
    });
  }

  function arrancar() {
    // 1. Sprites en títulos y subtítulos (h1 y h2)
    document.querySelectorAll("canvas.sprite[data-sprite]").forEach(montarSprite);

    // 2. Escenas de cabecera de sección
    document.querySelectorAll("canvas.escena-seccion[data-escena-seccion]").forEach((c) => {
      const id = c.dataset.escenaSeccion;
      montarEscena(c, ESCENAS_SECCION[id]);
    });

    // 3. Escena de pie de página
    document.querySelectorAll("canvas.escena-pie[data-escena-pie]").forEach((c) => {
      montarEscena(c, escenaMarinaPie);
    });

    // 4. Divisores pixelados
    montarDivisores();

    // 5. Escuchar cambios de tema para repintar
    const refrescarTodo = () => {
      document.querySelectorAll("canvas").forEach((c) => {
        if (typeof c._repintar === "function") c._repintar();
      });
    };
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", refrescarTodo);
    new MutationObserver(refrescarTodo).observe(document.documentElement, {
      attributes: true, attributeFilter: ["data-theme"],
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", arrancar);
  } else {
    arrancar();
  }
})();
