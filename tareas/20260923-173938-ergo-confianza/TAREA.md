# Propuesta: simplificar la invocación confiada y el error de caso generar

- ESTADO: CERRADA
- PRIORIDAD: 70
- ETIQUETAS: ergonomia, propuesta

## Alcance propuesto

Derivada de [ergonomia](../20260923-120207-ergonomia/VERIFICACION.md), entrada 6.1, grupo 1. Es una propuesta: no se implementó en la auditoría.

El arnés de ergonomia reproduce la exigencia de confianza en cinco comandos, aun con escalares.py sin funciones y medidas sin llamadas externas. Caso generar además deja escapar EscalaresNoConfiables con traceback.

La forma mínima es documentar un wrapper local que pase explícitamente --proyecto y --confiar-escalares, y unificar el tratamiento de esa excepción en caso generar. No habilitar ejecución externa por omisión ni introducir un mecanismo global de confianza persistente.

## Aceptación propuesta

- El wrapper permite los comandos afectados conservando argumentos y códigos de salida.
- Sin confianza, caso generar informa la causa y cómo continuar sin traceback ni archivos generados; no ejecuta el archivo externo.
- Los demás comandos conservan su contrato. VERSION_ALGEBRA 0.8 y VERSION_SINTAXIS 0.6 no cambian.

### Nota (2026-09-23 17:43:54 UTC)

Propuesta derivada de ergonomia 6.1: cinco comandos reproducidos y traceback de caso generar en SALIDAS.txt. Sólo se escribió alcance y aceptación; sin implementación ni commits.

### Nota (2026-09-23 20:10:02 UTC)

Implementada la forma mínima: receta oracle-local en README con proyecto y confianza explícitos, y captura de EscalaresNoConfiables/EscalaresInvalidas en cmd_caso_generar. Regresión real por subprocess: rechazo sin ejecución ni archivos; receta extraída del README y ejecutada para verificar argumentos, código de salida y los cinco comandos. Evidencia roja al retirar sólo la captura: verificacion/antes.log. Se conservan cambios previos de ergo-orden; sin cambios de álgebra/sintaxis ni commits.

## 2026-09-23 — cortada por cuota

Codex se quedó sin cuota a mitad del encargo. Lo hecho vive en la rama `t-ergo2` (commit WIP, no está
en `main`): mensaje de `tools/cli.py`, sección del README con el wrapper `oracle-local`, y
`tests/test_confianza_cli.py`. Falta revisar lo hecho, correr la suite y regenerar cifras. Se retoma
sobre esa rama.

### Nota (2026-09-23 22:48:07 UTC)

Revisado HEAD 8b4418b: la captura y la receta local cumplen el alcance mínimo, sin tocar lenguaje. Se reforzó test_confianza_cli: la equivalencia wrapper/directo podía aprobar con ambos en error por corpus vacío; ahora el fixture tiene casos verde y rojo y exige exit 0 para los cinco comandos. Tres tests pasan; al retirar temporalmente sólo la captura fallan las regresiones (verificacion/antes.log), luego se restauró. Suite completa en curso.

### Nota (2026-09-23 22:49:54 UTC)

Aceptación completa: los 3 tests específicos pasan; sin la captura fallan 4 subcasos (antes.log). Suite solicitada: python3 -m unittest discover -s tests, exit 0, 2422 tests en 86.377s, OK (verificacion/suite.log). Ejecutado python3 tools/cifras.py --actualizar: README actualizado a 2422 tests y 7909 sitios; comprobación posterior CIFRAS OK. Se conserva la implementación mínima del WIP; sólo se reforzó el fixture y la aserción de éxito. Álgebra 0.8 y sintaxis 0.6 intactas. Sin commits ni escrituras en .git.

## Próximo paso

Ninguno: tarea completa y CERRADA. Evidencia en `verificacion/antes.log`, `despues.log` y `suite.log`; cifras regeneradas. Cambios listos para revisión, sin commits por instrucción del usuario.
