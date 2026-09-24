# Contrato: la implementación de referencia, llevada al álgebra 0.8

Este archivo, `ESPECIFICACION.md`, `docs/decisiones/DECISION-001-RELACIONES-COMO-BOLSAS.md`,
`docs/decisiones/DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md`, `evaluador.py`, `test_evaluador.py` y `DECISIONES.md`
son **todo** lo que hay en este directorio, y todo lo que se puede leer. No hay otra implementación
que mirar, y no hay que buscarla.

`evaluador.py` es una implementación independiente del álgebra, escrita sólo a partir de la
especificación. Está al día con el álgebra `0.7`. La especificación ya describe la versión vigente
—su primera línea de §0 dice cuál es—. No se te dice qué cambió: encontrarlo leyendo es parte del
trabajo.

## Lo que hay que hacer

1. Llevar **`evaluador.py`** a la versión vigente del álgebra, sin dependencias fuera de la
   biblioteca estándar, con la misma superficie pública:

   ```python
   VERSION_ALGEBRA = "<la versión vigente>"

   class ErrorDeAlgebra(ValueError): ...

   def evaluar(medida: list, evidencia: dict, escalares: dict | None = None) -> dict: ...
   ```

   - `medida` es la **forma canónica** (JSON ya parseado); no hay que leer la superficie `.oracle`.
   - `evidencia` es un mapa `relación → lista de filas`.
   - Devuelve `"id"`, `"valor"` (o el texto exacto `"SIN EVIDENCIA"`), `"ok"` y `"testigos"`.
   - Toda medida mal formada, operación inválida o evidencia que no se puede juzgar levanta
     `ErrorDeAlgebra`. **Ninguna otra excepción puede escaparse de `evaluar`.**
   - Lo que ya estaba bien no se reescribe: el cambio tiene que ser el mínimo que pide la versión.

2. Ampliar **`test_evaluador.py`** (`unittest`) con los tests que te parezcan necesarios para lo nuevo,
   incluidos sus bordes. El test de la versión tiene que decir la vigente.

3. Agregar a **`DECISIONES.md`** cada punto donde la especificación te dejó margen, con la sección
   que quedó abierta y lo que elegiste. **Es la parte más valiosa de la entrega.**

## Reglas

- Sólo se lee y se escribe dentro de este directorio.
- Sin red, sin instalar paquetes, sin buscar otra implementación del álgebra.
- Si algo no está en la especificación, no lo inventes en silencio: decidilo y anotalo.
