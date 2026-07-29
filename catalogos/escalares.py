"""Funciones escalares declaradas — el mecanismo de UDF del álgebra.

Se **declaran** con `@escalar` en vez de importarse sueltas, por el mismo motivo que un umbral lleva
su defensa: lo que no está declarado no se puede inventariar, contar ni discutir. Importar una
función de Python a mano la mete al lenguaje por la puerta de atrás.

Hoy hay una sola, y eso es correcto: la regla dice que nada entra al lenguaje hasta que una medida lo
necesite.
"""

from __future__ import annotations

from nucleo.algebra import escalar


@escalar("contiene")
def contiene(texto, aguja) -> bool:
    """¿`aguja` aparece en `texto`? Sensible a mayúsculas a propósito: se usa para exigir que un
    `alcance` enuncie algo en negativo («NO ve…»), y ahí las mayúsculas son la señal."""
    return str(aguja) in str(texto)
