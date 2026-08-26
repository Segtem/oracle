"""Entry point único para Oracle.

    oracle init [ruta]                      inicializa un proyecto con catalogos/, corpus/, diferencial/ y oracle.json
    oracle nueva <dominio.nombre>          crea una nueva medida en catalogos/ con plantilla lista
    oracle caso <grupo/id>                 crea un nuevo caso en corpus/ con plantilla lista
    oracle revisar <archivo>               revisa y evalúa una medida suelta contra la evidencia del proyecto
    oracle test [--rapido]                 ejecuta la secuencia completa de verificación con veredicto final
    oracle relaciones                      hechos y campos disponibles derivados de la evidencia
    oracle escalares                       funciones de dominio y operadores disponibles
    oracle expandir <archivo>              muestra la forma canónica de una medida escrita con macros
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos  # noqa: F401,E402
from nucleo.caso import rutas_de_corpus  # noqa: E402
from nucleo.medida import cargar_catalogo  # noqa: E402
from nucleo.proyecto import (  # noqa: E402
    ESQUEMA_PROYECTO,
    EscalaresInvalidas,
    EscalaresNoConfiables,
    Proyecto,
    ProyectoInvalido,
    catalogos_a_cargar,
    confiar_escalares,
    escalares_del_proyecto,
    macros_del_proyecto,
    presentar_ruta,
    problemas_estructura,
    resolver,
    sin_bandera,
    sin_banderas_comunes,
)
from tools import aceptacion, corpus, diferencial, medida, mutar, sintaxis  # noqa: E402


def ayuda() -> None:
    print("""Oracle — metalenguaje para medir evidencia, alcance y mutación.

Uso:
  oracle init [ruta]                      Inicializa un proyecto nuevo
  oracle nueva <dominio.nombre>          Crea una medida con plantilla lista para editar
  oracle caso <grupo/id>                 Crea un caso de prueba en el corpus
  oracle revisar <archivo>               Revisa y evalúa una medida suelta
  oracle test [--rapido]                 Ejecuta la secuencia completa de verificación
  oracle relaciones                      Muestra las relaciones y campos observados
  oracle escalares                       Muestra las funciones escalares y operadores
  oracle expandir <archivo>              Muestra la forma canónica de una macro
  oracle --help                          Muestra esta ayuda

