# Informe — Normalización de la nota del DSL en el Vault de Jam

- **Fecha:** 2026-09-16
- **Agente:** Agy (Antigravity)
- **Tarea asociada:** [`20260916-151553-vault-jam`](../../tareas/20260916-151553-vault-jam/TAREA.md)
- **Encargo:** [`ENCARGO-AGY.md`](ENCARGO-AGY.md)

---

## 1. Documento entregado

- **Ruta absoluta:** `/home/workstation/Dev/jam/Vault-kb/04-Ejecucion-y-pruebas/2026-09-10-GUIA-DSL-De-Jam-v1.0.md`
- **Nombre de archivo:** `2026-09-10-GUIA-DSL-De-Jam-v1.0.md`
- **Carpeta:** `04-Ejecucion-y-pruebas`
- **Tipo:** `GUIA`
- **Área declarada en frontmatter:** `04-Ejecucion-y-pruebas`
- **Título:** `El DSL (Domain-Specific Language) de Jam`
- **Versión:** `1.0`
- **Fecha de creación / actualización:** `2026-09-10`
- **Estado:** `vigente`

---

## 2. Decisiones tomadas y justificación («por qué»)

### Tipo elegido: `GUIA`

En la convención declarada en `Vault-kb/00-Proceso/2026-07-29-GUIA-Convencion-Documentacion-Vault-v1.0.md`, los tipos tienen propósitos diferenciados:
- `INFORME`: describe lo que se midió o implementó (cerrado, experimental o histórico).
- `PLAN`: especifica trabajo pendiente o en curso.
- `CONCEPTO`: describe un principio de diseño abstracto, no una implementación concreta.
- `GUIA`: cómo se usa algo (tutoriales, manuales, convenciones de uso).

La nota original es fundamentalmente un **manual de referencia y uso práctico del lenguaje de comandos de Jam**:
1. Describe la arquitectura operativa del DSL (`dsl.py` y `panel.py:824`) y cómo se ejecuta desde la consola y la Dash Bar.
2. Define la sintaxis formal (`<verbo> [nombre_asset] [param=valor ...]`), reglas de insensitive casing, resolución de assets, aliases cortos (`n`, `s`, `h`, `t`) y coerción de booleanos.
3. Proporciona un catálogo de comandos de ejemplo para probar (`place`, `scatter`, `drop`, `spline`, `pivot`/`normalize`, `mesh_*`) y controles de flujo interactivo (`confirm`, `discard`, `verify`, `search`, `pick`, `preset`, `help`).

Por lo tanto, `GUIA` describe con máxima precisión la naturaleza del texto («cómo se usa el DSL de Jam»).

### Carpeta elegida: `04-Ejecucion-y-pruebas`

La taxonomía fija del Vault (`CARPETAS` en `tools/vault.py`) contempla cinco categorías:
1. `00-Proceso`: Proceso y dirección.
2. `01-Graph`: Graph — el editor de nodos.
3. `02-TreeGen`: TreeGen — el árbol procedural.
4. `03-Mesh-y-materiales`: Mesh y materiales.
5. `04-Ejecucion-y-pruebas`: Ejecución, presets y pruebas.

**Descarte de `05-DSL`:** La carpeta original `05-DSL` no existe en `CARPETAS` y era una de las causas directas del rojo en las medidas de vault. Agregar una sexta categoría alteraría la taxonomía del proyecto sin decisión previa del dueño.

**Por qué no `01-Graph`:** Se analizó `01-Graph` (que en la guía se menciona como «el editor de nodos y sus paneles»). Sin embargo:
- El Graph es el lienzo visual de nodos, cables y pines (`.jamgraph`).
- La propia nota contrasta explícitamente el DSL con el Graph en los puntos 1.3 y 1.4:
  - De los 171 verbos, 83 corren en la consola/DSL y 88 son exclusivos del Graph por requerir cables complejos (mallas `M`, frames `F`).
  - En el Graph, `scatter` sólo genera puntos (`P`) requiriendo un nodo `instance` posterior; en la consola, el comando `scatter` compone automáticamente el cálculo de puntos con `place` para una colocación inmediata.
