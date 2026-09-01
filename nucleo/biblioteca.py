"""Bibliotecas locales de políticas: datos verificables antes de resolver paquetes.

Esta primera versión fija el contrato ``oracle.biblioteca/v1`` sobre una carpeta física. No
descubre distribuciones ni importa módulos: manifiesto, medidas, casos, macros y relaciones se leen
como datos. Encontrar Python o un binario ejecutable es un error, no una invitación a confiarlo.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .caso import CasoMalDeclarado, cargar_casos
from .macro import MacroMalDeclarada, cargar_macros, macros_base
from .medida import (Medida, MedidaMalDeclarada, cargar_catalogo, relaciones_de_medida,
                     relaciones_del_lenguaje_declaradas)
from .mutacion import correr as mutar_medidas
from .relacion import RelacionMalDeclarada, cargar_relaciones
from .version import (VersionInvalida, compatible, del_nucleo, del_nucleo_sintaxis,
                      parsear)


ESQUEMA_BIBLIOTECA = "oracle.biblioteca/v1"
ARCHIVO_MANIFIESTO = "oracle-biblioteca.toml"
ID_BIBLIOTECA_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
VERSION_BIBLIOTECA_RE = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
SUFIJOS_EJECUTABLES = frozenset({".py", ".pyc", ".pyd", ".so", ".dll", ".dylib"})
CLAVES_CONTENIDO = frozenset({"catalogos", "corpus", "relaciones", "macros"})


class BibliotecaInvalida(ValueError):
    """La carpeta no satisface el contrato de una biblioteca de datos."""


@dataclass
class ManifiestoBiblioteca:
    raiz: Path
    id: str
    version: str
    algebra: str
    sintaxis: str
    catalogos: tuple[Path, ...]
    corpus: tuple[Path, ...]
    relaciones: tuple[Path, ...]
    macros: tuple[Path, ...]
    requiere_relaciones: tuple[str, ...]
    certificacion_mutantes: int


@dataclass
class InformeBiblioteca:
    manifiesto: ManifiestoBiblioteca
    medidas: int
    casos: int
    defectos_rojos: int
    verdes_correctos: int
    relaciones: int
    mutantes: int
    detalle_medidas: tuple[Medida, ...]


def _claves_exactas(datos: dict, esperadas: set[str] | frozenset[str], donde: str) -> None:
    recibidas = set(datos)
    if recibidas != set(esperadas):
        faltan = sorted(set(esperadas) - recibidas)
        sobran = sorted(recibidas - set(esperadas))
        partes = []
        if faltan:
            partes.append(f"faltan {faltan}")
        if sobran:
            partes.append(f"sobran {sobran}")
        raise BibliotecaInvalida(f"{donde}: {'; '.join(partes)}")


def _texto(datos: dict, nombre: str, donde: str) -> str:
    valor = datos.get(nombre)
    if not isinstance(valor, str):
        raise BibliotecaInvalida(f"{donde}.{nombre} debe ser texto no vacío y sin bordes")
    if not valor.strip():
        raise BibliotecaInvalida(f"{donde}.{nombre} debe ser texto no vacío y sin bordes")
    if valor != valor.strip():
        raise BibliotecaInvalida(f"{donde}.{nombre} debe ser texto no vacío y sin bordes")
    return valor


def _directorio_confinado(raiz: Path, texto: str, donde: str) -> Path:
    if not isinstance(texto, str):
        raise BibliotecaInvalida(f"{donde} debe ser una ruta POSIX relativa no vacía")
    if not texto:
        raise BibliotecaInvalida(f"{donde} debe ser una ruta POSIX relativa no vacía")
    if "\\" in texto:
        raise BibliotecaInvalida(f"{donde} debe ser una ruta POSIX relativa no vacía")
    relativa = PurePosixPath(texto)
    if relativa.is_absolute():
        raise BibliotecaInvalida(f"{donde} debe quedar dentro de la biblioteca: {texto!r}")
    if ".." in relativa.parts:
        raise BibliotecaInvalida(f"{donde} debe quedar dentro de la biblioteca: {texto!r}")
    ruta = raiz.joinpath(*relativa.parts)
    if ruta.is_symlink():
        raise BibliotecaInvalida(f"{donde} debe ser un directorio físico: {texto!r}")
    if not ruta.is_dir():
        raise BibliotecaInvalida(f"{donde} debe ser un directorio físico: {texto!r}")
    try:
        ruta.resolve().relative_to(raiz)
    except (OSError, ValueError) as e:
        raise BibliotecaInvalida(f"{donde} escapa de la biblioteca: {texto!r}") from e
    return ruta


def _lista_directorios(raiz: Path, contenido: dict, nombre: str) -> tuple[Path, ...]:
    valores = contenido.get(nombre)
    if not isinstance(valores, list):
        raise BibliotecaInvalida(
            f"contenido.{nombre} debe ser una lista de rutas sin duplicados")
    if any(not isinstance(valor, str) for valor in valores):
        raise BibliotecaInvalida(
            f"contenido.{nombre} debe ser una lista de rutas sin duplicados")
    if len(valores) != len(set(valores)):
        raise BibliotecaInvalida(
            f"contenido.{nombre} debe ser una lista de rutas sin duplicados")
    return tuple(
        _directorio_confinado(raiz, valor, f"contenido.{nombre}[{indice}]")
        for indice, valor in enumerate(valores)
    )


def _lista_relaciones(datos: dict) -> tuple[str, ...]:
    valores = datos.get("relaciones")
    if not isinstance(valores, list):
        raise BibliotecaInvalida("requiere.relaciones debe ser una lista de nombres sin duplicados")
    if any(not isinstance(valor, str) for valor in valores):
        raise BibliotecaInvalida("requiere.relaciones debe ser una lista de nombres sin duplicados")
    if any(not valor.strip() for valor in valores):
        raise BibliotecaInvalida("requiere.relaciones debe ser una lista de nombres sin duplicados")
    if any(valor != valor.strip() for valor in valores):
        raise BibliotecaInvalida("requiere.relaciones debe ser una lista de nombres sin duplicados")
    if len(valores) != len(set(valores)):
        raise BibliotecaInvalida("requiere.relaciones debe ser una lista de nombres sin duplicados")
    return tuple(valores)


def _numero_mutantes(certificacion: dict) -> int:
    _claves_exactas(certificacion, {"mutantes"}, "certificacion")
    numero = certificacion.get("mutantes")
    if isinstance(numero, bool):
        raise BibliotecaInvalida(
            "certificacion.mutantes debe publicar un entero positivo medido por tools/mutar.py")
    if not isinstance(numero, int):
        raise BibliotecaInvalida(
            "certificacion.mutantes debe publicar un entero positivo medido por tools/mutar.py")
    if numero <= 0:
        raise BibliotecaInvalida(
            "certificacion.mutantes debe publicar un entero positivo medido por tools/mutar.py")
    return numero


def _comprobar_version(nombre: str, declarada: str, disponible) -> None:
    try:
        necesitada = parsear(declarada)
    except VersionInvalida as e:
        raise BibliotecaInvalida(f"{nombre}: {e}") from e
    if not compatible(necesitada, disponible):
        raise BibliotecaInvalida(
            f"la biblioteca pide {nombre} {necesitada} y Oracle implementa {disponible}")


def cargar_manifiesto(ruta) -> ManifiestoBiblioteca:
    recibida = Path(ruta).expanduser()
    if recibida.is_symlink():
        raise BibliotecaInvalida(f"la biblioteca debe ser un directorio físico: {recibida}")
    if not recibida.is_dir():
        raise BibliotecaInvalida(f"la biblioteca debe ser un directorio físico: {recibida}")
    try:
        raiz = recibida.resolve()
    except OSError as e:
        raise BibliotecaInvalida(f"no se pudo resolver la biblioteca {recibida}: {e}") from e

    manifiesto = raiz / ARCHIVO_MANIFIESTO
    if manifiesto.is_symlink():
        raise BibliotecaInvalida(f"falta {ARCHIVO_MANIFIESTO} como archivo físico")
    if not manifiesto.is_file():
        raise BibliotecaInvalida(f"falta {ARCHIVO_MANIFIESTO} como archivo físico")
    try:
        datos = tomllib.loads(manifiesto.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as e:
        raise BibliotecaInvalida(f"no se pudo leer {ARCHIVO_MANIFIESTO}: {e}") from e
    if not isinstance(datos, dict):
        raise BibliotecaInvalida("el manifiesto debe ser una tabla TOML")
    _claves_exactas(
        datos,
        {"esquema", "id", "version", "algebra", "sintaxis", "datos_solamente",
         "contenido", "requiere", "certificacion"},
        "manifiesto",
    )

    if datos["esquema"] != ESQUEMA_BIBLIOTECA:
        raise BibliotecaInvalida(
            f"esquema debe ser {ESQUEMA_BIBLIOTECA!r}, no {datos['esquema']!r}")
    identificador = _texto(datos, "id", "manifiesto")
    if ID_BIBLIOTECA_RE.fullmatch(identificador) is None:
        raise BibliotecaInvalida(
            "manifiesto.id debe tener componentes ASCII en minúsculas separados por puntos")
    version = _texto(datos, "version", "manifiesto")
    if VERSION_BIBLIOTECA_RE.fullmatch(version) is None:
        raise BibliotecaInvalida("manifiesto.version debe ser MAYOR.MENOR.PARCHE")
    algebra = _texto(datos, "algebra", "manifiesto")
    sintaxis = _texto(datos, "sintaxis", "manifiesto")
    _comprobar_version("álgebra", algebra, del_nucleo())
    _comprobar_version("sintaxis", sintaxis, del_nucleo_sintaxis())
    if datos["datos_solamente"] is not True:
        raise BibliotecaInvalida("oracle.biblioteca/v1 exige datos_solamente = true")

    contenido = datos["contenido"]
    requiere = datos["requiere"]
    certificacion = datos["certificacion"]
    if not isinstance(contenido, dict):
        raise BibliotecaInvalida("contenido debe ser una tabla TOML")
    if not isinstance(requiere, dict):
        raise BibliotecaInvalida("requiere debe ser una tabla TOML")
    if not isinstance(certificacion, dict):
        raise BibliotecaInvalida("certificacion debe ser una tabla TOML")
    _claves_exactas(contenido, CLAVES_CONTENIDO, "contenido")
    _claves_exactas(requiere, {"relaciones"}, "requiere")

    catalogos = _lista_directorios(raiz, contenido, "catalogos")
    corpus = _lista_directorios(raiz, contenido, "corpus")
    relaciones = _lista_directorios(raiz, contenido, "relaciones")
    macros = _lista_directorios(raiz, contenido, "macros")
    if not catalogos:
        raise BibliotecaInvalida("contenido.catalogos no puede quedar vacío")
    if not corpus:
        raise BibliotecaInvalida("contenido.corpus no puede quedar vacío")

    for archivo in raiz.rglob("*"):
        if archivo.is_symlink():
            raise BibliotecaInvalida(f"una biblioteca de datos no admite symlinks: {archivo}")
        if archivo.is_file() and archivo.suffix.lower() in SUFIJOS_EJECUTABLES:
            raise BibliotecaInvalida(
                f"oracle.biblioteca/v1 no ejecuta código: archivo prohibido {archivo}")

    return ManifiestoBiblioteca(
        raiz=raiz,
        id=identificador,
        version=version,
        algebra=algebra,
        sintaxis=sintaxis,
        catalogos=catalogos,
        corpus=corpus,
        relaciones=relaciones,
        macros=macros,
        requiere_relaciones=_lista_relaciones(requiere),
        certificacion_mutantes=_numero_mutantes(certificacion),
    )


def _cargar_corpus(directorios: tuple[Path, ...]) -> list[dict]:
    salida = []
    ids: set[str] = set()
    for directorio in directorios:
        for caso in cargar_casos(directorio):
            if caso["id"] in ids:
                raise BibliotecaInvalida(f"el id de caso «{caso['id']}» está repetido")
            ids.add(caso["id"])
            salida.append(caso)
    return salida


def verificar_biblioteca(ruta) -> InformeBiblioteca:
    manifiesto = cargar_manifiesto(ruta)
    try:
        registro_macros = macros_base()
        cargar_macros(manifiesto.macros, registro=registro_macros)
        catalogo = cargar_catalogo(manifiesto.catalogos, macros=registro_macros)
        relaciones = cargar_relaciones(manifiesto.relaciones)
        casos = _cargar_corpus(manifiesto.corpus)
    except (CasoMalDeclarado, MacroMalDeclarada, MedidaMalDeclarada,
            RelacionMalDeclarada) as e:
        raise BibliotecaInvalida(str(e)) from e

    if not catalogo:
        raise BibliotecaInvalida("el catálogo de la biblioteca está vacío")
    if not casos:
        raise BibliotecaInvalida("el corpus de la biblioteca está vacío")

    consumidas = {
        relacion
        for medida in catalogo.values()
        for relacion in (*relaciones_de_medida(medida), *medida.requiere)
    }
    declaradas = set(manifiesto.requiere_relaciones)
    faltan_requisitos = sorted(consumidas - declaradas)
    if faltan_requisitos:
        raise BibliotecaInvalida(
            f"requiere.relaciones no declara las relaciones consumidas: {faltan_requisitos}")

    internas = set(relaciones_del_lenguaje_declaradas())
    sin_contrato = sorted(declaradas - internas - set(relaciones))
    if sin_contrato:
        raise BibliotecaInvalida(
            f"relaciones requeridas sin contrato en contenido.relaciones: {sin_contrato}")

    ejercitadas: set[str] = set()
    defectos_rojos = 0
    verdes_correctos = 0
    for caso in casos:
        mid = caso.get("medida")
        if mid not in catalogo:
            raise BibliotecaInvalida(
                f"el caso «{caso['id']}» reclama una medida ausente: {mid!r}")
        medida = catalogo[mid]
        necesarias = set(relaciones_de_medida(medida)) | set(medida.requiere)
        ausentes = sorted(r for r in necesarias if not caso["evidencia"].get(r))
        if ausentes:
            raise BibliotecaInvalida(
                f"el caso «{caso['id']}» no trae relaciones necesarias: {ausentes}")
        veredicto = medida.evaluar(caso["evidencia"])
        if veredicto.sin_evidencia:
            raise BibliotecaInvalida(
                f"el caso «{caso['id']}» no ejercita la medida: falta {veredicto.sin_evidencia}")
        esperado_ok = caso["etiqueta"] == "verde_correcto"
        if veredicto.ok != esperado_ok:
            esperado = "VERDE" if esperado_ok else "ROJO"
            raise BibliotecaInvalida(
                f"el caso «{caso['id']}» esperaba {esperado} y dio {veredicto.linea()}")
        ejercitadas.add(mid)
        if esperado_ok:
            verdes_correctos += 1
        else:
            defectos_rojos += 1

    sin_caso = sorted(set(catalogo) - ejercitadas)
    if sin_caso:
        raise BibliotecaInvalida(f"medidas sin ningún caso que las ejercite: {sin_caso}")

    evidencia_mutacion = mutar_medidas(catalogo, casos)
    mutantes = evidencia_mutacion["mutante"]
    numero_mutantes = len(mutantes)
    if numero_mutantes != manifiesto.certificacion_mutantes:
        raise BibliotecaInvalida(
            "certificacion.mutantes publica "
            f"{manifiesto.certificacion_mutantes}, pero tools/mutar.py mide {numero_mutantes}")
    vivos = [m for m in mutantes
             if not m["detecciones_conductuales"] and not m["rechazos_del_algebra"]]
    if vivos:
        cambios = [f"{m['apunta_a']}·{m['cambio']}" for m in vivos]
        raise BibliotecaInvalida(
            f"la biblioteca no se certifica: sobrevivieron {len(vivos)} mutantes: {cambios}")

    return InformeBiblioteca(
        manifiesto=manifiesto,
        medidas=len(catalogo),
        casos=len(casos),
        defectos_rojos=defectos_rojos,
        verdes_correctos=verdes_correctos,
        relaciones=len(relaciones),
        mutantes=numero_mutantes,
        detalle_medidas=tuple(catalogo[mid] for mid in sorted(catalogo)),
    )
