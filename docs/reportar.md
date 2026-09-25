# Reportar un límite

Cuando el lenguaje no alcanza para algo que necesitás medir, eso es un límite de Oracle y vale la
pena reportarlo. Oracle prepara el reporte en tu máquina: vos ves todo lo que saldría y decidís si lo
pegás en un issue público. El comando no publica nada, no usa la red y no recibe credenciales.

## Preparar, revisar, pegar

1. Desde el proyecto donde apareció el límite, corré `oracle reportar`.
2. Contá qué esperabas, qué ocurrió y cómo lo detectaste.
3. Leé el reporte completo que aparece en pantalla.
4. Abrí [la plantilla de reporte](https://github.com/Segtem/oracle/issues/new?template=reporte-de-limite.md) y pegá el reporte tal cual.

```bash
cd <tu-proyecto>
oracle reportar

# también se puede guardar una vista previa local
oracle reportar --salida reporte.md
```

La salida conserva la estructura de un caso del corpus: `sintoma`, `como_se_detecto` y
`diagnostico`. Si los pedís, suma la medida y la evidencia. Como esos nombres son los mismos de un
archivo `.caso`, el reporte ya queda listo para una reproducción posterior.

**Los datos de tu dominio quedan afuera por omisión.** `--incluir-medida` y `--incluir-evidencia`
son inclusiones explícitas. Oracle redacta las rutas que conoce, pero no puede reconocer secretos ni
datos privados dentro de tu prosa o de tu evidencia. Revisá todo antes de pegar: el issue es público.

## Qué significa abrirlo

El issue registra que alguien encontró un límite y deja un lugar donde reproducirlo. Todavía no es un
caso del corpus y no cambia ninguna medida. Tampoco promete diagnóstico, prioridad, fecha ni arreglo.

## Del issue a un caso del corpus

Pasar un reporte al corpus no es copiar el Markdown. Una persona responsable del repositorio hace
primero lo que Oracle no puede decidir: comprueba que el comportamiento se reproduce y sostiene que
lo esperado por el reporte es verdad para ese dominio. Después:

1. Reduce y reproduce el hallazgo en una versión identificable, con fecha, origen y una procedencia
   honesta: `observada`, `construida` o `generada`.
2. Convierte lo reproducido en evidencia: un mapa no vacío de relaciones a filas planas, con campos
   escalares. Una captura, un log libre o `evidencia: {}` todavía no son evidencia del corpus.
3. Elige la `etiqueta` que fija la polaridad esperada, redacta un solo `sintoma` con lo esperado y lo
   ocurrido, conserva `como_se_detecto` y escribe la `leccion` que el caso tiene que dejar fijada.
4. Nombra una medida existente, o usa `medida: null`. En ese caso declara `estado_sin_medida:
   abierto` y explica `sin_medida_todavia`: no se inventa un id que parezca plausible.
5. Crea el andamio con `oracle caso <grupo/NNN-descripcion>`, completa los campos y corre el
   verificador y la aceptación antes de proponer el archivo.

```bash
oracle caso <grupo/NNN-descripcion>
oracle-corpus --proyecto .
oracle-aceptacion --proyecto .
```

El verificador del corpus rechaza ids que no coinciden con el archivo, campos obligatorios
ausentes, vocabularios desconocidos, evidencia vacía o anidada y una medida nula sin estado ni
explicación. La aceptación comprueba además que la medida nombrada exista y que el caso tome la
polaridad declarada. Si se quiere afirmar que una medida quedó fijada, los casos fabricados no
alcanzan solos: la evidencia observada tiene que sostenerla.

**Si nadie puede reproducirlo, no se fabrica un caso.** El issue puede quedar como conversación o
cerrarse como no reproducible, pero queda fuera del corpus: no cambia sus conteos, no fija una medida
y no se vuelve una deuda prometida. Una reproducción posterior puede retomar el camino.