- Conforme a `00-Proceso/2026-08-06-CONCEPTO-Graph-Autoria-Dash-Consumo-v1.0.md`, el Graph es el entorno de *autoría* de herramientas, mientras que la Dash Bar / consola es la superficie de *consumo*.

**Por qué `04-Ejecucion-y-pruebas`:**
- El DSL es el motor de ejecución en línea de comandos de Jam (`dsl.py` parsea y `panel.py:824` ejecuta).
- El documento detalla el ciclo de ejecución transaccional: previsualización (`preview`), confirmación (`confirm`) y descarte (`discard`).
- Cubre explícitamente la ejecución de presets (`preset list`, `preset "..."`) y la invocación de pruebas del oráculo (`verify`/`oracle`).
- Esta carpeta ya concentra los documentos sobre el modelo de ejecución y contratos unificados del plugin (`PLAN-Contrato-Unificado-Graph-Flow-Presets-Web`, `PLAN-Compilacion-Estricta-Preview-Bake`, `PLAN-Contratos-Defensivos-Tools-Assets`).

### Nombre de archivo y slug

- Patrón: `AAAA-MM-DD-TIPO-Nombre-vX.X.md`
- Fecha: `2026-09-10` (fecha de la nota original).
- TIPO: `GUIA`.
- Slug: `DSL-De-Jam` (ASCII estricto, sin tildes ni caracteres especiales, legible y conciso).
- Versión: `v1.0`.
- Resultado: `2026-09-10-GUIA-DSL-De-Jam-v1.0.md`.

### Tratamiento del contenido

- Se conservó íntegramente el contenido original bajo el nuevo título de nivel 1 `# El DSL (Domain-Specific Language) de Jam`.
- No se reescribió prosa, tablas ni ejemplos.
- Se limpiaron únicamente los espacios y caracteres en blanco sobrantes al final de cada línea resultantes del pegado original.

---

## 3. Documentos que deberían enlazar al nuevo (sugerencias)

Conforme a la regla de no modificar otros documentos del vault, se listan los documentos que se beneficiarían de enlazar a `[[2026-09-10-GUIA-DSL-De-Jam-v1.0|El DSL de Jam]]`:

1. `Vault-kb/README.md`:
   - Se actualizará automáticamente al regenerar el índice con `python tools/vault.py --indice`, incluyéndolo en la sección `## Ejecución, presets y pruebas`.
2. `Vault-kb/01-Graph/2026-08-11-INFORME-Definicion-De-Tools-Y-Superficies-v1.0.md`:
   - Analiza cómo una tool llega a la Dash Bar filtrando por `graph_only`. La guía del DSL es la referencia complementaria directa de cómo se invocan esos verbos en la barra.
3. `Vault-kb/00-Proceso/2026-08-06-CONCEPTO-Graph-Autoria-Dash-Consumo-v1.0.md`:
   - Expone la tesis de «Graph autor, Dash consumidor». Esta guía describe el lenguaje de consumo de la Dash Bar.
4. `Vault-kb/04-Ejecucion-y-pruebas/2026-07-25-PLAN-Contrato-Unificado-Graph-Flow-Presets-Web-v1.0.md`:
   - Define el contrato de ejecución entre Graph, Flow, Presets y Web/Consola.
5. `Vault-kb/01-Graph/2026-08-02-PLAN-Verbos-Math-Numeros-Vectores-Matrices-v1.0.md` y `Vault-kb/01-Graph/2026-08-12-PLAN-Multi-Salida-En-El-Graph-v1.0.md`:
   - Ambos documentos discuten el comportamiento de `dsl.coaccionar` al procesar parámetros.

---

## 4. Estado de la nota original y verificaciones

- **Nota original:** `Vault-kb/05-DSL/El DSL (Domain-Specific Language) de Jam.md` **no fue borrada** ni modificada. Queda en el árbol para que Claude proceda a su eliminación tras la revisión.
- **Verificaciones:** En apego a las instrucciones del encargo (**NO shell, NO tests, NO commits**), **no se corrió ninguna verificación por línea de comandos** (`tools/vault.py`, `oracle test`, ni diffs en git). La ejecución de las pruebas y la regeneración de fixtures quedan reservadas para Claude.
