"""Entry point único para Oracle.

    oracle <sustantivo> <verbo>             forma canónica (medida, caso, proyecto)
    oracle <sustantivo>                     ayuda del sustantivo con sus verbos

    oracle medida nueva <dominio.nombre>    crea una nueva medida en catalogos/ con plantilla lista
    oracle medida revisar <archivo>         revisa y evalúa una medida suelta contra la evidencia
    oracle medida listar                    lista las medidas del catálogo con umbral, alcance y fijación
    oracle medida expandir <archivo>        muestra la forma canónica de una medida escrita con macros

    oracle caso nuevo <grupo/id>            crea un nuevo caso en corpus/ con plantilla lista
    oracle caso listar                      lista los casos del corpus, su etiqueta y qué medida reclaman

    oracle proyecto init [ruta]             inicializa un proyecto con catalogos/, corpus/, diferencial/ y oracle.json
    oracle proyecto test [--rapido|--todo]  ejecuta la secuencia completa de verificación con veredicto final
    oracle proyecto relaciones              hechos y campos disponibles derivados de la evidencia
    oracle proyecto escalares               funciones de dominio y operadores disponibles

    oracle convertir <archivo>              traduce entre superficie y JSON (por la extensión)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos  # noqa: F401,E402
from nucleo.caso import rutas_de_corpus  # noqa: E402
from nucleo.medida import cargar_catalogo, rutas_de_catalogo  # noqa: E402
from nucleo.proyecto import (  # noqa: E402
    ESQUEMA_PROYECTO,
    ID_CASO_RE,
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
  oracle medida <verbo>                   Operaciones sobre medidas (nueva, revisar, listar, expandir)
  oracle caso <verbo>                     Operaciones sobre casos del corpus (nuevo, listar)
  oracle proyecto <verbo>                 Operaciones sobre el proyecto (init, test, relaciones, escalares)
  oracle convertir <archivo>              Traduce entre superficie y JSON (por la extensión)
  oracle --help                           Muestra esta ayuda

Atajos directos:
  oracle init [ruta]                      Inicializa un proyecto nuevo
  oracle nueva <dominio.nombre>          Crea una medida con plantilla lista para editar
  oracle caso <grupo/id>                 Crea un caso de prueba en el corpus
  oracle revisar <archivo>               Revisa y evalúa una medida suelta
  oracle test [--rapido|--todo]          Ejecuta la secuencia completa de verificación
  oracle relaciones                      Muestra las relaciones y campos observados
  oracle escalares                       Muestra las funciones escalares y operadores
  oracle expandir <archivo>              Muestra la forma canónica de una macro

Banderas comunes:
  --proyecto <ruta>      Ruta al proyecto (por defecto: directorio actual o $ORACLE_PROYECTO)
  --confiar-escalares    Autoriza la ejecución de funciones en `escalares.py`
  --rapido               En `oracle test`, conserva la ruta rápida histórica
  --todo                 En `oracle test`, incluye la mutación de código del propio Oracle""")


def ayuda_medida() -> None:
    print("""oracle medida — operaciones sobre medidas del catálogo

Uso:
  oracle medida nueva <dominio.nombre>    Crea una medida con plantilla lista para editar
  oracle medida revisar <archivo>         Revisa y evalúa una medida suelta
  oracle medida listar                    Lista las medidas del catálogo con umbral, alcance y fijación
  oracle medida expandir <archivo>        Muestra la forma canónica de una macro""")


def ayuda_caso() -> None:
    print("""oracle caso — operaciones sobre casos del corpus

Uso:
  oracle caso nuevo <grupo/id>            Crea un caso de prueba en el corpus con plantilla lista
  oracle caso listar                      Lista los casos del corpus, su etiqueta y qué medida reclaman""")


