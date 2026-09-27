# Avance: Mutación por niveles, paralelismo (-j N) y selección de tests

**Fecha**: 2026-09-27  
**Tarea**: `20260926-212700-mutacion-niveles`  
**Autor**: agy (en contenedor de worktree)

---

## 1. Resumen de lo implementado

Se implementó el diseño completo especificado en la tarea para los dos ejes ortogonales de la mutación de código:

### Eje 1: Velocidad (Paralelismo y Selección de Tests)
1. **Concurrencia multislot con aislamiento estricto**:
   - Argumento `-j N` / `--paralelo N` en `tools/mutar_codigo.py` (por omisión `max(1, núcleos // 2)`).
   - Runner paralelo en `perfiles/python/mutacion_codigo.py`: crea `N` slots independientes, cada uno con su propia copia completa del proyecto y su propio subdirectorio `TMPDIR` aislado (`tmp/slot_i`), evitando colisiones de archivos temporales entre procesos concurrentes.
   - Mantiene el bloqueo global por raíz de proyecto (`bloqueo.lock`).
   - El límite `--limite-memoria-mb` aplica de forma independiente por proceso hijo (`RLIMIT_AS`), sin exceder el presupuesto configurado.
   - Manifiesto atómico y reanudación thread-safe (`--manifiesto` / `--reanudar`) con sincronización mediante mutex y orden canónico determinista de mutantes, garantizando consistencia absoluta entre corridas con `-j N` y `-j 1`.

2. **Selección previa de tests con mapa de cobertura**:
   - Rastreador de cobertura en `tools/ejecutar_suite_mutacion.py` (`_RastreadorCobertura`) utilizando `sys.monitoring` en Python 3.12+ con fallback automático a `sys.settrace` (stdlib estándar, sin dependencias externas).
   - Opciones CLI `--guardar-cobertura` y `--objetivo-cobertura` en `ejecutar_suite_mutacion.py` para emitir el mapa JSON `{archivo: {linea: [tests...]}}`.
   - Captura automática de cobertura durante la corrida de línea base en `correr()`.
   - Ejecución en dos fases por mutante: primero se corren únicamente los tests que pasan por la línea mutada; si cualquiera falla, el mutante se declara muerto inmediatamente sin pagar el costo de la suite completa. Si ninguno falla o no hay tests mapeados, se ejecuta la suite completa de confirmación. Ningún sobreviviente es declarado vivo sin haber pasado la suite entera.

### Eje 2: Alcance (Niveles de Mutación)
1. **Cuatro niveles basados en Git**:
   - `--bajo`: sitios en líneas modificadas contra `HEAD` (`git diff -U0 HEAD`, incluyendo modificaciones locales no commiteadas en el árbol de trabajo o índice). Marca la ronda como parcial (`parcial: true`, código de salida 2).
   - `--medio`: sitios en líneas modificadas desde el último tag de Git (`git describe --tags --abbrev=0`). Marca la ronda como parcial (código de salida 2).
   - `--alto`: módulos enteros del perfil que hayan tenido cambios desde el último tag. Ronda completa de esos módulos (código de salida 0 si todos mueren, lo requerido para validar un release).
   - `--muy-alto`: todo el perfil completo de código del núcleo y herramientas custodias.
   - Sin nivel: comportamiento preexistente sin cambios.

2. **Validación estricta de exclusión y combinaciones**:
   - Los cuatro niveles son mutuamente excluyentes entre sí.
   - Ningún nivel admite `--lineas` ni `--sitio`.
   - `--alto` y `--muy-alto` definen su propio conjunto de módulos y no admiten `--objetivo`.
   - `--bajo` y `--medio` admiten `--objetivo` para acotar la inspección de líneas modificadas a módulos específicos.
   - Funciones auxiliares en `tools/mutar_codigo.py`: `_git`, `ultimo_tag`, `lineas_cambiadas_git`, `modulos_cambiados_git`, `validar_argumentos`.

3. **Documentación y sincronización**:
   - Ayuda CLI y docstrings de `tools/mutar_codigo.py`.
   - Sección `## Niveles de mutación y paralelismo (-j N)` en `docs/mutacion-memoria.md`.
   - Sincronización de `docs/mutacion-memoria.html` mediante `python3 -B tools/sitio.py --escribir`.
   - Reubicación automática de la declaración de mutante equivalente en `equivalentes.json` (`tools/mutar_codigo.py:796:31:constante`) mediante `--reapuntar-equivalentes`.

