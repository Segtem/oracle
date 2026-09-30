# Informe de Ejecución: «Tu primer juego con un LLM, y cómo saber si está bien»

Este informe documenta la reproducción paso a paso de la guía `/guia/de-cero.md`, ejecutada desde una carpeta vacía en `/work` siguiendo al pie de la letra cada instrucción y comparando los resultados observados con lo estipulado en el documento.

---

## 1. Estado por paso

- **Paso 1 · Preparar la carpeta**: **distinto** (la ruta emitida por `oracle init` fue absoluta `/work/batalla-naval:` en lugar de la relativa mostrada en la guía, los cuatro comandos se agruparon en una única salida en el texto, y la versión de PyPI no estaba especificada en la guía).
- **Paso 2 · El tablero**: **hecho** (se crearon `index.html` y `css/style.css`; la estructura visual y controles cargaron conforme a lo descripto).
- **Paso 3 · El juego**: **hecho** (se crearon los cuatro archivos de JavaScript: `js/audio.js`, `js/trace.js`, `js/engine.js` y `js/ui.js`; la lógica del juego y sintaxis están operativas).
- **Paso 4 · Que el juego cuente lo que pasó**: **hecho** (paso conceptual explicativo sobre el registro inmutable de hechos vs. conclusiones; no introduce comandos ni archivos adicionales).
- **Paso 5 · La primera regla, empezando por el caso rojo**: **hecho** (se creó el caso 005, falló con ACEPTACIÓN ✗; se creó la medida `naval.barcos_dentro_del_tablero`, se formateó y falló con MUTACIÓN en ROJO, tal como indicaba la guía).
- **Paso 6 · Un caso rojo no alcanza: la mutación**: **hecho** (se agregó el caso verde 006 matando mutantes pero quedando 4 vivos; luego se agregaron los casos 026, 027 y 028 alcanzando el VEREDICTO: VERDE con 18 mutantes muertos de 18).
- **Paso 7 · Diez reglas más, y la trampa de los pocos casos**: **hecho** (se crearon las 10 medidas y los casos 001 y 002 dando ROJO por 9 medidas sin casos; luego se incorporaron los 26 casos restantes alcanzando VEREDICTO: VERDE con 33 casos y 209 mutantes muertos de 209).
- **Paso 8 · Juzgar una partida de verdad**: **hecho** (se juzgó `hechos_partida.json` obteniendo verde en las 11 medidas y la lista SIN MIRAR; luego se generó `sin-tiros.json` y `oracle juzgar` reportó 7 medidas no aplicadas por falta de relación `tiro`).
- **Paso 9 · Qué le falta a este juego**: **hecho** (análisis de reglas pendientes; al activar `"catalogo_base": true` en `oracle.json` y correr `oracle test`, el veredicto pasó a ROJO reclamando unidades declaradas y evidencia observada, exactamente como anticipaba la guía).

---

## 2. Registro detallado de problemas y diferencias

### Problema 1: Versión no fijada en comando de instalación (Paso 1)

- **Cita textual** (línea 27):
```bash
uv tool install oracle-metalenguaje
```
- **Comando corrido**:
```bash
uv tool install oracle-metalenguaje==0.38.0
```
- **Salida obtenida**:
```text
Resolved 1 package in 291ms
Prepared 1 package in 211ms
Installed 1 package in 38ms
 + oracle-metalenguaje==0.38.0
Installed 9 executables: oracle, oracle-aceptacion, oracle-corpus, oracle-diferencial, oracle-estudio, oracle-lsp, oracle-medida, oracle-mutar, oracle-mutar-codigo
```

---

### Problema 2: Discrepancia en la ruta emitida por `oracle init` y agrupación de salidas (Paso 1)

