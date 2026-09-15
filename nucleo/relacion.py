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

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .vocabulario import AMBITOS, opciones


class RelacionMalDeclarada(ValueError):
    pass


RELACIONES_DE_RELACION = frozenset({
    "relacion_declarada",
    "campo_declarado",
    "ambito_de_relacion",
})

AMBITOS_DE_RELACIONES = {
    "relacion_declarada": "universal",
    "campo_declarado": "universal",
    "ambito_de_relacion": "universal",
}

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
class Variante:
    valor: str
    campos: tuple[Campo, ...]

    def a_datos(self) -> list:
        return ["variante", self.valor, *(c.a_datos() for c in self.campos)]


@dataclass(frozen=True)
class Relacion:
    nombre: str
    campos: tuple[Campo, ...]
    alcance: str
    variantes: tuple[Variante, ...] = ()
    discriminante: str = ""

    @property
    def todos_los_campos(self) -> tuple[Campo, ...]:
        vistos: set[str] = set()
        resultado: list[Campo] = []
        for c in self.campos:
            if c.nombre not in vistos:
                vistos.add(c.nombre)
                resultado.append(c)
        for v in self.variantes:
            for c in v.campos:
                if c.nombre not in vistos:
                    vistos.add(c.nombre)
                    resultado.append(c)
        return tuple(resultado)

    @classmethod
    def de_datos(cls, d: list) -> "Relacion":
        if not isinstance(d, list) or len(d) not in (4, 5) or d[0] != "relacion":
            raise RelacionMalDeclarada(
                "una relación es ['relacion', nombre, ['campos', ...], ['alcance', ...]] "
                "o con ['variantes', discriminante, ...]")

        if len(d) == 4:
            _, nombre, nodo_campos, nodo_alcance = d
            nodo_variantes = None
        else:
            _, nombre, nodo_campos, nodo_variantes, nodo_alcance = d

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

        variantes_lista: list[Variante] = []
        discriminante = ""

        if nodo_variantes is not None:
            if not (isinstance(nodo_variantes, list) and nodo_variantes and nodo_variantes[0] == "variantes"):
                raise RelacionMalDeclarada(
                    f"{nombre}: `variantes` debe ser ['variantes', discriminante, ['variante', ...], ...]")
            if len(nodo_variantes) < 3:
                raise RelacionMalDeclarada(
                    f"{nombre}: debe declarar al menos una variante en `variantes`")

            discriminante = nodo_variantes[1]
            if not isinstance(discriminante, str) or discriminante not in nombres_vistos:
                raise RelacionMalDeclarada(
                    f"{nombre}: el discriminante «{discriminante}» debe ser un campo común declarado")

            campo_disc = next(c for c in campos_lista if c.nombre == discriminante)
            if campo_disc.tipo != "texto":
                raise RelacionMalDeclarada(
                    f"{nombre}: el discriminante «{discriminante}» debe ser de tipo 'texto', no «{campo_disc.tipo}»")

            variantes_vistas: set[str] = set()
            campos_variantes_tipos: dict[str, tuple[str, str]] = {}

            for item in nodo_variantes[2:]:
                # Al menos un campo: `['variante', valor]` sola es la misma forma inválida.
                if not (isinstance(item, list) and len(item) >= 3 and item[0] == "variante"):
                    raise RelacionMalDeclarada(
                        f"{nombre}: cada variante debe ser ['variante', valor, ['campo', ...], ...], "
                        "con al menos un campo")
                valor = item[1]
                if not isinstance(valor, str) or not valor.strip():
                    raise RelacionMalDeclarada(
                        f"{nombre}: valor de variante vacío o inválido")
                if valor in variantes_vistas:
                    raise RelacionMalDeclarada(
                        f"{nombre}: variante «{valor}» repetida")
                variantes_vistas.add(valor)

                v_campos: list[Campo] = []
                v_nombres_vistos: set[str] = set()

                for v_item in item[2:]:
                    if not (isinstance(v_item, list) and len(v_item) == 4 and v_item[0] == "campo"):
                        raise RelacionMalDeclarada(
                            f"{nombre}.{valor}: campo de variante debe ser ['campo', nombre, tipo, unidad]")
                    _, vc_nombre, vc_tipo, vc_unidad = v_item

                    if not isinstance(vc_nombre, str) or NOMBRE_CAMPO_RE.fullmatch(vc_nombre) is None:
                        raise RelacionMalDeclarada(
                            f"{nombre}.{valor}: nombre de campo inválido: «{vc_nombre}»")
                    if vc_nombre in v_nombres_vistos:
                        raise RelacionMalDeclarada(
                            f"{nombre}.{valor}: el campo «{vc_nombre}» está repetido en la variante")
                    if vc_nombre in nombres_vistos:
                        raise RelacionMalDeclarada(
                            f"{nombre}.{valor}: el campo «{vc_nombre}» ya está declarado en los campos comunes")
                    v_nombres_vistos.add(vc_nombre)

                    if not isinstance(vc_tipo, str) or vc_tipo not in TIPOS_VALIDOS:
                        raise RelacionMalDeclarada(
                            f"{nombre}.{valor}.{vc_nombre}: tipo «{vc_tipo}» inválido — "
                            f"debe ser uno de {sorted(TIPOS_VALIDOS)}")

                    if not isinstance(vc_unidad, str) or not vc_unidad.strip():
                        raise RelacionMalDeclarada(
                            f"{nombre}.{valor}.{vc_nombre}: falta unidad — debe ser una magnitud o «sin_unidad»")

                    vc_unidad_limpia = vc_unidad.strip()
                    if vc_nombre in campos_variantes_tipos:
                        prev_tipo, prev_unidad = campos_variantes_tipos[vc_nombre]
                        if prev_tipo != vc_tipo or prev_unidad != vc_unidad_limpia:
                            raise RelacionMalDeclarada(
                                f"{nombre}.{valor}.{vc_nombre}: el campo «{vc_nombre}» fue declarado "
                                f"en otra variante con diferente tipo/unidad ({prev_tipo}/{prev_unidad} vs {vc_tipo}/{vc_unidad_limpia})")
                    else:
                        campos_variantes_tipos[vc_nombre] = (vc_tipo, vc_unidad_limpia)

                    v_campos.append(Campo(nombre=vc_nombre, tipo=vc_tipo, unidad=vc_unidad_limpia))

                variantes_lista.append(Variante(valor=valor, campos=tuple(v_campos)))

        if not (isinstance(nodo_alcance, list) and len(nodo_alcance) == 2
                and nodo_alcance[0] == "alcance"
                and isinstance(nodo_alcance[1], str) and nodo_alcance[1].strip()):
            raise RelacionMalDeclarada(
                f"{nombre}: falta `alcance` — hay que declarar qué NO lee el sensor")

        return cls(
            nombre=nombre,
            campos=tuple(campos_lista),
            alcance=nodo_alcance[1].strip(),
            variantes=tuple(variantes_lista),
            discriminante=discriminante,
        )

    def a_datos(self) -> list:
        base = [
            "relacion",
            self.nombre,
            ["campos", *(c.a_datos() for c in self.campos)],
        ]
        if self.variantes:
            base.append(["variantes", self.discriminante, *(v.a_datos() for v in self.variantes)])
        base.append(["alcance", self.alcance])
        return base


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


