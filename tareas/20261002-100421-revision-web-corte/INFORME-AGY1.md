# Informe de Revisión de Contenido Web y Documentación (AGY1)

- **Tarea**: `20261002-100421-revision-web-corte`
- **Revisor**: `agy1` (revisión en espacio aislado `/tmp/oracle-web-corte/agy1`)
- **Versión analizada**: Oracle `0.38.0` (catálogo base: 64 medidas, 221 casos de prueba, 6 macros, 0 mutantes vivos)
- **Fecha**: 2026-10-02
- **Entorno de ejecución**: Linux x86_64, Python 3.12.9
- **Reglas del rol**: No se modificaron archivos fuente ni documentación del repositorio; no se realizaron commits ni push; no se corrió la suite completa de mutación de código; todas las citas fueron contrastadas literalmente contra los archivos locales; todos los registros y pruebas reproducibles se almacenaron en `evidencia/`.

---

## Resumen Ejecutivo

Se auditó de forma exhaustiva el sitio web y la documentación técnica de Oracle, contrastando cada afirmación, comando, fragmento de código, versión y enlace contra el comportamiento efectivo del CLI y del motor relacional.

Se confirmaron **8 defectos fácticos objetivos** y **1 ambigüedad de sintaxis de comando en portada**, desglosados en:
1. **Prioridad Alta (2)**: Trabas bloqueantes de reproducción en tutoriales y afirmaciones falsas sobre el comportamiento del evaluador sintáctico ante omisión de campos.
2. **Prioridad Media (6)**: Desfases de completitud del lenguaje (omisión del operador `sin` y de macros estándar `-requiere`), explicaciones contradictorias con la salida del CLI, y enlaces rotos o con extensión inadecuada.
3. **Prioridad Baja / Ambigüedad (1)**: Comando CLI en portada que omite el argumento posicional obligatorio.

Se separaron estrictamente los **hechos comprobados** de las **preferencias editoriales**. Paralelamente, se verificaron 6 aspectos estructurales mayores (generación web, sincronización de manual, métricas de catálogo, ejecución de guías paso a paso, integridad de enlaces internos y API de Python) que resultaron **100% conformes y libres de regresiones**.

---

## 1. Defectos Confirmados (Hechos Objetivos Verificados)

### Defecto 1 (ALTA): Árbol de proyecto en Tutorial Práctico omite `diferencial/`, bloqueando `oracle test`

- **Archivo y líneas**: `docs/tutorial-practico.md:638-648` (y su vista generada `docs/tutorial-practico.html:361-365`).
- **Cita literal verificada**:
```
### 8.1 La carpeta

mi-proyecto/
  oracle.json
  escalares.py
  catalogos/
    tareas/
      tareas.vencida_sin_dueno.oracle
  corpus/
    tareas/
      001-vencida-sin-nadie.caso
      002-vencida-con-dueno.caso
```
- **Pasos para reproducir**:
  1. Crear la estructura de carpetas indicada en §8.1:
     ```bash
     mkdir -p test_rep/catalogos/tareas test_rep/corpus/tareas
     ```
  2. Crear `oracle.json`, `catalogos/tareas/tareas.vencida_sin_dueno.oracle`, y los casos `001` y `002` tal como indican los pasos 8.2 a 8.5.
  3. Ejecutar el comando indicado en el paso 8.6 (línea 746):
     ```bash
     cd test_rep
     oracle test
     ```
- **Salida real obtenida**:
  ```text
  PROYECTO INVÁLIDO — falta `diferencial/`

  VEREDICTO: ROJO (estructura de proyecto inválida)
  ```
  *(Código de salida: 1)*
