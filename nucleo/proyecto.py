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

from .version import (VersionInvalida, compatible, del_nucleo, del_nucleo_sintaxis,
                      parsear)

RAIZ_ORACLE = Path(__file__).resolve().parents[1]


class ProyectoInvalido(ValueError):
    pass


class EscalaresNoConfiables(ProyectoInvalido):
    pass


class EscalaresInvalidas(ProyectoInvalido):
    pass


ESQUEMA_PROYECTO = "oracle.proyecto/v1"
NOMBRE_PERFIL_RE = re.compile(r"^[a-z][a-z0-9_-]*$")


def _normalizar_raices_perfiles(raices) -> tuple[Path, ...]:
    if isinstance(raices, (str, bytes, os.PathLike)):
        raise ProyectoInvalido("`raices_perfiles` debe ser una colección de directorios")
    try:
        candidatas = tuple(raices)
    except TypeError as e:
        raise ProyectoInvalido("`raices_perfiles` debe ser una colección de directorios") from e
    salida = []
    for candidata in candidatas:
        try:
            salida.append(Path(candidata).expanduser())
        except TypeError as e:
            raise ProyectoInvalido(f"raíz de perfiles inválida: {candidata!r}") from e
    return tuple(salida)


def _descubrir_perfiles(raiz_perfiles: Path, *, requerida: bool) -> dict[str, Path]:
    if raiz_perfiles.is_symlink() or not raiz_perfiles.is_dir():
        if requerida:
            raise ProyectoInvalido(
                f"la raíz de perfiles debe ser un directorio físico: {raiz_perfiles}")
        return {}
    try:
        raiz_fisica = raiz_perfiles.resolve()
    except OSError as e:
        if requerida:
            raise ProyectoInvalido(f"no se pudo resolver la raíz de perfiles: {raiz_perfiles}") from e
        return {}
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


def perfiles_incluidos(raices_adicionales=()) -> dict[str, Path]:
    """Descubre perfiles empaquetados y raíces entregadas explícitamente por el host.

    Cada raíz contiene ``<nombre>/catalogos``. Las adicionales nunca salen de ``oracle.json``: el
    proceso anfitrión les concede autoridad al construir su motor. Un nombre ambiguo falla cerrado.
    """
    raices = _normalizar_raices_perfiles(raices_adicionales)
    fuentes = [
        (_descubrir_perfiles(RAIZ_ORACLE / "perfiles", requerida=False), "oracle"),
        *[(_descubrir_perfiles(raiz, requerida=True), str(raiz.resolve())) for raiz in raices],
    ]
    disponibles: dict[str, Path] = {}
    procedencias: dict[str, str] = {}
    for encontrados, procedencia in fuentes:
        for nombre, catalogos in encontrados.items():
            if nombre in disponibles:
                raise ProyectoInvalido(
                    f"perfil ambiguo «{nombre}» en {procedencias[nombre]} y {procedencia}")
            disponibles[nombre] = catalogos
            procedencias[nombre] = procedencia
    return disponibles


@dataclass(frozen=True)
class ConfiguracionProyecto:
    perfiles: tuple[str, ...] = ()
    catalogo_base: bool = False
    bibliotecas: tuple[str, ...] = ()
    # Medidas que se evalúan y se reportan pero NO hacen fallar. Cada una declara desde cuándo y
    # por qué, para que «lo tengo en sombra hace ocho meses» sea un hecho que se lee en cada
    # corrida y no una comodidad silenciosa.
    sombra: tuple["EnSombra", ...] = ()


@dataclass(frozen=True)
class EnSombra:
    """Una medida heredada que todavía no obliga, con la fecha y el motivo de por qué.

    Existe porque adoptar un catálogo de políticas te pone en rojo, y con razón: sus medidas ven
    cosas que las tuyas no veían. Pero si la primera experiencia de heredar un catálogo es que el
    proyecto entero deja de pasar, no se hereda una segunda vez.

    La sombra no silencia: declara. Lo que se apaga es la consecuencia —el veredicto rojo—, no la
    medición, que se sigue haciendo y se sigue informando con su cuenta y su antigüedad.
    """

    medida: str
    desde: str = ""
    porque: str = ""


