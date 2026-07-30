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

import os
from dataclasses import dataclass
from pathlib import Path

RAIZ_ORACLE = Path(__file__).resolve().parents[1]


class ProyectoInvalido(ValueError):
    pass


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


def catalogos_a_cargar(proy: "Proyecto") -> list[Path]:
    """El catálogo BASE de oracle más el del proyecto.

    Oracle trae medidas que valen para cualquiera que construya con un LLM —mutantes que sobreviven,
    afirmaciones sin alcance, verificaciones vencidas, corridas irreproducibles— y el proyecto agrega
    las de su dominio. Que las universales vengan incluidas es la diferencia entre una herramienta y
    un repositorio de ejemplos.
    """
    base = RAIZ_ORACLE / "catalogos"
    if proy.catalogos.resolve() == base.resolve():
        return [base]
    return [base, proy.catalogos]


def registrar_escalares(proy: "Proyecto") -> str:
    """Importa `<proyecto>/escalares.py` si existe, para que sus funciones de dominio queden
    declaradas. Sin esto, una medida del proyecto que use una escalar propia falla al evaluarse con
    «no es escalar declarada», y el error aparece lejos de la causa."""
    if proy.es_el_propio_oracle:
        return ""
    archivo = proy.raiz / "escalares.py"
    if not archivo.exists():
        return ""
    import importlib.util
    spec = importlib.util.spec_from_file_location(f"escalares_{proy.raiz.name}", archivo)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return str(archivo)


def _valido(ruta: Path) -> bool:
    return (ruta / "catalogos").is_dir()


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
