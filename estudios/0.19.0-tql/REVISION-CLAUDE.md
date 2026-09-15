# Revisión de Claude — 0.19.0 (consultas de tareas)

2026-09-15. Tarea [`20260915-023750-tql`](../../tareas/20260915-023750-tql/TAREA.md).

## Lo verificado

`tests/test_tareas_consulta_revision.py` —escrito contra el encargo antes de leer el código— pasa
entero sobre la entrega: gramática, precedencia, bordes de los comparadores, ID exacto, etiquetas sin
distinguir mayúsculas, errores con columna en caracteres, `--explicar` sin tracker, `--por-id` e
`--invertir`, `desetiquetar --consulta`, `referencias` sin ID e `init --sin-readme`. Con los tests de
agy y los del tracker, CLI y herramientas: 641 en verde. El AST tipado verifica los tipos al compilar,
como pedía el encargo.

## Corregido por Claude

La entrega agregaba superficie que el encargo no pedía y código sin conducta. Se corrigió en la
revisión, sin ronda de agy, porque ninguna corrección cambia el contrato pedido:

- **Comparadores simbólicos.** `tareas_consulta.py` aceptaba `<`, `<=`, `>`, `>=`, `==`, `=` y `!=`
  además de las palabras, y `docs/12-tareas.md` los documentaba. El dueño eligió sólo español, y
  `<`/`>` redirigen en la shell —la razón por la que tatr tampoco los usa—. Se quitaron del lenguaje y
  de la documentación; un test fija que salen 2.
- **Código muerto:** `PALABRAS_CLAVE` sin uso; valores por defecto de `getattr` que una `Tarea` nunca
  necesita; el `raise` de operador desconocido, inalcanzable; `bool()` redundantes. Los comparadores
  pasan a una tabla de operadores.
- **Dos formatos de error.** `listar` usaba `formato(texto)` y `desetiquetar` `str(e)`; ahora hay uno
  solo, y la consulta viaja con la excepción. Un test fija el `^` también en `desetiquetar`.
- **`-c` para `--consulta`**, no pedido; en tatr `-c` significa «cerradas». Quitado.
- `ID_COMPLETO_RE` está copiada en `tareas_consulta.py` porque importarla de `tareas.py` sería un ciclo;
  un test fija que las dos expresiones sean la misma.

## Para el registro

- `tools/mutar_codigo.py`, `.github/workflows/verificar.yml` y `tools/verificar_instalacion.py` —de
  Claude según el encargo— aparecieron modificados a las 07:52, durante la sesión de agy (hasta las
  08:08): registran `tareas_consulta.py` como custodia y agregan una consulta al recorrido instalado.
  El informe de agy afirma que esos archivos quedaron intactos. Los logs de agy no permiten atribuirlo.
  Los cambios son correctos y se conservan.
- `tareas_consulta.py` se siguió editando a las 08:07, después del informe (08:03).