def ayuda_proyecto() -> None:
    print("""oracle proyecto — operaciones sobre el proyecto y su entorno

Uso:
  oracle proyecto init [ruta]             Inicializa un proyecto nuevo
  oracle proyecto test [--rapido|--todo]  Ejecuta la secuencia completa de verificación
  oracle proyecto relaciones              Muestra las relaciones y campos observados
  oracle proyecto escalares               Muestra las funciones escalares y operadores""")



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
            # `catalogo_base` NO es opcional en un proyecto nuevo, y es lo más importante que
            # escribe `init`. Sin él, el proyecto carga SÓLO sus propias medidas y se queda sin las
            # universales: nadie comprueba que un umbral traiga defensa, que una medida declare
            # `alcance`, que toda medida esté fijada por un caso, ni —la que más importa— que un
            # caso se ponga como su etiqueta declara.
            #
            # Medido: una medida con el predicado INVERTIDO —que selecciona lo que está bien en vez
            # de lo que ofende— más un caso que la declara `falso_verde`, daban
            # «ACEPTACIÓN ✓ · VEREDICTO VERDE». Con `catalogo_base`, `meta.el_caso_se_pone_como_debe`
            # la pone en rojo. Los dos consumidores lo tenían porque se armaron a mano copiando de
            # Oracle; quien empezaba por el camino documentado se quedaba sin ninguna guarda.
            datos = {"esquema": ESQUEMA_PROYECTO, "catalogo_base": True, "perfiles": []}
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


def cmd_medida_listar(proy: Proyecto, argv: list[str]) -> int:
    return medida.listar(proy, argv)


def cmd_caso(proy: Proyecto, ubicacion: str) -> int:
    return corpus.nuevo(proy, ubicacion)


def cmd_caso_listar(proy: Proyecto) -> int:
    return corpus.listar(proy)


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


def cmd_convertir(proy: Proyecto, ruta_str: str) -> int:
    """Traduce entre los dos formatos, mirando la extensión.

    Existía sólo como `python tools/sintaxis.py --imprimir|--leer`, que exige tener el checkout de
    Oracle y saber dónde está. Era el último paso del recorrido de autoría que seguía obligando a
    eso, y la documentación tenía que dejarlo escrito así por no inventar un comando que no existía.

    Un solo verbo en vez de dos —`--imprimir` y `--leer`— porque la dirección la dice la extensión
    del archivo y pedirle a la persona que además la nombre es hacerle repetir lo que ya escribió.
    """
    from nucleo import caso as caso_superficie
    from nucleo.medida import cargar_fuente_medida
    from nucleo.sintaxis import ErrorSintaxis, fragmento_de_error, imprimir, leer

    ruta = Path(ruta_str)
    if not ruta.exists():
        ruta = proy.raiz / ruta_str
    if not ruta.exists():
        print(f"no existe: {ruta_str}")
        return 1

    texto = ruta.read_text(encoding="utf-8")
    try:
        if ruta.suffix == ".json":
            print(imprimir(cargar_fuente_medida(ruta)), end="")
        elif ruta.suffix == ".oracle":
            print(json.dumps(leer(texto), ensure_ascii=False, separators=(",", ":")))
        elif ruta.suffix == ".caso":
            print(json.dumps(caso_superficie.leer(texto), ensure_ascii=False, indent=2))
        else:
            print(f"no sé convertir «{ruta.suffix or ruta.name}»: esperaba .oracle, .caso o .json")
            return 1
    except (ErrorSintaxis, caso_superficie.CasoMalDeclarado) as e:
        print(f"✗ {ruta}: {fragmento_de_error(e, texto)}")
        return 1
    return 0


COMANDO_UNITARIOS = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-q"]


def _imprimir_bloque(texto: str) -> None:
    if texto:
        print(texto, end="" if texto.endswith("\n") else "\n")


def _ejecutar_unitarios(proy: Proyecto) -> int:
    print("UNITARIOS: python -m unittest discover -s tests -t . -q")
    resultado = subprocess.run(
        COMANDO_UNITARIOS, cwd=proy.raiz, capture_output=True, text=True)
    _imprimir_bloque(resultado.stdout)
    _imprimir_bloque(resultado.stderr)
    print("UNITARIOS OK" if resultado.returncode == 0 else "UNITARIOS ✗")
    return resultado.returncode


def _veredicto_verde(*, todo: bool, omisiones: list[str]) -> None:
    if omisiones:
        print(f"VEREDICTO: VERDE (se salteó: {'; '.join(omisiones)})")
    elif todo:
        print("VEREDICTO: VERDE (todo: todas las verificaciones en regla, 0 mutantes sobrevivientes)")
    else:
        print("VEREDICTO: VERDE (todas las verificaciones aplicables en regla)")


