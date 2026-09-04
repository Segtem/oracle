"""Declaración del referente que leyó un sensor (Nivel L−2).

La declaración no afirma que el referente exista ni que la huella le corresponda. Sólo deja juntos
el objeto que el sensor dice haber leído, la huella que declaró al leerlo y el momento de esa
lectura. La frescura se expresa emparejando esa declaración con otra posterior: el emisor presenta
las dos huellas y una medida del lenguaje hace la comparación.

Forma canónica JSON, por referente:

```json
["referente", "Content/Props/silla.uasset", "sha256:...", "2026-08-27T09:14:00"]
```

Una colección de declaraciones se reifica como la relación `referente_declarado`. Dos colecciones,
al leer y ahora, se reifican como `referente_comparado`. El campo
`tiene_huella` no reemplaza la huella: hace observable para el lenguaje si la declaración vino sin
una, sin inventar un valor por omisión.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class ReferenteMalDeclarado(ValueError):
    pass


# El catálogo descubre esta relación leyendo el emisor, igual que `relacion.py` declara las suyas.
RELACIONES_DE_REFERENTE = frozenset({"referente_declarado", "referente_comparado"})

AMBITOS_DE_RELACIONES = {
    "referente_declarado": "universal",
    "referente_comparado": "universal",
}


@dataclass(frozen=True)
class Referente:
    que: str
    huella: str
    cuando: str

    def __post_init__(self) -> None:
        for nombre, valor in (("que", self.que), ("huella", self.huella),
                              ("cuando", self.cuando)):
            if not isinstance(valor, str):
                raise ReferenteMalDeclarado(
                    f"`{nombre}` tiene que ser texto, no {type(valor).__name__}")
        if not self.que.strip():
            raise ReferenteMalDeclarado("`que` no puede estar vacío")
        if not self.cuando.strip():
            raise ReferenteMalDeclarado("`cuando` no puede estar vacío")

    @classmethod
    def de_datos(cls, datos: list) -> "Referente":
        if not (isinstance(datos, list) and len(datos) == 4 and datos[0] == "referente"):
            raise ReferenteMalDeclarado(
                "un referente es ['referente', que, huella, cuando]")
        _, que, huella, cuando = datos
        return cls(que=que, huella=huella, cuando=cuando)

    def a_datos(self) -> list:
        return ["referente", self.que, self.huella, self.cuando]


def hechos_de_referentes(referentes: Iterable[Referente]) -> dict[str, list[dict]]:
    """Sirve un conjunto de declaraciones como hechos que el lenguaje puede medir."""
    try:
        iterador = iter(referentes)
    except TypeError as e:
        raise ReferenteMalDeclarado(
            f"se esperaba una colección de Referente, no {type(referentes).__name__}") from e

    filas = []
    for indice, referente in enumerate(iterador):
        if not isinstance(referente, Referente):
            raise ReferenteMalDeclarado(
                f"referente[{indice}] tiene que ser Referente, no {type(referente).__name__}")
        filas.append({
            "que": referente.que,
            "huella": referente.huella,
            "cuando": referente.cuando,
            "tiene_huella": bool(referente.huella.strip()),
        })
    return {"referente_declarado": filas}


def hechos_de_frescura(
    leidos: Iterable[Referente],
    actuales: Iterable[Referente],
) -> dict[str, list[dict]]:
    """Empareja declaraciones por `que`; no decide si las huellas coinciden."""
    filas_leidas = hechos_de_referentes(leidos)["referente_declarado"]
    filas_actuales = hechos_de_referentes(actuales)["referente_declarado"]

    def indexar(filas: list[dict], momento: str) -> dict[str, dict]:
        indice = {}
        for fila in filas:
            que = fila["que"]
            if que in indice:
                raise ReferenteMalDeclarado(
                    f"el referente {que!r} aparece repetido en la declaración {momento}")
            indice[que] = fila
        return indice

    por_leido = indexar(filas_leidas, "al leer")
    por_actual = indexar(filas_actuales, "actual")
    if set(por_leido) != set(por_actual):
        faltan = sorted(set(por_leido) - set(por_actual))
        sobran = sorted(set(por_actual) - set(por_leido))
        raise ReferenteMalDeclarado(
            f"los referentes actuales no corresponden a los leídos; faltan {faltan}, sobran {sobran}"
        )

    filas = []
    for que, leido in por_leido.items():
        actual = por_actual[que]
        filas.append({
            "que": que,
            "huella_leida": leido["huella"],
            "huella_actual": actual["huella"],
            "cuando_lectura": leido["cuando"],
            "cuando_actual": actual["cuando"],
        })
    return {"referente_comparado": filas}


def como_hechos(referentes: Iterable[Referente]) -> dict[str, list[dict]]:
    return hechos_de_referentes(referentes)
