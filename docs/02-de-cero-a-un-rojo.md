# De cero a un rojo con testigos

Cinco minutos, sin abrir el código de Oracle. Al final vas a tener una regla que **falla** sobre un
defecto de verdad y te dice **qué filas** lo causaron.

Todo lo que sigue está copiado de una corrida real con Oracle 0.5.0. Si algo no te da igual,
es un defecto de esta página: [abrí un issue](https://github.com/Segtem/oracle/issues).

---

## 1. Instalar

```bash
uv tool install oracle-metalenguaje
```

```
$ oracle --version
oracle 0.5.0
  álgebra:  0.6   (qué SIGNIFICA una medida)
  sintaxis: 0.2   (cómo se ESCRIBE)
  corriendo desde: …/oracle-metalenguaje/lib/python3.12/site-packages/oracle_metalenguaje
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

```
$ oracle init biblioteca
Proyecto Oracle inicializado en …/biblioteca:
  · catalogos/
  · corpus/
  · diferencial/
  · oracle.json

Próximos pasos:
  1. Creá una medida:  oracle nueva <dominio.nombre>
  2. Creá un caso:     oracle caso <grupo/id>
  3. Verificá todo:    oracle test
```

Tres carpetas y un archivo. `oracle.json` viene con `"catalogo_base": true`: tu proyecto hereda las
medidas universales de Oracle, que van a juzgar **tus** medidas.

Un proyecto vacío pasa, y lo dice sin disimular:

```
$ oracle test
VEREDICTO: VERDE (proyecto vacío: 0 medidas, 0 casos)
```

## 3. Una medida

```
$ oracle nueva documento.nombre_sigue_la_convencion
creada: catalogos/documento/documento.nombre_sigue_la_convencion.oracle
```

La plantilla viene con los huecos en mayúsculas:

```
ninguno documento.nombre_sigue_la_convencion:
    de RELACION x
    donde x.CAMPO == false
    # segun: medicion · contrato · convencion · tanteo
    umbral <= 0 segun SEGUN porque "POR QUE ese numero y no otro…"
    alcance "QUE NO VE esta medida…"
```

Si la revisás sin tocarla, el error te dice dónde y con qué opciones:

```
$ oracle revisar catalogos/documento/documento.nombre_sigue_la_convencion.oracle
✗ línea 5, columna 23: se esperaba segun en ['contrato', 'convencion', 'medicion', 'tanteo']; llegó 'SEGUN'
   5 |     umbral <= 0 segun SEGUN porque "POR QUE ese numero…"
     |                       ^
```

Completala así:

```
ninguno documento.nombre_sigue_la_convencion:
    de documento d
    donde d.sigue_convencion == false
    umbral <= 0 segun contrato porque "la convención de nombres es lo que hace que el índice se pueda generar solo; un archivo fuera de convención lo rompe"
    alcance "no ve el contenido del documento, sólo su nombre; y no juzga si la convención en sí es buena"
```

**`segun` no es decoración.** Dice de dónde salió el número, de un conjunto cerrado. Acá es
`contrato` porque el cero no se midió: es una regla que alguien decidió. Si fuera un umbral puesto
a ojo sería `tanteo`, y entonces la explicación pasa a ser obligatoria.

**`alcance` tampoco.** Es qué NO mira. Sin eso, un verde se lee como «está todo bien» cuando en
realidad significa «está bien lo poco que miré».

```
$ oracle revisar catalogos/documento/documento.nombre_sigue_la_convencion.oracle
✓ bien declarada: documento.nombre_sigue_la_convencion   (forma: ninguno)
    umbral   <= 0
    segun    contrato
    porque   la convención de nombres es lo que hace que el índice se pueda generar solo…
    alcance  no ve el contenido del documento, sólo su nombre…

contra la evidencia que hay: 0 verde · 0 rojo · 0 error

⚠ nunca se pone roja. Una medida que no puede fallar no mide nada — hace falta
  evidencia donde el defecto exista. Agregá un caso al corpus con esa evidencia.
```

Está bien declarada **y la herramienta te avisa que todavía no sirve**. Es la primera vez que vas a
ver la tesis del proyecto: una regla que nada puede romper es decoración.

## 4. El rojo, sin escribir todavía un caso

```
$ oracle medida probar catalogos/documento/documento.nombre_sigue_la_convencion.oracle \
      --con 'documento: nombre, sigue_convencion
    "2026-08-31-GUIA-Convencion-v1.0.md", true
    "notas finales.md", false'
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

```
$ oracle caso documento/001-un-nombre-fuera-de-convencion
creado: corpus/documento/001-un-nombre-fuera-de-convencion.caso

Ya completos, leídos del repositorio: fecha.
Reemplazá los marcadores en MAYÚSCULAS. Tres campos tienen valores cerrados:

  etiqueta:         deuda_de_diseño · falso_rojo · falso_verde · medida_correcta_conclusion_errada · verde_correcto
  procedencia:      construida · generada · observada
  como_se_detecto:  accidente · herramienta_ajena · mutacion · observacion · persona
```

Escribí **dos**, uno de cada polaridad:

```
caso 001-un-nombre-fuera-de-convencion:
    …
    etiqueta: falso_verde
    medida: documento.nombre_sigue_la_convencion
    evidencia:
        documento: nombre, sigue_convencion
            "notas finales.md", false
```

```
caso 002-un-lote-en-convencion:
    …
    etiqueta: verde_correcto
    evidencia:
        documento: nombre, sigue_convencion
            "2026-08-31-GUIA-Convencion-v1.0.md", true
            "2026-09-01-INFORME-Primera-Medida-v1.0.md", true
```

**Los dos hacen falta, y no por simetría.** Sin el rojo, la medida nunca falla. Sin el verde, el
mutador que le *quita el filtro* sobrevive: una medida sin `donde` marca todo, y si nunca viste un
caso donde no debía marcar nada, no lo notás.

## 6. El ciclo completo

```
$ oracle test
CORPUS OK · 2 casos · esquema, evidencia L0 y trazabilidad en regla

  ROJO  001-un-nombre-fuera-de-convencion  documento.nombre_sigue_la_convencion  (valor 1)
  verde 002-un-lote-en-convencion          documento.nombre_sigue_la_convencion  (valor 0)

mutantes de medida (medida × mutador): 7 · murieron 7 · sobrevivieron 0
detecciones evaluadas (mutante × caso): 14

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada        0 (<= 0)
  ✓ meta.toda_medida_esta_fijada            0 (<= 0)
  ✓ proceso.test_con_mutante_que_lo_mata    0 (<= 0)
```

**Los siete mutantes son el punto.** Oracle rompió tu medida de siete maneras distintas —le sacó el
filtro, le aflojó el umbral, le dio vuelta un comparador— y comprobó que tus dos casos lo notaran.
Los siete murieron: tus casos la fijan.

Pero la aceptación queda en rojo, y hay que leerlo:

```
  ✗ meta.la_medida_no_se_fija_solo_con_evidencia_fabricada   1 (<= 0)
  ✗ meta.toda_cantidad_comparada_tiene_unidad_derivable      1 (<= 0)
```

Ésas no son tus medidas: son las universales que heredaste, juzgándote.

## 7. Declarar el sensor (L−1)

La segunda dice que comparaste un campo cuya **unidad** nadie declaró. Falta decir qué produce el
sensor:

```json
["relacion", "documento",
 ["campos",
  ["campo", "nombre", "texto", "sin_unidad"],
  ["campo", "sigue_convencion", "booleano", "sin_unidad"]],
 ["alcance", "el sensor lee el NOMBRE del archivo y nada más: no abre el documento, no mira su contenido ni su fecha de modificación"]]
```

En `relaciones/documento.json`. Fijate que **la relación también declara su alcance**: la medida
dice qué no mira, el sensor dice hasta dónde llega.
 
```
$ oracle relaciones
RELACIONES que se pueden medir hoy:

  documento
      nombre                       str
      sigue_convencion             bool
      · aparece en: 001-un-nombre-fuera-de-convencion, 002-un-lote-en-convencion
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

- [Por qué la mutación](05-por-que-la-mutacion.md) — dos autores, 28 mutadores en aislamiento y qué hacer
  cuando uno sobrevive.
- [Conectar Oracle a un proyecto propio](07-conectar-a-un-proyecto-propio.md) — de dónde sale la
  evidencia `observada`, migración a PyPI y la sombra.
- [ESCRIBIR-UNA-MEDIDA.md](../ESCRIBIR-UNA-MEDIDA.md) — la guía de autoría con `oracle contexto`.
- `oracle manual` — la referencia del lenguaje en la terminal (con `oracle manual medidas` para
  las 54 universales y sus puntos ciegos).
- [El editor](../editores/README.md) — diagnósticos, completado con unidades y CodeLens en Emacs y
  VS Code.
- [ESPECIFICACION.md](../ESPECIFICACION.md) — la referencia formal del lenguaje.