- **Cita textual** (línea 36):
```text
Proyecto Oracle inicializado en batalla-naval:
```
- **Comando corrido**:
```bash
oracle init batalla-naval
```
- **Salida obtenida**:
```text
Proyecto Oracle inicializado en /work/batalla-naval:
  · catalogos/
  · corpus/
  · diferencial/
  · relaciones/
  · oracle.json

Próximos pasos:
  1. Creá un caso:     oracle caso <grupo/id>
  2. Creá una medida:  oracle nueva <dominio.nombre>
  3. Verificá todo:    oracle test
```
*Diferencia*: La guía muestra `Proyecto Oracle inicializado en batalla-naval:` (relativa), mientras que la herramienta imprimió la ruta absoluta `Proyecto Oracle inicializado en /work/batalla-naval:`.

Asimismo, en las líneas 26-31 la guía agrupa cuatro órdenes consecutivas en un solo bloque:
```bash paso
uv tool install oracle-metalenguaje
oracle init batalla-naval
cd batalla-naval
oracle test
```
Y presenta en las líneas 35-59 una sola salida combinada que pega la salida de `oracle init` y de `oracle test`, omitiendo la salida de instalación de `uv` y sin explicitar qué comando produce cada tramo de texto.

El comando posterior:
```bash
oracle test
```
Produjo:
```text
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS: sin casos guardados para verificar
SINTAXIS: salteado (sin medidas ni casos todavía)
ACEPTACIÓN: salteado (sin medidas ni casos todavía)
DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)
MUTACIÓN: salteada (sin medidas todavía)

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

PRODUCTO: sin nueva medición; no se ejecutó el producto.
VEREDICTO: SIN MEDICIÓN (advertencia: proyecto vacío: 0 medidas propias, 0 casos, 0 fixtures diferenciales)
```

---

### Problema 3: Subdirectorios de dominio inexistentes en la estructura inicial (Paso 5 y Paso 7)

