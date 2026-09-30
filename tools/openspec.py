"""`oracle requisito importar <spec.md | openspec/specs>`: las promesas de OpenSpec como requisitos.

Cada `### Requirement: <nombre>` de una spec de OpenSpec se vuelve un `.requisito` con su texto (el
párrafo SHALL), su fuente y un `sin_medir` que nombra los escenarios que todavía no mide nada. Nace
sin medir a propósito: el importador no sabe qué medida prueba qué, y un enlace inventado es peor
que ninguno, porque se lee como cubierto. Cada escenario se mide después con
`oracle medida nueva <id> --escenario-de <spec.md> "<escenario>" --requisito <requisito>`.

Sin `--escribir` sólo muestra lo que haría. Un requisito que ya existe no se toca nunca: puede tener
medidas enlazadas y un `sin_medir` reescrito a mano.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from nucleo.requisito import ID_RE, Requisito, RequisitoMalDeclarado, cargar_requisitos, imprimir


def _slug(texto: str) -> str:
    ascii_ = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_.lower()).strip("_")
    if not slug or slug[0].isalpha():
        return slug              # vacío: el id queda inválido y se dice
    return f"r_{slug}"


def requisitos_de_spec(ruta: Path, dominio: str) -> list[Requisito]:
    """Los `### Requirement:` de una spec, fuera de los bloques de código, en orden."""
    crudos: list[dict] = []
    en_codigo = False
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        if linea.lstrip().startswith("```"):
            en_codigo = not en_codigo
            continue
        if en_codigo:
            continue
        requisito = re.fullmatch(r"### Requirement:\s*(.*?)\s*", linea)
        escenario = re.fullmatch(r"#### Scenario:\s*(.*?)\s*", linea)
        if requisito:
            crudos.append({"nombre": requisito[1], "texto": [], "escenarios": []})
        elif re.match(r"#{1,3} ", linea):
            crudos.append(None)          # otra sección: lo que sigue ya no es del requisito
        elif crudos and crudos[-1] is not None:
            if escenario:
                crudos[-1]["escenarios"].append(escenario[1])
            elif not crudos[-1]["escenarios"] and linea.strip():
                crudos[-1]["texto"].append(re.sub(r"^[-*]\s+", "", linea.strip()))
    salida: list[Requisito] = []
    for c in filter(None, crudos):
        rid = f"{dominio}.{_slug(c['nombre'])}"
        if not ID_RE.fullmatch(rid):
            raise RequisitoMalDeclarado(f"{ruta}: «{c['nombre']}» no da un id válido ({rid})")
        if any(r.id == rid for r in salida):
            raise RequisitoMalDeclarado(f"{ruta}: dos requisitos dan el mismo id {rid}")
        pendientes = ", ".join(f"«{e}»" for e in c["escenarios"])
        sin_medir = f"sin medida todavía; escenarios: {pendientes}" if pendientes else "sin medida todavía"
        salida.append(Requisito(rid, " ".join(c["texto"]) or c["nombre"], f"{ruta}#{c['nombre']}",
                                sin_medir=sin_medir))
    return salida


def _specs(ruta: Path) -> list[tuple[Path, str]]:
    """(spec.md, dominio): uno suelto, o cada `<capacidad>/spec.md` de un `openspec/specs`."""
    specs = [ruta] if ruta.is_file() else sorted(ruta.glob("*/spec.md"))
    return [(s, _slug(s.parent.name)) for s in specs]


def main(proy, ruta: str, *, escribir: bool, dominio: str | None = None) -> int:
    origen = Path(ruta)
    if not origen.exists():
        print(f"✗ no existe {origen}")
        return 1
    specs = _specs(origen)
    if not specs:
        print(f"✗ {origen} no tiene ninguna <capacidad>/spec.md")
        return 1
    if dominio is not None and not ID_RE.fullmatch(f"{dominio}.x"):
        print(f"✗ dominio inválido: {dominio!r} (minúsculas, dígitos y `_`)")
        return 1
    directorio = proy.raiz / "requisitos"
    try:
        existentes = cargar_requisitos(directorio)
        nuevos = [r for spec, dom in specs for r in requisitos_de_spec(spec, dominio or dom)]
    except (OSError, UnicodeDecodeError, RequisitoMalDeclarado) as e:
        print(f"✗ {e}")
        return 1
    escritos = 0
    for r in nuevos:
        if r.id in existentes:
            print(f"= {r.id}   ya existe; no se toca")
            continue
        print(f"+ {r.id}   {r.sin_medir}")
        if escribir:
            directorio.mkdir(exist_ok=True)
            (directorio / f"{r.id}.requisito").write_text(imprimir(r.a_datos()), encoding="utf-8")
            escritos += 1
    faltan = len(nuevos) - sum(r.id in existentes for r in nuevos)
    if escribir:
        print(f"\n{escritos} requisitos escritos en {directorio}")
    else:
        print(f"\n{faltan} requisitos nuevos; repetí con --escribir para escribirlos")
    return 0
