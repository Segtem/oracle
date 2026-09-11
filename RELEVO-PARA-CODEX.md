# Relevo para codex — desde 0.14.0

> Continuación del 2026-09-10: [trabajo y verificaciones](RELEVO-2026-09-10.md).
> El estado que sigue se conserva como antecedente fechado.

**Escrito el 2026-09-09 por Claude**, al quedarse sin crédito. El árbol está limpio en `0.14.0`,
empujado, con tag y release, y el paquete sube a PyPI por mano del dueño.

**Trabajá en español.** El proyecto entero —código, comentarios, medidas, casos, estudios— está en
español, y el idioma es parte del diseño: una medida se lee en voz alta.

---

## Dónde está el proyecto hoy

```
ACEPTACIÓN ✓ — 115 defectos en rojo, 81 verdes correctos, 0 huecos declarados sin tapar
```

**Esto es nuevo y vale entenderlo antes de tocar nada.** Desde el 2026-08-26 y durante veintitrés
días, `tools/aceptacion.py` salía con **código 1 a propósito**: DECISION-004 declaraba que dos
medidas quedaban sostenidas sólo por evidencia fabricada, y en vez de aflojar la medida que las
señalaba, el proyecto declaró la consecuencia y la sostuvo. **El 2026-09-09 la decisión quedó
CUMPLIDA.** El CI perdió el `|| true` que arrastraba y su chequeo literal pasa de `1 rojo` a `0`.

Números al cierre:

| | |
|---|---|
| suite | 1506 tests |
| corpus | 203 casos |
| medidas | 60 · 40 universales · **959/959 mutantes de medida** |
| custodias | 14 declaradas · **13 en la matriz de CI** |
| deuda en sombra | 94 casos observados sin `origen`, con cota 94 |
| consumidores | Jam 28/3 · LyraGASP 43/78, los dos en verde |

---

## Lo que sigue abierto, medido y sin adornar

### 1. `tools/metamorficas.py` no está en `HERRAMIENTAS_CUSTODIAS`, y debería

**Es el hallazgo más concreto que queda, y lo dejé sin cerrar a propósito** para no mezclarlo con el
cierre de DECISION-004.

`metamorficas.py` genera las sondas que sostienen `meta.sintaxis_cubre_algebra` y
`meta.sintaxis_casos_cubre_casos` — **las dos medidas que acaban de cerrar esa decisión**. Si dejara
de generar una esquina en silencio, las dos darían **verde vacuamente** y nadie se enteraría. Es la
definición literal de la lista: *«si el instrumento se rompe, la afirmación queda sin nadie que la
verifique»*.

**Qué hacer:** medirlo (`python3 -B tools/mutar_codigo.py --objetivo tools/metamorficas.py
--timeout 120 --manifiesto /tmp/prog.json`), cerrar los sobrevivientes si los hay, y meterlo a
`HERRAMIENTAS_CUSTODIAS` y a la matriz de `.github/workflows/verificar.yml`. Necesita también una
entrada en `PRIORIDADES` con sus módulos de tests.

⚠ Antes de agregarlo a `PRIORIDADES`, mirá `test_todo_objetivo_de_mutacion_declara_sus_tests_prioritarios`
y `LasCustodiasQueNadieMide` en `tests/test_herramientas.py`: los dos vigilan esa lista en las dos
direcciones y te van a decir si falta algo.

### 2. `tools/cli.py`: bajó 66% y no alcanzó

**No es deuda: está en 504/504 sin sobrevivientes.** Es costo: **12,5 minutos**, bajado de 36,5, y el
umbral para entrar a la matriz son ~10. El número real está en `CUSTODIAS_SIN_MEDIR` con su razón;
**no relajes el umbral**, bajá el costo o dejalo afuera.

El techo está medido y es de dónde hay que atacar:

- `tests.test_biblioteca` 0,23 s · `tests.test_vigilar` 0,08 s · `tests.test_cli` 9,0 s ·
  `tests.test_herramientas` **18,4 s**
