# Propuesta: simplificar la invocación confiada y el error de caso generar

- ESTADO: ABIERTA
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

## Próximo paso

Revisar esta propuesta junto con VERIFICACION.md de ergonomia y decidir su implementación; comenzar por el diagnóstico de caso generar y la receta local, sin cambiar el lenguaje.

### Nota (2026-09-23 20:10:02 UTC)

Implementada la forma mínima: receta oracle-local en README con proyecto y confianza explícitos, y captura de EscalaresNoConfiables/EscalaresInvalidas en cmd_caso_generar. Regresión real por subprocess: rechazo sin ejecución ni archivos; receta extraída del README y ejecutada para verificar argumentos, código de salida y los cinco comandos. Evidencia roja al retirar sólo la captura: verificacion/antes.log. Se conservan cambios previos de ergo-orden; sin cambios de álgebra/sintaxis ni commits.

## 2026-09-23 — cortada por cuota

Codex se quedó sin cuota a mitad del encargo. Lo hecho vive en la rama `t-ergo2` (commit WIP, no está
en `main`): mensaje de `tools/cli.py`, sección del README con el wrapper `oracle-local`, y
`tests/test_confianza_cli.py`. Falta revisar lo hecho, correr la suite y regenerar cifras. Se retoma
sobre esa rama.
