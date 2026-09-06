"""Prepara un reporte de límite para revisar y publicar a mano.

Este módulo no conoce GitHub, credenciales ni el corpus. Recibe el diagnóstico que ya reunió
`oracle diagnostico`, arma un artefacto Markdown y, sólo cuando la persona lo pidió, incorpora la
medida o la evidencia. La salida completa es el consentimiento: nada se comparte desde acá.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from nucleo.caso import DETECCIONES
from nucleo.diagnostico import Diagnostico, redactar


class ReporteInvalido(ValueError):
    """El reporte no tiene la forma mínima necesaria para que otra persona lo entienda."""


@dataclass(frozen=True)
class Reporte:
    """El texto exacto que la persona revisa antes de decidir si lo copia."""

    texto: str


def _texto_requerido(nombre: str, valor: str, *, recortar: bool = True) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ReporteInvalido(f"`{nombre}` no puede estar vacío")
    return valor.strip() if recortar else valor


def _bloque(contenido: str, lenguaje: str = "text") -> str:
    """Encierra contenido sin permitir que sus propios acentos graves oculten una parte.

    La vista previa tiene que mostrar TODO. Una cerca fija de tres acentos se cerraría antes de
    tiempo si la evidencia trajera otra cerca Markdown, y el resto se renderizaría como estructura
    del issue en vez de como los bytes que la persona está por compartir.
    """
    mayor = 0
    actual = 0
    for caracter in contenido:
        if caracter == "`":
            actual += 1
            mayor = max(mayor, actual)
        else:
            actual = 0
    cerca = "`" * max(3, mayor + 1)
    return f"{cerca}{lenguaje}\n{contenido}\n{cerca}"


def preparar(*, esperado: str, ocurrido: str, como_se_detecto: str,
             diagnostico: Diagnostico, proy=None, medida: str | None = None,
             evidencia: str | None = None) -> Reporte:
    """Arma el Markdown; medida y evidencia entran sólo mediante argumentos explícitos."""
    esperado = _texto_requerido("esperado", esperado)
    ocurrido = _texto_requerido("ocurrido", ocurrido)
    if como_se_detecto not in DETECCIONES:
        opciones = ", ".join(sorted(DETECCIONES))
        raise ReporteInvalido(f"`como_se_detecto` debe ser una de: {opciones}")
    if medida is not None:
        medida = _texto_requerido("medida", medida)
    if evidencia is not None:
        # En filas tabulares, los espacios y el salto final pueden ser parte de la evidencia. Se
        # valida que haya contenido sin reescribir lo que la persona pidió mostrar.
        evidencia = _texto_requerido("evidencia", evidencia, recortar=False)

    # Se redacta también la prosa libre. No alcanza para llamarla segura —Oracle no sabe qué es
    # secreto en un negocio—, pero una ruta conocida no debe sobrevivir sólo porque apareció en
    # `ocurrido` en vez de dentro de la evidencia.
    esperado = redactar(esperado, proy)
    ocurrido = redactar(ocurrido, proy)
    diagnostico_json = json.dumps(diagnostico.datos, ensure_ascii=False, indent=2)

    partes = [
        "# Reporte de límite de Oracle",
        "",
        "## sintoma",
        "",
        "### que_se_quiso_expresar_o_medir",
        "",
        _bloque(esperado),
        "",
        "### que_ocurrio_en_cambio",
        "",
        _bloque(ocurrido),
        "",
        "## como_se_detecto",
        "",
        f"`{como_se_detecto}`",
        "",
        "## diagnostico",
        "",
        _bloque(diagnostico_json, "json"),
    ]
    if medida is not None:
        partes.extend(("", "## medida", "", _bloque(redactar(medida, proy))))
    if evidencia is not None:
        partes.extend(("", "## evidencia", "", _bloque(redactar(evidencia, proy))))
    return Reporte("\n".join(partes) + "\n")


def leer_evidencia(ruta: str) -> str:
    """Lee sólo la ruta que la persona nombró; no busca evidencia dentro del proyecto."""
    try:
        return Path(ruta).expanduser().read_text(encoding="utf-8")
    except OSError as e:
        raise ReporteInvalido(f"no se pudo leer la evidencia `{ruta}`: {e}") from e