def _sombra_declarada(datos: dict) -> tuple[EnSombra, ...]:
    """Lee `sombra` de `oracle.json`. Falla cerrado ante cualquier forma que no entienda."""
    crudo = datos.get("sombra", {})
    if not isinstance(crudo, dict):
        raise ProyectoInvalido(
            "`sombra` debe ser un mapa de id de medida a `{desde, porque}`")
    entradas = []
    for mid, valor in crudo.items():
        if not isinstance(mid, str) or not mid.strip():
            raise ProyectoInvalido(f"id de medida inválido en `sombra`: {mid!r}")
        if not isinstance(valor, dict):
            raise ProyectoInvalido(f"`sombra[{mid}]` debe ser un objeto con `desde` y `porque`")
        # `desde` y `porque` NO se exigen acá: los exige una medida del catálogo
        # (`meta.toda_sombra_declara_desde_y_porque`), que es donde vive la política. Rechazarlos
        # en el lector haría que la regla estuviera escrita dos veces, y una de las dos envejecería.
        desde, porque = valor.get("desde", ""), valor.get("porque", "")
        if not isinstance(desde, str) or not isinstance(porque, str):
            raise ProyectoInvalido(f"`sombra[{mid}]`: `desde` y `porque` son texto")
        entradas.append(EnSombra(mid, desde.strip(), porque.strip()))
    ids = [e.medida for e in entradas]
    if len(ids) != len(set(ids)):
        raise ProyectoInvalido("`sombra` repite una medida")
    return tuple(sorted(entradas, key=lambda e: e.medida))


def configuracion(proy: "Proyecto", *, raices_perfiles=()) -> ConfiguracionProyecto:
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
    desconocidos = set(perfiles) - set(perfiles_incluidos(raices_perfiles))
    if desconocidos:
        raise ProyectoInvalido(f"perfiles desconocidos: {sorted(desconocidos)}")
    catalogo_base = datos.get("catalogo_base", False)
    if not isinstance(catalogo_base, bool):
        raise ProyectoInvalido("`catalogo_base` debe ser booleano")
    bibliotecas = datos.get("bibliotecas", [])
    if (not isinstance(bibliotecas, list)
            or any(not isinstance(bid, str) or ID_MEDIDA_RE.fullmatch(bid) is None
                   for bid in bibliotecas)
            or len(bibliotecas) != len(set(bibliotecas))):
        raise ProyectoInvalido(
            "`bibliotecas` debe ser una lista sin duplicados de ids de biblioteca")
    # Un proyecto puede declarar qué versión del álgebra necesita. Es OPCIONAL: quien no la declara
    # sigue funcionando (los consumidores existentes no se rompen), pero quien la declara y no coincide
    # falla cerrado acá, antes de cargar ni una medida — con un mensaje que dice cuál hay y cuál se
    # pidió.
    algebra = datos.get("algebra")
    if algebra is not None:
        try:
            necesitada = parsear(algebra)
        except VersionInvalida as e:
            raise ProyectoInvalido(f"`oracle.json`: {e}") from e
        disponible = del_nucleo()
        if not compatible(necesitada, disponible):
            raise ProyectoInvalido(
                f"`oracle.json` pide el álgebra {necesitada} y este núcleo implementa {disponible}; "
                "un proyecto que declara una versión incompatible no se evalúa")
    # Igual que el álgebra: un proyecto puede declarar qué versión de la SUPERFICIE necesita. Es
    # OPCIONAL y comparte la misma regla de compatibilidad — misma MAYOR y MENOR al menos tan nueva
    # como la pedida—. Quien no la declara sigue funcionando.
    sintaxis = datos.get("sintaxis")
    if sintaxis is not None:
        try:
            necesitada = parsear(sintaxis)
        except VersionInvalida as e:
            raise ProyectoInvalido(f"`oracle.json`: {e}") from e
        disponible = del_nucleo_sintaxis()
        if not compatible(necesitada, disponible):
            raise ProyectoInvalido(
                f"`oracle.json` pide la sintaxis {necesitada} y este núcleo implementa "
                f"{disponible}; un proyecto que declara una versión incompatible no se evalúa")
    return ConfiguracionProyecto(
        perfiles=tuple(perfiles),
        catalogo_base=catalogo_base,
        bibliotecas=tuple(bibliotecas),
        sombra=_sombra_declarada(datos),
    )


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


