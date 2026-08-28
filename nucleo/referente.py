"""Declaración del referente que leyó un sensor (Nivel L−2).

La declaración no afirma que el referente exista ni que la huella le corresponda. Sólo deja juntos
el objeto que el sensor dice haber leído, la huella que declaró al leerlo y el momento de esa
lectura. La comprobación de frescura —comparar esa huella con otra posterior— es otra etapa.

Forma canónica JSON, por referente:

```json
["referente", "Content/Props/silla.uasset", "sha256:...", "2026-08-27T09:14:00"]
```

Una colección de declaraciones se reifica como la relación `referente_declarado`. El campo
`tiene_huella` no reemplaza la huella: hace observable para el lenguaje si la declaración vino sin
una, sin inventar un valor por omisión.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class ReferenteMalDeclarado(ValueError):
    pass


# El catálogo descubre esta relación leyendo el emisor, igual que `relacion.py` declara las suyas.
RELACIONES_DE_REFERENTE = frozenset({"referente_declarado"})


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


def como_hechos(referentes: Iterable[Referente]) -> dict[str, list[dict]]:
    return hechos_de_referentes(referentes)