- Los dos módulos baratos sólo matan **98 de 504** mutantes (19,4 %)
- **83 mutantes llegan hasta `test_herramientas`** y pagan sus 18 segundos enteros

La palanca no es reordenar más: es que `test_herramientas` sea más barato, o que los mutantes que
llegan hasta ahí mueran antes. `tests/test_cli_integracion.py` ya se separó con ese criterio.

### 3. Los 49 casos sin procedencia de los consumidores

Jam **23**, LyraGASP **26**. No es deuda de Oracle sino de ellos, pero lo que la haría barata sí es
de Oracle: **`observar.py` sigue conectado sólo al trabajo del propio Oracle**. Hoy Oracle puede
capturar su propia aceptación (`observaciones/aceptacion.plan.json`), y un consumidor no tiene el
equivalente. Un plan por consumidor haría que sus casos nuevos nazcan con comando y registro
probados en vez de escritos de memoria.

⚠ **LyraGASP está trabajando sobre MetaHuman ahora mismo — no toques ese repo.**

### 4. Los 94 `origen`: cerrada como irrecuperable, no pendiente

No se cierran hacia atrás sin inventar: el árbol contra el que corrieron ya no existe. La cota los
tiene en 94 y `meta.ninguna_sombra_supera_su_cota` hace fallar la corrida si suben. **Dejá de
tratarla como tarea.**

### 5. Autenticidad: pregunta de investigación, no tarea

Nada distingue una corrida de una transcripción, y cada observación lo declara. Está desarrollado en
`PLAN-0.14-LO-QUE-FALTA.md`, fase 3, con lo que **no** hay que hacer (firmar con una clave del
propio proyecto prueba que Oracle lo escribió, no que el sensor corrió). El entregable sería un
estudio, no código.

---

## Lo que el dueño pidió como dirección: rendimiento y accesibilidad humana

Esto es abierto, así que van pistas medidas en vez de una lista de deseos.

**Rendimiento.** El costo del proyecto está concentrado y medido: la suite entera tarda ~44 s, y de
ahí `tests.test_herramientas` son 18,4 s con 157 tests. Cada segundo ahí se multiplica por cada
mutante de cada archivo cuyo perfil lo incluya — que son muchos. Medí antes de optimizar: hay un
patrón repetido de tests que corren `oracle test` o construyen ruedas sobre proyectos temporales, y
esos son los caros. El precedente: `tools/contexto.py` pasó de **858 a 56 segundos** sólo cambiando
el orden de su perfil, y `tools/medida.py` de ~90 minutos a 201 segundos escribiendo los tests que
faltaban.

**Accesibilidad para humanos.** Lo que ya existe y por dónde seguir:

- `oracle manual --html` y `docs/manual.html`, que es exactamente su salida y un test lo fija.
- `oracle censar --html` produce una página; `oracle reportar` produce un informe.
- El LSP (`tools/lsp.py`) da diagnósticos en el editor. **Salió de `HERRAMIENTAS_CUSTODIAS` el
  2026-09-09** porque no custodia ninguna afirmación, pero eso no lo hace menos útil: es la
  superficie por donde una persona escribe una medida.
- Los mensajes de error del proyecto **son parte del producto**. Dos defectos reales de esta semana
  fueron mensajes que hablaban de otra cosa: `--verificar` ignoraba argumentos y salía 0, y
  `oracle corpus` moría con «no se pudo leer la medida…: Is a directory». Buscá más de ésos.

---

## Las reglas que el proyecto sostiene, y por qué

No son estilo. Cada una salió de un defecto concreto.

1. **Un test que EJECUTA una rama no es un test que la FIJA.** El criterio: si el mutante estuviera
   aplicado, ¿este test falla? Comprobalo aplicando el cambio a mano en una copia. Ya lo hiciste con
   60 reemplazos en `sintaxis.py` y con 20 en `censar.py` — seguí así.
2. **Un equivalente genuino se borra, no se declara.** Declararlo acepta para siempre un mutante que
   nadie puede matar.
