# Contrato de la implementación independiente del álgebra 0.7

Este archivo, `ESPECIFICACION.md`, `DECISION-001-RELACIONES-COMO-BOLSAS.md` y
`DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md` son **todo** lo que hay en este directorio, y todo lo
que se puede leer. No hay otra implementación que mirar, y no hay que buscarla.

## Lo que hay que escribir

1. **`evaluador.py`**, un módulo de Python ≥ 3.11 sin dependencias fuera de la biblioteca estándar,
   con exactamente esta superficie pública:

   ```python
   VERSION_ALGEBRA = "0.7"

   class ErrorDeAlgebra(ValueError):
       """Todo error del álgebra se informa con esta excepción, y con ninguna otra."""

   def evaluar(medida: list, evidencia: dict, escalares: dict | None = None) -> dict:
       ...
   ```

   - `medida` es la **forma canónica** de una medida (JSON ya parseado), tal como la describe
     `ESPECIFICACION.md`. No hay que leer la superficie `.oracle`: sólo la forma canónica.
   - `evidencia` es un mapa `relación → lista de filas`, y cada fila es un mapa `campo → escalar`.
   - `escalares` es un mapa `nombre → función` con las funciones escalares declaradas; puede venir
     vacío.
   - Devuelve un mapa con `"id"` (el id de la medida), `"valor"` (el número que produjo el resumen,
     o el texto exacto `"SIN EVIDENCIA"` cuando una relación requerida no aportó filas), `"ok"`
     (booleano) y `"testigos"` (lista de filas).
   - Cualquier medida mal formada, operación inválida o evidencia que la medida no puede juzgar
     levanta `ErrorDeAlgebra`. **Ninguna otra excepción puede escaparse de `evaluar`.**

2. **`test_evaluador.py`**, los tests que te parezcan necesarios, con `unittest`. Podés correrlos.

3. **`DECISIONES.md`**: cada punto donde la especificación te dejó margen y tuviste que elegir, con
   la sección que quedó abierta y lo que elegiste. **Es la parte más valiosa de la entrega**: no se
   busca un evaluador, se buscan los lugares donde el documento no alcanza para escribir uno.

## Reglas

- Sólo se lee y se escribe dentro de este directorio.
- Sin red, sin instalar paquetes, sin buscar otra implementación del álgebra.
- Si algo no está en la especificación, no lo inventes en silencio: decidilo y anotalo en
  `DECISIONES.md`.
