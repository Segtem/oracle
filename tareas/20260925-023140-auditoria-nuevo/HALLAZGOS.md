# Auditoría de Experiencia de Inicio en Oracle (PyPI: oracle-metalenguaje)

Esta auditoría documenta cada punto de fricción, inconsistencia o bloqueo que experimenta un usuario nuevo (humano o modelo de lenguaje) que instala Oracle vía PyPI (`pip install oracle-metalenguaje`) y recorre el flujo básico: `oracle --help`, `oracle init`, redacción de la primera medida (`docs/02-de-cero-a-un-rojo.md`, `docs/03-escribir-una-medida.md`, `docs/13-primer-valor.md`), creación del primer caso, `oracle test`, `oracle juzgar` y el tracker de tareas (`oracle tarea`).

Cada hallazgo referencia el archivo y las líneas exactas inspeccionadas en el código y la documentación, y propone la forma más chica y quirúrgica de resolverlo.

---

## 1. Descubrimiento y Ayuda General (`oracle --help`)

### Hallazgo 1: `oracle --help` omite el comando `oracle manual`
- **Ubicación**: `tools/cli.py:112-156` (función `ayuda()`) frente a `tools/cli.py:46-58` (docstring del módulo) y `tools/manual.py:1-510`.
- **Problema**: La función `ayuda()` lista los comandos principales (`init`, `proyecto`, `medida`, `corpus`, `juzgar`, `test`, `mutar`, `tarea`) y atajos comunes, pero omite por completo `oracle manual [tema]`. A pesar de que la documentación (`docs/02-de-cero-a-un-rojo.md:272`, `docs/03-escribir-una-medida.md:299-304`) y el docstring de `tools/cli.py` presentan el manual integrado como la herramienta de referencia de primer orden, quien ejecuta `oracle --help` nunca se entera de su existencia.
- **Impacto**: Un usuario o agente LLM que explora el CLI a través de `--help` no descubre el manual ni los vocabularios cerrados (`etiqueta`, `operador`, `origen_umbral`, `procedencia`), recurriendo a adivinar la sintaxis.
- **Forma más chica de arreglarlo**: En `tools/cli.py:125`, agregar a la lista de comandos de `ayuda()`:
  ```python
  "  oracle manual         manual integrado y vocabularios",
  ```

### Hallazgo 2: `oracle --help` y `oracle proyecto --help` omiten `oracle contexto`
- **Ubicación**: `tools/cli.py:119`, `tools/cli.py:128-142`, `tools/cli.py:180-188` frente a `docs/03-escribir-una-medida.md:63-95` y `tools/cli.py:656-692`.
- **Problema**: `docs/03:63-64` y `75-95` define `oracle contexto` como la herramienta obligatoria para que el autor conozca el inventario de relaciones, campos y medidas activas antes de redactar una nueva medida. Sin embargo, `oracle contexto` no figura ni en la lista de comandos ni en los atajos de `ayuda()`, ni tampoco en `ayuda_proyecto()`.
- **Impacto**: El usuario no encuentra en el CLI el comando clave que la guía le pide usar para inspeccionar el estado del proyecto.
- **Forma más chica de arreglarlo**: Agregar `"  oracle contexto       inventario de relaciones y medidas activas"` en la lista de comandos/atajos de `tools/cli.py:119` y en `tools/cli.py:186`.

### Hallazgo 3: `oracle medida` omite el verbo `probar` en el resumen de `ayuda()`
- **Ubicación**: `tools/cli.py:116` frente a `tools/cli.py:380` y `tools/medida.py:380-450`.
- **Problema**: En `tools/cli.py:116`, la ayuda general resume: `oracle medida         (nueva, revisar, listar, expandir)`. Omite el subcomando `probar`, el cual está plenamente implementado (`oracle medida probar <archivo> --datos <json>`).
- **Impacto**: El usuario asume que no existe una forma de evaluar una medida unitariamente contra datos directos sin correr la suite completa o crear un caso de corpus.
- **Forma más chica de arreglarlo**: En `tools/cli.py:116`, reemplazar por:
  ```python
  "  oracle medida         gestión de medidas (nueva, revisar, probar, listar, expandir)",
  ```