3. **No aflojes una medida para que pase.** Ni umbrales, ni asserts, ni mutadores. Si una medida
   molesta, el defecto suele estar del otro lado.
4. **Un timeout no mata a nadie.** Una ronda con timeouts informa un número que parece medido y no lo
   está: vale menos que no correrla. La matriz corre con `--timeout 120`.
5. **No edites el árbol mientras corre una ronda de mutación.** El arnés copia el proyecto y la
   corrida se pierde. Pasó cinco veces, dos de ellas ayer.
6. **Cada test dice POR QUÉ existe** en su docstring: qué defecto real dejaría pasar si no estuviera.
7. **Cuando algo se descarta, el argumento que lo descarta tiene que declarar su premisa.** Ésta es
   nueva, del 2026-09-09: un informe riguroso concluyó «no hay defecto» y **contenía el defecto en
   la sección de lo descartado**, porque el argumento era cierto bajo una premisa que el sistema no
   garantiza.
8. **Un hueco declarado no es un hueco medido.** Tres veces seguidas un `alcance` declaró un hueco
   con una estimación de su tamaño, y las tres el hueco era peor. Cuando declares uno, declará
   también **qué mediste** para creer que es chico.

---

## Cómo se verifica un corte, en orden

```bash
python3 -B -m unittest discover -s tests -q     # tiene que quedar OK
python3 -B tools/corpus.py                       # CORPUS OK
python3 -B tools/aceptacion.py                   # ✓ y CÓDIGO 0 — desde 0.14.0 ya no sale 1
python3 -B tools/mutar.py                        # 959/959 o más, sin sobrevivientes
python3 -B tools/cifras.py --actualizar          # las cifras del README las genera él
python3 -B tools/cli.py manual --html > docs/manual.html
python3 -B tools/verificar_instalacion.py        # WHEEL OK
python3 -B tools/sondear_generador.py
python3 -B tools/sondear_procedencia.py
python3 -B tools/trazar.py
```

Y sobre los dos consumidores, con el árbol y no con el paquete publicado:

```bash
cd ~/Dev/jam && PYTHONPATH=~/Dev/oracle python3 -B ~/Dev/oracle/tools/aceptacion.py \
    --proyecto medidas --confiar-escalares
```

**Las tres versiones se deciden por separado** y el criterio está en `ESPECIFICACION.md` §0, con un
párrafo por corte explicando por qué subió lo que subió. Leé los últimos cinco antes de tocar
`nucleo/version.py`.

---

## Cosas de esta máquina que cuestan tiempo si no se saben

- **`codex exec` se cuelga esperando stdin.** Usá `< /dev/null`. Un turno perdió diez horas por eso,
  y lo peor fue que el vigilante miraba si el proceso EXISTÍA, no si avanzaba.
- **`pgrep -f <patrón>` se matchea a sí mismo.** El truco: `mutar_codig[o].py`.
- **`/tmp` es tmpfs**, o sea RAM. No fue causa de ningún problema medido, pero conviene saberlo.
- **`tools/verificar_instalacion.py` deja ~100 MB por corrida** en `/tmp/oracle-wheel-test-*`.
- **PyPI lo sube el dueño**, con `uvx twine upload dist/oracle_metalenguaje-<version>*`.
- **La mutación de código NO corre en cada push** (`if: github.event_name != 'push'`): corre en pull
  requests y a pedido, porque la cuenta agotó su cupo de Actions una vez.

---

## Lo que NO hay que hacer

- **No cambies versiones por tu cuenta.** Proponé el número con su argumento y esperá.
- **No hagas commit ni push sin que el dueño lo pida.**
- **No toques `~/Dev/games/unreal/LyraGASP`**: está trabajando sobre MetaHuman.
- **No reclasifiques evidencia vieja para mejorar cifras**, ni conviertas casos `observada` en
  `construida` para que una medida pase.
- **No desactives sombras.** Si una molesta, el problema está debajo.