def bibliotecas_del_proyecto(proy: "Proyecto", *, config=None):
    """Resuelve sólo los ids seleccionados; instalar una distribución no la activa."""
    from .biblioteca import BibliotecaInvalida, descubrir_bibliotecas

    config = config or configuracion(proy)
    if not config.bibliotecas:
        return ()
    try:
        disponibles = descubrir_bibliotecas()
    except BibliotecaInvalida as e:
        raise ProyectoInvalido(f"bibliotecas instaladas inválidas: {e}") from e
    desconocidas = sorted(set(config.bibliotecas) - set(disponibles))
    if desconocidas:
        raise ProyectoInvalido(f"bibliotecas no instaladas: {desconocidas}")
    return tuple(disponibles[bid] for bid in config.bibliotecas)


def catalogos_base_a_cargar(proy: "Proyecto", *, raices_perfiles=()) -> list[Path]:
    """Políticas base, perfiles y bibliotecas activadas explícitamente por el proyecto."""
    raices = _normalizar_raices_perfiles(raices_perfiles)
    disponibles = perfiles_incluidos(raices)
    config = configuracion(proy, raices_perfiles=raices)
    bibliotecas = bibliotecas_del_proyecto(proy, config=config)
    return [
        *([RAIZ_ORACLE / "catalogos"] if config.catalogo_base else []),
        *(disponibles[nombre] for nombre in config.perfiles),
        *(directorio for biblioteca in bibliotecas for directorio in biblioteca.catalogos),
    ]


def catalogos_a_cargar(proy: "Proyecto", *, raices_perfiles=()) -> list[Path]:
    """Los catálogos base/perfiles declarados más el catálogo del proyecto.

    Oracle ofrece políticas para proyectos construidos con un LLM —mutantes que sobreviven,
    afirmaciones sin alcance, verificaciones vencidas, corridas irreproducibles— pero el host decide
    si incorporarlas con ``"catalogo_base": true``. Sin configuración sólo carga su propio catálogo.
    """
    bases = catalogos_base_a_cargar(proy, raices_perfiles=raices_perfiles)
    if proy.catalogos.resolve() == (RAIZ_ORACLE / "catalogos").resolve():
        return bases
    return [*bases, proy.catalogos]


def relaciones_del_proyecto(proy: "Proyecto", *, raices_perfiles=()) -> dict[str, Any]:
    """Carga juntas las relaciones seleccionadas para que ningún id repetido gane en silencio."""
    from .relacion import cargar_relaciones

    config = configuracion(proy, raices_perfiles=raices_perfiles)
    directorios = []
    if config.catalogo_base:
        dir_base = RAIZ_ORACLE / "relaciones"
        if dir_base.is_dir():
            directorios.append(dir_base)
    directorios.extend(
        directorio
        for biblioteca in bibliotecas_del_proyecto(proy, config=config)
        for directorio in biblioteca.relaciones
    )
    dir_proy = proy.raiz / "relaciones"
    if (dir_proy.is_dir()
            and all(dir_proy.resolve() != directorio.resolve() for directorio in directorios)):
        directorios.append(dir_proy)
    return cargar_relaciones(directorios)