def _ambitos_del_arbol(arbol: ast.AST, archivo: Path) -> dict[str, str]:
    """Lee declaraciones literales sin importar el módulo que produce la evidencia."""
    salida = {}
    for nodo in getattr(arbol, "body", []):
        if not (isinstance(nodo, (ast.Assign, ast.AnnAssign))
                and isinstance(getattr(nodo, "value", None), ast.Dict)):
            continue
        objetivos = (nodo.targets if isinstance(nodo, ast.Assign) else (nodo.target,))
        if not any(isinstance(objetivo, ast.Name)
                   and objetivo.id == "AMBITOS_DE_RELACIONES" for objetivo in objetivos):
            continue
        for clave, valor in zip(nodo.value.keys, nodo.value.values):
            if not (isinstance(clave, ast.Constant) and isinstance(clave.value, str)
                    and isinstance(valor, ast.Constant) and isinstance(valor.value, str)):
                raise RelacionMalDeclarada(
                    f"{archivo.name}: AMBITOS_DE_RELACIONES debe ser un mapa literal de textos")
            if valor.value not in AMBITOS:
                raise RelacionMalDeclarada(
                    f"{archivo.name}: ámbito {valor.value!r} de {clave.value!r} inválido; "
                    f"debe ser uno de:\n{opciones(AMBITOS)}")
            if clave.value in salida:
                raise RelacionMalDeclarada(
                    f"{archivo.name}: ámbito repetido para la relación {clave.value!r}")
            salida[clave.value] = valor.value
    return salida


def ambitos_de_relaciones_declarados(raiz: Path | None = None) -> dict[str, str]:
    """Reúne ámbitos junto a los sensores, sin ejecutarlos ni deducirlos por su ruta."""
    raiz_proy = Path(__file__).resolve().parents[1] if raiz is None else Path(raiz)
    salida = {}
    archivos = [ruta for nombre in ("nucleo", "tools")
                for ruta in sorted((raiz_proy / nombre).glob("*.py"))
                if ruta.is_file() and not ruta.is_symlink()]
    for archivo in archivos:
        fuente = archivo.read_text(encoding="utf-8")
        if "AMBITOS_DE_RELACIONES" not in fuente:
            continue
        try:
            declarados = _ambitos_del_arbol(ast.parse(fuente, filename=str(archivo)), archivo)
        except (OSError, SyntaxError) as e:
            raise RelacionMalDeclarada(f"no se pudo leer ámbitos de {archivo}: {e}") from e
        repetidos = set(salida).intersection(declarados)
        if repetidos:
            raise RelacionMalDeclarada(
                f"ámbito de relación declarado más de una vez: {sorted(repetidos)}")
        salida.update(declarados)
    return salida


def hechos_de_relaciones(relaciones: Iterable[Relacion], *, ambitos=None) -> dict[str, list[dict]]:
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
            "variantes": len(r.variantes),
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
                "variante": "",
            })
        for v in r.variantes:
            for c in v.campos:
                campos_filas.append({
                    "relacion": r.nombre,
                    "campo": c.nombre,
                    "tipo": c.tipo,
                    "unidad": c.unidad,
                    "tiene_unidad": bool(c.unidad),
                    "es_magnitud": c.es_magnitud,
                    "es_sin_unidad": c.es_sin_unidad,
                    "variante": v.valor,
                })
    ambitos = {} if ambitos is None else dict(ambitos)
    for nombre, ambito in ambitos.items():
        if not isinstance(nombre, str) or not nombre.strip() or ambito not in AMBITOS:
            raise RelacionMalDeclarada("los ámbitos de relaciones deben mapear nombres a AMBITOS")
    return {
        "relacion_declarada": relaciones_filas,
        "campo_declarado": campos_filas,
        "ambito_de_relacion": [
            {"relacion": nombre, "ambito": ambito}
            for nombre, ambito in sorted(ambitos.items())
        ],
    }


def como_hechos(relaciones: Iterable[Relacion], *, ambitos=None) -> dict[str, list[dict]]:
    return hechos_de_relaciones(relaciones, ambitos=ambitos)