### Hallazgo 4: `oracle test --help` ejecuta la suite de tests en lugar de mostrar ayuda
- **Ubicación**: `tools/cli.py:1085-1104` frente a `nucleo/proyecto.py:610-662` y `tools/cli.py:1188`.
- **Problema**: En `tools/cli.py:1085`, `cmd_test(argv)` no intercepta los flags `-h` o `--help`. Llama directamente a `resolver(argv)`. Si el usuario corre `oracle test --help` fuera de la raíz de un proyecto, la ejecución aborta con un error de proyecto inválido. Si lo corre dentro de un proyecto, ¡ejecuta todos los tests de punta a punta!
- **Impacto**: Cualquier humano o LLM que intente ver los flags disponibles para `test` (como `--solo`, `--fallas`, `--resumen`, `--formato`) termina corriendo toda la suite inadvertidamente.
- **Forma más chica de arreglarlo**: En `tools/cli.py:1085`, agregar al inicio de `cmd_test`:
  ```python
  if "-h" in argv or "--help" in argv:
      imprimir("USO: oracle test [--solo PATRÓN] [--fallas] [--resumen] [--formato FORMATO]")
      return 0
  ```

---

## 2. Inicialización de Proyecto (`oracle init`)

### Hallazgo 5: Orden contradictorio entre el mensaje de éxito de `oracle init` y la guía metodológica
- **Ubicación**: `tools/cli.py:590-594` frente a `docs/03-escribir-una-medida.md:48-56` y `tools/cli.py:908-910`.
- **Problema**: Al completar la inicialización, `tools/cli.py:590-594` imprime:
  ```text
  Próximos pasos:
    1. Creá una medida:  oracle medida nueva <nombre>
    2. Creá un caso:     oracle caso nuevo <nombre>
    3. Verificá todo:    oracle test
  ```
  Sin embargo, `docs/03:48` titula enfáticamente: *«El orden importa: primero el caso, después la medida»*. Peor aún: si el usuario sigue al pie de la letra el paso 1 de `oracle init` (crea una medida) y de inmediato ejecuta `oracle test`, la suite falla en rojo con:
  `ACEPTACIÓN ✗ — sin casos en el corpus (escribí al menos un caso con etiqueta para cada medida)` (`tools/cli.py:908-910`).
- **Impacto**: El primer paso que sugiere la propia herramienta conduce directamente a un error de validación evitable.
- **Forma más chica de arreglarlo**: En `tools/cli.py:591-593`, invertir el orden de los pasos sugeridos:
  ```python
  "  1. Creá un caso:     oracle caso nuevo <nombre>",
  "  2. Creá una medida:  oracle medida nueva <nombre>",
  "  3. Verificá todo:    oracle test",
  ```

### Hallazgo 6: `oracle init` no crea la carpeta `relaciones/` requerida por la documentación
- **Ubicación**: `tools/cli.py:558-566` frente a `docs/02-de-cero-a-un-rojo.md:217-232`.
- **Problema**: `cmd_init` crea `catalogos/`, `corpus/` y `diferencial/`, pero no crea `relaciones/`. En la sección 7 de `docs/02` (*«Declarar el sensor en relaciones/documento.json»*), se pide crear un archivo JSON dentro de `relaciones/`. Si el usuario hace `cat > relaciones/documento.json` o un editor intenta guardarlo, falla porque el directorio no existe.
- **Impacto**: Fricción innecesaria durante la guía paso a paso donde el usuario debe detenerse a diagnosticar por qué no puede guardar el sensor.
- **Forma más chica de arreglarlo**: En `tools/cli.py:566`, agregar:
  ```python
  (raiz / "relaciones").mkdir(exist_ok=True)
  ```

### Hallazgo 7: Mensaje críptico de "autocertificación" si se invoca `oracle test` o `juzgar` fuera de un proyecto
- **Ubicación**: `nucleo/proyecto.py:657-660`.
- **Problema**: Cuando `resolver()` no encuentra un `oracle.json` ni una carpeta `catalogos/`, emite:
  `PROYECTO INVÁLIDO — esta instalación no incluye el proyecto de autocertificación; indicá --proyecto RUTA`.
  Este mensaje asume el entorno interno de desarrollo de Oracle (donde el proyecto por defecto es el propio compilador), pero carece por completo de sentido para un usuario de PyPI que ejecutó `oracle test` en una carpeta vacía o en su proyecto sin inicializar.
