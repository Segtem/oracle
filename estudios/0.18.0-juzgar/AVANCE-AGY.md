# Avance 0.18.0 — Hallazgo P0 y Plan de Implementación (`oracle juzgar`)

**Fecha:** 2026-09-15  
**Autor:** AGY (Antigravity)  
**Revisa y verifica:** Claude (Claude Code)  
**Encargo:** `estudios/0.18.0-juzgar/ENCARGO-AGY.md`  
**Plan base:** `PLAN-0.18.0-JUZGAR.md`

---

## 1. Recepción y Cumplimiento de Restricciones

Se confirma la recepción del encargo para el tramo 0.18.0.
Se respetan estrictamente todas las reglas operativas:
- **Exclusivamente herramientas de lectura y edición de archivos**: no se ejecutarán comandos de shell (`run_command`), no se correrán suites de pruebas, no se invocarán herramientas de mutación, no se crearán ni usarán subagentes, no habrá acceso a red ni operaciones de Git / commits.
- **Propiedad estricta de archivos**:
  - Propiedad de AGY: `tools/juzgar.py` (nuevo), `tools/cli.py` (despacho, alias, ayudas), `tests/test_juzgar.py` (nuevo), sección en `docs/12-tareas.md`, `estudios/0.18.0-juzgar/AVANCE-AGY.md` e `INFORME-AGY.md`.
  - Propiedad exclusiva de Claude (NO tocar): `README.md`, `NOTAS-DE-RELEASE.md`, `ESPECIFICACION.md`, `nucleo/version.py`, `ejemplo/seguimiento-tareas/`, `tools/verificar_instalacion.py`, `tools/mutar_codigo.py`, `.github/`, `docs/manual.html`, tests existentes y de revisión.

---

## 2. P0: Con qué catálogo juzga hoy un consumidor

Se realizó la lectura exhaustiva del código fuente del repositorio para responder las tres preguntas planteadas:

### 2.1. Selección de medidas en `oracle test` / `tools/aceptacion.py` para proyectos externos

1. **Función y selección de medidas**:
   - En `tools/cli.py` (`cmd_test`, línea 877):
     ```python
     rc_aceptacion = aceptacion._ejecutar(proy)
     ```
   - En `tools/aceptacion.py` (`_ejecutar`, línea 105):
     ```python
     catalogo = catalogo_efectivo(proy, macros=macros_del_proyecto(proy))
     ```
   - En `nucleo/proyecto.py` (`catalogo_efectivo`, líneas 380–410):
     `catalogo_efectivo` carga las fuentes con `catalogos_a_cargar(proy, raices_perfiles=raices_perfiles)` (línea 399) y luego **filtra estrictamente por ámbito** (`ambito`):
     ```python
     return catalogo.filtrar(
         lambda entrada: (
             entrada.medida.ambito in ("universal", AMBITO_SIN_DECLARAR)
             or (entrada.medida.ambito == "del_origen"
                 and _el_origen_es_el_proyecto(entrada.origen, proy))
         )
     )
     ```
   - En `nucleo/proyecto.py` (`_el_origen_es_el_proyecto`, líneas 373–377):
     ```python
     def _el_origen_es_el_proyecto(origen: OrigenCatalogo, proy: "Proyecto") -> bool:
         if origen == ORIGEN_PROYECTO:
             return True
         return origen == ORIGEN_CATALOGO_BASE and proy.es_el_propio_oracle
     ```
     Para un proyecto externo, si este activa `"catalogo_base": true`, las medidas base del catálogo empaquetado de Oracle que tengan `ambito: del_origen` (18 de las 55 medidas base según DECISION-012) son **descartadas**: NO forman parte de su `catalogo_efectivo`. Sólo entran las `universal` (o `sin_declarar`) y las medidas locales de su propio catálogo.

