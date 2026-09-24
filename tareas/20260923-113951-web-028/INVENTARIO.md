# Inventario de contenidos web: estado actual, brechas desde 0.26 y propuesta de índice

**Fecha:** 2026-09-23  
**Tarea de referencia:** [`tareas/20260923-113951-web-028/TAREA.md`](TAREA.md)  
**Destinatario:** Brian  
**Responsable:** Agente (confinado a lectura y edición, sin ejecución en shell ni commits)

---

## 1. Propósito y método del inventario

Este inventario responde al **Próximo paso** establecido en [`tareas/20260923-113951-web-028/TAREA.md`](TAREA.md#L35-L38):
> *«Inventario: qué dice hoy la página, qué falta, y un índice propuesto para revisión de Brian.»*

Para garantizar que el relevo sea fáctico y verificable:
- Cada afirmación sobre el estado del repositorio cita el archivo y rango de líneas exacto que la sustenta.
- No se asume el contenido de ningún archivo que no haya sido leído expresamente.
- No se han realizado movimientos, eliminaciones ni renombrados en el árbol de trabajo.
- Toda cifra y ejemplo técnico proviene de corridas registradas en la documentación y código existentes.

---

## 2. Qué dice hoy la página (`docs/index.html`)

La página publicada en GitHub Pages (`docs/index.html`, 466 líneas, leída íntegra) se regenera automáticamente en tres marcas dinámicas (`sitio_version`, `sitio_medidas`, `sitio_casos`) mediante [`tools/cifras.py`](../../tools/cifras.py#L215-L235), pero la prosa y las secciones que la componen corresponden conceptualmente a Oracle 0.25 / 0.26 temprano.

### Desglose sección por sección:

1. **Barra de navegación y cabecera ([`docs/index.html#L173-L191`](../../docs/index.html#L173-L191)):**
   - Muestra la versión dinámica `0.28.0` dentro del bloque `<!-- sitio_version:inicio -->`.
   - Menú de navegación a anclas internas (`#empezar`, `#medida`, `#tracker`) y páginas complementarias (`donde-entra.html`, `de-cero.html`, `reportar.html`, `manual.html`).
   - Enlaces externos a GitHub: `docs/README.md`, `#las-decisiones-y-por-qué` y la raíz del repositorio.

2. **Hero ([`docs/index.html#L193-L205`](../../docs/index.html#L193-L205)):**
   - Lema: *«Medir no opinar»*.
   - Definición del metalenguaje: *«Un lenguaje para escribir reglas que fallan —con un número, un umbral y las filas que ofendieron— en vez de documentos que aconsejan»*.
   - Botones de acción hacia `#empezar` y GitHub, destacando `Python ≥ 3.11 · sin dependencias · MIT`.

3. **El problema Goodhart y la mutación ([`docs/index.html#L207-L228`](../../docs/index.html#L207-L228)):**
   - Argumenta por qué quien construye una herramienta con un LLM no debe escribir sus propios tests en la misma pasada sin un marco que lo contradiga.
   - Concluye que *«una medida que nada puede romper es decoración»*, justificando la mutación del catálogo para matar reglas redundantes o permisivas.

4. **Una medida en el editor ([`docs/index.html#L230-L262`](../../docs/index.html#L230-L262)):**
   - Simula un archivo `.oracle` (`documento.nombre_sigue_la_convencion.oracle`) con las directivas `ninguno`, `de`, `donde`, `umbral <= 0 segun contrato porque "..."` y `alcance "..."`.
   - Muestra la línea virtual de LSP (*lens*): `3 casos · 1 verde · 2 rojos · umbral <= 0 segun contrato`.
   - Explica que cargar una medida no ejecuta Python (es segura ante código malicioso).

5. **Visualización de un fallo en rojo ([`docs/index.html#L264-L287`](../../docs/index.html#L264-L287)):**
   - Ejemplo de salida en terminal con veredicto `ROJO`, valor medido (2 contra umbral `<= 0`), procedencia contractual, testigos (`2026-07-25-informe.md`, `notas finales.md`) y el texto del alcance.
   - Enfatiza el valor de los testigos para evitar discusiones subjetivas sobre el veredicto.

6. **Elementos obligatorios de una medida ([`docs/index.html#L289-L315`](../../docs/index.html#L289-L315)):**
   - Detalla la obligatoriedad de tres conceptos: `umbral segun` (`medicion`, `contrato`, `convencion`, `tanteo`), `alcance` (prosa con el punto ciego) y `testigos` (filas infractoras).

7. **Cinco niveles de representación ([`docs/index.html#L317-L345`](../../docs/index.html#L317-L345)):**
   - Clasificación de niveles: L−2 (identidad/frescura), L−1 (sensor y unidades), L0 (filas de evidencia), L1 (medidas declaradas) y L2 (catálogo juzgándose a sí mismo).

8. **Cifras del proyecto ([`docs/index.html#L347-L356`](../../docs/index.html#L347-L356)):**
   - Bloques custodiados: 62 medidas universales (`sitio_medidas`), 212 casos en el corpus (`sitio_casos`), 0 mutantes vivos en el núcleo y 0 dependencias.

9. **El tracker local de tareas ([`docs/index.html#L358-L393`](../../docs/index.html#L358-L393)):**
   - Explica el subsistema `oracle tarea` basado en tatr: carpetas en `tareas/`, archivo `TAREA.md`, ID fecha/hora, sin base de datos ni servidor, versionado en Git.
   - Menciona que el tracker emite hechos relacionales auditados por el propio catálogo y soporta consultas en lenguaje natural (`:metalenguaje y prioridad desde 70`).
   - Comandos mostrados: `oracle tarea init`, `oracle tarea nueva ... --sufijo sensor`, `oracle tarea listar ...`, `oracle tarea cerrar 20260916-014153-sensor`. Enlaza a [`docs/12-tareas.md`](../../docs/12-tareas.md).

10. **Empezar ([`docs/index.html#L395-L425`](../../docs/index.html#L395-L425)):**
    - Menciona requisitos (Python ≥ 3.11, entornos virtuales por PEP 668), instalación de 10 comandos, catálogo base empaquetado y LSP para Emacs y VS Code.
    - Comandos mostrados: `uv tool install oracle-metalenguaje`, `oracle init mi-proyecto`, `cd mi-proyecto`, `oracle nueva documento.nombre_sigue_la_convencion`, `oracle test`.
    - Enlaza al tutorial [`docs/02-de-cero-a-un-rojo.md`](../../docs/02-de-cero-a-un-rojo.md).

11. **Aviso de madurez ([`docs/index.html#L427-L444`](../../docs/index.html#L427-L444)):**
    - Declara que el proyecto es experimental, que L2 continúa fijado en Python, y remite a las decisiones de diseño y notas de release.

12. **Pie de página ([`docs/index.html#L451-L463`](../../docs/index.html#L451-L463)):**
    - Metadatos: MIT, Python ≥ 3.11, cero dependencias, enlaces a PyPI, GitHub y subpáginas.

---

## 3. Qué falta: brechas de lo incorporado desde 0.26

Contrastando la portada actual con las notas de versión ([`NOTAS-DE-RELEASE.md#L1-L200`](../../NOTAS-DE-RELEASE.md#L1-L200)) y las tareas cerradas del proyecto, se identifican **siete avances mayores** completamente ausentes en la web:

### Brecha 1: El álgebra puede decir «ninguna» (`sin`, 0.26)
- **Sustento documental:** [`NOTAS-DE-RELEASE.md#L139-L175`](../../NOTAS-DE-RELEASE.md#L139-L175), [`nucleo/vocabulario.py#L78-L79`](../../nucleo/vocabulario.py#L78-L79).
- **Situación actual:** La web solo muestra `ninguno` (macro de conteo cero), `de` y `donde`. No explica la anti-junta `sin … donde …` introducida en el álgebra 0.8 / sintaxis 0.6.
- **Qué aporta:** Permite formular reglas del tipo «deja pasar cada fila para la cual *ninguna* fila de otra relación satisface la condición». Elimina conteos externos en Python y habilita la mutación formal de anti-juntas (`quitar_antijunta`).
- **Ejemplo copiable real:**
  ```oracle
  medida seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre:
      de tarea_seguimiento t
      donde t.estado_declarado == "CERRADA"
      sin commit_seguimiento c donde c.tarea_nombrada == t.id y c.es_cierre == true
      resumen contar(1)
      umbral <= 0 segun convención porque "toda tarea cerrada debe dejar su commit registrado"
      alcance "no inspecciona el árbol de trabajo ni tareas abiertas"
  ```

### Brecha 2: Una sombra perdona hasta su cota, y `juzgar` nombra lo que no se aplicó (0.27)
- **Sustento documental:** [`NOTAS-DE-RELEASE.md#L65-L89`](../../NOTAS-DE-RELEASE.md#L65-L89), [`tools/juzgar.py#L285-L346`](../../tools/juzgar.py#L285-L346), [`nucleo/medida.py#L700-L780`](../../nucleo/medida.py#L700-L780).
- **Situación actual:** `oracle juzgar` ni siquiera se menciona en la portada principal (sólo se nombra `oracle test`). Tampoco se explican las cotas de sombra ni la rendición de cuentas de medidas no evaluadas.
- **Qué aporta:**
  1. *Cotas de sombra:* Una medida en sombra no es un pase libre infinito; declara una cota de tolerancia (ej. tolerar hasta 4 incidencias). Si el valor medido supera la cota, el veredicto vuelve a fallar como `SUPERA SU COTA N`.
  2. *Transparencia en no aplicadas:* Si la evidencia aportada no contiene las relaciones que exige una medida del proyecto, Oracle no finge que pasó ni calla: imprime la sección `NO SE APLICARON (N) — su relación no vino en la evidencia` con la lista de relaciones faltantes.
  3. *Honestidad del verde:* Cuando todo pasa por sombra, el veredicto imprime explícitamente `VEREDICTO: verde por sombra en N medidas (M en sombra perdonadas). SIN MIRAR:`.
- **Salida real registrada en terminal:**
  ```text
  ✗ proceso.lineas_largas                       12 (<= 0)   [EN SOMBRA] (SUPERA SU COTA 4: la sombra no la perdona; desde 2026-09-01; porque: deuda técnica)
        → archivo='nucleo/algebra.py', linea=142

  NO SE APLICARON (1) — su relación no vino en la evidencia:
    · colocacion.dentro_del_tablero: falta celda_ocupada

  VEREDICTO: 1 de 2 medidas en rojo
  ```

### Brecha 3: El servidor MCP con cinco herramientas de sólo lectura y su justificación (0.27)
- **Sustento documental:** [`tools/mcp.py#L47-L731`](../../tools/mcp.py#L47-L731), [`docs/mcp-contrato.md#L8-L38`](../../docs/mcp-contrato.md#L8-L38), [`NOTAS-DE-RELEASE.md#L96-L110`](../../NOTAS-DE-RELEASE.md#L96-L110).
- **Situación actual:** Totalmente ausente en la web. No hay mención a la integración de Oracle con agentes mediante Model Context Protocol.
- **Qué aporta:** Servidor JSON-RPC autónomo (`oracle-mcp`) sobre stdio con cinco herramientas especializadas:
  1. `oracle_catalogo_efectivo`: Consulta qué medidas obligan al proyecto y sus alcances.
  2. `oracle_evaluar`: Evalúa una medida puntual contra hechos JSON en memoria.
  3. `oracle_desafiar`: Desafía una medida contra corpus y mutaciones sin persistir archivos.
  4. `oracle_juzgar`: Juzga evidencia contra el catálogo completo respetando sombras y cotas.
  5. `oracle_tareas`: Consulta el tracker (`listar`, `ver`, `buscar`, `hechos`).
- **Por qué sólo lectura:** La especificación ([`docs/mcp-contrato.md#L8-L33`](../../docs/mcp-contrato.md#L8-L33)) fundamenta la decisión: los defectos habituales de los agentes de IA se producen al interpretar la realidad (falsos verdes por leer mal la evidencia); permitir escrituras mediante MCP crearía una falsa sensación de aprobación y rompería la correspondencia atómica que el tracker mantiene con cada commit de Git.

### Brecha 4: Retomar es leer una tarea: el tracker como relevo, sufijos y `CIERRA CON` (0.28)
- **Sustento documental:** [`NOTAS-DE-RELEASE.md#L9-L25`](../../NOTAS-DE-RELEASE.md#L9-L25), [`docs/12-tareas.md#L44-L86`](../../docs/12-tareas.md#L44-L86), [`AGENTS.md#L1-L25`](../../AGENTS.md#L1-L25).
- **Situación actual:** La sección `#tracker` de `docs/index.html` describe únicamente el formato básico de archivos y consultas en español. No aborda el cambio de paradigma de 0.28.
- **Qué aporta:**
  1. *El tracker como protocolo de relevo:* Erradicación de notas sueltas (`RELEVO.md`, planes volátiles). La tarea es la única fuente de verdad; cada tarea culmina en una sección única `## Próximo paso` que indica la acción inmediata para continuar el trabajo entre distintos agentes o programadores humanos.
  2. *Búsqueda flexible por sufijo:* Ya no se exige recordar la marca temporal completa. `oracle tarea ver sensor` resuelve inequívocamente `20260916-014153-sensor`. Si no coincide, el CLI sugiere hasta 3 tareas parecidas (*«¿quisiste decir…?»*).
  3. *Cierre formal con medidas (`CIERRA CON`):* En el encabezado de `TAREA.md`:
     ```markdown
     - ESTADO: ABIERTA
     - PRIORIDAD: 70
     - ETIQUETAS: colocacion, buques
     - CIERRA CON: colocacion.dentro_del_tablero, colocacion.sin_solapamiento
     ```
     La política de proceso exige que toda tarea marcada como `CERRADA` demuestre que sus medidas asociadas existen y están verdes en la aceptación del catálogo.

### Brecha 5: `oracle test` honesto: declara lo que no midió (`SIN MEDICIÓN` y alcance de producto, 0.28)
- **Sustento documental:** [`NOTAS-DE-RELEASE.md#L26-L37`](../../NOTAS-DE-RELEASE.md#L26-L37), [`tools/cli.py#L768-L772`](../../tools/cli.py#L768-L772), [`tools/cli.py#L838-L852`](../../tools/cli.py#L838-L852).
- **Situación actual:** La web describe un veredicto verde simple, lo que alimenta la confusión habitual de creer que un test de catálogo verde equivale a certificar el código de una aplicación.
- **Qué aporta:**
  1. *Declaración explícita de límites en cada corrida:*
     ```text
     ALCANCE: verificación de medidas contra casos guardados del corpus.
     PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
     ```
  2. *Veredicto honesto para proyectos recién creados:* Un proyecto con `catalogo_base: true` pero sin medidas propias, casos ni fixtures antes daba verde engañoso. Ahora emite:
     ```text
     VEREDICTO: SIN MEDICIÓN (advertencia: proyecto vacío: 0 medidas propias, 0 casos, 0 fixtures diferenciales)
     ```
     (Conservando código de salida 0 para no romper pipelines recién inicializados).

### Brecha 6: La ruta mínima hacia el primer valor observable (`docs/13-primer-valor.md`)
- **Sustento documental:** [`docs/13-primer-valor.md#L1-L306`](../../docs/13-primer-valor.md#L1-L306), [`ejemplo/primer-valor/README.md#L1-L100`](../../ejemplo/primer-valor/README.md#L1-L100).
- **Situación actual:** No está enlazado en `docs/index.html` ni en el menú de navegación (sólo figura el tutorial antiguo `02-de-cero-a-un-rojo.md` en el hero y empezar).
- **Qué aporta:** Un recorrido integral de 5 pasos con una aplicación mínima de Batalla Naval ([`ejemplo/primer-valor/colocador.py`](../../ejemplo/primer-valor/colocador.py)):
  1. Producto emite hechos L0 (`celda_ocupada: barco, fila, columna`).
  2. Medida enuncia lo que ofende (`colocacion.dentro_del_tablero.oracle` con `requiere celda_ocupada`).
  3. Corpus fija la regla con casos de ambas polaridades (falso verde y verde correcto; 6 casos construidos, 20/20 mutantes muertos).
  4. `oracle test` valida el catálogo en aislamiento.
  5. `oracle juzgar` juzga el producto vivo: corrida con defecto sale 1 (señalando testigo `fila: 10`); corrida corregida sale 0 e imprime `SIN MIRAR:` con su punto ciego.

### Brecha 7: Jev como sensor probabilístico de prosa: hechos vs juicio, calibración y plantilla en PyPI
- **Sustento documental:** [`docs/14-sensor-prosa.md#L1-L120`](../../docs/14-sensor-prosa.md#L1-L120), [`tareas/20260923-113127-jev-pypi/TAREA.md#L8-L60`](../20260923-113127-jev-pypi/TAREA.md#L8-L60), [`vault-kb/estudios/JEV-COMO-SENSOR.md#L9-L84`](../../vault-kb/estudios/JEV-COMO-SENSOR.md#L9-L84), [`tareas/20260922-220029-jev-porque-v2/TAREA.md#L10-L57`](../20260922-220029-jev-porque-v2/TAREA.md#L10-L57), [`ejemplo/sensor-prosa/README.md#L1-L47`](../../ejemplo/sensor-prosa/README.md#L1-L47).
- **Situación actual:** La web no menciona en absoluto el uso de modelos de lenguaje ni el patrón de sensores de prosa.
- **Qué aporta:**
  1. *División rigurosa sensor vs. juez:* Un modelo probabilístico no es un juez. El modelo actúa como **sensor** emitiendo hechos (`afirmacion_prosa`); **Oracle juzga** esas filas de forma determinista, reproducible y sin conexión a red.
  2. *Cifras reales medidas (sin promesas vacías):*
     - En el primer estudio ([`vault-kb/estudios/JEV-COMO-SENSOR.md#L9-L19`](../../vault-kb/estudios/JEV-COMO-SENSOR.md#L9-L19)): Jev detectó 10/10 controles de prosa vacía, con costo observado de **US$ 0,000877** (menos de 0,1 centavos de dólar). En preguntas sobre `alcance` coincidió 15/15 con Claude como juez ciego.
     - En la segunda corrida ([`docs/14-sensor-prosa.md#L36-L42`](../../docs/14-sensor-prosa.md#L36-L42), [`tareas/20260922-220029-jev-porque-v2/TAREA.md#L55`](../20260922-220029-jev-porque-v2/TAREA.md#L55)): Acuerdo 15/15 en reales y 10/10 en controles con referencia ciega; los *sí* se ubicaron entre 0,50 y 0,68; los *no* entre 0,09 y 0,33.
  3. *Zona media a revisión humana:* La estrechez de margen no autoriza automatización ciega. Las filas con probabilidad entre 0,4 y 0,6 se aíslan en `revision-humana.json` y el sensor finaliza con código 2; la decisión final sobre la prosa sigue siendo humana.
  4. *Disponible en PyPI:* Tras cerrarse [`tareas/20260923-113127-jev-pypi/TAREA.md`](../20260923-113127-jev-pypi/TAREA.md), quien instala Oracle vía pip o uv recibe la plantilla directamente con el comando:
     ```bash
     oracle plantilla sensor-prosa <directorio-nuevo>
     ```
     permitiendo probar la preparación de lotes y el juzgamiento sin red ni API key ([`ejemplo/sensor-prosa/README.md#L9-L20`](../../ejemplo/sensor-prosa/README.md#L9-L20)).

---

## 4. Dependencias del repositorio y coordinación con `repo-limpio`

En [`tareas/20260923-113951-web-028/TAREA.md#L30-L31`](TAREA.md#L30-L31) se especifica:
> *«Que la página no dependa de este repo desordenado: se escribe después de `repo-limpio` si esa tarea cambia rutas, para no enlazar lo que se va a mover.»*

En [`tareas/20260923-113951-repo-limpio/TAREA.md#L20-L75`](../20260923-113951-repo-limpio/TAREA.md#L20-L75) se detallan los movimientos previstos:
1. Las decisiones `DECISION-*.md` se mudarán a `docs/decisiones/` (o permanecerán normativas en `docs/`).
2. El contrato del MCP (`docs/mcp-contrato.md`) se trasladará a `docs/` como documentación viva del producto, generada desde `tools/mcp.py`.
3. Relatos, planes viejos (`PLAN-*`), relevos y estudios experimentales pasarán a la base de conocimiento `vault-kb/`.
4. El motor esencial (`nucleo/`, `catalogos/`, `tools/`, `tareas/`, `docs/`, `ejemplo/`) se mantendrá en su ubicación.

**Implicancia directa para la web:**
- Ningún enlace de `docs/index.html` debe apuntar directamente a archivos en `vault-kb/estudios/` o planes `PLAN-*.md`.
- Los enlaces documentales deben referenciar exclusivamente archivos dentro de `docs/` o URL canónicas del sitio (`https://segtem.github.io/oracle/manual.html`, etc.).
- Las cifras dinámicas del HTML continuarán garantizadas por `tools/cifras.py` ([`tools/cifras.py#L285`](../../tools/cifras.py#L285)) y la coherencia del manual por el test `LaPaginaPublicadaNoSeDespegaTests` ([`tests/test_manual.py#L240-L250`](../../tests/test_manual.py#L240-L250)).

---

## 5. Índice propuesto para la nueva web (`docs/index.html`)

A continuación se presenta la propuesta de estructura editorial y técnica para la renovación de `docs/index.html`, organizada en **12 bloques articulados**, diseñada para someterse a la revisión y aprobación de Brian:

```
================================================================================
ÍNDICE PROPUESTO PARA LA PORTADA (docs/index.html)
================================================================================

1. BARRA Y ENCABEZADO
   · Marca Oracle con versión dinámica (0.28.0 vía cifras.py).
   · Navegación: El lenguaje · Juzgar · Primer valor · Tracker · Jev · MCP · Manual.
   · Enlaces externos: GitHub · PyPI · Documentación.

2. HERO: MEDIR, NO OPINAR
   · Lema principal: Reglas que fallan con testigos y umbrales contrastables.
   · Diferencia clave frente a linters y asserts tradicionales: el punto ciego
     se explicita en prosa, no se asume cobertura total.
   · Llamada a la acción: Botón «Primer valor (5 min)» y «Ver en GitHub».
   · Ficha técnica: Python ≥ 3.11 · cero dependencias · MIT.

3. EL PROBLEMA GOODHART Y LA MUTACIÓN
   · Por qué cuando un LLM o agente escribe el código y el test a la vez,
     el criterio pierde independencia.
   · El catálogo se muta: reglas debilitadas a propósito que el corpus debe atrapar.
   · Cifras en vivo: 62 medidas universales · 212 casos · 0 mutantes vivos.

4. EL LENGUAJE Y SUS OPERADORES (ÁLGEBRA 0.8 / SINTAXIS 0.6)
   · Editor interactivo / visual con syntax highlighting.
   · Desglose de operadores de tubería:
     - `de`: relación de evidencia de entrada.
     - `donde`: filtro de filas que ofenden.
     - `sin ... donde ...`: la anti-junta que dice «ninguna» (0.26).
     - `unir` / `agrupar` / `resumen contar(1)`.
   · Componentes obligatorios: `umbral segun`, `requiere` y `alcance`.

5. ANATOMÍA DE UN FALLO: VEREDICTOS HONESTOS
   · Salida real en terminal de un veredicto ROJO:
     - Valor medido contra umbral.
     - Lista explícita de testigos infractores.
     - Puntos ciegos confesados en `alcance`.
   · Honestidad en `oracle test`:
     - Distinción entre verificar catálogo y certificar producto.
     - Transparencia: `ALCANCE` y `PRODUCTO: sin nueva medición`.
     - Proyectos vacíos: `VEREDICTO: SIN MEDICIÓN` (exit 0).

6. JUZGAR EL PRODUCTO VIVO (`oracle juzgar`)
   · Cómo se conecta el producto con Oracle mediante hechos JSON (nivel L0).
   · Las dos protecciones clave de 0.27:
     - Una sombra perdona sólo hasta su cota (`SUPERA SU COTA N`).
     - Transparencia en relaciones faltantes (`NO SE APLICARON`).
   · Ejemplo con terminal: salida real mostrando perdón en sombra y medidas omitidas.

7. EL CAMINO CORTO A LA PRIMERA MEDIDA REAL (PRIMER VALOR)
   · Guía paso a paso basada en `docs/13-primer-valor.md` (Batalla Naval mínima):
     1. El sensor exporta `celda_ocupada(barco, fila, columna)`.
     2. Se define `colocacion.dentro_del_tablero.oracle`.
     3. El corpus fija la regla con casos positivos y negativos (20/20 mutantes muertos).
     4. `oracle test` confirma consistencia.
     5. `oracle juzgar` detecta desborde de fila 10 y da verde al corregir.
   · Bloque de comandos listo para copiar y pegar.

8. JEV: UN MODELO COMO SENSOR DE PROSA
   · La división que hace que valga:
     - El sensor produce hechos estructurados (`afirmacion_prosa`).
     - Oracle juzga sin llamadas a red ni dependencias.
     - Oracle jamás invoca un LLM directamente.
   · Lo medido en la práctica:
     - 10/10 controles de prosa vacía detectados.
     - 15/15 acuerdo en medidas reales frente a juez ciego independiente.
     - Costo real registrado: US$ 0,00088 (fracción de centavo).
   · Límites y zona de revisión humana:
     - Probabilidad 0,4–0,6 se deriva a `revision-humana.json` (exit code 2).
   · Cómo se usa desde PyPI:
     - `oracle plantilla sensor-prosa <destino>` (ejecución y juzgamiento local).

9. EL TRACKER COMO RELEVO ENTRE SESIONES Y AGENTES
   · Más que un gestor documental: un protocolo de relevo en Git.
   · Cada tarea tiene una única sección final `## Próximo paso` como relevo determinista.
   · Búsqueda inteligente por sufijo (`oracle tarea ver sensor` con sugerencias de cercanía).
   · Cierre contractual: `CIERRA CON: medida.id` vigilado por medidas en el CI.
   · Comandos copiables del flujo diario de trabajo.

10. INTEGRACIÓN PARA AGENTES Y HERRAMIENTAS: EL SERVIDOR MCP
    · `oracle-mcp`: Servidor stdio de sólo lectura para Claude Desktop, Cursor, AGY, etc.
    · Cinco herramientas para cinco preguntas:
      1. `oracle_catalogo_efectivo`: ¿Qué reglas aplican?
      2. `oracle_evaluar`: ¿Qué hace una medida con una evidencia?
      3. `oracle_desafiar`: Falsación y mutación rápida en memoria.
      4. `oracle_juzgar`: Juicio global del proyecto.
      5. `oracle_tareas`: Consulta del estado del tracker.
    · Justificación técnica: por qué el servidor no escribe ni crea archivos.

11. LOS CINCO NIVELES DE REPRESENTACIÓN
    · Arquitectura conceptual: L−2 (frescura) a L2 (catálogo juzgándose a sí mismo).
    · Por qué la mayoría de herramientas del mercado confunden L0 con L1.

12. EMPEZAR Y LÍMITES CONOCIDOS
    · Instalación con `uv tool install oracle-metalenguaje` (o pip en venv).
    · Inicialización limpia en 3 comandos.
    · El editor: LSP unificado para Emacs y VS Code.
    · Límites transparentes: experimental, L2 reflexivo en desarrollo, 8 decisiones.
    · Pie de página con enlaces a manual HTML, GitHub y PyPI.
================================================================================
```

---

## 6. Próximo paso propuesto para la tarea

Una vez que Brian revise este inventario y valide el índice propuesto:
1. Coordinar con la resolución de [`tareas/20260923-113951-repo-limpio/TAREA.md`](../20260923-113951-repo-limpio/TAREA.md) para confirmar las rutas definitivas de documentos y decisiones.
2. Redactar el contenido de cada nueva sección en `docs/index.html` con ejemplos reproducibles extraídos de corridas reales.
3. Ejecutar las comprobaciones automáticas existentes: `python3 tools/cifras.py` y `python3 -m unittest tests/test_manual.py`.

---

## Revisión de Claude (2026-09-23)

Contrastado contra el código. Las siete brechas son ciertas; el índice sirve de base. Errores que
no pueden pasar a la web tal cual:

- **Brecha 1, «ejemplo copiable real»: no es real.** La medida existe
  (`ejemplo/seguimiento-tareas/catalogos/seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre.oracle`),
  pero el ejemplo cambia `segun contrato` por `segun convención`, que además lleva tilde, e
  inventa el `porque` y el `alcance`. También le falta `ambito del_origen`. En la web va el
  archivo verdadero o un recorte marcado como recorte.
- **Brecha 2, la salida de terminal no es una corrida registrada.** Las frases existen
  (`tools/juzgar.py:317`, `:334–343`; `nucleo/medida.py:762`), pero esa combinación de las dos
  (`proceso.lineas_largas` con `colocacion.dentro_del_tablero`) está armada a mano. En la web va
  una corrida real.
- **Índice §12, «8 decisiones»:** son 12 (`DECISION-001` … `DECISION-012`).
- **Índice §10, «Claude Desktop, Cursor, AGY»:** probados hay tres clientes: Claude Code, Codex y
  agy (tarea `mcp-tokens`). Esa tarea midió además que cada uno ve una parte distinta de la
  respuesta, un dato que vale la pena mostrar.
- **Índice §8, «15/15 acuerdo en medidas reales»:** es 15/15 en la pregunta sobre el `porque`
  (segunda corrida). En otras preguntas y en los pilotos de Jam y LyraGASP el acuerdo fue menor
  (por ejemplo, síntoma 9/15 en LyraGASP, con Jev indulgente en los 9 desacuerdos). La web tiene
  que decir las dos cosas.
- **Brecha 3:** el contrato del MCP ya no se copia a mano: se genera (`tools/mcp_contrato.py`).