- **Impacto**: El usuario de PyPI cree que la instalación de pip está rota ("no incluye autocertificación") en lugar de entender que debe ejecutar `oracle init`.
- **Forma más chica de arreglarlo**: En `nucleo/proyecto.py:658-660`, cambiar el texto de error cuando `raiz is None`:
  ```python
  "no se encontró un proyecto de Oracle en el directorio actual (falta catalogos/); "
  "ejecutá 'oracle init' para inicializarlo o indicá --proyecto RUTA"
  ```

---

## 3. Redacción de la Primera Medida (`oracle medida`, `docs/02`, `docs/03`)

### Hallazgo 8: Desincronización crítica entre la plantilla de medida de `docs/02` y la plantilla real de `oracle medida nueva`
- **Ubicación**: `docs/02-de-cero-a-un-rojo.md:71-78, 84` frente a `tools/medida.py:59-70` y `nucleo/sintaxis.py:605-621`.
- **Problema**:
  1. `docs/02:71-78` muestra un bloque de medida sin el campo `ambito AMBITO`. En cambio, la plantilla real generada por `oracle medida nueva` (`tools/medida.py:68`) incluye obligatoriamente `ambito AMBITO`.
  2. Si el usuario copia el bloque de `docs/02` y luego corre `oracle revisar`, el parser falla exigiendo `ambito`. Si usa la plantilla de `oracle medida nueva` pero sigue `docs/02` (que nunca explica qué poner en `ambito`), deja el marcador `AMBITO`, fallando con: `se esperaba un ámbito entre estas opciones: unidad, integracion, sistema, contrato, aceptacion` (`nucleo/sintaxis.py:614-617`).
  3. Además, `docs/02:84` afirma que el error en `segun` saldrá en la *línea 5*. Pero en la plantilla real de `tools/medida.py:59-70`, `peor SEGUN` está en la *línea 7* debido a los comentarios de ayuda al inicio de la plantilla.
- **Impacto**: Quien sigue la guía paso a paso encuentra discrepancias inmediatas entre lo que lee en el tutorial y lo que produce el código.
- **Forma más chica de arreglarlo**:
  - En `docs/02-de-cero-a-un-rojo.md:71-78`, agregar `ambito unidad` a la medida de ejemplo.
  - En `docs/02-de-cero-a-un-rojo.md:84`, corregir el número de línea de la explicación.

### Hallazgo 9: El mensaje de ayuda de `oracle medida nueva` omite mencionar los marcadores `SEGUN` y `AMBITO`
- **Ubicación**: `tools/medida.py:287`.
- **Problema**: Al crear una medida con `oracle medida nueva`, el CLI imprime:
  `Reemplazá RELACION, CAMPO y los dos textos en MAYÚSCULAS.`
  Sin embargo, la plantilla contiene cuatro marcadores en mayúsculas: `RELACION`, `CAMPO`, `SEGUN` y `AMBITO`, además de `MENSAJE CUANDO SUPERA EL UMBRAL` y `DESCRIPCIÓN DE LA MEDIDA`. Olvidar reemplazar `SEGUN` o `AMBITO` provoca que `oracle revisar` falle inmediatamente por vocabulario no reconocido.
- **Impacto**: Instrucción incompleta que induce a error sintáctico inmediato.
- **Forma más chica de arreglarlo**: En `tools/medida.py:287`, actualizar la cadena a:
  ```python
  "Reemplazá RELACION, CAMPO, SEGUN, AMBITO y los dos textos en MAYÚSCULAS."
  ```

### Hallazgo 10: `oracle manual ambito` arroja error de tema desconocido pese a ser un vocabulario cerrado obligatorio
- **Ubicación**: `nucleo/vocabulario.py:55-60` frente a `tools/manual.py:40-47` y `tools/manual.py:270-281`.
- **Problema**: El campo `ambito` es obligatorio en toda medida sintácticamente válida (`nucleo/sintaxis.py:605-621`) y está restringido al vocabulario cerrado `AMBITOS` (`nucleo/vocabulario.py:57`: `("unidad", "integracion", "sistema", "contrato", "aceptacion")`). Sin embargo, en `tools/manual.py:40-47`, `VOCABULARIOS` registra `etiqueta`, `operador`, `origen_umbral` y `procedencia`, pero NO incluye `ambito`. Si un usuario intenta consultar las opciones válidas con `oracle manual ambito`, el comando responde:
  `tema desconocido: 'ambito'. Temas disponibles: etiqueta, operador, origen_umbral, procedencia.`
