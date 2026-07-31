"""A qué proyecto se le mide. Oracle es la herramienta; el proyecto es de otro.

Las herramientas tenían la ruta del catálogo clavada en el propio repositorio, y eso las volvía
inútiles para cualquier otro: podías escribir medidas de tu dominio y no había forma de correrlas.
Una herramienta que sólo sabe medirse a sí misma no es multipropósito.

Un **proyecto** es cualquier directorio con esta forma. Nada más:

    <proyecto>/
      catalogos/     las medidas, agrupadas por dominio
      corpus/        los casos donde la medición dijo bien y no estaba bien
      diferencial/   los fixtures contra implementaciones independientes

Se resuelve en este orden, y el primero que aparece gana:

    --proyecto <ruta>        explícito
    $ORACLE_PROYECTO         para no repetirlo en cada comando
    el directorio actual     si tiene `catalogos/`
    el repositorio de oracle si no hay nada más — para que oracle pueda medirse a sí mismo
"""

from __future__ import annotations

import json
import os
import re
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

RAIZ_ORACLE = Path(__file__).resolve().parents[1]


class ProyectoInvalido(ValueError):
    pass


class EscalaresNoConfiables(ProyectoInvalido):
    pass


class EscalaresInvalidas(ProyectoInvalido):
    pass


ESQUEMA_PROYECTO = "oracle.proyecto/v1"
NOMBRE_PERFIL_RE = re.compile(r"^[a-z][a-z0-9_-]*$")


def perfiles_incluidos() -> dict[str, Path]:
    """Descubre perfiles empaquetados sin enseñar sus nombres al núcleo.

    Un perfil es un directorio físico ``perfiles/<nombre>/catalogos``. Añadir otro lenguaje o sensor
    no exige modificar este módulo; ``oracle.json`` sigue siendo quien decide cuáles se activan.
    """
    raiz_perfiles = RAIZ_ORACLE / "perfiles"
    if not raiz_perfiles.is_dir() or raiz_perfiles.is_symlink():
        return {}
    raiz_fisica = RAIZ_ORACLE.resolve()
    disponibles = {}
    for perfil in sorted(raiz_perfiles.iterdir()):
        catalogos = perfil / "catalogos"
        if (NOMBRE_PERFIL_RE.fullmatch(perfil.name) is None
                or perfil.is_symlink() or not perfil.is_dir()
                or catalogos.is_symlink() or not catalogos.is_dir()):
            continue
        try:
            catalogos.resolve().relative_to(raiz_fisica)
        except (OSError, ValueError):
            continue
        disponibles[perfil.name] = catalogos
    return disponibles


@dataclass(frozen=True)
class ConfiguracionProyecto:
    perfiles: tuple[str, ...] = ()


def configuracion(proy: "Proyecto") -> ConfiguracionProyecto:
    """Lee perfiles explícitos; sin `oracle.json`, el proyecto recibe sólo el núcleo."""
    ruta = proy.raiz / "oracle.json"
    if not ruta.exists() and not ruta.is_symlink():
        return ConfiguracionProyecto()
    raiz = proy.raiz.resolve()
    try:
        fisica = ruta.resolve()
        fisica.relative_to(raiz)
    except (OSError, ValueError) as e:
        raise ProyectoInvalido("`oracle.json` debe estar dentro del proyecto") from e
    if ruta.is_symlink() or not fisica.is_file():
        raise ProyectoInvalido("`oracle.json` debe ser un archivo físico, no un symlink")
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ProyectoInvalido(f"no se pudo leer `oracle.json`: {e}") from e
    if not isinstance(datos, dict) or datos.get("esquema") != ESQUEMA_PROYECTO:
        raise ProyectoInvalido(f"`oracle.json` debe declarar esquema {ESQUEMA_PROYECTO!r}")
    perfiles = datos.get("perfiles", [])
    if (not isinstance(perfiles, list)
            or any(not isinstance(p, str) or NOMBRE_PERFIL_RE.fullmatch(p) is None
                   for p in perfiles)
            or len(perfiles) != len(set(perfiles))):
        raise ProyectoInvalido(
            "`perfiles` debe ser una lista sin duplicados de nombres portables")
    desconocidos = set(perfiles) - set(perfiles_incluidos())
    if desconocidos:
        raise ProyectoInvalido(f"perfiles desconocidos: {sorted(desconocidos)}")
    return ConfiguracionProyecto(tuple(perfiles))


