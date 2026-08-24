"""Genera y comprueba las cifras publicadas en el README de Oracle.

Un número escrito a mano en la prosa es una afirmación sin medida: nadie lo ejercita, así que no
puede fallar. Este archivo existe para que no queden. Cada bloque `<!-- <nombre>:inicio -->` del
README lo produce una función de acá, y `main()` sin `--actualizar` falla si alguno venció.

La deriva no es hipotética: el corte anterior publicaba «2202 líneas de núcleo», «106 negativas» y
una proporción de «trece a uno» cuando ya iban 2654, 150 y 16,2. Justamente la proporción es el
criterio de falsación declarado del proyecto —si no baja, el lenguaje no valió la pena—, y era el
número que nadie estaba midiendo.
"""

from __future__ import annotations

import json
import sys
import unittest
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

# Qué cuenta como «el metalenguaje» a los efectos de la proporción. Se declara acá, y no se deduce
# de un glob amplio, porque redefinir el denominador es la forma más barata de sastrear la medición:
# `perfiles/` es plataforma —hoy Python, mañana otra— y `tools/` son instrumentos, no lenguaje.
NUCLEO = "nucleo"


def _fuentes_del_nucleo() -> list[Path]:
    return sorted(p for p in (RAIZ / NUCLEO).glob("*.py") if p.name != "__init__.py")


def _lenguaje() -> list[Path]:
    """Todo lo que ES el lenguaje, no importa en qué archivo esté escrito.

    La biblioteca estándar de macros vive en `nucleo/macros/*.json` desde que dejó de ser un
    diccionario de Python. Si el numerador contara sólo `.py`, mover código a datos «mejoraría» la
    proporción sin que el lenguaje encogiera un gramo — que es exactamente el sastreo contra el que
    esta medición existe. Se cuenta lo uno y lo otro.
    """
    return _fuentes_del_nucleo() + sorted((RAIZ / NUCLEO / "macros").glob("*.json"))


def _medidas_universales() -> list[Path]:
    """Las medidas que Oracle publica: catálogo base más los perfiles empaquetados."""
    return sorted((RAIZ / "catalogos").glob("*/*.json")) + sorted(
        (RAIZ / "perfiles").glob("*/catalogos/*/*.json"))


def _lineas(rutas: list[Path]) -> int:
    return sum(len(r.read_text(encoding="utf-8").splitlines()) for r in rutas)


def _negativas(rutas: list[Path]) -> int:
    """Cuenta sentencias `raise`: la naturaleza del instrumento es declinar, y eso se cuenta."""
    return sum(
        1
        for r in rutas
        for linea in r.read_text(encoding="utf-8").splitlines()
        if linea.strip().startswith("raise ")
    )


def _casos_del_corpus() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((RAIZ / "corpus").glob("*/*.json"))]


def negativas() -> str:
    """La naturaleza del instrumento, contada. Sale de las mismas funciones que `escala()`, así que
    las dos secciones del README no pueden contradecirse."""
    fuentes = _fuentes_del_nucleo()
    return (f"En este corte hay {_lineas(_lenguaje())} líneas de lenguaje y "
            f"**{_negativas(fuentes)} negativas explícitas** (`raise`).")


def escala() -> str:
    """El costo del lenguaje contra lo escrito en él — el criterio de falsación del proyecto."""
    lineas_nucleo = _lineas(_lenguaje())
    negativas_ = _negativas(_fuentes_del_nucleo())

    medidas = _medidas_universales()
    lineas_medidas = _lineas(medidas)
    # Sin guarda defensiva a propósito. `_medidas_universales()` sólo devuelve medidas del catálogo
    # publicado, que ya están validadas: la rama `if datos and isinstance(...) else "?"` que había
    # acá era inalcanzable —la mutación la marcó, dos veces— y además convertía un catálogo roto en
    # una categoría silenciosa en vez de un error. Si un archivo no tiene forma de medida, que grite.
    formas = Counter(
        json.loads(m.read_text(encoding="utf-8"))[0] for m in medidas)
    por_macro = sum(cantidad for forma, cantidad in formas.items() if forma != "medida")

    # Decimal con coma: el README está en español y `16.2` se lee como otra cifra.
    proporcion = f"{lineas_nucleo / lineas_medidas:.1f}".replace(".", ",")
    return (
        f"**{lineas_nucleo} líneas de lenguaje** (`{NUCLEO}/`, código y macros) y "
        f"**{negativas_} negativas explícitas** "
        f"(`raise`). Contra las {len(medidas)} medidas universales escritas en él "
        f"({lineas_medidas} líneas): **{proporcion} a 1**. "
        f"{por_macro} de las {len(medidas)} pasan por una macro."
    )


def corpus() -> str:
    """Composición del corpus: lo que cambia cada vez que se captura un caso nuevo."""
    casos = _casos_del_corpus()
    etiquetas = Counter(c.get("etiqueta") for c in casos)
    archivados = Counter(
        c.get("estado_sin_medida") for c in casos if c.get("estado_sin_medida"))

    verdes = etiquetas["verde_correcto"]
    defectos = len(casos) - verdes
    resueltos = archivados["resuelto"]
    limites = archivados["limite_humano"]
    abiertos = archivados["abierto"]
    en_rojo = defectos - resueltos - limites - abiertos

    return (
        f"**{len(casos)} casos**: {defectos} defectos y {verdes} verdes correctos. "
        f"De los defectos, {en_rojo} deben ponerse en rojo · {abiertos} huecos abiertos · "
        f"{resueltos} resueltos conservados · {limites} límite humano. "
        f"Por etiqueta: {etiquetas['falso_verde']} falsos verdes, "
        f"{etiquetas['falso_rojo']} falsos rojos, "
        f"{etiquetas['medida_correcta_conclusion_errada']} conclusión causal incorrecta pese a una "
        f"medida correcta y {etiquetas['deuda_de_diseño']} deudas de diseño."
    )