def macros_del_proyecto(proy: "Proyecto", *, raices_perfiles=()) -> "RegistroMacros":
    """Biblioteca estándar más macros de bibliotecas seleccionadas y del proyecto.

    Las macros son DATOS, no código: se leen y se sustituyen, así que no necesitan la confianza
    explícita que sí exige `escalares.py`. Lo que sí se exige es lo mismo que a todo lo demás —que el
    directorio sea físico y esté confinado— y que un nombre no tape al de otra fuente: si un proyecto
    quiere cambiar `ninguno`, la llama distinto.
    """
    from .macro import cargar_macros, macros_base

    registro = macros_base()
    config = configuracion(proy, raices_perfiles=raices_perfiles)
    for biblioteca in bibliotecas_del_proyecto(proy, config=config):
        cargar_macros(biblioteca.macros, registro=registro)
    directorio = proy.raiz / "macros"
    if not directorio.is_dir():
        return registro
    raiz = proy.raiz.resolve()
    if directorio.is_symlink():
        raise ProyectoInvalido("`macros/` no puede ser un symlink")
    try:
        directorio.resolve().relative_to(raiz)
    except (OSError, ValueError) as e:
        raise ProyectoInvalido(f"`macros/` no está confinado en {raiz}") from e
    cargar_macros(directorio, registro=registro)
    return registro


