"""CLI para la superficie infija de autoría.

    python tools/sintaxis.py --imprimir catalogos/meta/meta.donde_compone.json
    python tools/sintaxis.py --leer medida.oracle
    python tools/sintaxis.py --verificar
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo.sintaxis import (  # noqa: E402,F401
    ErrorSintaxis,
    Lectura,
    Ubicacion,
    fragmento_de_error,
    imprimir,
    leer,
    leer_con_mapa,
    ubicar_ruta,
)
from nucleo import caso as sintaxis_caso  # noqa: E402
from nucleo.medida import cargar_fuente_medida, rutas_de_catalogo  # noqa: E402


def _rutas_catalogo(raiz: Path = RAIZ) -> list[Path]:
    return rutas_de_catalogo(
        raiz / "catalogos",
        *sorted((raiz / "perfiles").glob("*/catalogos")),
    )


def _rutas_macros(raiz: Path = RAIZ) -> list[Path]:
    """La biblioteca estándar de macros. Una macro es la otra mitad del lenguaje: si la superficie
    cubre las medidas y no las macros, es la sintaxis de la mitad del lenguaje."""
    from nucleo.macro import EXTENSIONES_DE_MACRO

    dir_macros = raiz / "nucleo" / "macros" if (raiz / "nucleo" / "macros").is_dir() else raiz / "macros"
    if not dir_macros.is_dir():
        return []
    return sorted(p for p in dir_macros.iterdir()
                  if p.suffix in EXTENSIONES_DE_MACRO and p.is_file())


def _rutas_corpus(raiz: Path = RAIZ) -> list[Path]:
    return sintaxis_caso.rutas_de_corpus(raiz / "corpus")


def _puntuacion(texto: str) -> int:
    return sum(1 for c in texto if unicodedata.category(c).startswith("P"))


def _fila_ilegible(ruta: Path, raiz: Path, e: Exception) -> dict:
    """La fila de un archivo que NO se pudo recorrer entero. No es lo mismo que uno cuya ida y
    vuelta no coincidió, y por eso lleva su propio campo.

    Un `json_igual: false` a secas diría «la superficie perdió información», que es una afirmación
    sobre el lenguaje. Acá la verdad es otra: no se llegó a comparar nada. Es la misma distinción
    que el núcleo hace con `Veredicto.sin_evidencia` —un rojo dice «el mundo está mal» y eso dice
    «no hay con qué mirar»— y la misma que la relación `equivalencia` ya modela con su campo
    `error`, que las cuatro medidas `meta.sintaxis_*` miran aparte de los booleanos.

    Los conteos van en cero: sumar caracteres de un archivo que no se imprimió sería inventarlos.

    ## Por qué `json_igual` va en `false` y no en `true`

    `agy` argumentó lo contrario, y el argumento es bueno: `nucleo/marco.py` neutraliza los campos
    que no tienen nada que decir —iguala `dio` a `esperado` cuando no hay medida— para que la
    medida de coincidencia no juzgue una fila que no le corresponde, y de la falta se ocupe otra.
    Aplicado acá sería poner los dos booleanos en `true`.

    No se hizo, y la razón es de qué lado se cae cada elección. `esperado_ok` y `dio_ok` son un PAR
    que se compara consigo mismo: ningún valor fijo es más seguro que otro, así que igualarlos es
    la única salida neutral. `json_igual` es un booleano suelto con un lado seguro y uno peligroso,
    y `Veredicto.sin_evidencia` ya decidió cuál: «`ok` sigue en False porque lo único inaceptable es
    que salga verde».

    Con `false`, si alguien borra el informe de ilegibles de `cmd_test` la corrida sigue saliendo
    roja por el camino viejo. Con `true`, sale VERDE y nadie se entera. Fail-closed contra
    fail-open, y este proyecto ya eligió ese lado en todos los demás.
    """
    return {
        "ruta": str(ruta.relative_to(raiz)),
        "imprimio": False,
        "error": f"{type(e).__name__}: {e}",
        "json_igual": False,
        "texto_igual": False,
        "caracteres_json": 0,
        "caracteres_superficie": 0,
        "puntuacion_json": 0,
        "puntuacion_superficie": 0,
    }


def _fila_verificacion(ruta: Path, raiz: Path) -> dict:
    try:
        texto = ruta.read_text(encoding="utf-8")
        datos = leer(texto) if ruta.suffix == ".oracle" else json.loads(texto)
        superficie = imprimir(datos)
        releida = leer(superficie)
        reimpresa = imprimir(releida)
    except Exception as e:                 # noqa: BLE001
        # A propósito TODA excepción, y no una lista de las conocidas: el impresor recorre datos de
        # un consumidor cualquiera, y lo que se está arreglando es justamente que una que nadie
        # previó matara la corrida entera en vez de contarse. La que se atrapa queda escrita en la
        # fila con su tipo y su mensaje; ninguna se convierte en verde.
        return _fila_ilegible(ruta, raiz, e)
    json_compacto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    return {
        "ruta": str(ruta.relative_to(raiz)),
        "imprimio": True,
        "error": "",
        "json_igual": releida == datos,
        "texto_igual": reimpresa == superficie,
        "caracteres_json": len(json_compacto),
        "caracteres_superficie": len(superficie),
        "puntuacion_json": _puntuacion(json_compacto),
        "puntuacion_superficie": _puntuacion(superficie),
    }


def _fila_verificacion_caso(ruta: Path, raiz: Path) -> dict:
    try:
        datos = sintaxis_caso.cargar_fuente_caso(ruta)
        superficie = sintaxis_caso.imprimir(datos)
        releida = sintaxis_caso.leer(superficie)
        reimpresa = sintaxis_caso.imprimir(releida)
    except Exception as e:                 # noqa: BLE001
        return _fila_ilegible(ruta, raiz, e)
    json_compacto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    return {
        "ruta": str(ruta.relative_to(raiz)),
        "imprimio": True,
        "error": "",
        "json_igual": releida == datos,
        "texto_igual": reimpresa == superficie,
        "caracteres_json": len(json_compacto),
        "caracteres_superficie": len(superficie),
        "puntuacion_json": _puntuacion(json_compacto),
        "puntuacion_superficie": _puntuacion(superficie),
    }


def verificar_catalogo(raiz: Path = RAIZ) -> dict:
    filas_medidas = [_fila_verificacion(r, raiz) for r in _rutas_catalogo(raiz)]
    filas_macros = [_fila_verificacion(r, raiz) for r in _rutas_macros(raiz)]
    filas_casos = [_fila_verificacion_caso(r, raiz) for r in _rutas_corpus(raiz)]
    filas = filas_medidas + filas_macros + filas_casos
    ilegibles = [f for f in filas if f["error"]]
    total = {
        "medidas": len(filas_medidas),
        "macros": len(filas_macros),
        "casos": len(filas_casos),
        # Lo que NO se pudo recorrer, aparte y con su nombre. Antes esto no existía porque la
        # primera excepción se llevaba puesta la corrida: `oracle test` moría con un traceback en
        # vez de decir cuántos archivos no pudo imprimir. Medido contra un consumidor real, eran 33
        # de 41 medidas, y ninguna de las otras 8 llegaba a informarse.
        "ilegibles": ilegibles,
        "json_igual": all(f["json_igual"] for f in filas),
        "texto_igual": all(f["texto_igual"] for f in filas),
        "caracteres_json": sum(f["caracteres_json"] for f in filas),
        "caracteres_superficie": sum(f["caracteres_superficie"] for f in filas),
        "puntuacion_json": sum(f["puntuacion_json"] for f in filas),
        "puntuacion_superficie": sum(f["puntuacion_superficie"] for f in filas),
        "filas": filas,
    }
    return total


# Los documentos que enseñan la superficie llevan bloques cercados. Sólo ```oracle promete ser una
# medida completa y verificable; las otras dos etiquetas declaran por qué un bloque NO se ejecuta, y
# esa declaración es el punto. `ORACLE-TUTORIAL-PRACTICO.md` afirma en su encabezado que todos sus
# ejemplos fueron verificados contra el código vigente, y hasta hoy esa afirmación no la ejercitaba
# nada: la sostenía la palabra de quien escribió el documento, que es exactamente la clase de
# afirmación que este repositorio no acepta en ningún otro lado.
# Los cuatro documentos que muestran superficie. Eran dos: al entrar la superficie de CASOS, los
# ejemplos nuevos aparecieron también en el README y en la especificación, y ahí nadie los miraba.
DOCUMENTOS_CON_SUPERFICIE = ("ESCRIBIR-UNA-MEDIDA.md", "ORACLE-TUTORIAL-PRACTICO.md",
                             "README.md", "ESPECIFICACION.md")
# Dos superficies, dos lectores. `oracle` es una medida y `caso` es un caso del corpus; las
# etiquetas con sufijo declaran por qué un bloque NO se ejecuta, y esa declaración es el punto.
BLOQUE_RE = re.compile(
    r"```(oracle|caso)(-gramatica|-fragmento)?\n(.*?)```", re.S)


def verificar_documentos(raiz: Path = RAIZ) -> dict:
    """Cada bloque ```oracle de los documentos tiene que leer y volver idéntico."""
    fallas, ejecutables, declarados = [], 0, 0
    for nombre in DOCUMENTOS_CON_SUPERFICIE:
        ruta = raiz / nombre
        if not ruta.exists():
            # Un documento declarado que no está es un ERROR, no un salto: si faltara en silencio,
            # sacar un documento de la verificación sería tan barato como renombrarlo.
            fallas.append(f"{nombre}: declarado pero no está en el árbol")
            continue
        texto = ruta.read_text(encoding="utf-8")
        for m in BLOQUE_RE.finditer(texto):
            superficie, sufijo, bloque = m.group(1), m.group(2), m.group(3)
            linea = texto[:m.start()].count("\n") + 1
            if sufijo:
                declarados += 1
                continue
            ejecutables += 1
            leer_, imprimir_ = ((leer, imprimir) if superficie == "oracle"
                                else (sintaxis_caso.leer, sintaxis_caso.imprimir))
            try:
                datos = leer_(bloque)
            except (ErrorSintaxis, sintaxis_caso.CasoMalDeclarado) as e:
                fallas.append(f"{nombre}:{linea}: no lee — {e}")
                continue
            if imprimir_(datos) != bloque:
                fallas.append(f"{nombre}:{linea}: lee pero no es la forma canónica que imprime la "
                              "herramienta")
    return {"ejecutables": ejecutables, "declarados": declarados, "fallas": fallas}


def _porcentaje(num: int, den: int) -> str:
    return f"{(100 * num / den):.1f}%".replace(".", ",") if den else "0,0%"


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--imprimir":
        if len(argv) != 2:
            print("uso: python tools/sintaxis.py --imprimir <medida.json|medida.oracle>")
            return 1
        print(imprimir(cargar_fuente_medida(Path(argv[1]))), end="")
        return 0
    if argv[0] == "--leer":
        if len(argv) != 2:
            print("uso: python tools/sintaxis.py --leer <medida.oracle>")
            return 1
        # El LECTOR es puro a propósito y no juzga la versión declarada; eso es trabajo del que
        # carga. Pero esta rama del CLI también carga: sin la comprobación, `--leer` traducía en
        # silencio —y con exit 0— un archivo escrito contra una sintaxis que este núcleo no
        # implementa, mientras `cargar_fuente_medida` y `cargar_macros` lo rechazaban. Una salida
        # fail-open al lado de dos fail-closed es peor que no tener ninguna: enseña a confiar.
        from nucleo.version import VersionInvalida, exigir_sintaxis_compatible

        texto = Path(argv[1]).read_text(encoding="utf-8")
        try:
            lectura = leer_con_mapa(texto)
            exigir_sintaxis_compatible(lectura.version)
        except (ErrorSintaxis, VersionInvalida) as e:
            print(f"✗ {fragmento_de_error(e, texto)}")
            return 1
        datos = lectura.datos
        print(json.dumps(datos, ensure_ascii=False, separators=(",", ":")))
        return 0
    if argv[0] == "--verificar":
        informe = verificar_catalogo()
        docs = verificar_documentos()
        ok = (informe["json_igual"] and informe["texto_igual"] and informe["medidas"] > 0
              and informe["macros"] > 0 and informe["casos"] > 0 and not docs["fallas"]
              and docs["ejecutables"] > 0)
        print(f"medidas convertidas: {informe['medidas']}")
        print(f"macros convertidas: {informe['macros']}")
        print(f"casos convertidos: {informe['casos']}")
        print(f"ida JSON: {'OK' if informe['json_igual'] else 'FALLA'}")
        print(f"vuelta texto: {'OK' if informe['texto_igual'] else 'FALLA'}")
        print(f"caracteres: JSON {informe['caracteres_json']} · superficie "
              f"{informe['caracteres_superficie']}")
        print(f"puntuación: JSON {informe['puntuacion_json']} "
              f"({_porcentaje(informe['puntuacion_json'], informe['caracteres_json'])}) · "
              f"superficie {informe['puntuacion_superficie']} "
              f"({_porcentaje(informe['puntuacion_superficie'], informe['caracteres_superficie'])})")
        print(f"bloques de documentación: {docs['ejecutables']} verificados · "
              f"{docs['declarados']} declarados como gramática o fragmento")
        for falla in docs["fallas"]:
            print(f"  ✗ {falla}")
        return 0 if ok else 1
    print(f"opción desconocida: {argv[0]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