2. **Aplicación de sombras (`sombra`)**:
   - En `tools/aceptacion.py` (`_ejecutar`, líneas 196–212):
     ```python
     en_sombra = {e.medida for e in configuracion(proy).sombra}
     ...
     if v.id in en_sombra:
         ensombrecidas.append(v)
     else:
         fallas.append(f"{v.id}: el marco no cumple su propia regla")
     ```
     En `aceptacion._ejecutar`, una medida que produce veredicto `v.ok == False` **no añade falla** a la suite si su identificador figura en `en_sombra`: la sombra tolera el rojo y evita que la corrida caiga. (Además, en líneas 215–246, las medidas que vigilan la sombra inspeccionan su vigencia y cota).

---

### 2.2. Qué usa `Motor.desde_proyecto`

En `oracle_metalenguaje/motor.py` (`Motor.desde_proyecto`, líneas 135–160):
```python
with escalares_del_proyecto(
        proy, confiar=confiar_escalares, registro=registro):
    catalogo = cargar_catalogo(
        catalogos_a_cargar(proy, raices_perfiles=raices_perfiles),
        registro=registro,
        limites=limites_propios,
        macros=macros,
    )
return cls._crear(
    catalogo.values(), registro, limites_propios, proyecto=raiz)
```
Y en `Motor.evaluar` (líneas 170–180):
```python
def evaluar(self, evidencia: dict) -> Informe:
    aplicables = medidas_aplicables(self._medidas, evidencia)
    if not aplicables:
        raise SinMedidasAplicables(
            "ninguna medida es aplicable a las relaciones declaradas en la evidencia")
    return evaluar(
        aplicables,
        evidencia,
        self.limites,
        registro=self._registro,
    )
```

**Diferencias concretas de `Motor` frente a `oracle test`**:
1. `Motor.desde_proyecto` carga usando directamente `catalogos_a_cargar(proy)`.
2. **NO llama a `catalogo_efectivo`**: no aplica el filtro de `ambito`. En consecuencia, si el proyecto tiene `"catalogo_base": true`, `Motor._medidas` conserva las 18 medidas del catálogo base que tienen `ambito: del_origen`. Si una evidencia aportada por el consumidor contiene relaciones leídas por alguna de esas medidas, `Motor.evaluar` la considera aplicable y la evalúa, violando la jurisdicción declarada en DECISION-012.
3. **NO aplica sombras**: `Motor` no lee `configuracion(proy).sombra`. En `Motor.evaluar`, devuelve un `Informe` donde `informe.ok = all(v.ok for v in self.veredictos)`. Cualquier veredicto rojo hace que `informe.ok` sea `False`, ignorando completamente si la medida estaba declarada en sombra en `oracle.json`.

---

### 2.3. Proyecto mínimo reproducible donde `Motor.evaluar` y `oracle test` difieren

Se describe un proyecto mínimo concreto para que Claude pueda reproducir la discrepancia:

#### Caso 1: Divergencia por `ambito` (`del_origen` del catálogo base)
- **Estructura del proyecto**:
  - `oracle.json`:
    ```json
    {
      "esquema": "oracle.proyecto/v1",
      "catalogo_base": true
    }
    ```
  - `catalogos/demo/`: directorio con una medida inocua (o vacío).
  - `corpus/demo/001-dummy.caso`: caso válido para aceptación.
- **Evidencia evaluada por el consumidor**:
  ```json
  {
    "verbo_del_cli": [
      {
        "sustantivo": "proyecto",
        "verbo": "inventado",
        "nombrado_en_la_ayuda": false
      }
    ]
  }
  ```
- **Comportamiento en `oracle test` / `catalogo_efectivo`**:
  La medida `meta.todo_verbo_del_cli_esta_en_la_ayuda` tiene `ambito: del_origen` en `catalogos/meta/meta.todo_verbo_del_cli_esta_en_la_ayuda.oracle`. Al evaluar el proyecto externo, `_el_origen_es_el_proyecto(ORIGEN_CATALOGO_BASE, proy)` devuelve `False`. Por lo tanto, `catalogo_efectivo` **descarta la medida**. No existe ninguna medida aplicable a `verbo_del_cli` en el catálogo efectivo.