- **Evidencia guardada**: Registro de reproducción en `evidencia/test_mi_proyecto/` (verificado tanto con y sin la carpeta `diferencial/`).
- **Impacto**: Bloqueo total. Cualquier lector que siga el tutorial práctico paso a paso obtendrá un veredicto ROJO por estructura inválida en su primer intento de verificación, contradiciendo la promesa del tutorial ("oracle test tiene que confirmar: el caso 001 se pone ROJO con tareas.vencida_sin_dueno, y el 002 se pone VERDE"). Además contradice a `oracle init`, que sí genera `diferencial/` por defecto.
- **Corrección concreta mínima**:
  En `docs/tutorial-practico.md`, añadir `diferencial/` al árbol de directorios de la sección 8.1:
  ```markdown
  mi-proyecto/
    oracle.json
    escalares.py
    catalogos/
      tareas/
        tareas.vencida_sin_dueno.oracle
    corpus/
      tareas/
        001-vencida-sin-nadie.caso
        002-vencida-con-dueno.caso
    diferencial/
  ```

---

### Defecto 2 (ALTA): Afirmación falsa sobre el evaluador sintáctico en omisión de `ambito`

- **Archivo y línea**: `docs/como-funciona.md:87` (y `docs/como-funciona.html:81`).
- **Cita literal verificada**:
  `| `ambito universal` | dónde obliga la regla: `universal` (siempre) o `del_origen` (sólo en el proyecto que la escribió) | se asume `sin_declarar` |`
- **Pasos para reproducir**:
  1. Tomar una medida escrita con macro (`ninguno-requiere`) y omitir la línea `ambito universal` (archivo testigo guardado en `evidencia/test_sin_ambito.oracle`).
  2. Ejecutar `oracle medida expandir evidencia/test_sin_ambito.oracle` o `oracle probar`:
     ```bash
     oracle medida expandir evidencia/test_sin_ambito.oracle
     ```
- **Salida real obtenida**:
  ```text
  nucleo.medida.MedidaMalDeclarada: evidencia/test_sin_ambito.oracle: línea 7, columna 1: a la macro ninguno-requiere le falta `ambito`. Su cuerpo son estas 6 líneas, en este orden: de, donde, umbral, requiere, ambito, alcance
  ```
  *(Código de salida: 1)*
- **Evidencia guardada**: `evidencia/test_sin_ambito.oracle` y verificación contra `nucleo/sintaxis.py:978` (`_falta_o_sobra`).
- **Impacto**: Información falsa sobre el contrato del metalenguaje. La tabla afirma explícitamente que si falta `ambito`, *"se asume sin_declarar"*. En la realidad, por `DECISION-012`, las macros exigen que `ambito` esté siempre declarado de forma explícita; omitirlo es un error sintáctico fatal.
- **Corrección concreta mínima**:
  En `docs/como-funciona.md:87`, reemplazar la celda *"se asume `sin_declarar`"* por:
  ```markdown
  | `ambito universal` | dónde obliga la regla: `universal` (siempre) o `del_origen` (sólo en el proyecto que la escribió) | error de sintaxis: las macros exigen declarar el ámbito |
  ```

---

### Defecto 3 (MEDIA): Afirmación de clausura desactualizada y omisión del operador `sin` en Tutorial Práctico

- **Archivo y líneas**: `docs/tutorial-practico.md:150, 152, 155-161, 243-260` (y `docs/tutorial-practico.html:100-101`).
- **Citas literales verificadas**:
  - Línea 150: `## 3. El álgebra: cinco operadores, y nada más`
  - Línea 152: `Toda la sintaxis sale de combinar **cinco operadores**.`
  - Líneas 155-161: La tabla lista únicamente `de`, `donde`, `unir`, `agrupar`, `resumen`.
  - Líneas 243-247 (§3.7): `### 3.7 agrupar — cómo se expresa la AUSENCIA sin usar null \n Este es el operador que más cuesta la primera vez, porque resuelve algo que en SQL pide un LEFT JOIN con nulos — y acá no hay nulos. La pregunta es «¿qué módulos no tienen NINGÚN importador real?» — una ausencia, no una presencia.`
- **Pasos para reproducir**:
  1. Consultar los operadores vigentes del álgebra con `oracle contexto`:
     ```bash
     oracle contexto | grep "operadores:"
     ```
     Salida: `operadores: agrupar · de · desde · donde · resumen · sin · unir`
  2. Consultar `tutorial-practico.md:894` (glosario propio del tutorial):
     `| tubería | secuencia de pasos del álgebra (de, unir, sin, agrupar, donde, resumen) |`
