# Hacer funcionar oracle-estudio desde el wheel instalado

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

## Evidencia

Al instalar un wheel local en un venv aislado y ejecutar `oracle-estudio --proyecto <checkout>
--destino <temporal>` fuera del árbol, el proceso sale con código 1: `tools/estudio.py`
busca `README.md` bajo `site-packages/oracle_metalenguaje/`, donde el wheel no lo incluye.
Desde el árbol, `python3 tools/estudio.py --destino <temporal>` sí generó los 10 documentos.
La mudanza de `repo-limpio` no resuelve esta frontera de empaquetado.

### Nota (2026-09-24 23:38:05 UTC)

Prueba de regresión agregada al wheel instalado: antes falló con FileNotFoundError en site-packages/oracle_metalenguaje/README.md; después genera 10 documentos desde --proyecto <checkout> fuera del árbol. El generador lee README, especificación, guía, código y git del checkout, y evita duplicar el catálogo base del wheel.

### Nota (2026-09-24 23:40:15 UTC)

Verificación: python3 -m unittest discover -s tests: 2440 tests, OK; python3 tools/cli.py test --rapido: VEREDICTO VERDE; python3 tools/estudio.py --destino <temporal>: 10 documentos; prueba del wheel aislado en verde. equivalentes.json no contiene ids de tools/estudio.py ni tests/test_cli_integracion.py, por lo que no hubo reapuntes.

## Próximo paso

Ninguno: tarea cerrada y verificada.
