"""Un requisito: la promesa en prosa, y cómo se mide o por qué no se mide.

Superficie `.requisito`, en `requisitos/` del proyecto:

```
requisito cli_validate.rutas_de_archivo:
    texto "Todo error, aviso o info SHALL incluir la ruta del archivo fuente"
    fuente "openspec/specs/cli-validate/spec.md"
    medido_por openspec.todo_problema_nombra_su_archivo, openspec.otra
```

Después de `medido_por` puede ir `sin_medir "…"`: qué parte de la promesa no mide ninguna medida y
por qué. Las dos juntas hacen un requisito **parcial**; `sin_medir` sola, uno que no se mide. Alguna
de las dos es obligatoria: un requisito que no dice cómo se mide ni por qué no se mide es justo el
hueco que esto existe para escribir.

El enlace va del requisito a la medida y no al revés, como en OpenSpec, donde el requisito es dueño
de sus escenarios: así la medida no cambia de forma y el álgebra no se entera de que esto existe.

Forma interna:

```json
["requisito", "<id>", ["texto", "<prosa>"], ["fuente", "<de dónde>"]?,
  ["medido_por", "<medida>", ...]?, ["sin_medir", "<qué y por qué>"]?]
```
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class RequisitoMalDeclarado(ValueError):
    pass


RELACIONES_DE_REQUISITO = frozenset({"requisito_declarado", "requisito_medido_por"})

AMBITOS_DE_RELACIONES = {
    "requisito_declarado": "universal",
    "requisito_medido_por": "universal",
}

CAMPOS_DE_RELACIONES = {
    "requisito_declarado": ("requisito", "texto", "fuente", "medidas", "cobertura", "sin_medir"),
    "requisito_medido_por": ("requisito", "medida"),
}

ID_RE = re.compile(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+")
_TEXTO_RE = r'("(?:[^"\\]|\\.)*")'


@dataclass(frozen=True)
class Requisito:
    id: str
    texto: str
    fuente: str = ""
    medido_por: tuple[str, ...] = ()
    sin_medir: str = ""

    @property
    def cobertura(self) -> str:
        return "ninguna" if not self.medido_por else ("parcial" if self.sin_medir else "total")

    @classmethod
    def de_datos(cls, datos) -> "Requisito":
        if not (isinstance(datos, list) and len(datos) >= 3 and datos[0] == "requisito"):
            raise RequisitoMalDeclarado("se esperaba ['requisito', id, ['texto', …], …]")
        rid = datos[1]
        if not isinstance(rid, str) or not ID_RE.fullmatch(rid):
            raise RequisitoMalDeclarado(f"id de requisito inválido: {rid!r} (se espera dominio.nombre en ASCII)")
        clausulas = list(datos[2:])
        siguiente = lambda nombre: clausulas.pop(0) if clausulas and isinstance(clausulas[0], list) and clausulas[0][:1] == [nombre] else None  # noqa: E731
        texto = _clausula(rid, siguiente("texto"), "texto")
        fuente = siguiente("fuente")
        medido_por = siguiente("medido_por")
        sin_medir = siguiente("sin_medir")
        if clausulas or (medido_por is None and sin_medir is None):
            raise RequisitoMalDeclarado(
                f"{rid}: van texto, fuente (opcional), medido_por y sin_medir, en ese orden y al menos "
                "una de las dos últimas")
        medidas = tuple(medido_por[1:]) if medido_por is not None else ()
        if medido_por is not None and (not medidas or any(not isinstance(m, str) or not ID_RE.fullmatch(m) for m in medidas)):
            raise RequisitoMalDeclarado(f"{rid}: `medido_por` nombra una o más medidas por su id")
        if len(set(medidas)) != len(medidas):
            raise RequisitoMalDeclarado(f"{rid}: `medido_por` repite una medida")
        return cls(rid, texto,
                   _clausula(rid, fuente, "fuente") if fuente is not None else "",
                   medidas,
                   _clausula(rid, sin_medir, "sin_medir") if sin_medir is not None else "")

    def a_datos(self) -> list:
        datos: list = ["requisito", self.id, ["texto", self.texto]]
        if self.fuente:
            datos.append(["fuente", self.fuente])
        if self.medido_por:
            datos.append(["medido_por", *self.medido_por])
        if self.sin_medir:
            datos.append(["sin_medir", self.sin_medir])
        return datos


def _clausula(rid: str, clausula, nombre: str) -> str:
    if not (isinstance(clausula, list) and len(clausula) == 2 and clausula[0] == nombre
            and isinstance(clausula[1], str) and clausula[1].strip()):
        raise RequisitoMalDeclarado(f"{rid}: se esperaba `{nombre}` con un texto no vacío")
    return clausula[1]


def imprimir(datos: list) -> str:
    r = Requisito.de_datos(datos)
    comillas = lambda t: json.dumps(t, ensure_ascii=False)  # noqa: E731
    lineas = [f"requisito {r.id}:", f"    texto {comillas(r.texto)}"]
    if r.fuente:
        lineas.append(f"    fuente {comillas(r.fuente)}")
    if r.medido_por:
        lineas.append(f"    medido_por {', '.join(r.medido_por)}")
    if r.sin_medir:
        lineas.append(f"    sin_medir {comillas(r.sin_medir)}")
    return "\n".join(lineas) + "\n"


def leer(texto: str) -> list:
    # Las líneas `#` completas no son parte del árbol, igual que en las otras superficies.
    lineas = [(n, linea) for n, linea in enumerate(texto.splitlines(), 1)
              if linea.strip() and not linea.lstrip().startswith("#")]
    cabecera = re.fullmatch(r"requisito (\S+):", lineas[0][1]) if lineas else None
    if not cabecera:
        raise RequisitoMalDeclarado("se esperaba `requisito <dominio.nombre>:`")
    datos: list = ["requisito", cabecera[1]]
    for numero, linea in lineas[1:]:
        m = re.fullmatch(r"    (texto|fuente|sin_medir) " + _TEXTO_RE, linea)
        if m:
            datos.append([m[1], json.loads(m[2])])
            continue
        m = re.fullmatch(r"    medido_por (\S+(?:, \S+)*)", linea)
        if m:
            datos.append(["medido_por", *m[1].split(", ")])
            continue
        raise RequisitoMalDeclarado(
            f"línea {numero}: se esperaba `texto \"…\"`, `fuente \"…\"`, `medido_por <medidas>` "
            f"o `sin_medir \"…\"`: {linea.strip()}")
    return Requisito.de_datos(datos).a_datos()


def cargar(ruta: Path) -> Requisito:
    from .forma import error_forma, leer_texto
    ruta = Path(ruta)
    if ruta.suffix != ".requisito":
        raise RequisitoMalDeclarado(f"{ruta}: un requisito se escribe en .requisito")
    try:
        texto = leer_texto(ruta)
    except OSError as e:
        raise RequisitoMalDeclarado(f"no se pudo leer el requisito {ruta}: {e}") from e
    try:
        datos = leer(texto)
    except RequisitoMalDeclarado as e:
        raise RequisitoMalDeclarado(f"{ruta}: {e}") from e
    error = error_forma(ruta, texto, imprimir(datos))
    if error:
        raise RequisitoMalDeclarado(error)
    requisito = Requisito.de_datos(datos)
    if ruta.stem != requisito.id:
        raise RequisitoMalDeclarado(f"{ruta}: el archivo se llama como su id: {requisito.id}.requisito")
    return requisito


def cargar_requisitos(directorio) -> dict[str, Requisito]:
    """Los requisitos de un directorio. Sin directorio no hay requisitos, y eso no es un error."""
    base = Path(directorio)
    if not base.is_dir():
        return {}
    salida: dict[str, Requisito] = {}
    for ruta in sorted(base.rglob("*.requisito")):
        if ruta.is_symlink():
            raise RequisitoMalDeclarado(f"un requisito no puede ser symlink: {ruta}")
        r = cargar(ruta)
        if r.id in salida:
            raise RequisitoMalDeclarado(f"el requisito «{r.id}» está dos veces")
        salida[r.id] = r
    return salida


def hechos_de_requisitos(requisitos: Iterable[Requisito]) -> dict[str, list[dict]]:
    declarados, medidos = [], []
    for r in requisitos:
        declarados.append({
            "requisito": r.id, "texto": r.texto, "fuente": r.fuente, "medidas": len(r.medido_por),
            "cobertura": r.cobertura, "sin_medir": r.sin_medir,
        })
        medidos.extend({"requisito": r.id, "medida": m} for m in r.medido_por)
    return {"requisito_declarado": declarados, "requisito_medido_por": medidos}
