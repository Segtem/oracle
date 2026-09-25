# De cero a un rojo con testigos

Cinco minutos, sin abrir el código de Oracle. Al final vas a tener una regla que **falla** sobre un
defecto de verdad y te dice **qué filas** lo causaron.

Todo lo que sigue está copiado de una corrida real con Oracle 0.30.0. Si algo no te da igual,
es un defecto de esta página: [abrí un issue](https://github.com/Segtem/oracle/issues).

---

## 1. Instalar

```bash paso
uv tool install oracle-metalenguaje
oracle --version
```

```text salida
oracle 0.31.0
  álgebra:  1.0   (qué SIGNIFICA una medida)
  sintaxis: 0.7   (cómo se ESCRIBE)
  corriendo desde: …/oracle
```


Tres versiones porque son tres contratos distintos, y envejecen por separado. La del paquete sube
cuando se arregla una herramienta; la del **álgebra** cuando cambia qué significa una medida; la de
la **sintaxis** cuando cambia cómo se escribe.

> **Por qué `uv` y no `pip`.** En Arch, Debian 12+, Ubuntu 23.04+ y Fedora, `pip install` al Python
> del sistema falla con `externally-managed-environment` (PEP 668). Con `pip` andá a un entorno
> propio: `python3 -m venv venv && source venv/bin/activate`. Pero para el editor eso **no
> alcanza**: los clientes de Emacs y VS Code buscan `oracle-lsp` en el `PATH`, y dentro de un venv
> sólo se ve con el venv activado.

## 2. Un proyecto

```bash paso
oracle init biblioteca
cd biblioteca
```

```text salida
Proyecto Oracle inicializado en ./biblioteca:
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

Cuatro carpetas y un archivo. `oracle.json` viene con `"catalogo_base": true`: tu proyecto hereda las
medidas universales de Oracle, que van a juzgar **tus** medidas.

Un proyecto vacío conserva código de salida `0` para CI, con una advertencia: todavía no hay
casos para verificar ni una medición del producto. No equivale a un corpus validado:

```bash paso
oracle test
```

```text salida
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

## 3. Una medida

```bash paso
oracle nueva documento.nombre_sigue_la_convencion
```

```text salida
creada: catalogos/documento/documento.nombre_sigue_la_convencion.oracle

casos de andamio: corpus/documento/001-nombre-sigue-la-convencion-rojo.caso y corpus/documento/002-nombre-sigue-la-convencion-verde.caso
Reemplazá RELACION, CAMPO, SEGUN, AMBITO y los dos textos en MAYÚSCULAS. Después:
  oracle revisar catalogos/documento/documento.nombre_sigue_la_convencion.oracle
Completá ambos casos con evidencia que ejerza la medida y quitá la marca ANDAMIO.
```

La plantilla viene con los huecos en mayúsculas. `oracle nueva` también crea dos casos de andamio (rojo y verde) para completar; los quitamos después de mostrar el diagnóstico de la medida vacía y escribimos dos casos con nombres más descriptivos:

```
ninguno documento.nombre_sigue_la_convencion:
    de RELACION x
    donde x.CAMPO == false
    # Si medís una magnitud (días, cm, segundos), consultá `oracle manual peor`:
    # su tolerancia es la cota del dominio; `ninguno` cuenta defectos y exige cero.
    # segun: medicion · contrato · convencion · tanteo
    umbral <= 0 segun SEGUN porque "POR QUE ese numero y no otro…"
    # ambito: universal · del_origen
    ambito AMBITO
    alcance "QUE NO VE esta medida…"
```

Si la revisás sin tocarla, el error te dice dónde y con qué opciones:

```bash paso
oracle revisar catalogos/documento/documento.nombre_sigue_la_convencion.oracle
```

```text salida
✗ catalogos/documento/documento.nombre_sigue_la_convencion.oracle: línea 7, columna 23: se esperaba segun en ['contrato', 'convencion', 'medicion', 'tanteo']; llegó 'SEGUN'
   7 |     umbral <= 0 segun SEGUN porque "POR QUE ese numero y no otro. Si SEGUN es tanteo, esta explicacion es obligatoria."
     |                       ^
```

Completala así:

```oracle archivo=catalogos/documento/documento.nombre_sigue_la_convencion.oracle incluir=ejemplo/biblioteca-guia/catalogos/documento/documento.nombre_sigue_la_convencion.oracle
```

**`segun` no es decoración.** Dice de dónde salió el número, de un conjunto cerrado. Acá es
`contrato` porque el cero no se midió: es una regla que alguien decidió. Si fuera un umbral puesto
a ojo sería `tanteo`, y entonces la explicación pasa a ser obligatoria.

**`alcance` tampoco.** Es qué NO mira. Sin eso, un verde se lee como «está todo bien» cuando en
realidad significa «está bien lo poco que miré».

```bash paso
rm -f corpus/documento/001-nombre-sigue-la-convencion-rojo.caso
rm -f corpus/documento/002-nombre-sigue-la-convencion-verde.caso
oracle revisar catalogos/documento/documento.nombre_sigue_la_convencion.oracle
```

```text salida
✓ bien declarada: documento.nombre_sigue_la_convencion   (forma: ninguno)
    umbral   <= 0
    segun    contrato
    porque   la convención de nombres es lo que hace que el índice se pueda generar solo; un archivo fuera de convención lo rompe
    alcance  no ve el contenido del documento, sólo su nombre; y no juzga si la convención en sí es buena

contra la evidencia que hay: 0 verde · 0 rojo · 0 error

⚠ nunca se pone roja. Una medida que no puede fallar no mide nada — hace falta
  evidencia donde el defecto exista. Agregá un caso al corpus con esa evidencia.
```

Está bien declarada **y la herramienta te avisa que todavía no sirve**. Es la primera vez que vas a
ver la tesis del proyecto: una regla que nada puede romper es decoración.

## 4. El rojo, sin escribir todavía un caso

```bash paso
oracle medida probar catalogos/documento/documento.nombre_sigue_la_convencion.oracle --con 'documento: nombre, sigue_convencion
    "2026-08-31-GUIA-Convencion-v1.0.md", true
    "notas finales.md", false'
```

```text salida
ROJO   valor 1  (<= 0)

  testigos (1) — las filas que ofenden, no un resumen:
    {'d': {'nombre': 'notas finales.md', 'sigue_convencion': False}}

  alcance: no ve el contenido del documento, sólo su nombre; y no juzga si la convención en sí es buena
```

**Eso es un rojo de Oracle.** No dice «falló la verificación»: dice el valor medido (`1`), contra
qué se lo comparó (`<= 0`), **qué fila exacta lo produjo**, y qué no estaba mirando.

Un rojo sin testigos te obliga a creerle. Con testigos se puede discutir — y a veces la equivocada
resulta ser la medida.

## 5. Los dos casos

Un caso es evidencia guardada que **pone a prueba la medida**.

```bash paso
oracle caso documento/001-un-nombre-fuera-de-convencion
```

```text salida
creado: corpus/documento/001-un-nombre-fuera-de-convencion.caso

Ya completos, leídos del repositorio: fecha.
Reemplazá los marcadores en MAYÚSCULAS. Tres campos tienen valores cerrados:

  etiqueta:         deuda_de_diseño · falso_rojo · falso_verde · medida_correcta_conclusion_errada · verde_correcto
  procedencia:      construida · generada · observada
  como_se_detecto:  accidente · herramienta_ajena · mutacion · observacion · persona

Consultá `oracle manual etiqueta` para conocer la polaridad esperada de cada etiqueta.
Después:  oracle test
```

Escribí **dos**, uno de cada polaridad:

```caso archivo=corpus/documento/001-un-nombre-fuera-de-convencion.caso incluir=ejemplo/biblioteca-guia/corpus/documento/001-un-nombre-fuera-de-convencion.caso
```

Guardá el segundo caso en `corpus/documento/002-un-lote-en-convencion.caso`:

```caso archivo=corpus/documento/002-un-lote-en-convencion.caso incluir=ejemplo/biblioteca-guia/corpus/documento/002-un-lote-en-convencion.caso
```

**Los dos hacen falta, y no por simetría.** Sin el rojo, la medida nunca falla. Sin el verde, el
mutador que le *quita el filtro* sobrevive: una medida sin `donde` marca todo, y si nunca viste un
caso donde no debía marcar nada, no lo notás.

## 6. El ciclo completo

```bash paso
oracle test
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 2 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 2 casos

catálogo: 40 medidas · corpus: 2 casos

  ROJO  001-un-nombre-fuera-de-convencion      documento.nombre_sigue_la_convencion  (valor 1)
  verde 002-un-lote-en-convencion              documento.nombre_sigue_la_convencion  (valor 0)

defectos que se pusieron rojos: 1 · verdes correctos: 1 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:
  ✓ meta.el_caso_reclama_una_medida_que_existe          0 (<= 0)
  ✓ meta.el_caso_se_pone_como_debe                      0 (<= 0)
  ✓ meta.el_hueco_declarado_explica_por_que             0 (<= 0)
  ✓ meta.el_nivel_no_se_confunde_con_el_dominio         0 (<= 0)
  ✗ meta.la_medida_no_se_fija_solo_con_evidencia_fabricada        1 (<= 0)
      → _={'medida': 'documento.nombre_sigue_la_convencion', 'casos': 2, 'no_observados': 2}
  ✓ meta.ningun_campo_sin_unidad_declarada              0 (<= 0)
  ✓ meta.ningun_flotante_comparado_por_igualdad_en_un_filtro        0 (<= 0)
  ✓ meta.ningun_umbral_de_igualdad                      0 (<= 0)
  ✓ meta.ningun_umbral_flotante_de_igualdad             0 (<= 0)
  ✓ meta.ninguna_medida_sin_alcance                     0 (<= 0)
  ✗ meta.toda_cantidad_comparada_tiene_unidad_derivable        1 (<= 0)
      → c={'medida': 'documento.nombre_sigue_la_convencion', 'unidad': 'sin_declarar', 'es_derivable': False}
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

mutantes de medida (medida × mutador): 9 · murieron 9 · sobrevivieron 0
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 9 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 18

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

**Los nueve mutantes son el punto.** Oracle rompió tu medida de nueve maneras distintas —le sacó el
filtro, le aflojó el umbral, le dio vuelta un comparador— y comprobó que tus dos casos lo notaran.
Los nueve murieron: tus casos la fijan.

Pero la aceptación queda en rojo, y hay que leerlo:

```
  ✗ meta.la_medida_no_se_fija_solo_con_evidencia_fabricada   1 (<= 0)
  ✗ meta.toda_cantidad_comparada_tiene_unidad_derivable      1 (<= 0)
```

Ésas no son tus medidas: son las universales que heredaste, juzgándote.

## 7. Declarar el sensor (L−1)

La segunda dice que comparaste un campo cuya **unidad** nadie declaró. Falta decir qué produce el
sensor:

```json archivo=relaciones/documento.json incluir=ejemplo/biblioteca-guia/relaciones/documento.json
```

En `relaciones/documento.json`. Fijate que **la relación también declara su alcance**: la medida
dice qué no mira, el sensor dice hasta dónde llega.
 
```bash paso
oracle relaciones
```

```text salida
RELACIONES que se pueden medir hoy:

  documento
      nombre                       str
      sigue_convencion             bool
      · aparece en: 001-un-nombre-fuera-de-convencion, 002-un-lote-en-convencion

Un hecho nuevo se agrega desde su SENSOR, no acá: el sensor produce, el álgebra juzga.
```

Con eso, ese rojo se cierra. Si en cualquier momento querés ver las relaciones,
campos, escalares y medidas de tu proyecto en una sola salida, `oracle contexto`
(o `oracle contexto --compacto`) reúne todo en un solo lugar.

## 8. El rojo que queda, y por qué está bien

```
  ✗ meta.la_medida_no_se_fija_solo_con_evidencia_fabricada   1 (<= 0)
```

Tus dos casos declaran `procedencia: construida` — los escribiste a mano. Y eso es cierto: nunca
corriste un sensor sobre una biblioteca real.

**Oracle acaba de atraparte inventando evidencia**, en un proyecto de cinco minutos. No es un falso
positivo: es la diferencia entre «probé que mi regla funciona sobre casos que yo mismo diseñé» y
«probé que atrapa algo que pasó de verdad».

Para cerrarlo hace falta evidencia `observada`: correr un sensor sobre documentos reales y guardar
lo que devolvió. Hasta entonces el rojo es honesto y conviene dejarlo a la vista.

---

## Qué sigue

- [Por qué la mutación](05-por-que-la-mutacion.md) — dos autores, 30 mutadores en aislamiento y qué hacer
  cuando uno sobrevive.
- [Conectar Oracle a un proyecto propio](07-conectar-a-un-proyecto-propio.md) — de dónde sale la
  evidencia `observada`, migración a PyPI y la sombra.
- [docs/03-escribir-una-medida.md](03-escribir-una-medida.md) — la guía de autoría con `oracle contexto`.
- `oracle manual` — la referencia del lenguaje en la terminal (con `oracle manual medidas` para
  las 54 universales y sus puntos ciegos).
- [El editor](../editores/README.md) — diagnósticos, completado con unidades y CodeLens en Emacs y
  VS Code.
- [ESPECIFICACION.md](../ESPECIFICACION.md) — la referencia formal del lenguaje.