- **Evidencia guardada**: `evidencia/todos_los_comandos.txt` y comparación con `nucleo/sintaxis.py`.
- **Impacto**: Desfase documental. Oracle 0.26.0 incorporó formalmente el operador `sin` (anti-join / diferencia relacional). El tutorial continúa afirmando que son "cinco operadores, y nada más", omitiendo `sin` de la tabla principal y enseñando en §3.7 la técnica histórica de `agrupar + suma == 0` sin advertir al lector que hoy existe un operador de primer orden concebido específicamente para la ausencia relacional.
- **Corrección concreta mínima**:
  1. En `docs/tutorial-practico.md:150`, titular: `## 3. El álgebra: los operadores de tubería`.
  2. En línea 152, actualizar a seis operadores de tubería (`de`, `donde`, `unir`, `sin`, `agrupar`, `resumen`).
  3. Agregar la fila de `sin` a la tabla:
     `| sin | sin <relacion> <alias> [donde <predicado>] | diferencia relacional: conserva filas que no tienen pareja |`
  4. En §3.7, agregar una nota técnica aclarando que para ausencias directas entre relaciones hoy se dispone del operador nativo `sin`.

---

### Defecto 4 (MEDIA): Tabla de macros incompleta en "Escribir una medida"

- **Archivo y líneas**: `docs/03-escribir-una-medida.md:224-229` (y `docs/03-escribir-una-medida.html:121`).
- **Cita literal verificada**:
```markdown
| Macro | Para qué |
|---|---|
| `ninguno` | ninguna fila debe cumplir el predicado |
| `ninguno-requiere` | lo mismo, declarando evidencia indispensable |
| `ninguno-par` | lo mismo sobre PARES de la misma relación |
| `peor` | el peor caso de una expresión no pasa de una tolerancia |
```
- **Pasos para reproducir**:
  1. Consultar las macros del sistema mediante el manual CLI:
     ```bash
     oracle manual macros
     ```
  2. Consultar el glosario de `docs/tutorial-practico.md:888` y `NOTAS-DE-RELEASE.md:178`.
- **Salida real obtenida**:
  Existen 6 macros oficiales:
  - `ninguno`
  - `ninguno-par`
  - `ninguno-par-requiere`
  - `ninguno-requiere`
  - `peor`
  - `peor-requiere`
- **Evidencia guardada**: Verificación contra `nucleo/sintaxis.py:REGISTRO_MACROS` y salida de `oracle manual macros`.
- **Impacto**: Incompletitud en la página de referencia de medidas. Se omiten dos macros estándar fundamentales: `ninguno-par-requiere` y `peor-requiere`. El usuario que lee esta tabla de referencia ignora que puede exigir evidencia indispensable en comparaciones de pares o en cotas de peor caso.
- **Corrección concreta mínima**:
  Incorporar las dos macros restantes a la tabla en `docs/03-escribir-una-medida.md`:
  ```markdown
  | `ninguno-par-requiere` | lo mismo sobre pares, exigiendo evidencia de origen |
  | `peor-requiere` | el peor caso de una expresión, exigiendo evidencia de origen |
  ```

---

### Defecto 5 (MEDIA): Omisión de operadores en el inventario de `oracle contexto`

- **Archivo y línea**: `docs/03-escribir-una-medida.md:88`.
- **Cita literal verificada**:
  `3. Con qué se escribe: operadores (`agrupar`, `de`, `donde`, `resumen`, `unir`), comparadores,`
- **Pasos para reproducir**:
  1. Ejecutar `oracle contexto` en la raíz del proyecto.
  2. Observar la sección `## CON QUÉ SE ESCRIBE`:
     `operadores: agrupar · de · desde · donde · resumen · sin · unir`
