const assert = require('node:assert/strict');
const { test } = require('node:test');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { runInNewContext } = require('node:vm');
const html = readFileSync(join(__dirname, '../../docs/de-cero.html'), 'utf8');
const script = html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];

function montar({ chica = false, clipboard } = {}) {
  const menu = { open: true };
  const media = { matches: chica, addEventListener(_, cb) { this.cambiar = cb; } };
  const codigo = { textContent: 'medida prueba:\n    umbral <= 0\n' };
  let boton, seleccionado;
  const pre = { querySelector: () => codigo, append(b) { boton = b; } };
  const contexto = {
    matchMedia: () => media,
    navigator: { clipboard },
    setTimeout: () => {},
    getSelection: () => ({ removeAllRanges() {}, addRange(r) { seleccionado = r.nodo; } }),
    document: {
      querySelector: () => menu,
      querySelectorAll: () => [pre],
      createElement: () => ({ addEventListener(_, cb) { this.click = cb; } }),
      createRange: () => ({ selectNodeContents(nodo) { this.nodo = nodo; } }),
    },
  };
  runInNewContext(script, contexto);
  return { menu, media, codigo, get boton() { return boton; }, get seleccionado() { return seleccionado; } };
}

test('el menú vuelve a abrirse al pasar de móvil a escritorio', () => {
  const pagina = montar({ chica: true });
  assert.equal(pagina.menu.open, false);
  pagina.media.matches = false;
  pagina.media.cambiar();
  assert.equal(pagina.menu.open, true);
  pagina.media.matches = true;
  pagina.media.cambiar();
  assert.equal(pagina.menu.open, false);
});

test('copiar conserva exactamente el salto final del archivo', async () => {
  let texto;
  const pagina = montar({ clipboard: { async writeText(value) { texto = value; } } });
  await pagina.boton.click();
  assert.equal(texto, pagina.codigo.textContent);
  assert.equal(pagina.boton.textContent, 'Copiado');
  assert.equal(pagina.seleccionado, undefined);
});

for (const [nombre, clipboard] of [
  ['sin API de portapapeles', undefined],
  ['con permiso denegado', { async writeText() { throw new Error('denegado'); } }],
]) {
  test(`copiar ${nombre} selecciona sólo el código y avisa`, async () => {
    const pagina = montar({ clipboard });
    await pagina.boton.click();
    assert.equal(pagina.seleccionado, pagina.codigo);
    assert.equal(pagina.boton.textContent, 'Texto seleccionado: copialo');
  });
}

const pixel = readFileSync(join(__dirname, '../../docs/assets/pixel.js'), 'utf8');
for (const reducido of [true, false]) {
  test(`las escenas quietas repintan al cambiar el tema (movimiento reducido: ${reducido})`, async () => {
    let tema = 'claro', cambioSistema, cambioAtributo, fotogramas = 0;
    const colores = [];
    const ctx = { fillRect() { colores.push(this.fillStyle); }, fillText() {} };
    const canvas = { dataset: { escena: 'testigos' }, getContext: () => ctx };
    runInNewContext(pixel, {
      matchMedia: (consulta) => ({
        matches: consulta.includes('reduced-motion') && reducido,
        addEventListener(_, cb) { cambioSistema = cb; },
      }),
      getComputedStyle: () => ({ getPropertyValue: (nombre) => `${tema}:${nombre}` }),
      document: { documentElement: {}, querySelectorAll: () => [canvas] },
      performance: { now: () => 0 },
      requestAnimationFrame: () => { fotogramas++; },
      IntersectionObserver: class { observe() {} },
      MutationObserver: class {
        constructor(cb) { cambioAtributo = cb; }
        observe() {}
      },
    });
    await Promise.resolve();
    assert.ok(colores.length > 0);
    colores.length = 0;
    tema = 'oscuro';
    cambioSistema();
    assert.ok(colores.some((c) => c.startsWith('oscuro:')));
    colores.length = 0;
    tema = 'claro';
    cambioAtributo();
    assert.ok(colores.some((c) => c.startsWith('claro:')));
    assert.equal(fotogramas, 0);
  });
}
