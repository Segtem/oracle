"""Implementación de los entry points; la distribución la instala bajo `oracle_metalenguaje`.

Acá se registra el alias de nivel superior `tools`, y el LUGAR es la decisión.

Hasta 0.3.2 lo hacía la fachada: importar `oracle_metalenguaje` metía `tools` en `sys.modules`, y
eso **hace desaparecer el `tools/` del consumidor**. Es el nombre de paquete más común que hay en un
repositorio, y se lo llevaba puesto un `import` que el consumidor hace para usar la biblioteca. Lo
encontró un consumidor real, que murió con `ModuleNotFoundError: No module named 'tools.referencias'`
sobre un paquete suyo que existía.

Registrarlo acá lo ata a lo único que lo necesita: los módulos de `tools/` se importan entre sí por
nombre absoluto (`from tools.sesion import resolver_cli`), y eso pasa cuando corre un entry point de
Oracle —su propio proceso, donde ocupar el nombre no le saca nada a nadie—. Un consumidor que sólo
usa `Motor` o `escalar` ya no lo ve.

`setdefault` y no asignación: si alguien ya tiene un `tools` cargado, gana el suyo. En el checkout
`__name__` ya es `tools`, así que la línea no hace nada.
"""

import sys

sys.modules.setdefault("tools", sys.modules[__name__])