- **Evidencia guardada**: Registro de salida en `evidencia/comandos_extraidos.txt`.
- **Impacto**: La enumeración que la documentación atribuye a `oracle contexto` no coincide con lo que el comando emite realmente, omitiendo el operador relacional `sin` y la fuente parametrizada `desde`.
- **Corrección concreta mínima**:
  Actualizar la línea 88 a:
  `3. Con qué se escribe: operadores (`agrupar`, `de`, `desde`, `donde`, `resumen`, `sin`, `unir`), comparadores,`

---

### Defecto 6 (MEDIA): Redacción contradictoria en la guía "De cero a un rojo"

- **Archivo y línea**: `docs/02-de-cero-a-un-rojo.md:301-302` (y `docs/02-de-cero-a-un-rojo.html:150`).
- **Cita literal verificada**:
  `Aunque ese rojo ya no aparece en esta corrida, declarás qué produce el sensor y el alcance de sus hechos:`
- **Pasos para reproducir**:
  1. Seguir la guía hasta el paso 6 (líneas 261-263). La salida real de `oracle test` muestra:
     ```text
     ACEPTACIÓN ✗ — 2 problema(s)
       · meta.la_medida_no_se_fija_solo_con_evidencia_fabricada: el marco no cumple su propia regla
       · meta.toda_cantidad_comparada_tiene_unidad_derivable: el marco no cumple su propia regla
     ```
  2. Leer el encabezado del paso 7 (línea 301): *"Aunque ese rojo ya no aparece en esta corrida..."*.
  3. Ejecutar el paso 8 (línea 330): tras crear `relaciones/documento.relacion` en el paso 7, la salida de `oracle test` pasa de 2 problemas a 1:
     `ACEPTACIÓN ✗ — 1 problema(s)` (se resolvió `meta.toda_cantidad_comparada_tiene_unidad_derivable`).
- **Evidencia guardada**: Verificación ejecutada por `tools/guia.py` sobre `docs/02-de-cero-a-un-rojo.md` y proyecto reproducible en `evidencia/test_de_cero_a_rojo/`.
- **Impacto**: Confusión pedagógica. La frase afirma que el rojo ya no aparece antes de que el usuario haga nada, cuando en realidad el paso 6 arrojó DOS fallas y es precisamente la acción del paso 7 (declarar la relación con su unidad) la que elimina el rojo de `toda_cantidad_comparada_tiene_unidad_derivable`.
- **Corrección concreta mínima**:
  Reemplazar la frase de la línea 301 por una explicación exacta:
  `Para resolver el segundo problema de aceptación (`toda_cantidad_comparada_tiene_unidad_derivable`), declarás qué produce el sensor y el alcance de sus hechos:`

---

### Defecto 7 (MEDIA): Enlaces con extensión `.html` en documento Markdown (`docs/de-cero.md`)

- **Archivo y líneas**: `docs/de-cero.md:1579-1580`.
- **Cita literal verificada**:
  `Después de esto, podés consultar la documentación en el sitio web de Oracle: [La primera medida real](13-primer-valor.html) muestra el mismo recorrido con menos explicación, y [Escribir una medida](03-escribir-una-medida.html) es la referencia completa del lenguaje.`
- **Pasos para reproducir**:
  1. Abrir `docs/de-cero.md` en GitHub o en cualquier visualizador Markdown local.
  2. Hacer clic en `[La primera medida real](13-primer-valor.html)` o `[Escribir una medida](03-escribir-una-medida.html)`.
- **Salida real obtenida**: Error 404 (archivo no encontrado en el repositorio de fuentes, ya que en el árbol fuente los archivos se llaman `13-primer-valor.md` y `03-escribir-una-medida.md`).
- **Evidencia guardada**: Análisis de enlaces en `evidencia/urls_externas.txt` y lógica de compilación en `tools/sitio.py:85-98` (que reescribe automáticamente enlaces `.md` a `.html` al generar la web, pero preserva enlaces `.html` crudos rompiendo la lectura en repositorio).
- **Impacto**: Rompe la navegación fluida para desarrolladores y colaboradores que leen la documentación desde el repositorio o editores Markdown. Todos los demás `.md` del proyecto enlazan a archivos `.md`.
- **Corrección concreta mínima**:
  Cambiar los destinos a `.md`:
  `[La primera medida real](13-primer-valor.md)` y `[Escribir una medida](03-escribir-una-medida.md)`.