def deteccion() -> str:
    """Por qué vía salió a la luz cada caso. `como_se_detecto` ya era un campo estructurado, así que
    la afirmación del README sobre las vías era computable y nadie la estaba computando."""
    casos = _casos_del_corpus()
    via = Counter(c.get("como_se_detecto") for c in casos)
    observacion = via["observacion"]
    no_observacionales = len(casos) - observacion

    nombres = {"mutacion": "la mutación", "persona": "una persona",
               "accidente": "la casualidad", "herramienta_ajena": "una herramienta ajena"}
    reparto = ", ".join(
        f"{via[clave]} {nombre}" for clave, nombre in nombres.items() if via[clave])
    sobran = sorted(set(via) - set(nombres) - {"observacion"})
    if sobran:
        raise ValueError(
            f"vías de detección sin nombre para el README: {sobran} — agregalas a `nombres`")

    return (f"Los {no_observacionales} casos no observacionales salieron a la luz por vías que no "
            f"aceptan el verde nominal: {reparto}.")


def cifras() -> str:
    suite = unittest.defaultTestLoader.discover(
        str(RAIZ / "tests"), top_level_dir=str(RAIZ))
    cantidad_tests = suite.countTestCases()

    from nucleo.medida import cargar_catalogo
    from nucleo.mutacion import correr as mutar_medidas
    from nucleo.proyecto import Proyecto, catalogos_a_cargar, macros_del_proyecto
    from perfiles.python.mutacion_codigo import sitios_de
    from tools import mutar as cli_medidas
    from tools.mutar_codigo import objetivos_disponibles

    proy = Proyecto(RAIZ)
    catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
    evidencia = mutar_medidas(catalogo, cli_medidas.casos(proy, catalogo))
    mutantes_medida = evidencia["mutante"]
    muertos_medida = sum(
        1 for fila in mutantes_medida
        if fila["detecciones_conductuales"] or fila["rechazos_del_algebra"])

    por_objetivo = {
        nombre: len(sitios_de(ruta, RAIZ))
        for nombre, ruta in objetivos_disponibles().items()
    }
    motor_python = por_objetivo["perfiles/python/mutacion_codigo.py"]
    total_codigo = sum(por_objetivo.values())
    resto_codigo = total_codigo - motor_python
    return (
        f"{cantidad_tests} tests · {muertos_medida}/{len(mutantes_medida)} mutantes de medida · "
        f"**{total_codigo} sitios de mutación de código** "
        f"({resto_codigo} + {motor_python} del motor Python)."
    )


BLOQUES = {"cifras": cifras, "escala": escala, "corpus": corpus, "negativas": negativas,
           "deteccion": deteccion}


def actualizar(contenido: str, nombre: str, bloque: str, ruta: str = "README.md") -> str:
    inicio = f"<!-- {nombre}:inicio -->"
    fin = f"<!-- {nombre}:fin -->"
    antes, separador, resto = contenido.partition(inicio)
    if not separador:
        raise ValueError(f"falta {inicio} en {ruta}")
    _viejo, separador, despues = resto.partition(fin)
    if not separador:
        raise ValueError(f"falta {fin} en {ruta}")
    return f"{antes}{inicio}\n{bloque}\n{fin}{despues}"


def render(contenido: str, ruta: str = "README.md") -> str:
    """Aplica los bloques que el documento declara con sus marcas.

    Un bloque **marcado** que no se puede generar es un error, no un salto: borrar la marca no puede
    ser la manera de librarse de la medición. Pero no todo documento publica todas las cifras, así
    que un bloque que el documento no marca simplemente no le aplica.
    """
    for nombre, generar in BLOQUES.items():
        if f"<!-- {nombre}:inicio -->" not in contenido:
            continue
        contenido = actualizar(contenido, nombre, generar(), ruta=ruta)
    return contenido


# Todo documento VERSIONADO que publique cifras se custodia acá. Sólo versionado, y el test
# `test_solo_se_custodian_documentos_versionados` lo hace cumplir: `estudio/` estuvo un rato en esta
# lista y era un error que las siete verificaciones locales no podían ver, porque la carpeta existe
# en el disco de quien la generó y está en `.gitignore`. En un checkout limpio —el CI— reventaba.
#
# Custodiar un artefacto generado además no sirve: `estudio/` y `ORACLE-PARA-NOTEBOOKLM.md` salen de
# `tools/estudio.py`, así que una cifra vencida ahí es un síntoma de que la fuente venció, y la
# fuente es el README, que sí está acá. Se arregla regenerando, no vigilando la copia.
DOCUMENTOS = ("README.md",)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    actualizar_todo = "--actualizar" in argv
    vencidos = []
    for nombre in DOCUMENTOS:
        ruta = RAIZ / nombre
        previo = ruta.read_text(encoding="utf-8")
        esperado = render(previo, ruta=nombre)
        if actualizar_todo:
            if previo != esperado:
                ruta.write_text(esperado, encoding="utf-8")
                print(f"{nombre} actualizado")
            continue
        if previo != esperado:
            vencidos.append(nombre)
    if actualizar_todo:
        return 0
    if vencidos:
        print(f"cifras vencidas en {', '.join(vencidos)}; "
              "ejecutá `python tools/cifras.py --actualizar`")
        return 1
    print("CIFRAS OK")
    for nombre, generar in BLOQUES.items():
        print(f"  {nombre}: {generar()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
