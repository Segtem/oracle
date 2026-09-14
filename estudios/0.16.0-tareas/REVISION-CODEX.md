# Revisión de Codex — primera implementación P0–P1

2026-09-11. Reproducciones por `python3 -B tools/cli.py tarea ...` en un directorio temporal,
sin modificar tareas reales. Estos fallos deben corregirse antes de cerrar la entrega.

Actualización 2026-09-12: observaciones corregidas y verificadas. El detalle siguiente conserva
los hallazgos históricos; los resultados finales están en [CIERRE-P0-P1.md](CIERRE-P0-P1.md).

## Fallos observados

1. `init --help` devuelve 0 y CREA `tareas/`; debe mostrar ayuda sin escrituras.
2. `listar --inventada` devuelve 0; argumentos desconocidos deben fallar. Aplicar el contrato a
   todos los verbos, incluyendo argumentos extra y combinaciones incompatibles.
3. `nueva --etiqueta bug "Titulo real" --json` crea una tarea titulada `bug`. El parser confunde
   valores de opciones con posicionales. `nueva bug --etiqueta bug` falla porque se borran TODAS
   las ocurrencias iguales al título. Usar argparse con un único parser de opciones por verbo,
   sin listas ad hoc ni eliminación por igualdad; soportar opciones antes/después del posicional.
4. `cerrar` convierte TODO un documento CRLF a LF, no sólo el estado. Preservar bytes fuera del
   valor del estado, incluyendo sangría, asterisco/guion, espacios y final de línea del campo.
5. Una carpeta normal con `TAREA.md` simbólico a un archivo fuera de `tareas/` se lee por `ver`,
   y `revisar` devuelve OK. Comprobar confinamiento tanto de carpeta como de archivo y raíz del
   tracker en TODOS los caminos (listar, revisar, ver, cerrar, reabrir, init, nueva). No basta
   con revisar la carpeta al resolver ID. Contemplar links rotos y ciclos con diagnóstico.
6. `nueva` con título que contiene saltos de línea acepta inyectar metadatos y devuelve éxito
   con un registro inválido. Rechazar saltos de línea en título/etiquetas antes de escribir nada.

## Problemas adicionales visibles en código/contrato que requieren fijación

- La auditoría no valida la identidad de las carpetas (acepta nombres fuera de YYYYMMDD-HHMMSS).
  Distinguir validez de ID completo y validez de prefijo. Diagnosticar candidatos rotos.
- Temp de actualización por PID es predecible y permite seguir un link preexistente. Usar
  tempfile con creación exclusiva; conservar permisos razonables y no truncar destinos ajenos.
- Generación seguida de mkdir puede colisionar entre procesos: reservar la carpeta con mkdir
  exclusivo y reintentar de manera acotada sin sobrescribir. El caso secuencial no prueba esto.
- No incorporar un ejecutable adicional `oracle-tarea` sólo porque el módulo existe: la interfaz
  asignada es `oracle tarea`. Si se conserva, justificarlo y verificar su paridad; prefiero retirarlo.
- El ejemplo KB dice que `-B` evita reutilizar .pyc. Es incorrecto: evita ESCRIBIR bytecode, no
  leer cachés válidas existentes. Corregir esa afirmación o usar un ejemplo ajeno a esa sutileza.
- No ampliar la búsqueda de ID a sufijos para satisfacer un test inventado: el contrato pide
  prefijos del ID. Si querés ofrecer también sufijos, justificar y documentar semántica/ambigüedad;
  no resolver un conflicto eligiendo una tarea silenciosamente.

## Coordinación

Agy conserva la propiedad de `tools/tareas.py`, CLI, docs y `tests/test_tareas.py`; Codex prepara
pruebas independientes en `tests/test_tareas_revision.py` y verificaciones reproducibles del
paquete instalado. No editar ese módulo de revisión para hacer desaparecer sus fallos.
No iniciar mutación hasta que ambos terminen las ediciones. Conservar resultados reales en el
informe. Una suite verde previa a estas correcciones no verifica la entrega final.

## Segunda pasada tras los 13 tests verdes

Reproducido en temporales después de las correcciones:

1. `tareas/README.md` como symlink roto a `../afuera.md`: `init` devuelve 0 y CREA el archivo
   externo. La política de no seguir links también se aplica a los auxiliares que se escriben.
   Crear README con apertura exclusiva; no seguir ni reemplazar enlaces ajenos.
2. `ver nombre-invalido` devuelve 0 si esa carpeta contiene TAREA.md aunque `revisar` denuncia
   el nombre. Validar ID completo también al resolver una coincidencia directa.
3. `ESTADO: abierta` carga bien por normalización, pero `cerrar` falla buscando sólo ABIERTA
   en mayúsculas. Mantener lectura/cambio consistentes y preservar lo demás.
4. `init <ruta-a-archivo>` produce traceback. Traducir errores del sistema de archivos en la
   frontera pública; lo mismo para fallos de escritura y lectura. No reportar éxito parcial.
5. Documentar el código 2 real de errores de argumentos (o unificarlo con 1), y preservar el
   modo del archivo en el reemplazo, puesto que el contrato dice cambiar sólo estado.

Codex amplió `tools/verificar_instalacion.py` con un recorrido instalado real del tracker; no editar
ese archivo mientras Codex lo verifica. La nueva prueba se ejecuta al correr el verificador normal.