---

### Defecto 8 (MEDIA): Enlace roto relativo en notas de release anteriores

- **Archivo y línea**: `docs/notas/anteriores-a-0.20.md:245` (y `docs/notas/anteriores-a-0.20.html:110`).
- **Cita literal verificada**:
  `- [Contrato y tutorial](../../docs/12-tareas.md).`
- **Pasos para reproducir**:
  1. Verificar la existencia del destino relativo:
     ```bash
     ls docs/12-tareas.md
     ```
- **Salida real obtenida**:
  `ls: cannot access 'docs/12-tareas.md': No such file or directory`
- **Evidencia guardada**: Registro en `evidencia/urls_externas.txt`.
- **Impacto**: Enlace roto (404) tanto en GitHub como en el sitio web generado. En la versión 0.34.0 el módulo de tareas fue desacoplado y extraído al repositorio independiente `trackertast`, eliminando `docs/12-tareas.md` pero dejando este enlace huérfano.
- **Corrección concreta mínima**:
  Reemplazar el enlace por una referencia al repositorio externo o nota explicativa:
  `- Contrato y tutorial (trasladado al repositorio de [trackertast](https://github.com/Segtem/trackertast)).`

---

### Defecto 9 (BAJA / AMBIGÜEDAD): Sintaxis incompleta de comando en portada (`index.html`)

- **Archivo y línea**: `docs/index.html:262`.
- **Cita literal verificada**:
  `<code>oracle medida nueva --escenario-de</code> crea las medidas que cierran el circuito entre la spec y el código.`
- **Pasos para reproducir**:
  1. Copiar y pegar el comando mostrado en una terminal:
     ```bash
     oracle medida nueva --escenario-de
     ```
- **Salida real obtenida**:
  ```text
  id inválido: el id debe ser `dominio.nombre`, sólo con minúsculas ASCII, dígitos y `_`
  ```
  *(Código de salida: 1)*
- **Evidencia guardada**: Comprobación interactiva en `evidencia/todos_los_comandos.txt` y comparación con `docs/openspec.md:35-37` y `docs/03-escribir-una-medida.md:77`.
- **Impacto**: Ambigüedad para el usuario que recién llega a la portada. Parece indicar que `--escenario-de` es un flag que permite omitir el id de la medida o que adivina el nombre desde la spec, cuando en realidad el argumento `<id>` es un parámetro posicional obligatorio.
- **Corrección concreta mínima**:
  En `docs/index.html:262`, explicitar el argumento posicional:
  `<code>oracle medida nueva &lt;dominio.nombre&gt; --escenario-de …</code>`

---

## 2. Preferencias y Sugerencias Editoriales (Separadas de Hechos)

Las siguientes observaciones corresponden a estilos, claridad pedagógica y consistencia de presentación; no constituyen errores de ejecución ni fallas de código:

1. **Aclaración sobre `oracle nueva` vs `oracle medida nueva`**:
   - En `docs/13-primer-valor.md:25`, la salida generada por `oracle init` recomienda: `2. Creá una medida: oracle nueva <dominio.nombre>`. En el resto de la web se promueve la sintaxis canónica `oracle medida nueva <dominio.nombre>`. Ambos comandos funcionan idénticamente (`nueva` es un alias directo de `medida nueva`), pero agregar una breve nota explicativa evitaría que el lector piense que son comandos distintos.
2. **Coordinación de versiones con `oracle-mcp`**:
   - En `docs/mcp.md:23-24`, el texto dice: *"`oracle-mcp` 0.1.1 fija Oracle 0.35.0; instalarlo no actualiza automáticamente su motor a Oracle 0.38.0"*. Es una advertencia honesta y correcta, pero convendría añadir una nota sobre la retrocompatibilidad del protocolo stdio con proyectos que corren en 0.38.0.