- **Impacto**: El comando diseñado para explicar los vocabularios cerrados desconoce uno de los vocabularios más frecuentes y obligatorios.
- **Forma más chica de arreglarlo**: En `tools/manual.py:40-47`, agregar a `VOCABULARIOS`:
  ```python
  "ambito": ("dónde obliga una medida (campo `ambito`)", AMBITOS),
  ```
  e importar `AMBITOS` desde `nucleo.vocabulario`.

### Hallazgo 11: `docs/03` remite a scripts internos de desarrollo inexistentes en una instalación de PyPI
- **Ubicación**: `docs/03-escribir-una-medida.md:105-106` frente a `pyproject.toml:50-53` y `tools/cli.py:695-704`.
- **Problema**: En la sección *«Inspección sintáctica»*, `docs/03:105-106` instruye:
  ```bash
  python tools/sintaxis.py --imprimir <archivo.oracle>
  python tools/sintaxis.py --leer <archivo.oracle>
  ```
  En una instalación estándar desde PyPI, no existe el directorio `tools/` ni el archivo `sintaxis.py`. El comando formal empaquetado para inspeccionar o convertir la sintaxis es `oracle convertir <archivo>`.
- **Impacto**: Un usuario que sigue la documentación oficial de autoría de medidas se encuentra con `No such file or directory: tools/sintaxis.py`.
- **Forma más chica de arreglarlo**: Reemplazar en `docs/03-escribir-una-medida.md:105-106` la referencia a `python tools/sintaxis.py` por:
  ```bash
  oracle convertir <archivo.oracle>
  ```

---

## 4. Creación del Primer Caso de Prueba (`oracle corpus`, `oracle caso`)

### Hallazgo 12: La plantilla de caso generada por `oracle caso nuevo` tiene el campo `procedencia:` comentado
- **Ubicación**: `tools/corpus.py:59` y `tools/corpus.py:164` frente a `nucleo/marco.py:294` y `catalogos/meta/meta.la_medida_no_se_fija_solo_con_evidencia_fabricada.oracle:1-12`.
- **Problema**: Al invocar `oracle caso nuevo foo`, la plantilla generada (`tools/corpus.py:59`) tiene comentada la procedencia:
  ```yaml
  caso foo:
    etiqueta ETIQUETA
    # procedencia: observacion | inspeccion | sintesis | perturbacion | fabricacion
  ```
  Pero en `tools/corpus.py:164`, el mensaje de éxito instruye:
  `Reemplazá NOMBRE, ETIQUETA y PROCEDENCIA con los valores de tu caso.`
  Si el usuario no descomenta la línea, el parser de casos le asigna por omisión `"sin_declarar"` (`nucleo/marco.py:294`). Al ejecutar `oracle test`, la medida meta `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` o la inspección de corpus falla con advertencias o errores sobre procedencia no declarada.
- **Impacto**: Ambigüedad en la plantilla entre lo que está comentado como ejemplo opcional y lo que el comando y las medidas meta exigen completar.
- **Forma más chica de arreglarlo**: En `tools/corpus.py:59`, descomentar la línea en la plantilla dejándola como:
  ```yaml
  caso NOMBRE:
    etiqueta ETIQUETA
    procedencia PROCEDENCIA
    # opciones: observacion | inspeccion | sintesis | perturbacion | fabricacion
  ```

### Hallazgo 13: `oracle caso nuevo` no orienta sobre la polaridad de las etiquetas ni remite a `oracle manual etiqueta`
- **Ubicación**: `tools/corpus.py:160-165` frente a `tools/manual.py:145-165`.
- **Problema**: El mensaje emitido por `oracle caso nuevo` lista: `etiquetas disponibles: valido, invalido, caso_borde, falso_verde, falso_rojo`. Quien llega por primera vez suele interpretar erróneamente `falso_verde` como un caso que *debe* dar verde, cuando en el formalismo de Oracle representa una prueba negativa donde se espera que la medida detecte la falla (dé ROJO). El comando no explica esta polaridad ni sugiere ejecutar `oracle manual etiqueta`.
- **Impacto**: Usuarios y LLMs asignan etiquetas invertidas en el corpus, causando que `oracle test` falle en la etapa de aceptación y calibración.
- **Forma más chica de arreglarlo**: En `tools/corpus.py:163`, agregar la sugerencia:
  ```python
  "Consultá 'oracle manual etiqueta' para entender la polaridad esperada de cada etiqueta."
  ```

---

## 5. Juicio de Evidencia Externa (`oracle juzgar`)