- **Cita textual** (línea 3018):
```text
En Oracle ese ejemplo se llama **caso**. Guardalo en `corpus/naval/`:
```
- **Cita textual** (línea 3077):
```text
```oracle archivo=catalogos/naval/naval.barcos_dentro_del_tablero.oracle
```
- **Problema encontrado**: El comando `oracle init batalla-naval` crea únicamente los directorios raíz `catalogos/`, `corpus/`, `diferencial/` y `relaciones/`, pero no crea las subcarpetas del dominio (`catalogos/naval/` ni `corpus/naval/`). Quien siga la guía desde la terminal e intente guardar los archivos directamente sin ejecutar previamente `mkdir -p corpus/naval` y `mkdir -p catalogos/naval` se encuentra con error de sistema (`No such file or directory` / carpeta no encontrada).

---

### Problema 4: Apertura y visualización en entornos de terminal (Paso 2 y Paso 3)

- **Cita textual** (líneas 1369-1370):
```text
Abrí `index.html` en el navegador (doble clic, o arrastralo a una pestaña). Vas a ver la cabecera y los paneles, **sin tableros todavía**: los tableros los dibuja el JavaScript.
```
- **Cita textual** (línea 2946):
```text
Recargá la página. Ahora se juega: colocá tus barcos (o usá el despliegue automático) y disparale a
la computadora.
```
- **Problema encontrado**: Quien trabaje en un entorno remoto, máquina virtual o contenedor sin interfaz gráfica de escritorio no dispone de «doble clic» ni de arrastre de archivos a una ventana. La guía no indica comandos alternativos para servir la página (por ejemplo `python3 -m http.server`).

---

### Problema 5: Ubicación de descarga de la evidencia `hechos_partida.json` (Paso 8)

- **Cita textual** (líneas 4293-4296):
```text
Las reglas ya están probadas. Ahora se juzga una partida real: jugá una partida entera, abrí el panel
de auditoría y descargá `hechos_partida.json` en la carpeta del proyecto. (Si todavía no jugaste, podés
[bajar la partida del ejemplo](https://github.com/Segtem/oracle/raw/main/ejemplo/batalla-naval/partida_real.json)
y guardarla con ese nombre.)
```
- **Problema encontrado**: Cuando el botón del juego web descarga el archivo JSON en el navegador, los navegadores lo depositan automáticamente en la carpeta de descargas del usuario del sistema operativo (e.g. `~/Downloads` o `~/Descargas`), no dentro de la carpeta del proyecto de la terminal (`/work/batalla-naval`). Un principiante que luego corra en la terminal el comando indicado en la línea 5896:
```bash
oracle juzgar --con hechos_partida.json
```
se encontraría con que el archivo no está en la carpeta de trabajo a menos que sepa moverlo o copiarlo manualmente.

---

### Problema 6: Comando condensado de Python para manipulación de JSON (Paso 8)

- **Cita textual** (líneas 5950-5953):
```bash paso
python3 -c "import json; d = json.load(open('hechos_partida.json')); json.dump({'celda_barco': d['celda_barco'], 'partida': d['partida']}, open('sin-tiros.json', 'w'))"
oracle juzgar --con sin-tiros.json
```
- **Comando corrido**:
```bash
python3 -c "import json; d = json.load(open('hechos_partida.json')); json.dump({'celda_barco': d['celda_barco'], 'partida': d['partida']}, open('sin-tiros.json', 'w'))"
oracle juzgar --con sin-tiros.json
```
- **Salida obtenida**:
```text
✓ naval.barcos_dentro_del_tablero                     0 (<= 0)
✓ naval.barcos_sin_solapamiento                       0 (<= 0)
✓ naval.flota_reglamentaria                           0 (<= 0)
✓ naval.ganador_legitimo                              0 (<= 0)

NO SE APLICARON (7) — su relación no vino en la evidencia:
  · naval.alternancia_turnos: falta tiro
  · naval.fin_de_juego_sin_tiros_posteriores: falta tiro
  · naval.tiros_dentro_del_tablero: falta tiro
  · naval.tiros_sin_repeticion: falta tiro
  · naval.turnos_sin_huecos: falta tiro
  · naval.veracidad_impacto_negativo: falta tiro
  · naval.veracidad_impacto_positivo: falta tiro

VEREDICTO: 7 medidas propias sin aplicar (usá --parcial para una corrida deliberadamente parcial)
```
- **Problema encontrado**: Para alguien que recién empieza a programar, la línea de Python es un comando complejo de una sola línea con manipulación de estructuras de datos en memoria sin explicar qué hace cada invocación (`import json`, `json.load`, `open`, `json.dump`).

---

### Problema 7: Activación del catálogo base sin guía para resolver los reclamos (Paso 9)

- **Cita textual** (líneas 6001-6003):
```text
Y el catálogo base que apagaste en el paso 1: encendelo (`"catalogo_base": true`) y corré `oracle
test`. Te va a pedir lo que falta para que estas reglas valgan fuera de esta guía: declarar las unidades
de los campos y sostener cada regla con partidas **observadas**, no sólo con casos construidos.
```
- **Comando corrido**:
```bash
oracle test
```
(tras establecer `"catalogo_base": true` en `oracle.json`).
- **Salida obtenida**:
```text
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 33 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 11 medidas · 0 macros · 33 casos · 0 relaciones

catálogo: 52 medidas · corpus: 33 casos

  ROJO  001-tiro-fuera-de-tablero              naval.tiros_dentro_del_tablero  (valor 1)
  verde 002-tiro-valido                        naval.tiros_dentro_del_tablero  (valor 0)
  ROJO  003-mismo-tirador-seguido              naval.alternancia_turnos  (valor 1)
  verde 004-tiradores-alternos                 naval.alternancia_turnos  (valor 0)
  ROJO  005-barco-fila-desbordada              naval.barcos_dentro_del_tablero  (valor 1)
  verde 006-barco-en-borde                     naval.barcos_dentro_del_tablero  (valor 0)
  ROJO  007-barcos-superpuestos                naval.barcos_sin_solapamiento  (valor 1)
  verde 008-barcos-separados                   naval.barcos_sin_solapamiento  (valor 0)
  ROJO  009-tiro-despues-del-final             naval.fin_de_juego_sin_tiros_posteriores  (valor 1)
  verde 010-tiro-en-turno-final                naval.fin_de_juego_sin_tiros_posteriores  (valor 0)
  ROJO  011-flota-de-dieciseis                 naval.flota_reglamentaria  (valor 1)
  verde 012-flota-de-diecisiete                naval.flota_reglamentaria  (valor 0)
  ROJO  013-ganador-con-dieciseis-impactos     naval.ganador_legitimo  (valor 1)
  verde 014-ganador-con-diecisiete-impactos    naval.ganador_legitimo  (valor 0)
  ROJO  015-tiro-repetido                      naval.tiros_sin_repeticion  (valor 1)
  verde 016-tiros-distintos                    naval.tiros_sin_repeticion  (valor 0)
  ROJO  017-turno-saltado                      naval.turnos_sin_huecos  (valor 1)
  verde 018-turnos-contiguos                   naval.turnos_sin_huecos  (valor 0)
  ROJO  019-barco-reportado-como-agua          naval.veracidad_impacto_negativo  (valor 1)
  verde 020-agua-reportada-como-agua           naval.veracidad_impacto_negativo  (valor 0)
  ROJO  021-impacto-fantasma                   naval.veracidad_impacto_positivo  (valor 1)
  verde 022-impacto-real                       naval.veracidad_impacto_positivo  (valor 0)
  ROJO  023-columna-desbordada                 naval.tiros_dentro_del_tablero  (valor 1)
  ROJO  024-fila-negativa                      naval.tiros_dentro_del_tablero  (valor 1)
  ROJO  025-columna-negativa                   naval.tiros_dentro_del_tablero  (valor 1)
  ROJO  026-barco-columna-desbordada           naval.barcos_dentro_del_tablero  (valor 1)
  ROJO  027-barco-fila-negativa                naval.barcos_dentro_del_tablero  (valor 1)
  ROJO  028-barco-columna-negativa             naval.barcos_dentro_del_tablero  (valor 1)
  SIN EVIDENCIA 029-flota-sin-celdas          naval.flota_reglamentaria  («celda_barco» vacía)
  SIN EVIDENCIA 030-sin-tiros-registrados     naval.turnos_sin_huecos  («tiro» vacía)
  verde 031-distinta-fila-igual-turno-ajeno    naval.tiros_sin_repeticion  (valor 0)
  verde 032-agua-declarada-agua                naval.veracidad_impacto_positivo  (valor 0)
  verde 033-fila-confundida-con-turno          naval.tiros_sin_repeticion  (valor 0)

defectos que se pusieron rojos: 17 · verdes correctos: 14 · sin evidencia esperada: 2 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:
  ✓ meta.el_caso_reclama_una_medida_que_existe          0 (<= 0)
  ✓ meta.el_caso_se_pone_como_debe                      0 (<= 0)
  ✓ meta.el_hueco_declarado_explica_por_que             0 (<= 0)
  ✓ meta.el_nivel_no_se_confunde_con_el_dominio         0 (<= 0)
  ✓ meta.el_requisito_nombra_medidas_que_existen        0 (<= 0)
  ✗ meta.la_medida_no_se_fija_solo_con_evidencia_fabricada       11 (<= 0)
      → _={'medida': 'naval.tiros_dentro_del_tablero', 'casos': 5, 'no_observados': 5}; _={'medida': 'naval.alternancia_turnos', 'casos': 2, 'no_observados': 2}; _={'medida': 'naval.barcos_dentro_del_tablero', 'casos': 5, 'no_observados': 5} +8
  ✓ meta.ningun_campo_sin_unidad_declarada              0 (<= 0)
  ✓ meta.ningun_flotante_comparado_por_igualdad_en_un_filtro        0 (<= 0)
  ✓ meta.ningun_umbral_de_igualdad                      0 (<= 0)
  ✓ meta.ningun_umbral_flotante_de_igualdad             0 (<= 0)
  ✓ meta.ninguna_medida_sin_alcance                     0 (<= 0)
  ✓ meta.se_escribe_en_superficie                       0 (<= 0)
  ✗ meta.toda_cantidad_comparada_tiene_unidad_derivable       28 (<= 0)
      → c={'medida': 'naval.alternancia_turnos', 'unidad': 'sin_declarar', 'es_derivable': False}; c={'medida': 'naval.alternancia_turnos', 'unidad': 'sin_declarar', 'es_derivable': False}; c={'medida': 'naval.barcos_dentro_del_tablero', 'unidad': 'sin_declarar', 'es_derivable': False} +25
  ✓ meta.toda_medida_de_ausencia_declara_requiere        0 (<= 0)
  ✓ meta.toda_medida_declara_su_ambito                  0 (<= 0)
  ✓ meta.toda_medida_filtra_o_agrupa                    0 (<= 0)
  ✓ meta.toda_medida_lee_campos_que_existen             0 (<= 0)
  ✓ meta.todo_caso_observado_declara_de_donde_salio        0 (<= 0)
  ✓ meta.todo_tanteo_explica_por_que                    0 (<= 0)
  ✓ meta.todo_umbral_declara_de_donde_sale              0 (<= 0)

ACEPTACIÓN ✗ — 2 problema(s)
  · meta.la_medida_no_se_fija_solo_con_evidencia_fabricada: el marco no cumple su propia regla
  · meta.toda_cantidad_comparada_tiene_unidad_derivable: el marco no cumple su propia regla

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 209 · murieron 209 · sobrevivieron 0
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 158 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 51 rechazados por el álgebra sin evaluar
  respaldo real: 0 de 209 muertos los mata al menos un caso observado; 209 sólo los sostiene evidencia construida, generada, sin procedencia o diferencial
detecciones evaluadas (mutante × caso): 634

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ⊘ proceso.codigo_con_mutante_que_lo_mata       SIN EVIDENCIA («mutante con m.tipo == "codigo"» vacía; no se midió)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: ROJO (falló: aceptación)
```
- **Problema encontrado**: La salida confirma lo anticipado por la guía (falla por unidades no declaradas y evidencia sólo construida), pero la guía no proporciona ejemplos de sintaxis para declarar unidades ni explica cómo convertir evidencia en caso observado con trazabilidad formal.

---

## 3. Conclusiones

### ¿Se pudo armar el juego entero y llegar a juzgar una partida?

**Sí.** Se pudo construir el juego en su totalidad (`index.html`, `css/style.css`, `js/audio.js`, `js/trace.js`, `js/engine.js`, `js/ui.js`) a partir del material de la guía. Los 11 archivos de catálogo formal de reglas y los 33 casos de prueba del corpus se verificaron con `oracle test`, pasando todas las etapas de sintaxis, aceptación y mutación (`VEREDICTO: VERDE`). 

Asimismo, se ejecutó `oracle juzgar --con hechos_partida.json` y se obtuvo:
```text
✓ naval.alternancia_turnos                            0 (<= 0)
✓ naval.barcos_dentro_del_tablero                     0 (<= 0)
✓ naval.barcos_sin_solapamiento                       0 (<= 0)
✓ naval.fin_de_juego_sin_tiros_posteriores            0 (<= 0)
✓ naval.flota_reglamentaria                           0 (<= 0)
✓ naval.ganador_legitimo                              0 (<= 0)
✓ naval.tiros_dentro_del_tablero                      0 (<= 0)
✓ naval.tiros_sin_repeticion                          0 (<= 0)
✓ naval.turnos_sin_huecos                             0 (<= 0)
✓ naval.veracidad_impacto_negativo                    0 (<= 0)
✓ naval.veracidad_impacto_positivo                    0 (<= 0)

VEREDICTO: verde en 11 medidas. SIN MIRAR:
  · naval.alternancia_turnos: compara el tirador del turno k con el tirador del turno k+1. No valida la ausencia de saltos si falta un turno completo.
  · naval.barcos_dentro_del_tablero: revisa los límites de cada celda de barco reportada. No verifica solapamientos ni continuidad.
  · naval.barcos_sin_solapamiento: detecta pares de celdas distintas del mismo jugador con id1 < id2 que colisionan en la misma coordenada. No comprueba barcos de jugadores opuestos.
  · naval.fin_de_juego_sin_tiros_posteriores: compara el turno de cada tiro contra el turno final registrado en el estado de la partida. No valida si la partida debió terminar antes.
  · naval.flota_reglamentaria: agrupa las casillas de barco por jugador y exige exactamente 17 casillas por flota. No comprueba la orientación lineal de los barcos.
  · naval.ganador_legitimo: comprueba que los impactos acumulados por el ganador sean exactamente 17. No valida si los tiros fueron asignados al tirador correcto.
  · naval.tiros_dentro_del_tablero: comprueba que las coordenadas de cada disparo estén en el rango [0, 9]. No comprueba si el casillero ya fue disparado previamente ni la validez del turno.
  · naval.tiros_sin_repeticion: detecta disparos repetidos del mismo jugador a la misma celda con diferente número de turno. No evalúa si el tiro fue agua o impacto.
  · naval.turnos_sin_huecos: compara la cantidad total de tiros registrados contra el turno máximo reportado más uno. No valida la alternancia de tiradores.
  · naval.veracidad_impacto_negativo: cruza cada disparo contra las celdas de la flota rival y detecta impactos omitidos registrados falsamente como agua. No verifica la secuencia de turnos.
  · naval.veracidad_impacto_positivo: detecta disparos registrados como impacto que no corresponden a ninguna celda ocupada por la flota del receptor. No verifica si el barco ya estaba completamente hundido.
```
Adicionalmente, se simuló una partida completa utilizando directamente el motor del juego (`NavalGame` y `TraceRecorder`) y al auditar la traza generada con `oracle juzgar`, arrojó idéntico veredicto verde con las 11 medidas satisfechas.

---

### ¿Qué le faltó a la guía para alguien que empieza?

1. **Instrucciones explícitas de creación de directorios**: La guía asume que subdirectorios como `corpus/naval/` o `catalogos/naval/` ya existen o que el editor los crea de forma transparente. Alguien que trabaja en terminal necesita los comandos `mkdir -p catalogos/naval corpus/naval css js` explícitos.
2. **Instrucciones sobre cómo modificar archivos**: En el Paso 1 se pide apagar `"catalogo_base": false` en `oracle.json`, pero no se indica con qué herramienta abrir y editar el archivo si el principiante está en la consola.
3. **Alternativas para ejecutar/servir la web sin entorno gráfico**: La indicación de «doble clic o arrastralo a una pestaña» falla en servidores remotos o entornos containerizados; falta indicar cómo iniciar un servidor HTTP básico (`python3 -m http.server 8000`).
4. **Puente entre la descarga web y la consola**: Al descargar `hechos_partida.json` desde el navegador, el archivo queda en la carpeta del sistema de descargas del usuario; falta explicar cómo moverlo a la carpeta del proyecto donde se ejecuta `oracle juzgar`.
5. **Automatización o comando para los 26 casos del Paso 7**: La guía exige crear 26 archivos individuales a mano dentro de un bloque desplegable; para alguien nuevo, copiar y pegar 26 archivos distintos con nombres precisos es proclive a errores tipográficos.
6. **Explicación de scripts en línea**: En el Paso 8 se emplea un comando `python3 -c "import json; ..."` de una línea sin desglosarlo para alguien novato en programación.