---

## 2. Archivos modificados y creados

- `tools/ejecutar_suite_mutacion.py`: Rastreador de cobertura con `sys.monitoring`/`sys.settrace`, argumentos `--guardar-cobertura` y `--objetivo-cobertura`.
- `perfiles/python/mutacion_codigo.py`: Runner paralelo multislot con copias y `TMPDIR` aislados, soporte de `mapa_cobertura`, `comando_seleccion`, y preservación del orden determinista de resultados.
- `tools/mutar_codigo.py`: Soporte de `-j`/`--paralelo`, niveles `--bajo`, `--medio`, `--alto`, `--muy-alto`, validaciones de exclusividad, funciones de git y docstring actualizado.
- `equivalentes.json`: Reubicada la entrada de `tools/mutar_codigo.py` tras añadir las nuevas funciones.
- `docs/mutacion-memoria.md`: Sección explicativa sobre velocidad (paralelismo y selección) y alcance (niveles).
- `docs/mutacion-memoria.html`: Regenerado vía `tools/sitio.py --escribir`.
- `tests/test_mutar_codigo_niveles.py`: Suite nueva con pruebas de Git en repos temporales, validación de opciones, paralelismo `-j 1` vs `-j 2` vs `-j 4`, y contrato de selección de tests.

*(No se tocaron `tools/cli.py` ni `oracle_metalenguaje/`).*

---

## 3. Pruebas ejecutadas y evidencia

Todas las ejecuciones se realizaron con `python3 -B`:

1. **`tests/test_mutar_codigo_niveles.py`**:
   - 12 tests en 1.93s, OK.
   - Verifica:
     - `GitReposTemporalesTests`: `ultimo_tag` con y sin tags, `lineas_cambiadas_git` (HEAD vs tag, cambios unstaged y staged), `modulos_cambiados_git`.
     - `OpcionesYNivelesValidacionTests`: rechazo de `-j 0`, exclusión mutua de niveles, incompatibilidad con `--lineas`/`--sitio`/`--objetivo`, y error explicativo cuando ningún módulo cambió desde el tag.
     - `ParalelismoTests`: corrida de un objetivo de juguete con mutantes reales comparando `-j 1` contra `-j 2` y `-j 4`. Los identificadores de mutantes, sus estados individuales, su resultado de muerte y las estadísticas globales son 100% idénticos.
     - `SeleccionTests`: prueba que el runner con selección ejecuta los tests directos, y confirma que todo mutante que la suite completa mata es declarado muerto sin excepción (nunca se declara vivo).

2. **`tests/test_mutacion_codigo.py`**:
   - 108 tests en 11.22s, OK.
   - Pasan todos los contratos de límite de memoria, aislamiento de copias, manifiesto y filtros.

3. **`tests/test_mutar_codigo_custodia.py`**:
   - 32 tests en 0.075s, OK.

4. **`tests/test_ejecutar_suite_mutacion.py`**:
   - 20 tests en 0.59s, OK.

5. **`tests/test_sitio.py` y `tests/test_sitio_rapido.py`**:
   - 25 tests en 0.27s, OK.

6. **Suite completa del repositorio**:
   - Comando: `python3 -B -m unittest discover -s tests`
   - Resultado: **Ran 2711 tests in 135.897s, OK**.
   - Toda la suite quedó 100% en verde.

---

## 4. Tiempos medidos

- Overhead de `sys.monitoring` sobre la suite en línea base: < 5 ms en el registro de eventos de línea.
- Suite de niveles y paralelismo (`tests/test_mutar_codigo_niveles.py`): 1.93s (12 tests, incluyendo inicializaciones de git y corridas multislot `-j 1`, `-j 2` y `-j 4`).
- Suite completa del repositorio (2711 tests): 135.897s.

---

## 5. Próximo paso

Queda listo para que Claude corra en el host la comparación final de una ronda real completa (`--alto` con `-j` y selección de tests vs corrida secuencial de referencia).