- **Comportamiento en `Motor.desde_proyecto`**:
  `Motor.desde_proyecto` cargó `meta.todo_verbo_del_cli_esta_en_la_ayuda` porque usó `catalogos_a_cargar`. Al llamar a `Motor.evaluar(evidencia)`, la medida es considerada aplicable. La evalúa: encuentra 1 fila donde `nombrado_en_la_ayuda == false`, con umbral `<= 0`. Resultado: **ROJO (✗)**, `informe.ok == False`.
- **Diagnóstico**: `Motor.evaluar` juzga al consumidor con una regla sobre la que no tiene jurisdicción ni posibilidad de remedio (infracción directa de DECISION-009 y DECISION-012).

#### Caso 2: Divergencia por `sombra`
- **Estructura del proyecto**:
  - `catalogos/demo/demo.infraccion.oracle`:
    ```oracle
    ninguno demo.infraccion:
        de item i
        donde i.falla == true
        umbral <= 0 segun contrato porque "cero fallas"
        ambito universal
        alcance "NO ve nada mas"
    ```
  - `oracle.json`:
    ```json
    {
      "esquema": "oracle.proyecto/v1",
      "catalogo_base": false,
      "sombra": {
        "demo.infraccion": {
          "desde": "2026-09-15",
          "porque": "deuda tecnica temporal"
        }
      }
    }
    ```
- **Evidencia**:
  ```json
  {"item": [{"id": "1", "falla": true}]}
  ```
- **Comportamiento**:
  - En `oracle test` / `aceptacion`: `demo.infraccion` falla pero está en `sombra`, por lo que se marca `[EN SOMBRA]` y la corrida sale en **VERDE** (código 0).
  - En `Motor.desde_proyecto`: `Motor` ignora `sombra` y devuelve `informe.ok == False` (**ROJO**).

#### Decisión arquitectónica para P1
Conforme al encargo:
> **No corregir nada todavía en `Motor`**: escribirlo en `AVANCE-AGY.md` y seguir con P1 usando la selección de `oracle test`, aislada en una función que ambos puedan compartir después.

Para `P1` (`tools/juzgar.py`), aislaremos la selección correcta en una función reutilizable:
```python
def catalogo_para_juzgar(proy: Proyecto, *, raices_perfiles=(), registro=None,
                         limites=None, macros=None) -> Catalogo:
    """Selección efectiva de medidas para juzgar (idéntica a oracle test)."""
    if macros is None:
        macros = macros_del_proyecto(proy, raices_perfiles=raices_perfiles)
    return catalogo_efectivo(
        proy,
        raices_perfiles=raices_perfiles,
        registro=registro,
        limites=limites,
        macros=macros,
    )
```
Cuando Claude y el dueño del proyecto decidan actualizar la fachada `Motor`, `Motor.desde_proyecto` podrá invocar esta misma función (o delegar en `catalogo_efectivo`).

---

## 3. Plan de Archivos para P1