### Hallazgo 14: `oracle juzgar` no informa qué relaciones espera el catálogo cuando no encuentra medidas aplicables
- **Ubicación**: `tools/juzgar.py:260-267`.
- **Problema**: Cuando la evidencia proporcionada en JSON no coincide con las relaciones que miden los catálogos del proyecto, `juzgar` emite:
  ```text
  SIN MEDIDAS APLICABLES — ninguna medida del catálogo aplica a las relaciones de la evidencia: ['mi_relacion']
  ```
  y retorna código de error 1, sin mostrar qué relaciones sí están definidas en el catálogo activo ni cómo descubrirlas.
- **Impacto**: El usuario no sabe si cometió un error tipográfico en la clave raíz del JSON o qué estructura de evidencia espera el catálogo, quedando bloqueado sin saber qué corregir.
- **Forma más chica de arreglarlo**: En `tools/juzgar.py:264-266`, listar las relaciones conocidas por el catálogo y sugerir `oracle contexto`:
  ```python
  relaciones_catalogo = sorted({m.relacion for m in catalogo.medidas.values() if m.relacion})
  imprimir(
      f"SIN MEDIDAS APLICABLES — ninguna medida del catálogo aplica a las relaciones "
      f"de la evidencia: {sorted(relaciones_evidencia)}.\n"
      f"Relaciones que espera el catálogo: {relaciones_catalogo}. "
      f"Usá 'oracle contexto' para ver el inventario completo."
  )
  ```

---

## 6. Sistema de Seguimiento de Tareas (`oracle tarea`)

### Hallazgo 15: Los errores de sintaxis y argumentos en `oracle tarea` se emiten en inglés
- **Ubicación**: `tools/tareas.py:56-63`.
- **Problema**: La clase `ParserDeSubcomando` hereda de `argparse.ArgumentParser` y redefine `error(self, message)` simplemente prefijando `oracle tarea {self.prog}: {message}`. Cuando un usuario omite un argumento obligatorio (por ejemplo `oracle tarea nueva` sin título) o pasa un flag inexistente, `argparse` genera mensajes en inglés de la biblioteca estándar de Python:
  `ERROR: oracle tarea nueva: the following arguments are required: titulo` o `unrecognized arguments: ...`.
  Esto contradice la directiva y regla fundamental de Oracle de interactuar y reportar consistentemente en español en toda su superficie CLI.
- **Impacto**: Inconsistencia idiomática en la experiencia de usuario dentro de una herramienta cuyo contrato explícito es operar en español.
- **Forma más chica de arreglarlo**: En `tools/tareas.py:58-63`, interceptar los mensajes comunes de `argparse` traduciéndolos al español (ej: `the following arguments are required` -> `se requieren los siguientes argumentos`).

---

## Resumen Cuantitativo y Prioridades Sugeridas

| # | Componente | Severidad para Usuario Nuevo | Archivo de Código / Doc |
|---|---|---|---|
| **1** | `oracle --help` | Media | `tools/cli.py:125` |
| **2** | `oracle contexto` en ayuda | Media | `tools/cli.py:119, 186` |
| **3** | `oracle medida probar` en ayuda | Baja | `tools/cli.py:116` |
| **4** | `oracle test --help` | Alta | `tools/cli.py:1085` |
| **5** | Orden en salida de `oracle init` | Alta | `tools/cli.py:591-593` |
| **6** | Creación de `relaciones/` en `init` | Media | `tools/cli.py:566` |
| **7** | Error de proyecto no encontrado | Alta | `nucleo/proyecto.py:658-660` |
| **8** | Desincronización plantilla `docs/02` | Crítica | `docs/02-de-cero-a-un-rojo.md:71-84` |
| **9** | Marcadores en `oracle medida nueva` | Alta | `tools/medida.py:287` |
| **10** | Falta `ambito` en `oracle manual` | Alta | `tools/manual.py:40-47` |
| **11** | Scripts de desarrollo en `docs/03` | Alta | `docs/03-escribir-una-medida.md:105-106` |
| **12** | `# procedencia:` comentado en plantilla caso | Alta | `tools/corpus.py:59` |
| **13** | Polaridad de etiquetas en `caso nuevo` | Media | `tools/corpus.py:163` |
| **14** | Guía de relaciones en `oracle juzgar` | Media | `tools/juzgar.py:264-266` |
| **15** | Errores en inglés en `oracle tarea` | Baja | `tools/tareas.py:58-63` |
