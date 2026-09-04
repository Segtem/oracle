"""Diagnóstico local: qué versión, qué entorno y qué proyecto — sin red y sin dominio.

Existe para que un reporte de problema no empiece con cinco preguntas de ida y vuelta. Es la
**fase 1** de la telemetría propuesta, y la única que se adopta ([`DECISION-007`], corrección 6):
se produce un archivo, la persona lo lee entero, y decide si lo comparte. **Acá no hay red.**

## Lo que NUNCA sale

Esta lista no es una precaución: es el contrato, y hay una medida que lo vigila.

    evidencia y filas          nombres de archivo del dominio      `porque` y `alcance`
    ids de medidas propias     remotos de git                      variables de entorno
    tokens                     el contenido de `escalares.py`      el nombre del host

De un proyecto sale su **forma** —qué carpetas existen, cuántas medidas y casos hay— nunca su
contenido. «Tiene 41 medidas» ayuda a reproducir un problema; cómo se llaman, no.

## Las rutas se reemplazan por marcadores

`/home/alguien/Dev/proyecto/catalogos` sale como `<PROYECTO>/catalogos`. El home sale como
`<HOME>`. Un nombre de usuario es un dato personal que se cuela en cualquier ruta absoluta.
"""

from __future__ import annotations

import platform
from dataclasses import dataclass
from pathlib import Path

from nucleo.version import VERSION_ALGEBRA, VERSION_DISTRIBUCION, VERSION_SINTAXIS

# Se reemplaza el más largo primero: el proyecto suele estar DENTRO del home, y al revés
# `<HOME>/Dev/proyecto` dejaría el nombre del directorio del proyecto a la vista.
MARCA_PROYECTO = "<PROYECTO>"
MARCA_HOME = "<HOME>"

CARPETAS = ("catalogos", "corpus", "relaciones", "diferencial", "macros")

AMBITOS_DE_RELACIONES = {"campo_diagnostico": "universal"}


@dataclass(frozen=True)
class Diagnostico:
    """Lo que se publica. Congelado: nadie le agrega un campo después de que lo revisaron."""

    datos: dict


def redactar(texto: str, proy=None) -> str:
    """Cambia rutas por marcadores. Devuelve el texto tal cual si no hay nada que redactar."""
    # El proyecto PRIMERO, y el orden está fijo por construcción, no ordenado en tiempo de
    # ejecución. Si el proyecto está dentro del home y se reemplaza el home primero, el nombre del
    # directorio del proyecto queda publicado. Acá había un `sorted(..., key=len)` cuyo mutante
    # sobrevivía: con dos elementos de orden conocido, ordenar es un cálculo que nada observa.
    reemplazos = []
    if proy is not None:
        reemplazos.append((str(Path(proy.raiz).resolve()), MARCA_PROYECTO))
    reemplazos.append((str(Path.home().resolve()), MARCA_HOME))
    for aguja, marca in reemplazos:
        texto = texto.replace(aguja, marca)
    return texto


def _forma_del_proyecto(proy) -> dict:
    """Qué carpetas hay y cuánto hay adentro. La FORMA, nunca los nombres."""
    raiz = Path(proy.raiz)
    forma = {nombre: (raiz / nombre).is_dir() for nombre in CARPETAS}
    # `is_file()` no es decoración: `rglob("*")` también devuelve DIRECTORIOS, y un directorio
    # tiene `suffix` vacío. Sin este filtro el conteo depende de que la extensión no coincida por
    # casualidad, y una carpeta llamada `x.json` contaría como medida.
    medidas = sum(1 for r in (raiz / "catalogos").rglob("*")
                  if r.is_file() and r.suffix in (".oracle", ".json"))
    casos = sum(1 for r in (raiz / "corpus").rglob("*")
                if r.is_file() and r.suffix in (".caso", ".json"))
    return {"carpetas": forma, "medidas": medidas, "casos": casos}


def reunir(proy=None, *, bibliotecas=None, perfiles=()) -> Diagnostico:
    """Arma el diagnóstico. `proy` opcional: preguntar la versión no exige tener un proyecto."""
    datos = {
        "oracle": {
            "distribucion": VERSION_DISTRIBUCION,
            "algebra": VERSION_ALGEBRA,
            "sintaxis": VERSION_SINTAXIS,
            # De dónde salió el paquete: distingue un checkout de una instalación, que es la
            # primera bifurcación de cualquier «a mí no me pasa».
            "corriendo_desde": redactar(str(Path(__file__).resolve().parent.parent), proy),
        },
        "entorno": {
            "python": platform.python_version(),
            "sistema": platform.system(),
            "arquitectura": platform.machine(),
            # `platform.node()` es el nombre del host y NO se incluye: identifica una máquina y no
            # ayuda a reproducir nada.
        },
        "proyecto": None,
        "bibliotecas": [],
        "perfiles": list(perfiles),
    }
    if proy is not None:
        datos["proyecto"] = _forma_del_proyecto(proy)
    for bid, manifiesto in sorted((bibliotecas or {}).items()):
        datos["bibliotecas"].append({
            "id": bid,
            "version": manifiesto.version,
            "algebra": manifiesto.algebra,
            "sintaxis": manifiesto.sintaxis,
            "mutantes_publicados": manifiesto.certificacion_mutantes,
        })
    return Diagnostico(datos)


RELACIONES_DEL_LENGUAJE = frozenset({"campo_diagnostico"})


def _textos(valor, camino=""):
    """Todos los valores de texto del diagnóstico, con el camino donde aparecen."""
    if isinstance(valor, str):
        yield camino, valor
    elif isinstance(valor, dict):
        for clave, hijo in valor.items():
            yield from _textos(hijo, f"{camino}.{clave}" if camino else str(clave))
    elif isinstance(valor, (list, tuple)):
        for i, hijo in enumerate(valor):
            yield from _textos(hijo, f"{camino}[{i}]")


def hechos_de_diagnostico(diagnostico: Diagnostico, secretos) -> dict:
    """Un hecho por valor de texto: si contiene algo que el proyecto declaró como suyo.

    `secretos` son las cadenas que NO pueden salir: ids de medidas, nombres de archivos del
    dominio, la raíz del proyecto y el home. La comparación es por contenido y no por igualdad —
    una ruta que EMPIEZA con el home ya publicó el nombre de usuario aunque siga con otra cosa.

    Que el contrato de este módulo sea prosa en un docstring no alcanza: un campo agregado el
    martes puede filtrar sin que nadie lo note hasta que alguien pegue el JSON en un issue. Por
    eso hay hechos y una medida —`meta.el_diagnostico_no_publica_el_dominio`— y no un comentario.
    """
    agujas = tuple(s for s in secretos if isinstance(s, str) and s.strip())
    filas = []
    for camino, texto in _textos(diagnostico.datos):
        filtrado = next((a for a in agujas if a in texto), "")
        filas.append({
            "campo": camino,
            "es_del_dominio": bool(filtrado),
            # Qué se coló, para que el rojo sea accionable. Va el NOMBRE de lo que se filtró, no
            # el valor completo: un testigo que reimprime el secreto lo publica igual.
            "que_se_colo": filtrado[:40],
        })
    return {"campo_diagnostico": filas}
