# La página de cero enseña una medida suelta; falta la guía completa de una batalla naval en HTML5, paso a paso, para quien empieza a programar con un LLM

- ESTADO: ABIERTA
- PRIORIDAD: 80
- ETIQUETAS: oracle, web, documentacion, guia


## Por qué

2026-09-24, Brian: `docs/de-cero.html` tiene que ser **la guía completa del ejemplo que venimos
haciendo**, una batalla naval en HTML5, paso por paso, para alguien que **recién empieza a programar**
y programa **con un LLM** («vibecoding»). Hoy la página enseña una sola medida
(`documento.nombre_sigue_la_convencion`), y la guía que existe es
`~/TestOracleEjemplo/GUIA22.md` (1171 líneas), que quedó desactualizada: se escribió contra 0.25.2 y
varias cosas cambiaron. Por ejemplo, la omisión silenciosa de `juzgar`, que 0.27 resolvió con
`NO SE APLICARON`; `mas()` en vez de `+`, que 0.30 resolvió; y la ergonomía de 0.29.

## Qué hacer

1. **El código completo del juego**, tomado de `~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280`
   (`index.html`, `css/`, `js/engine.js`, `trace.js`, `ui.js`, `audio.js`, `catalogos/naval/`,
   `corpus/naval/`, `verificar_oraculo.py`, `partida_real.json`), tal como está, dentro del repo en
   `ejemplo/batalla-naval/` para que la página lo enlace y un test lo corra. Brian dice que «le faltó
   más»: la guía lo dice y propone qué seguir, sin inventar que ya está.
2. **La guía, paso por paso**, para quien nunca programó:
   - qué es HTML5, CSS y JS lo justo para leer el juego;
   - cómo pedirle el juego a un LLM y qué revisar de lo que devuelve;
   - por qué el juego emite hechos (`celda_barco`, `tiro`, `partida`) en vez de validarse a sí mismo;
   - cómo escribir cada medida (colocación, turnos, hundimiento, final) en la superficie actual, con
     `a + 1` en vez de `mas(a, 1)`;
   - los casos rojo y verde, `oracle test`, la mutación y qué significa que un mutante sobreviva;
   - `oracle juzgar` sobre una partida real, qué dice `SIN MIRAR` y qué `NO SE APLICARON`;
   - qué le pasa a quien trabaja con un LLM: el postmortem de la batalla naval
     (`vault-kb/postmortems/`) como advertencia, con el verde que no medía nada.
3. **Todo verificable**: cada comando de la guía corre en un test (como `docs/13-primer-valor.md`),
   cada salida de terminal es de una corrida real, y `oracle test` del ejemplo es VERDE en CI.
4. **La página se ve bien en un teléfono** y conserva el estilo del sitio.

Base: GUIA22.md para el recorrido y el tono; naval-0280 para el código. Donde se contradigan, manda la
versión vigente de Oracle.

### Nota (2026-09-24 17:15:40 UTC)

2026-09-24, Brian: de-cero tiene que ser DE CERO, no un repo para bajar. La persona copia y pega y va creando el juego de a poco con oracle-metalenguaje: instala, oracle init, pega el primer HTML, lo abre, pega la primera medida, escribe su primer caso rojo, corre oracle test, lo ve fallar y lo arregla, y así hasta el juego entero. Cada paso es un bloque para copiar, lo que tiene que ver en la pantalla o la terminal, y qué hacer si ve otra cosa. El código en ejemplo/batalla-naval/ no es lo que se baja: es el respaldo que verifica la guía. Un test arma el juego pegando los bloques de la guía en orden, desde un directorio vacío, y corre oracle test después de cada paso; si un bloque de la página cambia, el test lo nota.

## Próximo paso

Revisar naval-0280 contra 0.30.0 (¿su catálogo y su corpus pasan `oracle test` hoy?), marcar qué de
GUIA22 quedó vencido, y partir el juego en pasos chicos que se puedan pegar en orden, cada uno con
algo visible que funcione y una medida o un caso nuevo.

### Nota (2026-09-24 17:18:15 UTC)

2026-09-24, Brian: el corpus de naval-0280 está flojo. Medido: 11 medidas en catalogos/naval/ y 2 casos en corpus/naval/ (001-tiro-fuera-de-tablero y 002-tiro-valido), los dos de naval.tiros_dentro_del_tablero; las otras diez no tienen ningún caso. Para la guía: cada medida con al menos un caso rojo (el defecto que atrapa, sacado de una partida plausible) y uno verde, y la mutación de medidas con todos los mutantes muertos. Si un mutante sobrevive, se agrega el caso que lo mata. Y la guía lo enseña como lección: primero muestra que 11 medidas con 2 casos dan verde igual, corre la mutación, ve sobrevivir a los mutantes y escribe los casos que faltan. Es la diferencia entre un verde que mide y uno que decora.