1. **`tools/juzgar.py` (Nuevo)**:
   - Implementación de `cmd_juzgar(proy: Proyecto, argv: list[str]) -> int`.
   - Parseo y validación de argumentos CLI:
     - `--con <ruta>` obligatorio. Faltante o sin ruta -> código 2, diagnóstico a `stderr`.
     - `--json`: salida en formato JSON vía `Informe.a_json()` sin ningún ruido en `stdout`.
     - `--confiar-escalares`: autorización explícita para `escalares.py`.
     - `--medida <id>`: repetible, sin duplicados. Si un ID está duplicado, no existe en el catálogo o no es aplicable a la evidencia -> código 2 con diagnóstico explícito nombrando el ID.
   - Lectura segura de evidencia:
     - Archivo físico, dentro de tope de tamaño explícito (`LIMITE_TAMANO_EVIDENCIA = 50 * 1024 * 1024` = 50 MiB).
     - Decodificación UTF-8 estricta (`errors="strict"`).
     - Validación estructural: objeto JSON (diccionario) con claves texto y valores listas de objetos (filas diccionario).
     - Archivo ausente, ilegible, tamaño excedido, UTF-8 inválido, JSON roto o estructura inválida -> código 2 a `stderr`, sin traceback.
   - Carga del catálogo efectivo con `catalogo_para_juzgar`:
     - Presencia de `escalares.py` sin `--confiar-escalares` -> código 2 con el mismo mensaje que `oracle test`.
     - Proyecto sin `catalogos/` o `oracle.json` roto -> código 2.
   - Aplicabilidad:
     - `medidas_aplicables(medidas, evidencia)`: si está vacía -> código 1, mensaje «SIN MEDIDAS APLICABLES» enumerando las relaciones aportadas en la evidencia.
   - Evaluación y emisión de veredicto:
     - `evaluar(aplicables, evidencia, limites, registro=registro)`
     - Salida: `Informe.texto()` por defecto en `stdout`; `Informe.a_json()` con `--json`.
     - Retorno: código 0 si `informe.ok` es verdadero, código 1 si no.

2. **`tools/cli.py` (Modificación)**:
   - Registro del verbo `juzgar` en `VERBOS["proyecto"]`.
   - Declaración de alias `oracle juzgar` en `ALIAS` y `VERBOS_DIRECTOS` (`"juzgar"`).
   - Documentación en docstring `__doc__`, `ayuda()`, y `ayuda_proyecto()`.
   - Despacho en `main()` para `oracle proyecto juzgar` y el alias directo `oracle juzgar`.

3. **`tests/test_juzgar.py` (Nuevo)**:
   - Pruebas unitarias y de integración del comando por CLI (`cli.main`):
     - Veredicto verde con alcance enumerado (código 0).
     - Veredicto rojo con testigos (código 1).
     - `--json`: salida parseable en `stdout` y limpia de diagnósticos.
     - Formas inválidas de evidencia: archivo ausente, no objeto, lista en vez de objeto, fila no objeto, JSON malformado, archivo > 50 MiB, UTF-8 inválido -> código 2 sin traceback.
     - Evidencia sin medidas aplicables -> código 1, «SIN MEDIDAS APLICABLES».
     - `--medida` con ID válido, inexistente, no aplicable y duplicado -> código 2 nombrando el ID.
     - `escalares.py` sin `--confiar-escalares` -> código 2; con `--confiar-escalares` -> ejecución autorizada.
     - Proyecto inválido -> código 2.
     - Paridad total entre `oracle proyecto juzgar` y el alias directo `oracle juzgar`.
     - Ayuda (`--help`) sin escrituras a disco.
     - Integración con el tracker: ejecución de `oracle tarea hechos` sobre un tracker temporal, juzgándolo con `ejemplo/seguimiento-tareas` en verde, y luego construyendo un defecto (referencia rota) para obtener código 1 con su testigo.

4. **`docs/12-tareas.md` (Modificación)**:
   - Nueva sección: cómo juzgar hechos reales del tracker con `oracle juzgar` contra las tres políticas de `ejemplo/seguimiento-tareas`.
   - Significado de cada política (`referencias_locales_presentes`, `archivos_confirmados_sin_cambios`, `lectura_sin_omisiones`).
   - Qué cubre y qué NO prueba cada política.

5. **`estudios/0.18.0-juzgar/INFORME-AGY.md` (Nuevo)**:
   - Informe final con la descripción de los cambios, respuestas de P0, detalle de la suite de pruebas implementada y declaración formal de no haber ejecutado verificaciones en el entorno.