@dataclass(frozen=True)
class Proyecto:
    raiz: Path

    @property
    def catalogos(self) -> Path:
        return self.raiz / "catalogos"

    @property
    def corpus(self) -> Path:
        return self.raiz / "corpus"

    @property
    def diferencial(self) -> Path:
        return self.raiz / "diferencial"

    @property
    def es_el_propio_oracle(self) -> bool:
        return self.raiz == RAIZ_ORACLE

    def __str__(self) -> str:
        return "oracle (sí mismo)" if self.es_el_propio_oracle else str(self.raiz)


def catalogos_base_a_cargar(proy: "Proyecto") -> list[Path]:
    """Catálogo universal y perfiles incluidos activados por el proyecto."""
    disponibles = perfiles_incluidos()
    return [RAIZ_ORACLE / "catalogos", *(
        disponibles[nombre] for nombre in configuracion(proy).perfiles)]


def catalogos_a_cargar(proy: "Proyecto") -> list[Path]:
    """El catálogo BASE de oracle más el del proyecto.

    Oracle trae medidas que valen para cualquiera que construya con un LLM —mutantes que sobreviven,
    afirmaciones sin alcance, verificaciones vencidas, corridas irreproducibles— y el proyecto agrega
    las de su dominio. Que las universales vengan incluidas es la diferencia entre una herramienta y
    un repositorio de ejemplos.
    """
    bases = catalogos_base_a_cargar(proy)
    if proy.catalogos.resolve() == (RAIZ_ORACLE / "catalogos").resolve():
        return bases
    return [*bases, proy.catalogos]


@contextmanager
def escalares_del_proyecto(proy: "Proyecto", *, confiar: bool = False):
    """Activa temporalmente las UDF de un proyecto explícitamente confiado.

    Restaura el registro aun si la importación o la evaluación falla. El archivo debe ser físico y
    estar dentro del proyecto: la confianza autoriza su código, no una ruta exterior inesperada.
    """
    if proy.es_el_propio_oracle:
        yield ""
        return
    archivo = proy.raiz / "escalares.py"
    if not archivo.exists():
        yield ""
        return
    if not confiar:
        raise EscalaresNoConfiables(
            f"{archivo} es código Python externo; repetí con `--confiar-escalares` para ejecutarlo")
    raiz = proy.raiz.resolve()
    try:
        fisica = archivo.resolve()
        fisica.relative_to(raiz)
    except (OSError, ValueError) as e:
        raise EscalaresInvalidas(f"`escalares.py` no está confinado en {raiz}") from e
    if archivo.is_symlink() or not fisica.is_file():
        raise EscalaresInvalidas("`escalares.py` debe ser un archivo físico, no un symlink")

    import hashlib
    import importlib.util
    from nucleo import algebra

    huella = hashlib.sha256(str(raiz).encode("utf-8")).hexdigest()
    spec = importlib.util.spec_from_file_location(f"oracle_escalares_{huella}", fisica)
    if spec is None or spec.loader is None:
        raise EscalaresInvalidas(f"no se pudo preparar la carga de {fisica}")
    modulo = importlib.util.module_from_spec(spec)
    anteriores = dict(algebra.ESCALARES)
    procedencia_anterior = algebra._PROCEDENCIA_ESCALAR
    algebra._PROCEDENCIA_ESCALAR = f"proyecto:{raiz}"
    try:
        try:
            spec.loader.exec_module(modulo)
            alteradas = [nombre for nombre, fn in anteriores.items()
                         if algebra.ESCALARES.get(nombre) is not fn]
            if alteradas:
                raise EscalaresInvalidas(
                    f"escalares.py alteró registros existentes: {sorted(alteradas)}")
            for nombre in set(algebra.ESCALARES) - set(anteriores):
                fn = algebra.ESCALARES[nombre]
                requeridos = ("nombre_escalar", "unidad", "aridad_min", "aridad_max",
                              "procedencia_escalar")
                if any(not hasattr(fn, campo) for campo in requeridos):
                    raise EscalaresInvalidas(
                        f"la escalar «{nombre}» evitó el decorador `@escalar`")
        except EscalaresInvalidas:
            raise
        except Exception as e:
            raise EscalaresInvalidas(
                f"falló {fisica}: {type(e).__name__}: {e}") from e
        yield str(fisica)
    finally:
        algebra.ESCALARES.clear()
        algebra.ESCALARES.update(anteriores)
        algebra._PROCEDENCIA_ESCALAR = procedencia_anterior