3. **Nomenclatura uniforme de operadores**:
   - En `docs/03-escribir-una-medida.md:88`, se agrupan todos bajo el término "operadores". Para mayor precisión formal frente al tutorial práctico, podría distinguirse entre *operadores de tubería* (`de`, `unir`, `sin`, `agrupar`, `donde`, `resumen`) y *generador de fuente parametrizada* (`desde`).

---

## 3. Verificaciones Satisfactorias (Evidencia Positiva y Ausencia de Regresiones)

Durante la auditoría se ejecutaron baterías de pruebas específicas y herramientas internas del repositorio para verificar la consistencia global del sitio web:

| Verificación | Herramienta / Método | Resultado | Evidencia |
|---|---|---|---|
| **Sincronización Web HTML** | `python3 tools/sitio.py` | **OK** (código 0). Todas las páginas HTML reflejan limpiamente sus fuentes Markdown. | Ejecución sincrónica en limpio |
| **Manual de Referencia HTML** | `python3 -m tools.cli manual --html` | **OK**. Coincidencia byte por byte contra `docs/manual.html`. | Salida binaria idéntica |
| **Cifras de Catálogo y Portada** | `python3 tools/cifras.py` | **OK** (`CIFRAS OK: 64 medidas, 221 casos, v0.38.0`). Coinciden portada, pie y metadata. | Verificado con AST y escaneo |
| **Guías Interactivas Reales** | `python3 tools/guia.py` | **OK** (código 0). 7 guías ejecutadas y verificadas contra salidas reales: `de-cero`, `como-funciona`, `02-de-cero-a-un-rojo`, `05-por-que-la-mutacion`, `07-conectar-a-un-proyecto-propio`, `13-primer-valor`, `recetas`. | Log completo de ejecución |
| **Bloques de Sintaxis en Docs** | `python3 tools/sintaxis.py --verificar` | **OK** (código 0). 24 bloques sintácticos embebidos en Markdown analizados y validados por el parser. | Validación sintáctica limpia |
| **Enlaces Internos HTML** | Script de validación de grafo de anclas y rutas relativas | **OK**. Cero enlaces rotos entre las 35 páginas HTML del sitio compilado. | Grafo de enlaces en `evidencia/` |
| **API Python Embebido** | Comprobación de `Motor.desde_proyecto` y `Motor.desde_texto` | **OK**. La biblioteca Python importa y juzga casos en memoria sin dependencias externas. | Prueba en `evidencia/` |

---

## 4. Plan de Acción Mínimo para el Próximo Corte

Para consolidar el corte sin incurrir en reescrituras de riesgo ni alterar la semántica del núcleo, se recomienda aplicar únicamente los siguientes cambios puntuales:

1. **Corregir `docs/tutorial-practico.md`**:
   - Insertar `diferencial/` en el árbol de directorios de §8.1.
   - Actualizar §3 para incluir `sin` en la tabla de operadores del álgebra.
2. **Corregir `docs/como-funciona.md`**:
   - En la tabla de la línea 87, aclarar que la omisión de `ambito` en una macro produce error sintáctico.
3. **Corregir `docs/03-escribir-una-medida.md`**:
   - Agregar `ninguno-par-requiere` y `peor-requiere` a la tabla de macros (§línea 224).
   - Incluir `sin` y `desde` en la lista de operadores de la línea 88.
4. **Corregir `docs/02-de-cero-a-un-rojo.md`**:
   - Reformular la línea 301 para conectar el paso 7 con la resolución del fallo de aceptación `toda_cantidad_comparada_tiene_unidad_derivable`.
5. **Corregir enlaces**:
   - En `docs/de-cero.md:1579-1580`, reemplazar extensiones `.html` por `.md`.
   - En `docs/notas/anteriores-a-0.20.md:245`, actualizar el enlace roto al repositorio de `trackertast`.
6. **Aclarar sintaxis en portada (`docs/index.html:262`)**:
   - Añadir `<dominio.nombre>` en la mención a `oracle medida nueva --escenario-de`.
7. **Regenerar vistas HTML**:
   - Ejecutar `python3 tools/sitio.py --escribir` para sincronizar las páginas web.
