"""Contrato de procedencia y frescura de los fixtures diferenciales.

Las huellas no prueban que una referencia sea correcta. Prueban algo más modesto y necesario: que
el fixture que se está releyendo fue generado con el emisor, la referencia, el catálogo y la
configuración que dice haber usado.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from .version import VersionInvalida, del_nucleo, parsear

ESQUEMA_DIFERENCIAL = "oracle.diferencial/v1"
ALGORITMO_HUELLA = "sha256"
HUELLA_RE = re.compile(r"^[0-9a-f]{64}$")


class ProcedenciaInvalida(ValueError):
    pass


@dataclass(frozen=True)
class Procedencia:
    """Archivos que hacen materialmente al fixture, relativos a una raíz estable."""

    raiz: Path
    emisor: tuple[str, ...]
    referencia: tuple[str, ...]
    desde_proyecto: str = "."

    def __post_init__(self) -> None:
        object.__setattr__(self, "raiz", Path(self.raiz))
        for nombre, rutas in (("emisor", self.emisor), ("referencia", self.referencia)):
            if not isinstance(rutas, tuple) or not rutas:
                raise ProcedenciaInvalida(f"{nombre} requiere al menos una ruta")
            if any(not isinstance(r, str) or not r.strip() for r in rutas):
                raise ProcedenciaInvalida(f"{nombre} contiene una ruta inválida")
        if (not isinstance(self.desde_proyecto, str)
                or self.desde_proyecto not in (".", "..")):
            raise ProcedenciaInvalida(
                "desde_proyecto sólo puede ser '.' o '..'; no se recorren ancestros arbitrarios")


def json_canonico(datos) -> bytes:
    try:
        return json.dumps(
            datos, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as e:
        raise ProcedenciaInvalida(f"los datos de procedencia no son JSON canónico: {e}") from e


def huella_datos(datos) -> str:
    return hashlib.sha256(json_canonico(datos)).hexdigest()


def _resolver_entrada(raiz: Path, entrada: str) -> tuple[str, Path]:
    relativa = Path(entrada)
    if relativa.is_absolute() or ".." in relativa.parts or relativa == Path("."):
        raise ProcedenciaInvalida(f"ruta de procedencia no confinada: {entrada!r}")
    try:
        raiz_fisica = raiz.resolve(strict=True)
    except OSError as e:
        raise ProcedenciaInvalida(f"raíz de procedencia inválida: {raiz}: {e}") from e
    candidata = raiz / relativa
    try:
        fisica = candidata.resolve(strict=True)
        fisica.relative_to(raiz_fisica)
    except (OSError, ValueError) as e:
        raise ProcedenciaInvalida(f"ruta de procedencia inválida: {entrada!r}: {e}") from e
    if candidata.is_symlink():
        raise ProcedenciaInvalida(f"una ruta de procedencia no puede ser symlink: {entrada!r}")
    return relativa.as_posix(), fisica


def _archivos(raiz: Path, entradas: tuple[str, ...] | list[str]) -> list[tuple[str, Path]]:
    encontrados: dict[str, Path] = {}
    try:
        raiz_fisica = raiz.resolve(strict=True)
    except OSError as e:
        raise ProcedenciaInvalida(f"raíz de procedencia inválida: {raiz}: {e}") from e
    for entrada in entradas:
        relativa, fisica = _resolver_entrada(raiz, entrada)
        candidatos = [fisica] if fisica.is_file() else sorted(p for p in fisica.rglob("*") if p.is_file())
        if not candidatos:
            raise ProcedenciaInvalida(f"la procedencia {entrada!r} no contiene archivos")
        for archivo in candidatos:
            if archivo.is_symlink():
                raise ProcedenciaInvalida(
                    f"una fuente de procedencia no puede ser symlink: {archivo}")
            try:
                ruta = archivo.resolve(strict=True).relative_to(raiz_fisica).as_posix()
            except (OSError, ValueError) as e:
                raise ProcedenciaInvalida(f"fuente fuera de la raíz: {archivo}: {e}") from e
            encontrados[ruta] = archivo
    return sorted(encontrados.items())


def huella_archivos(raiz: Path, entradas: tuple[str, ...] | list[str]) -> str:
    manifiesto = [
        {"ruta": ruta, "sha256": hashlib.sha256(archivo.read_bytes()).hexdigest()}
        for ruta, archivo in _archivos(Path(raiz), entradas)
    ]
    return huella_datos(manifiesto)


def huella_catalogo(medidas) -> str:
    canonicas = {m.id: m.a_datos() for m in sorted(medidas, key=lambda m: m.id)}
    if not canonicas:
        raise ProcedenciaInvalida("no se puede firmar un catálogo sin medidas")
    return huella_datos(canonicas)


def crear_frescura(procedencia: Procedencia, medidas, configuracion: dict) -> dict:
    if not isinstance(configuracion, dict):
        raise ProcedenciaInvalida("la configuración tiene que ser un mapa JSON")
    return {
        "algoritmo": ALGORITMO_HUELLA,
        "raiz_fuentes": procedencia.desde_proyecto,
        "fuentes": {
            "emisor": list(procedencia.emisor),
            "referencia": list(procedencia.referencia),
        },
        "configuracion": configuracion,
        "huellas": {
            "emisor": huella_archivos(procedencia.raiz, procedencia.emisor),
            "referencia": huella_archivos(procedencia.raiz, procedencia.referencia),
            "catalogo": huella_catalogo(medidas),
            "configuracion": huella_datos(configuracion),
        },
    }


def ids_de_medidas(datos: dict) -> list[str]:
    if "escenarios" in datos:
        return list(datos.get("medidas", []))
    return list(datos.get("grupos", {}))


def revisar_frescura(datos: dict, raiz: Path, catalogo: dict) -> list[str]:
    """Recalcula cada huella contra el proyecto actual. Un desacuerdo vence el fixture."""
    frescura = datos["frescura"]
    raiz_fuentes = Path(raiz) / frescura["raiz_fuentes"]
    fuentes = frescura["fuentes"]
    esperadas = frescura["huellas"]
    medidas = [catalogo[mid] for mid in ids_de_medidas(datos) if mid in catalogo]
    faltan = [mid for mid in ids_de_medidas(datos) if mid not in catalogo]
    if faltan:
        return [f"fixture vencido: faltan medidas actuales para recalcular el catálogo: {faltan}"]

    actuales = {"catalogo": huella_catalogo(medidas),
                "configuracion": huella_datos(frescura["configuracion"])}
    problemas = []
    for clase in ("emisor", "referencia"):
        try:
            actuales[clase] = huella_archivos(raiz_fuentes, fuentes[clase])
        except (OSError, ProcedenciaInvalida) as e:
            problemas.append(f"fixture vencido: no se pudo comprobar {clase}: {e}")
    for clase, esperada in esperadas.items():
        if clase in actuales and actuales[clase] != esperada:
            problemas.append(
                f"fixture vencido: cambió {clase} ({esperada[:12]}… → {actuales[clase][:12]}…)")
    return problemas


def comprobar_version_referencia(modulo) -> list[str]:
    """La referencia declara contra qué versión del álgebra se escribió; tiene que coincidir con la
    que implementa el núcleo.

    Es el caso que motivó el versionado: agregar `requiere` y `clave` invalidó en silencio a un
    evaluador escrito contra una versión anterior, y el contraste siguió publicando «0 desacuerdos»
    porque los fixtures no ejercitaban lo nuevo. La referencia se fija a una versión EXACTA — no a
    una compatible—: un agregado no rompe a quien no lo usa, pero sí a quien implementa el álgebra
    completo y no conoce el nodo.
    """
    declarada = getattr(modulo, "VERSION_ALGEBRA", None)
    if declarada is None:
        return ["la implementación de referencia no declara `VERSION_ALGEBRA`"]
    try:
        version = parsear(declarada)
    except VersionInvalida as e:
        return [str(e)]
    nucleo = del_nucleo()
    if version != nucleo:
        return [f"la referencia se escribió contra el álgebra {version} "
                f"y el núcleo implementa {nucleo}"]
    return []