def confiar_escalares(argv: list[str]) -> bool:
    return "--confiar-escalares" in argv


def sin_banderas_comunes(argv: list[str]) -> list[str]:
    return [a for a in sin_bandera(argv) if a != "--confiar-escalares"]


def _valido(ruta: Path) -> bool:
    return (ruta / "catalogos").is_dir()


def problemas_estructura(proy: "Proyecto", requeridos: tuple[str, ...]) -> list[str]:
    """Comprueba las partes que usa una herramienta y que no escapen mediante symlinks."""
    permitidos = {"catalogos", "corpus", "diferencial"}
    desconocidos = set(requeridos) - permitidos
    if desconocidos:
        raise ValueError(f"componentes de proyecto desconocidos: {sorted(desconocidos)}")
    raiz = proy.raiz.resolve()
    fallas = []
    for nombre in requeridos:
        ruta = proy.raiz / nombre
        if not ruta.is_dir():
            fallas.append(f"falta `{nombre}/`")
            continue
        try:
            ruta.resolve().relative_to(raiz)
        except (OSError, ValueError):
            fallas.append(f"`{nombre}/` no está confinado dentro del proyecto")
        if ruta.is_symlink():
            fallas.append(f"`{nombre}/` no puede ser un symlink")
    return fallas


ID_MEDIDA_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")


def ruta_de_medida_nueva(proy: "Proyecto", mid: str) -> Path:
    """Resuelve el destino de un id cerrado y demuestra su confinamiento antes de crear nada."""
    if not isinstance(mid, str) or ID_MEDIDA_RE.fullmatch(mid) is None:
        raise ProyectoInvalido(
            "el id debe ser `dominio.nombre`, sólo con minúsculas ASCII, dígitos y `_`")
    catalogos = proy.catalogos.resolve()
    destino = proy.catalogos / mid.split(".")[0] / f"{mid}.json"
    try:
        destino.resolve().relative_to(catalogos)
    except (OSError, ValueError) as e:
        raise ProyectoInvalido(f"el destino de {mid!r} escapa de `catalogos/`") from e
    return destino


def presentar_ruta(proy: "Proyecto", ruta: Path) -> str:
    """Ruta estable para humanos: relativa al proyecto si pertenece a él; absoluta si no."""
    fisica = ruta.resolve()
    try:
        return fisica.relative_to(proy.raiz.resolve()).as_posix()
    except ValueError:
        return str(fisica)


def resolver(argv: list[str] | None = None) -> Proyecto:
    argv = list(argv if argv is not None else [])
    if "--proyecto" in argv:
        i = argv.index("--proyecto")
        if i + 1 >= len(argv):
            raise ProyectoInvalido("--proyecto necesita una ruta")
        ruta = Path(argv[i + 1]).expanduser().resolve()
        if not _valido(ruta):
            raise ProyectoInvalido(f"{ruta} no parece un proyecto: le falta `catalogos/`")
        return Proyecto(ruta)

    delEntorno = os.environ.get("ORACLE_PROYECTO")
    if delEntorno:
        ruta = Path(delEntorno).expanduser().resolve()
        if not _valido(ruta):
            raise ProyectoInvalido(f"$ORACLE_PROYECTO={ruta} no tiene `catalogos/`")
        return Proyecto(ruta)

    aqui = Path.cwd().resolve()
    if _valido(aqui) and aqui != RAIZ_ORACLE:
        return Proyecto(aqui)

    return Proyecto(RAIZ_ORACLE)


def sin_bandera(argv: list[str]) -> list[str]:
    """El resto de los argumentos, sin `--proyecto <ruta>`."""
    salida, saltar = [], False
    for i, a in enumerate(argv):
        if saltar:
            saltar = False
            continue
        if a == "--proyecto":
            saltar = True
            continue
        salida.append(a)
    return salida