Banderas comunes:
  --proyecto <ruta>      Ruta al proyecto (por defecto: directorio actual o $ORACLE_PROYECTO)
  --confiar-escalares    Autoriza la ejecución de funciones en `escalares.py`
  --rapido               En `oracle test`, saltea la mutación de medidas""")


def cmd_init(ruta_str: str | None, argv: list[str]) -> int:
    if ruta_str is not None:
        raiz = Path(ruta_str).expanduser().resolve()
    elif "--proyecto" in argv:
        i = argv.index("--proyecto")
        if i + 1 >= len(argv):
            print("PROYECTO INVÁLIDO — --proyecto necesita una ruta", file=sys.stderr)
            return 1
        raiz = Path(argv[i + 1]).expanduser().resolve()
    else:
        raiz = Path.cwd().resolve()

    catalogos_dir = raiz / "catalogos"
    corpus_dir = raiz / "corpus"
    diferencial_dir = raiz / "diferencial"
    oracle_json = raiz / "oracle.json"

    try:
        catalogos_dir.mkdir(parents=True, exist_ok=True)
        corpus_dir.mkdir(parents=True, exist_ok=True)
        diferencial_dir.mkdir(parents=True, exist_ok=True)
        if not oracle_json.exists():
            datos = {"esquema": ESQUEMA_PROYECTO}
            oracle_json.write_text(json.dumps(datos, indent=2) + "\n", encoding="utf-8")
    except OSError as e:
        print(f"No se pudo inicializar el proyecto en {raiz}: {e}", file=sys.stderr)
        return 1

    print(f"Proyecto Oracle inicializado en {raiz}:")
    print("  · catalogos/")
    print("  · corpus/")
    print("  · diferencial/")
    print("  · oracle.json\n")
    print("Próximos pasos:")
    print("  1. Creá una medida:  oracle nueva <dominio.nombre>")
    print("  2. Creá un caso:     oracle caso <grupo/id>")
    print("  3. Verificá todo:    oracle test")
    return 0


def cmd_nueva(proy: Proyecto, mid: str) -> int:
    return medida.nueva(proy, mid)


def cmd_caso(proy: Proyecto, ubicacion: str) -> int:
    return corpus.nuevo(proy, ubicacion)


def cmd_revisar(proy: Proyecto, ruta_str: str, argv: list[str]) -> int:
    ruta = Path(ruta_str)
    if not ruta.exists():
        ruta = proy.raiz / ruta_str
    if not ruta.exists():
        print(f"no existe: {ruta_str}")
        return 1
    try:
        with escalares_del_proyecto(proy, confiar=confiar_escalares(argv)):
            return medida.revisar(proy, ruta)
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
        return 1


def cmd_relaciones(proy: Proyecto) -> int:
    return medida.relaciones(proy)


def cmd_escalares(proy: Proyecto, argv: list[str]) -> int:
    externas = not proy.es_el_propio_oracle and (proy.raiz / "escalares.py").exists()
    if externas and not confiar_escalares(argv):
        return medida.escalares(proy, externas_omitidas=True)
    try:
        with escalares_del_proyecto(proy, confiar=confiar_escalares(argv)):
            return medida.escalares(proy)
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
        return 1


def cmd_expandir(proy: Proyecto, ruta_str: str) -> int:
    ruta = Path(ruta_str)
    if not ruta.exists():
        ruta = proy.raiz / ruta_str
    if not ruta.exists():
        print(f"no existe: {ruta_str}")
        return 1
    return medida.expandir_archivo(ruta, macros_del_proyecto(proy))


def cmd_test(proy: Proyecto, argv: list[str]) -> int:
    rapido = "--rapido" in argv
    confiar = confiar_escalares(argv)

    estructura = problemas_estructura(proy, ("catalogos", "corpus", "diferencial"))
    if estructura:
        print("PROYECTO INVÁLIDO — " + "; ".join(estructura))
        print("\nVEREDICTO: ROJO (estructura de proyecto inválida)")
        return 1

    if (proy.raiz / "escalares.py").exists() and not proy.es_el_propio_oracle and not confiar:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {proy.raiz / 'escalares.py'} es código Python "
              "externo; repetí con `--confiar-escalares` para ejecutarlo")
        print("\nVEREDICTO: ROJO (escalares.py no confiado)")
        return 1

    macros = macros_del_proyecto(proy)
    try:
        catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros)
    except Exception as e:
        print(f"CATÁLOGO INVÁLIDO — {e}")
        print("\nVEREDICTO: ROJO (catálogo no pudo cargarse)")
        return 1

    casos_archivos = rutas_de_corpus(proy.corpus)
    rutas_diferencial = sorted(proy.diferencial.glob("*.json"))

    if len(catalogo) == 0 and len(casos_archivos) == 0 and len(rutas_diferencial) == 0:
        print("CORPUS OK · 0 casos · esquema y evidencia L0 en regla")
        print("SINTAXIS: salteado (sin medidas ni casos todavía)")
        print("ACEPTACIÓN: salteado (sin medidas ni casos todavía)")
        print("DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)")
        print("MUTACIÓN: salteada (sin medidas todavía)\n")
        print("VEREDICTO: VERDE (proyecto vacío: 0 medidas, 0 casos)")
        return 0

    fallas_suite: list[str] = []

    # 1. Corpus
    fallas_corpus, cargados_casos = corpus.verificar(proy.corpus)
    if fallas_corpus:
        print(f"CORPUS: {len(fallas_corpus)} problema(s)")
        for f in fallas_corpus:
            print("  ·", f)
        fallas_suite.append("corpus")
    else:
        print(f"CORPUS OK · {len(cargados_casos)} casos · esquema, evidencia L0 y trazabilidad en regla")
    print()

    # 2. Sintaxis
    if len(catalogo) == 0 and len(casos_archivos) == 0:
        print("SINTAXIS: salteado (sin medidas ni casos todavía)")
    else:
        informe_sintaxis = sintaxis.verificar_catalogo(proy.raiz)
        sintaxis_ok = (informe_sintaxis["json_igual"] and informe_sintaxis["texto_igual"])
        if not sintaxis_ok:
            print("SINTAXIS ✗ — la conversión de ida y vuelta falló")
            fallas_suite.append("sintaxis")
        else:
            docs_ok = True
            if proy.es_el_propio_oracle:
                docs = sintaxis.verificar_documentos(proy.raiz)
                if docs["fallas"]:
                    docs_ok = False
                    print(f"SINTAXIS ✗ — {len(docs['fallas'])} falla(s) en documentación")
                    for f in docs["fallas"]:
                        print("  ·", f)
                    fallas_suite.append("sintaxis (documentos)")
            if docs_ok:
                print(f"SINTAXIS OK · {informe_sintaxis['medidas']} medidas · "
                      f"{informe_sintaxis['macros']} macros · {informe_sintaxis['casos']} casos")
    print()

    # 3. Aceptación
    if len(catalogo) > 0 and len(casos_archivos) == 0:
        print("ACEPTACIÓN ✗ — sin casos en el corpus: un catálogo con medidas no puede verificarse sin casos")
        fallas_suite.append("aceptación")
    elif len(catalogo) == 0 and len(casos_archivos) == 0:
        print("ACEPTACIÓN: salteado (sin medidas ni casos todavía)")
    else:
        try:
            with escalares_del_proyecto(proy, confiar=confiar):
                rc_aceptacion = aceptacion._ejecutar(proy)
                if rc_aceptacion != 0:
                    fallas_suite.append("aceptación")
        except (EscalaresNoConfiables, EscalaresInvalidas) as e:
            print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
            fallas_suite.append("aceptación (escalares)")
    print()

    # 4. Diferencial
    if not rutas_diferencial:
        print("DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)")
    else:
        try:
            with escalares_del_proyecto(proy, confiar=confiar):
                rc_diferencial = diferencial._ejecutar(proy)
                if rc_diferencial != 0:
                    fallas_suite.append("diferencial")
        except (EscalaresNoConfiables, EscalaresInvalidas) as e:
            print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
            fallas_suite.append("diferencial (escalares)")
    print()

    # 5. Autocertificación de Oracle (si es el propio repo)
    if proy.es_el_propio_oracle:
        from tools import cifras, metamorficas, trazar
        rc_trazar = trazar.main([])
        if rc_trazar != 0:
            fallas_suite.append("trazar")
        print()

        rc_meta = metamorficas.main([])
        if rc_meta != 0:
            fallas_suite.append("metamórficas")
        print()

        rc_cifras = cifras.main([])
        if rc_cifras != 0:
            fallas_suite.append("cifras")
        print()

    # 6. Mutación de medidas
    if len(catalogo) == 0:
        print("MUTACIÓN: salteada (sin medidas todavía)")
    elif rapido:
        print("MUTACIÓN: salteada por --rapido")
    else:
        try:
            with escalares_del_proyecto(proy, confiar=confiar):
                rc_mutar = mutar._ejecutar(proy, [])
                if rc_mutar != 0:
                    fallas_suite.append("mutación")
        except (EscalaresNoConfiables, EscalaresInvalidas) as e:
            print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
            fallas_suite.append("mutación (escalares)")
    print()

    # Veredicto final
    if fallas_suite:
        print(f"VEREDICTO: ROJO (falló: {', '.join(fallas_suite)})")
        return 1

    if rapido:
        print("VEREDICTO: VERDE (rápido: se salteó la mutación)")
    else:
        print("VEREDICTO: VERDE (completo: todas las verificaciones en regla, 0 mutantes sobrevivientes)")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "help"):
        ayuda()
        return 0

    subcomando = argv[0]
    resto = argv[1:]

    if subcomando == "init":
        args = [a for a in sin_banderas_comunes(resto) if a != "--rapido"]
        ruta = args[0] if args else None
        return cmd_init(ruta, argv)

    # Para todos los demás subcomandos, resolvemos el proyecto
    try:
        proy = resolver(argv)
    except ProyectoInvalido as e:
        print(f"PROYECTO INVÁLIDO — {e}", file=sys.stderr)
        return 1

    if subcomando == "test":
        return cmd_test(proy, argv)

    if subcomando in ("nueva", "--nueva"):
        args = [a for a in sin_banderas_comunes(resto) if a != "--rapido"]
        if not args:
            print("falta el id: oracle nueva <dominio.nombre>")
            return 1
        return cmd_nueva(proy, args[0])

    if subcomando in ("caso", "--caso", "--nuevo"):
        args = [a for a in sin_banderas_comunes(resto) if a != "--rapido"]
        if not args:
            print("falta la ubicación: oracle caso <grupo/id>")
            return 1
        return cmd_caso(proy, args[0])

    if subcomando in ("revisar", "--revisar"):
        args = [a for a in sin_banderas_comunes(resto) if a != "--rapido"]
        if not args:
            print("falta el archivo: oracle revisar <archivo>")
            return 1
        return cmd_revisar(proy, args[0], argv)

    if subcomando in ("relaciones", "--relaciones"):
        return cmd_relaciones(proy)

    if subcomando in ("escalares", "--escalares"):
        return cmd_escalares(proy, argv)

    if subcomando in ("expandir", "--expandir"):
        args = [a for a in sin_banderas_comunes(resto) if a != "--rapido"]
        if not args:
            print("falta el archivo: oracle expandir <archivo>")
            return 1
        return cmd_expandir(proy, args[0])

    # Si pasaron un archivo directamente: `oracle medida.oracle`
    if Path(subcomando).exists() or (proy.raiz / subcomando).exists():
        return cmd_revisar(proy, subcomando, argv)

    print(f"subcomando desconocido: {subcomando}")
    print("Ejecutá `oracle --help` para ver las opciones disponibles.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
