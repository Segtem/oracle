"""Un escenario DADO/CUANDO/ENTONCES, escrito a mano o sacado de una spec de OpenSpec.

Acepta las palabras en inglés (GIVEN, WHEN, THEN, AND) y en castellano (DADO, CUANDO, ENTONCES, Y),
siempre en MAYÚSCULAS para que la «y» de una oración no se lea como palabra clave. Las viñetas y el
`**negrita**` de OpenSpec se ignoran; las subviñetas se pegan a la cláusula anterior.
"""

from __future__ import annotations

import re
from pathlib import Path

CLAVES = {"GIVEN": "dado", "DADO": "dado", "WHEN": "cuando", "CUANDO": "cuando",
          "THEN": "entonces", "ENTONCES": "entonces", "AND": None, "Y": None}
_CLAVE_RE = re.compile(r"(?<!\S)(" + "|".join(CLAVES) + r")(?=[\s:]|$)")


def leer(texto: str) -> dict[str, list[str]]:
    """Las cláusulas del escenario, en orden. Sin CUANDO o sin ENTONCES no es un escenario."""
    limpio = re.sub(r"^\s*[-*]\s+", "", texto.replace("**", ""), flags=re.M)
    partes = _CLAVE_RE.split(limpio)
    salida: dict[str, list[str]] = {"dado": [], "cuando": [], "entonces": []}
    actual = None
    for clave, cuerpo in zip(partes[1::2], partes[2::2]):
        actual = CLAVES[clave] or actual
        frase = " ".join(cuerpo.split()).strip(" :")
        if actual is None:
            raise ValueError(f"«{clave}» abre el escenario, pero continúa una cláusula que no existe")
        if frase:
            salida[actual].append(frase)
    if not salida["cuando"] or not salida["entonces"]:
        raise ValueError("un escenario necesita al menos un WHEN/CUANDO y un THEN/ENTONCES")
    return salida


def de_spec(ruta: Path, nombre: str) -> str:
    """El cuerpo de `#### Scenario: <nombre>` en una spec de OpenSpec, sin sus bloques de código."""
    cuerpo, dentro, en_codigo = [], False, False
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        if linea.lstrip().startswith("```"):
            en_codigo = not en_codigo
            continue
        if en_codigo:
            continue
        if linea.startswith("#"):
            if dentro:
                break
            encabezado = re.fullmatch(r"#### Scenario:\s*(.*?)\s*", linea)
            dentro = encabezado is not None and encabezado[1] == nombre
            continue
        if dentro:
            cuerpo.append(linea)
    if not dentro:
        raise ValueError(f"{ruta} no tiene un «#### Scenario: {nombre}»")
    return "\n".join(cuerpo)


def comentario(esc: dict[str, list[str]], titulo: str) -> str:
    """El escenario como líneas `#`, que no cuentan para la forma única de la medida."""
    lineas = [f"# {titulo}"]
    for clave in ("dado", "cuando", "entonces"):
        lineas.extend(f"#   {clave.upper()} {frase}" for frase in esc[clave])
    lineas.append("# Lo que ofende: que pase lo de CUANDO y no lo de ENTONCES.")
    return "\n".join(lineas) + "\n"