@contextmanager
def escalares_del_proyecto(proy: "Proyecto", *, confiar: bool = False, registro=None):
    """Activa temporalmente las UDF de un proyecto explícitamente confiado.

    Restaura el registro aun si la importación o la evaluación falla. El archivo debe ser físico y
    estar dentro del proyecto: la confianza autoriza su código, no una ruta exterior inesperada.

    Shi, Zhang y Cui, *A Programming Paradigm for Spatiotemporal Composability*, §3.1, llaman
    revertible al efecto que devuelve su inverso y dejan que el runtime lo acumule. En
    `algebra.trazar` y `algebra.usar_registro`, el token de `ContextVar.set()` es ese inverso. Acá
    no alcanza un token: hay dos efectos, el registro de escalares y el proceso trabajador, con dos
    inversos distintos —restaurar la copia previa y cerrar el trabajador—. La restauración por copia
    es deliberada. Lo que NO se toma del paper es convertir esta ruta en un acumulador general de
    efectos ni en un ciclo de vida dinámico de componentes: el contrato ya se conserva.
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

    from nucleo import algebra
    from nucleo.aislamiento.escalares import (ErrorEscalarAislada,
                                              registrar_escalares_aisladas)

    destino = algebra.ESCALARES if registro is None else registro
    if not isinstance(destino, algebra.RegistroEscalares):
        raise EscalaresInvalidas("`registro` debe ser una instancia de RegistroEscalares")

    anteriores = dict(destino)
    globales_anteriores = dict(algebra.ESCALARES)
    trabajador = None
    carga_confirmada = False
    try:
        try:
            trabajador = registrar_escalares_aisladas(raiz, fisica, destino)
        except ErrorEscalarAislada as e:
            raise EscalaresInvalidas(f"falló {fisica}: {e}") from e
        except Exception as e:
            raise EscalaresInvalidas(
                f"falló {fisica}: {type(e).__name__}: {e}") from e
        yield str(fisica)
        carga_confirmada = True
    finally:
        conservar = (destino is not algebra.ESCALARES and carga_confirmada
                     and trabajador is not None and bool(trabajador.declaradas))
        if trabajador is not None and not conservar:
            trabajador.cerrar()
        if destino is algebra.ESCALARES or not carga_confirmada:
            destino.clear()
            destino.update(anteriores)
        if destino is not algebra.ESCALARES:
            algebra.ESCALARES.clear()
            algebra.ESCALARES.update(globales_anteriores)


def confiar_escalares(argv: list[str]) -> bool:
    return "--confiar-escalares" in argv


def sin_banderas_comunes(argv: list[str]) -> list[str]:
    return [a for a in sin_bandera(argv) if a != "--confiar-escalares"]


def _valido(ruta: Path) -> bool:
    return (ruta / "catalogos").is_dir()


def problemas_estructura(proy: "Proyecto", requeridos: tuple[str, ...]) -> list[str]:
    """Comprueba las partes que usa una herramienta y que no escapen mediante symlinks."""
    permitidos = {"catalogos", "corpus", "diferencial", "macros"}
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


# La superficie infija es cómo se escribe; el JSON es cómo se guarda. Una medida NUEVA nace en
# la superficie: el formato en el que se autoriza a alguien a escribir es el primer mensaje que
# da el lenguaje, y hasta hoy ese mensaje era «escribí JSON a mano».
EXTENSION_DE_AUTORIA = ".oracle"


# La gramática del id de una medida: `dominio.nombre`, minúsculas ASCII, dígitos y `_`.
#
# El ASCII no es pereza y no es que el proyecto no sea en español —la prosa de `porque` y de
# `alcance` lo es entera—. Es que un id es también un NOMBRE DE ARCHIVO, y en Unicode dos nombres
# que se dibujan idénticos pueden ser bytes distintos:
#
#     "dueño"  →  b'due\xc3\xb1o'    (ñ precompuesta, NFC)
#     "dueño"  →  b'duen\xcc\x83o'   (n + tilde combinante, NFD)
#
# Son distintos para Python, para git y para un `dict`, y se ven iguales en pantalla. macOS
# normaliza a NFD al escribir y Linux no toca nada, así que el mismo catálogo clonado en dos
# máquinas puede tener dos ids que nadie puede distinguir mirando. Eso es una divergencia
# silenciosa entre dos copias del mismo dato, que es justo la clase de cosa que este repositorio
# existe para no tener. Se cierra por gramática y no por normalización, porque normalizar es
# aceptar la ambigüedad y después elegir por el autor.
ID_MEDIDA_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")

# La gramática del id de un caso: minúsculas ASCII, dígitos y `-`, con al menos un tramo de
# dígitos que lo ordene. Comparte la razón de `ID_MEDIDA_RE`: el id es nombre de archivo y no
# puede depender de cómo normalice Unicode cada sistema operativo.
#
# Ojo con cómo se derivó, porque casi entra mal. La primera versión salía SÓLO del corpus de este
# repositorio —`^[0-9]{3}-…`, tres dígitos y a otra cosa— y rechazaba 9 de los casos de un
# consumidor real, que numera por dominio: `scatter-004-coberturas-distintas`,
# `physics-tanda-001-…`. Derivar la gramática de un solo catálogo es la misma trampa que medir la
# superficie contra las medidas que uno mismo escribió: describe al autor, no al lenguaje.
#
# Lo que se exige es lo que hace falta para que el id sea portable y ordenable, y nada más: sin
# mayúsculas, sin acentos, sin `_`, sin dos guiones seguidos, y con un número adentro.
ID_CASO_RE = re.compile(r"^(?=.*[0-9])[a-z0-9]+(?:-[a-z0-9]+)*$")


def ruta_de_medida_nueva(proy: "Proyecto", mid: str) -> Path:
    """Resuelve el destino de un id cerrado y demuestra su confinamiento antes de crear nada."""
    if not isinstance(mid, str) or ID_MEDIDA_RE.fullmatch(mid) is None:
        raise ProyectoInvalido(
            "el id debe ser `dominio.nombre`, sólo con minúsculas ASCII, dígitos y `_`")
    catalogos = proy.catalogos.resolve()
    destino = proy.catalogos / mid.split(".")[0] / f"{mid}{EXTENSION_DE_AUTORIA}"
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

    if not (RAIZ_ORACLE / "corpus").is_dir():
        raise ProyectoInvalido(
            "esta instalación no incluye el proyecto de autocertificación; indicá `--proyecto`")
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
