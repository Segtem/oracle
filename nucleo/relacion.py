"""La declaración de una relación (L−1): qué lee el sensor, en qué unidad, y qué NO miró.

Forma canónica, tal como se guarda en `relaciones/`:

```json
["relacion", "<nombre>",
  ["campos",
    ["campo", "<nombre>", "<tipo>", "<unidad>"],
    ...
  ],
  ["alcance", "<qué NO lee el sensor>"]]
```

Un campo sin magnitud física —un identificador, un nombre, una clave categórica o booleana—
declara explícitamente `sin_unidad`. No hay defaults silenciosos: todo campo declara su unidad.
El `alcance` del sensor es obligatorio por la misma razón que en una medida: delimitar lo que el
sensor no observó.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class RelacionMalDeclarada(ValueError):
    pass


RELACIONES_DE_RELACION = frozenset({
    "relacion_declarada",
    "campo_declarado",
})

EXTENSIONES_DE_RELACION = frozenset({".json", ".oracle", ".relacion"})
NOMBRE_RELACION_RE = re.compile(r"^[a-z][a-z0-9_]*$")
NOMBRE_CAMPO_RE = re.compile(r"^[a-z][a-z0-9_]*$")
TIPOS_VALIDOS = frozenset({"texto", "entero", "flotante", "booleano"})


@dataclass(frozen=True)
class Campo:
    nombre: str
    tipo: str
    unidad: str

    @property
    def es_sin_unidad(self) -> bool:
        return self.unidad == "sin_unidad"

    @property
    def es_magnitud(self) -> bool:
        return self.unidad != "sin_unidad"

    def a_datos(self) -> list:
        return ["campo", self.nombre, self.tipo, self.unidad]


@dataclass(frozen=True)
class Relacion:
    nombre: str
    campos: tuple[Campo, ...]
    alcance: str

    @classmethod
    def de_datos(cls, d: list) -> "Relacion":
        if not isinstance(d, list) or len(d) != 4 or d[0] != "relacion":
            raise RelacionMalDeclarada(
                "una relación es ['relacion', nombre, ['campos', ...], ['alcance', ...]]")

        _, nombre, nodo_campos, nodo_alcance = d

        if not isinstance(nombre, str) or NOMBRE_RELACION_RE.fullmatch(nombre) is None:
            raise RelacionMalDeclarada(
                f"nombre de relación inválido: «{nombre}» — debe usar sólo minúsculas ASCII, "
                "dígitos y `_`")

        if not (isinstance(nodo_campos, list) and nodo_campos and nodo_campos[0] == "campos"):
            raise RelacionMalDeclarada(
                f"{nombre}: `campos` debe ser ['campos', ['campo', ...], ...]")

        campos_lista: list[Campo] = []
        nombres_vistos: set[str] = set()

        for idx, item in enumerate(nodo_campos[1:], start=1):
            if not (isinstance(item, list) and len(item) == 4 and item[0] == "campo"):
                raise RelacionMalDeclarada(
                    f"{nombre}.campo[{idx}]: debe ser ['campo', nombre, tipo, unidad]")
            _, c_nombre, c_tipo, c_unidad = item

            if not isinstance(c_nombre, str) or NOMBRE_CAMPO_RE.fullmatch(c_nombre) is None:
                raise RelacionMalDeclarada(
                    f"{nombre}: nombre de campo inválido: «{c_nombre}»")
            if c_nombre in nombres_vistos:
                raise RelacionMalDeclarada(
                    f"{nombre}: el campo «{c_nombre}» está repetido")
            nombres_vistos.add(c_nombre)

            if not isinstance(c_tipo, str) or c_tipo not in TIPOS_VALIDOS:
                raise RelacionMalDeclarada(
                    f"{nombre}.{c_nombre}: tipo «{c_tipo}» inválido — "
                    f"debe ser uno de {sorted(TIPOS_VALIDOS)}")

            if not isinstance(c_unidad, str) or not c_unidad.strip():
                raise RelacionMalDeclarada(
                    f"{nombre}.{c_nombre}: falta unidad — debe ser una magnitud o «sin_unidad»")

            campos_lista.append(Campo(nombre=c_nombre, tipo=c_tipo, unidad=c_unidad.strip()))

        if not campos_lista:
            raise RelacionMalDeclarada(
                f"{nombre}: la relación debe declarar al menos un campo")

        if not (isinstance(nodo_alcance, list) and len(nodo_alcance) == 2
                and nodo_alcance[0] == "alcance"
                and isinstance(nodo_alcance[1], str) and nodo_alcance[1].strip()):
            raise RelacionMalDeclarada(
                f"{nombre}: falta `alcance` — hay que declarar qué NO lee el sensor")

        return cls(nombre=nombre, campos=tuple(campos_lista), alcance=nodo_alcance[1].strip())

    def a_datos(self) -> list:
        return [
            "relacion",
            self.nombre,
            ["campos", *(c.a_datos() for c in self.campos)],
            ["alcance", self.alcance],
        ]


def _normalizar_directorios(directorios) -> tuple:
    if len(directorios) == 1 and isinstance(directorios[0], (list, tuple)):
        return tuple(directorios[0])
    return tuple(directorios)


def _rutas_en_directorio(directorio) -> list[Path]:
    base = Path(directorio)
    if not base.exists():
        return []
    if base.is_symlink() or not base.is_dir():
        raise RelacionMalDeclarada(f"el directorio de relaciones debe ser físico: {base}")
    try:
        base_fisica = base.resolve()
    except OSError as e:
        raise RelacionMalDeclarada(f"no se pudo resolver el directorio {base}: {e}") from e
    rutas = []
    for ruta in base.rglob("*"):
        if ruta.suffix not in EXTENSIONES_DE_RELACION:
            continue
        if ruta.is_symlink():
            raise RelacionMalDeclarada(f"una declaración de relación no puede ser symlink: {ruta}")
        try:
            fisica = ruta.resolve()
            fisica.relative_to(base_fisica)
        except (OSError, ValueError) as e:
            raise RelacionMalDeclarada(f"la relación {ruta} no está confinada en {base_fisica}") from e
        if not fisica.is_file():
            raise RelacionMalDeclarada(f"la relación debe ser un archivo físico: {ruta}")
        rutas.append(ruta)
    return sorted(rutas)


def rutas_de_relaciones(*directorios) -> list[Path]:
    return sorted(
        ruta
        for directorio in _normalizar_directorios(directorios)
        for ruta in _rutas_en_directorio(directorio)
    )


def cargar_fuente_relacion(ruta: Path) -> list:
    ruta = Path(ruta)
    try:
        texto = ruta.read_text(encoding="utf-8")
    except OSError as e:
        raise RelacionMalDeclarada(f"no se pudo leer la relación {ruta}: {e}") from e
    if ruta.suffix in (".json", ".oracle", ".relacion"):
        try:
            return json.loads(texto)
        except json.JSONDecodeError as e:
            raise RelacionMalDeclarada(f"{ruta}: JSON inválido — {e}") from e
    raise RelacionMalDeclarada(
        f"formato de relación no soportado: {ruta} (esperaba .json)")


def cargar(ruta: Path) -> Relacion:
    return Relacion.de_datos(cargar_fuente_relacion(ruta))


def cargar_relaciones(*directorios) -> dict[str, Relacion]:
    salida: dict[str, Relacion] = {}
    fuentes: dict[str, Path] = {}
    for p in rutas_de_relaciones(*directorios):
        r = cargar(p)
        if r.nombre in salida:
            raise RelacionMalDeclarada(
                f"la relación «{r.nombre}» está dos veces: {fuentes[r.nombre]} y {p}")
        salida[r.nombre] = r
        fuentes[r.nombre] = p
    return salida


def hechos_de_relaciones(relaciones: Iterable[Relacion]) -> dict[str, list[dict]]:
    relaciones_filas = []
    campos_filas = []
    for r in relaciones:
        if not isinstance(r, Relacion):
            raise RelacionMalDeclarada(f"se esperaba `Relacion`, no {type(r).__name__}")
        relaciones_filas.append({
            "relacion": r.nombre,
            "campos": len(r.campos),
            "alcance": r.alcance,
            "tiene_alcance": bool(r.alcance),
        })
        for c in r.campos:
            campos_filas.append({
                "relacion": r.nombre,
                "campo": c.nombre,
                "tipo": c.tipo,
                "unidad": c.unidad,
                "tiene_unidad": bool(c.unidad),
                "es_magnitud": c.es_magnitud,
                "es_sin_unidad": c.es_sin_unidad,
            })
    return {
        "relacion_declarada": relaciones_filas,
        "campo_declarado": campos_filas,
    }


def como_hechos(relaciones: Iterable[Relacion]) -> dict[str, list[dict]]:
    return hechos_de_relaciones(relaciones)