def cmd_test(proy: Proyecto, argv: list[str]) -> int:
    rapido = "--rapido" in argv
    todo = "--todo" in argv
    confiar = confiar_escalares(argv)

    if rapido and todo:
        print("USO INVÁLIDO — `--rapido` y `--todo` son niveles incompatibles")
        print("\nVEREDICTO: ROJO (nivel de verificación inválido)")
        return 1

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
        with escalares_del_proyecto(proy, confiar=confiar):
            catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros)
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
        print("\nVEREDICTO: ROJO (escalares.py no pudo cargarse)")
        return 1
    except Exception as e:
        print(f"CATÁLOGO INVÁLIDO — {e}")
        print("\nVEREDICTO: ROJO (catálogo no pudo cargarse)")
        return 1

    casos_archivos = rutas_de_corpus(proy.corpus)
    rutas_diferencial = sorted(proy.diferencial.glob("*.json"))
    fallas_suite: list[str] = []
    omisiones_veredicto: list[str] = []

    # 0. Tests unitarios de Oracle
    if proy.es_el_propio_oracle:
        if rapido:
            print("UNITARIOS: salteados por --rapido")
            omisiones_veredicto.append("tests unitarios (--rapido)")
        else:
            rc_unitarios = _ejecutar_unitarios(proy)
            if rc_unitarios != 0:
                fallas_suite.append("unitarios")
    else:
        print("UNITARIOS: salteados (sólo aplican al propio Oracle)")
    print()

    # «Vacío» se mide por las medidas PROPIAS, no por las cargadas. Desde que `init` declara
    # `catalogo_base`, un proyecto recién creado hereda 34 medidas universales y dejaba de contar
    # como vacío: `aceptacion` decía «SIN CASOS» y el primer `oracle test` de alguien salía ROJO.
    # Heredar las guardas no es tener un catálogo.
    propias = rutas_de_catalogo(proy.catalogos)
    if len(propias) == 0 and len(casos_archivos) == 0 and len(rutas_diferencial) == 0:
        print("CORPUS OK · 0 casos · esquema y evidencia L0 en regla")
        print("SINTAXIS: salteado (sin medidas ni casos todavía)")
        print("ACEPTACIÓN: salteado (sin medidas ni casos todavía)")
        print("DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)")
        print("MUTACIÓN: salteada (sin medidas todavía)\n")
        print("MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)\n")
        print("VEREDICTO: VERDE (proyecto vacío: 0 medidas, 0 casos)")
        return 0

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
        omisiones_veredicto.append("mutación de medidas (--rapido)")
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

    # 7. Mutación de código
    if proy.es_el_propio_oracle:
        if todo:
            from tools import mutar_codigo
            rc_mutar_codigo = mutar_codigo._ejecutar(proy, mutar_codigo.argumentos([]))
            if rc_mutar_codigo != 0:
                fallas_suite.append("mutación de código")
        else:
            if rapido:
                print("MUTACIÓN DE CÓDIGO: salteada por --rapido "
                      "(corré `oracle test --todo` para incluirla)")
            else:
                print("MUTACIÓN DE CÓDIGO: salteada "
                      "(corré `oracle test --todo` para incluirla)")
            omisiones_veredicto.append("mutación de código (corré `oracle test --todo`)")
    else:
        print("MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)")
    print()

    # Veredicto final
    if fallas_suite:
        print(f"VEREDICTO: ROJO (falló: {', '.join(fallas_suite)})")
        return 1

    _veredicto_verde(todo=todo, omisiones=omisiones_veredicto)
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    posicionales = sin_banderas_comunes(argv)
    if not posicionales or posicionales[0] in ("-h", "--help", "help"):
        ayuda()
        return 0

    subcomando = posicionales[0]
    resto = posicionales[1:]

    # 1. Ayudas por sustantivo (devuelven 0 y no requieren proyecto)
    if subcomando == "medida" and (not resto or resto[0] in ("-h", "--help", "help")):
        ayuda_medida()
        return 0
    if subcomando == "caso" and (not resto or resto[0] in ("-h", "--help", "help")):
        ayuda_caso()
        return 0
    if subcomando == "proyecto" and (not resto or resto[0] in ("-h", "--help", "help")):
        ayuda_proyecto()
        return 0

    # 2. Inicialización de proyecto (no requiere proyecto previo)
    if subcomando == "init":
        args = [a for a in resto if a != "--rapido"]
        ruta = args[0] if args else None
        return cmd_init(ruta, argv)
    if subcomando == "proyecto" and resto and resto[0] == "init":
        args = [a for a in resto[1:] if a != "--rapido"]
        ruta = args[0] if args else None
        return cmd_init(ruta, argv)

    # 3. Verbos desconocidos de sustantivos
    if subcomando == "medida" and resto and resto[0] not in (
        "nueva", "--nueva", "revisar", "--revisar", "listar", "--listar", "expandir", "--expandir"
    ):
        print(f"verbo desconocido para «medida»: {resto[0]}")
        print("Verbos disponibles: nueva, revisar, listar, expandir")
        return 1

    if subcomando == "caso" and resto and resto[0] not in (
        "nuevo", "--nuevo", "nueva", "--nueva", "listar", "--listar"
    ):
        # Atajo plano `oracle caso <grupo/id>`
        if "/" not in resto[0] and not ID_CASO_RE.fullmatch(resto[0]):
            print(f"verbo desconocido para «caso»: {resto[0]}")
            print("Verbos disponibles: nuevo, listar")
            return 1

    if subcomando == "proyecto" and resto and resto[0] not in (
        "init", "test", "relaciones", "--relaciones", "escalares", "--escalares"
    ):
        print(f"verbo desconocido para «proyecto»: {resto[0]}")
        print("Verbos disponibles: init, test, relaciones, escalares")
        return 1

    # Para todos los demás comandos resolvemos el proyecto
    try:
        proy = resolver(argv)
    except ProyectoInvalido as e:
        print(f"PROYECTO INVÁLIDO — {e}", file=sys.stderr)
        return 1

    # Despacho por sustantivo: medida
    if subcomando == "medida":
        verbo = resto[0]
        args = [a for a in resto[1:] if a != "--rapido"]
        if verbo in ("nueva", "--nueva"):
            if not args:
                print("falta el id: oracle medida nueva <dominio.nombre>")
                return 1
            return cmd_nueva(proy, args[0])
        if verbo in ("revisar", "--revisar"):
            if not args:
                print("falta el archivo: oracle medida revisar <archivo>")
                return 1
            return cmd_revisar(proy, args[0], argv)
        if verbo in ("listar", "--listar"):
            return cmd_medida_listar(proy, argv)
        if verbo in ("expandir", "--expandir"):
            if not args:
                print("falta el archivo: oracle medida expandir <archivo>")
                return 1
            return cmd_expandir(proy, args[0])

    # Despacho por sustantivo: caso
    if subcomando == "caso":
        verbo = resto[0]
        args = [a for a in resto[1:] if a != "--rapido"]
        if verbo in ("nuevo", "--nuevo", "nueva", "--nueva"):
            if not args:
                print("falta la ubicación: oracle caso nuevo <grupo/id>")
                return 1
            return cmd_caso(proy, args[0])
        if verbo in ("listar", "--listar"):
            return cmd_caso_listar(proy)
        # Atajo directo: oracle caso <grupo/id>
        return cmd_caso(proy, verbo)

    # Despacho por sustantivo: proyecto
    if subcomando == "proyecto":
        verbo = resto[0]
        if verbo == "test":
            return cmd_test(proy, argv)
        if verbo in ("relaciones", "--relaciones"):
            return cmd_relaciones(proy)
        if verbo in ("escalares", "--escalares"):
            return cmd_escalares(proy, argv)

    # Atajos directos históricos (planos)
    if subcomando == "test":
        return cmd_test(proy, argv)

    if subcomando in ("nueva", "--nueva"):
        args = [a for a in resto if a != "--rapido"]
        if not args:
            print("falta el id: oracle nueva <dominio.nombre>")
            return 1
        return cmd_nueva(proy, args[0])

    if subcomando in ("--caso", "--nuevo"):
        args = [a for a in resto if a != "--rapido"]
        if not args:
            print("falta la ubicación: oracle caso <grupo/id>")
            return 1
        return cmd_caso(proy, args[0])

    if subcomando in ("revisar", "--revisar"):
        args = [a for a in resto if a != "--rapido"]
        if not args:
            print("falta el archivo: oracle revisar <archivo>")
            return 1
        return cmd_revisar(proy, args[0], argv)

    if subcomando in ("relaciones", "--relaciones"):
        return cmd_relaciones(proy)

    if subcomando in ("escalares", "--escalares"):
        return cmd_escalares(proy, argv)

    if subcomando == "convertir":
        args = [a for a in resto if a != "--rapido"]
        if not args:
            print("falta el archivo: oracle convertir <archivo.oracle|.caso|.json>")
            return 1
        return cmd_convertir(proy, args[0])

    if subcomando in ("expandir", "--expandir"):
        args = [a for a in resto if a != "--rapido"]
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
