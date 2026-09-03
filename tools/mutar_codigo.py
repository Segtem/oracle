"""Muta el CÓDIGO del núcleo y mide el resultado con las medidas del catálogo.

    python tools/mutar_codigo.py                 → informe
    python tools/mutar_codigo.py --hechos        → volcar la evidencia (JSON)
    python tools/mutar_codigo.py --timeout 90    → límite por ejecución de tests
    python tools/mutar_codigo.py --manifiesto progreso.json [--reanudar]

Cada ronda copia el proyecto a un directorio temporal y sólo muta esa copia. Un bloqueo impide dos
rondas sobre la misma raíz; timeout y señales terminan el grupo de procesos y limpian el aislamiento.

Sale 1 si algún mutante sobrevivió y 2 si la ronda fue inconclusa. Timeout, error del arnés y fallo de
tests son estados distintos; sólo el último demuestra que el mutante murió.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos  # noqa: F401,E402
from nucleo.algebra import ErrorDeAlgebra  # noqa: E402
from nucleo.medida import cargar_catalogo, medidas_aplicables  # noqa: E402
from perfiles.python.mutacion_codigo import (CacheNoLimpio, EquivalenteInvalido,
                                              LineaBaseFallida, AislamientoRoto,
                                              ManifiestoInvalido, RondaEnCurso, correr,
                                              sitios_de)  # noqa: E402
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables, catalogos_a_cargar,
                             escalares_del_proyecto, macros_del_proyecto,
                             sin_bandera)  # noqa: E402
from tools.sesion import resolver_cli  # noqa: E402

TESTS = [sys.executable, str(RAIZ / "tools" / "ejecutar_suite_mutacion.py")]
EQUIVALENTES = RAIZ / "equivalentes.json"

PRIORIDADES = {
    "nucleo/algebra.py": ("tests.test_algebra", "tests.test_nucleo", "tests.test_motor"),
    "nucleo/biblioteca.py": ("tests.test_biblioteca",),
    "nucleo/aislamiento/escalares.py": ("tests.test_aislamiento_escalares",
                                        "tests.test_proyecto", "tests.test_motor"),
    "nucleo/caso.py": ("tests.test_sintaxis", "tests.test_herramientas"),
    "nucleo/diferencial.py": ("tests.test_dominio", "tests.test_herramientas"),
    "nucleo/diagnostico.py": ("tests.test_diagnostico", "tests.test_herramientas"),
    "nucleo/dominio.py": ("tests.test_dominio",),
    "nucleo/fixtures.py": ("tests.test_fixtures", "tests.test_herramientas"),
    "nucleo/generador.py": ("tests.test_generador", "tests.test_herramientas"),
    "nucleo/grafo.py": ("tests.test_nucleo",),
    "nucleo/macro.py": ("tests.test_macro",),
    "nucleo/marco.py": ("tests.test_marco",),
    "nucleo/medida.py": ("tests.test_medida", "tests.test_nucleo", "tests.test_motor"),
    "nucleo/mutacion.py": ("tests.test_mutacion",),
    "nucleo/proyecto.py": ("tests.test_proyecto", "tests.test_herramientas",
                            "tests.test_perfiles", "tests.test_motor"),
    "nucleo/referente.py": ("tests.test_referente", "tests.test_medida"),
    "nucleo/relacion.py": ("tests.test_relacion", "tests.test_nucleo"),
    "nucleo/sintaxis.py": ("tests.test_sintaxis", "tests.test_macro", "tests.test_nucleo"),
    "nucleo/vocabulario.py": ("tests.test_vocabulario", "tests.test_sintaxis"),
    "nucleo/simulacion.py": ("tests.test_simulacion",),
    "nucleo/unidad.py": ("tests.test_unidad", "tests.test_nucleo", "tests.test_medida"),
    "nucleo/version.py": ("tests.test_herramientas",),
    "oracle_metalenguaje/_compat.py": ("tests.test_motor",),
    "oracle_metalenguaje/motor.py": ("tests.test_motor",),
    "perfiles/python/marco.py": ("tests.test_perfiles",),
    "perfiles/python/mutacion_codigo.py": ("tests.test_mutacion_codigo",),
    "tools/cifras.py": ("tests.test_herramientas",),
    "tools/cli.py": ("tests.test_biblioteca", "tests.test_vigilar", "tests.test_cli",
                     "tests.test_herramientas"),
    "tools/corpus.py": ("tests.test_corpus_cli", "tests.test_herramientas", "tests.test_cli"),
    "tools/lsp.py": ("tests.test_lsp",),
    # Listo para cuando `aceptacion.py` entre a HERRAMIENTAS_CUSTODIAS; ver la nota de ahí.
    "tools/aceptacion.py": ("tests.test_herramientas", "tests.test_cli"),
    # SIN `tests.test_cli`: el despacho de `oracle manual` vive en `cli.py` y ya lo fija el
    # perfil de `cli.py`. Acá agregaba ~40 s de subprocesos por mutante —la ronda pasaba de
    # minutos a horas— sin matar un mutante que los otros dos módulos no maten.
    "tools/manual.py": ("tests.test_manual", "tests.test_vocabulario"),
    "tools/medida.py": ("tests.test_vigilar", "tests.test_herramientas", "tests.test_cli",
                        "tests.test_lsp"),
}


# `tools/` no entra entero: son instrumentos, y casi todo su cuerpo es plumbing de línea de comandos
# cuyo veredicto vive en `nucleo/`. Mutarlo completo sumaría 559 sitios —un 47% más de denominador—
# de muy poco valor. Entran DE A UNO, y sólo cuando el instrumento **custodia una afirmación que
# nadie más comprueba**: si el instrumento se rompe, la afirmación queda sin nadie que la verifique.
#
# `cifras.py` es el primero. Desde que genera los bloques del README es lo único que impide que una
# cifra publicada vuelva a derivar en silencio, y esa deriva ya ocurrió: el proyecto publicó «trece a
# uno» durante todo un corte mientras el valor real era 16,2.
# `aceptacion.py` CUMPLE el criterio desde el 2026-09-01: con el modo sombra custodia qué rojos
# tumban la corrida, y esa decisión no vive en ninguna medida —las medidas dicen si algo está mal,
# no si eso debe fallar—. Se midió antes de decidir: 45 sitios, 27 muertos, **17 sobrevivientes
# preexistentes** y 1 error de arnés en `aceptacion.py:183`, todos en el código de reporte anterior
# al modo sombra. Meterlo hoy pondría al proyecto en rojo por deuda ajena a ese cambio, así que
# entra cuando esos 17 estén cerrados. El código del modo sombra sí quedó medido en esa corrida:
# cero sobrevivientes.
# `manual.py` entra el 2026-09-01: su registro `VOCABULARIOS` es de dónde sale la relación
# `opcion_del_vocabulario`, así que si el registro se rompe —o deja de emitir un vocabulario— las
# dos medidas que vigilan el manual se ponen verdes sin mirar nada. Es el caso exacto del criterio:
# el instrumento custodia una afirmación (que el manual está completo) que nadie más comprueba.
# ⚠ ESTAR ACÁ NO ES ESTAR MEDIDO — y lo que costó averiguarlo cambió la conclusión.
#
# Esta lista tiene siete archivos; la matriz de `mutacion-codigo` del workflow corría UNO. Los otros
# seis entraban al perfil y no los mutaba nadie salvo a mano, declarado en el workflow como «sube el
# costo por corrida». Faltaba el número.
#
# El 2026-09-02 se midió `tools/medida.py` entero: **264 mutantes, 114 sobrevivientes, ~90 minutos**.
# Y se probaron los dos arreglos posibles, en ramas separadas y con los criterios fijados antes:
#
#   · escribir los tests que faltaban (616 líneas): quedó en **264/264, cero sobrevivientes, 201
#     segundos**;
#   · separar el archivo en un módulo custodio y dejar el CLI afuera del perfil: quedó en 3
#     sobrevivientes de 64 y **1.675 segundos**, ocho veces más lento, con 114 mutantes sin medir.
#
# Ganó escribir los tests, y el dato que da vuelta la intuición es el tiempo: el archivo tardaba 90
# minutos PORQUE estaba mal fijado. Confirmar un sobreviviente cuesta una corrida completa de la
# suite (~50 s); matarlo cuesta ~0,1 s. Fijarlo lo volvió 27 veces más rápido.
#
# Así que «no los agregamos a CI porque salen caros» decía en realidad «no los medimos porque nos
# iría mal»: medirlos bien es lo que los vuelve baratos. `tools/medida.py` ya está en la matriz.
#
# LOS OTROS CINCO, medidos el 2026-09-03 — y el resultado desmintió lo que se esperaba:
#
#   tools/lsp.py          140 mutantes ·  0 vivos ·   121 s
#   tools/corpus.py       112 mutantes ·  0 vivos ·   180 s
#   tools/aceptacion.py    49 mutantes ·  0 vivos ·   266 s
#   tools/cli.py          442 mutantes ·  0 vivos ·  1927 s
#   tools/manual.py        59 mutantes ·  3 vivos ·   242 s  ← se cerraron el mismo día
#
# No eran archivos abandonados: estaban fijados y nadie volvía a comprobarlo. `medida.py` era la
# excepción, no la regla.
#
# Y el costo NO se explica por los sobrevivientes: cuatro estaban en cero y `cli.py` igual tarda 32
# minutos. Son DOS componentes, y acá manda el segundo:
#
#   · confirmar un sobreviviente cuesta una corrida completa de la suite (~50 s);
#   · matar un mutante cuesta lo que tarde el arnés en LLEGAR al test que lo mata. Con
#     `failfast=True` y los módulos corriendo en el orden declarado, un mutante que muere en el
#     primer test del primer módulo no cuesta nada, y uno que muere al final del segundo pagó todo
#     el primero. Por eso `lsp.py` va a 0,86 s por mutante —declara UN módulo, chico y suyo— y
#     `aceptacion.py` a 5,4 —declara `herramientas` primero, que es grande—.
#
# De ahí sale una palanca que no cuesta código: REORDENAR los módulos prioritarios poniendo el más
# específico primero. No está hecha ni medida; si alguien la prueba, que deje el número.
#
# Los tres sobrevivientes de `manual.py` los introdujo quien agregó `--man`: lo midió en 39/39, lo
# siguió editando y no lo volvió a medir. Es el modo de fallar que este proyecto persigue, cometido
# adentro: medir una vez y quedarse con el número viejo en la cabeza.
HERRAMIENTAS_CUSTODIAS = ("aceptacion.py", "cifras.py", "cli.py", "corpus.py",
                          "lsp.py", "manual.py", "medida.py")


def objetivos_disponibles() -> dict[str, Path]:
    # RECURSIVO, y es el punto. Con `glob("*.py")` un módulo dentro de un subpaquete de `nucleo/`
    # quedaba INVISIBLE para el arnés: no era objetivo, no se mutaba, y nadie lo notaba porque el
    # informe sólo habla de lo que sí miró. Así estuvo `nucleo/aislamiento/escalares.py` —411 líneas
    # que son el confinamiento de las UDF de un proyecto: lo único que hace que `--confiar-escalares`
    # sea distinto de ejecutar código ajeno a ciegas—.
    #
    # Es el MISMO defecto que tenía `tools/cifras.py` en su numerador, y se arregló ahí el 2026-08-03
    # con estas palabras: «mover el archivo una carpeta más adentro» no puede ser una manera de salir
    # del criterio de falsación. Se arregló el lado que CUENTA y no el que MIDE, así que durante tres
    # semanas esas líneas figuraban en la proporción publicada y no las fijaba nada.
    rutas = [
        *(RAIZ / "nucleo").rglob("*.py"),
        *(RAIZ / "oracle_metalenguaje").glob("*.py"),
        *(RAIZ / "perfiles" / "python").glob("*.py"),
        *(RAIZ / "tools" / nombre for nombre in HERRAMIENTAS_CUSTODIAS),
    ]
    return {ruta.relative_to(RAIZ).as_posix(): ruta for ruta in sorted(rutas)
            if ruta.name != "__init__.py"}


def resolver_objetivos(declarados: list[str] | None) -> list[Path]:
    disponibles = objetivos_disponibles()
    if not declarados:
        return list(disponibles.values())
    desconocidos = [nombre for nombre in declarados if nombre not in disponibles]
    if desconocidos:
        raise ValueError(
            f"objetivos desconocidos o fuera del perfil activo: {sorted(set(desconocidos))}")
    if len(declarados) != len(set(declarados)):
        raise ValueError("un --objetivo no puede repetirse")
    return [disponibles[nombre] for nombre in declarados]


def comando_de_tests(objetivos: list[Path], *, priorizar: bool) -> list[str]:
    comando = list(TESTS)
    if priorizar:
        modulos = dict.fromkeys(
            modulo for ruta in objetivos
            for modulo in PRIORIDADES[ruta.relative_to(RAIZ).as_posix()])
        for modulo in modulos:
            comando.extend(("--prioridad", modulo))
    return comando


def dependencias_de_ronda() -> list[Path]:
    """Archivos que pueden cambiar el resultado aunque no sean el objetivo mutado."""
    carpetas = ("nucleo", "oracle_metalenguaje", "perfiles", "tests", "catalogos", "corpus",
                "diferencial")
    rutas = [ruta for nombre in carpetas for ruta in (RAIZ / nombre).rglob("*")
             if ruta.is_file() and "__pycache__" not in ruta.parts and ruta.suffix != ".pyc"]
    rutas.append(RAIZ / "tools" / "ejecutar_suite_mutacion.py")
    return sorted(set(rutas))


def argumentos(argv: list[str]):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--hechos", action="store_true", help="emitir sólo evidencia JSON")
    p.add_argument("--timeout", type=float, default=60.0,
                   help="segundos máximos para la baseline y cada mutante (60 por defecto)")
    p.add_argument("--limite-salida-kb", type=int, default=1024,
                   help="KiB máximos conservados por stdout y stderr en cada ejecución")
    p.add_argument("--manifiesto", type=Path,
                   help="guardar progreso atómico para poder reanudar la ronda")
    p.add_argument("--reanudar", action="store_true",
                   help="continuar un --manifiesto compatible, revalidando antes la baseline")
    p.add_argument("--objetivo", action="append", metavar="RUTA",
                   help="archivo relativo a Oracle que se muta; repetible para particionar")
    p.add_argument("--confiar-escalares", action="store_true",
                   help="ejecutar el escalares.py del proyecto externo")
    p.add_argument("--reapuntar-equivalentes", action="store_true",
                   help="reubicar los ids de equivalentes.json usando su contenido de línea y ordinal")
    return p.parse_args(argv)


def leer_declaraciones_equivalentes(ruta: Path) -> list[dict]:
    """Carga y valida la estructura de las declaraciones en equivalentes.json.

    La validación es estricta para evitar que errores tipográficos o corrupciones de formato
    se propaguen silenciosamente a la suite de mutación o al proceso de reubicación.
    """
    if not ruta.exists():
        return []
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise EquivalenteInvalido(f"no se pudo leer {ruta.name}: {e}") from e
    if not isinstance(datos, list):
        raise EquivalenteInvalido(f"{ruta.name} tiene que contener una lista")

    ids_vistos: set[str] = set()
    for i, entrada in enumerate(datos):
        if not isinstance(entrada, dict):
            raise EquivalenteInvalido(f"{ruta.name}[{i}] tiene que ser un objeto")
        mid, razon = entrada.get("id"), entrada.get("razon")
        if not isinstance(mid, str) or not mid.strip():
            raise EquivalenteInvalido(f"{ruta.name}[{i}].id tiene que ser texto no vacío")
        if not isinstance(razon, str) or not razon.strip():
            raise EquivalenteInvalido(f"{ruta.name}[{i}].razon tiene que ser texto no vacío")
        linea_texto = entrada.get("linea_texto")
        if linea_texto is not None and (not isinstance(linea_texto, str) or not linea_texto.strip()):
            raise EquivalenteInvalido(f"{ruta.name}[{i}].linea_texto tiene que ser texto no vacío")
        ordinal = entrada.get("ordinal")
        if ordinal is not None and (isinstance(ordinal, bool) or not isinstance(ordinal, int) or ordinal < 1):
            raise EquivalenteInvalido(f"{ruta.name}[{i}].ordinal tiene que ser entero positivo (>= 1)")
        if mid in ids_vistos:
            raise EquivalenteInvalido(f"id equivalente duplicado en {ruta.name}: {mid}")
        ids_vistos.add(mid)
    return datos


def cargar_equivalentes(ruta: Path) -> dict[str, str]:
    """Extrae el mapeo id -> razón para consumo del arnés de mutación.

    Mantiene compatibilidad con la interfaz que `correr()` y los tests existentes esperan,
    apoyándose en `leer_declaraciones_equivalentes` para centralizar la validación de esquema.
    """
    datos = leer_declaraciones_equivalentes(ruta)
    return {entrada["id"]: entrada["razon"] for entrada in datos}


def reapuntar_equivalentes(ruta: Path = EQUIVALENTES, raiz: Path = RAIZ,
                           *, destino: Path | None = None) -> int:
    """Reubica los ids posicionales de equivalentes según su contenido y ordinal de línea.

    Un id `archivo:linea:columna:tipo` es puramente posicional y se rompe ante cualquier inserción
    de líneas arriba. Esta función localiza las líneas cuyo texto coincida con `linea_texto` y toma
    la correspondiente a `ordinal`. Se valida contra el AST real (`sitios_de`) para no asumir a
    ciegas que el mutante sigue existiendo si el código interno de la línea cambió. Si el contenido
    no existe o el sitio mutante desapareció, se falla cerrado requiriendo inspección manual.
    """
    if destino is None:
        destino = ruta
    if not ruta.exists():
        print(f"no existe el archivo de equivalentes: {ruta}", file=sys.stderr)
        return 1

    try:
        datos = leer_declaraciones_equivalentes(ruta)
    except EquivalenteInvalido as e:
        print(f"declaraciones inválidas en {ruta.name}: {e}", file=sys.stderr)
        return 1

    sitios_por_archivo: dict[str, dict[str, Sitio]] = {}

    def sitios_de_archivo(rel: str) -> dict[str, Sitio]:
        # Se memoriza por archivo para no reparsear el AST múltiples veces ante varios equivalentes
        # en el mismo módulo.
        if rel not in sitios_por_archivo:
            ruta_f = raiz / rel
            if not ruta_f.is_file():
                sitios_por_archivo[rel] = {}
            else:
                sitios_por_archivo[rel] = {s.id: s for s in sitios_de(ruta_f, raiz)}
        return sitios_por_archivo[rel]

    reubicados: list[tuple[str, str]] = []
    poblados: list[str] = []
    intactos: list[str] = []
    no_resueltos: list[tuple[str, str]] = []

    for entrada in datos:
        mid = entrada["id"]
        partes = mid.split(":")
        if len(partes) != 4:
            no_resueltos.append((mid, "el id no tiene el formato archivo:linea:columna:tipo"))
            continue

        archivo_rel, linea_str, col_str, operador = partes
        try:
            linea_vieja = int(linea_str)
            col_vieja = int(col_str)
        except ValueError:
            no_resueltos.append((mid, "línea o columna no numérica en el id"))
            continue

        ruta_f = raiz / archivo_rel
        if not ruta_f.is_file():
            no_resueltos.append((mid, f"archivo '{archivo_rel}' no existe en el proyecto"))
            continue

        vigentes = sitios_de_archivo(archivo_rel)
        lineas = ruta_f.read_text(encoding="utf-8").splitlines()

        linea_texto = entrada.get("linea_texto")
        ordinal = entrada.get("ordinal")

        # Si una entrada no posee metadatos de línea pero su id actual es vigente, poblamos
        # `linea_texto` y `ordinal` a partir del estado actual del repositorio.
        if linea_texto is None or ordinal is None:
            if mid in vigentes and 1 <= linea_vieja <= len(lineas):
                linea_real = lineas[linea_vieja - 1].strip()
                coincidencias = [idx + 1 for idx, l in enumerate(lineas) if l.strip() == linea_real]
                if linea_vieja in coincidencias:
                    ord_calculado = coincidencias.index(linea_vieja) + 1
                    entrada["linea_texto"] = linea_real
                    entrada["ordinal"] = ord_calculado
                    poblados.append(mid)
                    continue
            no_resueltos.append((mid, "id no vigente y sin metadatos de línea para reubicar"))
            continue

        # Buscamos las líneas cuyo contenido coincida con `linea_texto` (ignorando indentación).
        coincidencias = [idx + 1 for idx, l in enumerate(lineas) if l.strip() == linea_texto]
        if not coincidencias:
            no_resueltos.append((mid, f"contenido «{linea_texto}» ya no existe en {archivo_rel}"))
            continue

        if ordinal > len(coincidencias):
            no_resueltos.append(
                (mid, f"se esperaba ordinal {ordinal} de «{linea_texto}», "
                      f"pero solo hay {len(coincidencias)} ocurrencia(s) en {archivo_rel}"))
            continue

        nueva_linea = coincidencias[ordinal - 1]
        nuevo_id = f"{archivo_rel}:{nueva_linea}:{col_vieja}:{operador}"

        # Comprobamos que el AST realmente contenga el mutante esperado en la posición resultante,
        # protegiendo contra mutaciones internas en la línea.
        if nuevo_id not in vigentes:
            no_resueltos.append(
                (mid, f"en {archivo_rel}:{nueva_linea} no existe el sitio mutante {operador} "
                      f"en columna {col_vieja}"))
            continue

        if nuevo_id == mid:
            intactos.append(mid)
        else:
            entrada["id"] = nuevo_id
            reubicados.append((mid, nuevo_id))

    hubo_cambios = bool(reubicados or poblados)
    if hubo_cambios:
        # Se estructuran las claves de manera homogénea para facilitar lectura y diffs.
        datos_ordenados = []
        for e in datos:
            obj = {"id": e["id"]}
            if "linea_texto" in e:
                obj["linea_texto"] = e["linea_texto"]
            if "ordinal" in e:
                obj["ordinal"] = e["ordinal"]
            obj["razon"] = e["razon"]
            datos_ordenados.append(obj)
        destino.write_text(
            json.dumps(datos_ordenados, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8")

    if reubicados:
        print(f"reubicados ({len(reubicados)}):")
        for viejo, nuevo in reubicados:
            print(f"  · {viejo} → {nuevo}")
    if poblados:
        print(f"poblados con metadatos de línea ({len(poblados)}):")
        for mid in poblados:
            print(f"  · {mid}")
    if intactos:
        print(f"intactos: {len(intactos)}")
    if no_resueltos:
        print(f"NO resueltos ({len(no_resueltos)}):", file=sys.stderr)
        for mid, motivo in no_resueltos:
            print(f"  ✗ {mid}: {motivo}", file=sys.stderr)
        return 1

    return 0


def equivalentes_del_alcance(equivalentes: dict[str, str], objetivos: list[Path]) -> dict[str, str]:
    """Recorta las declaraciones a los objetivos de esta ronda, comprobándolas contra TODOS.

    `correr()` exige que cada equivalente apunte a un sitio de la ronda, y con razón: uno que no
    apunta a nada es una afirmación que sobrevivió al código que la justificaba. Pero `equivalentes.json`
    es del proyecto, no de la partición, así que el CI —que corre un objetivo por job— hacía fallar
    todos los jobs salvo el del archivo declarado.

    Así que la vigencia se comprueba contra el inventario completo, y a `correr()` sólo se le pasa lo
    que le corresponde. Filtrar sin comprobar habría convertido «declaración vencida» en «declaración
    que nadie mira», que es peor que el error original.
    """
    vigentes = {
        sitio.id
        for ruta in objetivos_disponibles().values()
        for sitio in sitios_de(ruta, RAIZ)
    }
    vencidos = sorted(set(equivalentes) - vigentes)
    if vencidos:
        raise EquivalenteInvalido(
            f"equivalentes que no apuntan a ningún sitio del proyecto: {vencidos}")
    del_alcance = {
        f"{ruta.relative_to(RAIZ).as_posix()}" for ruta in objetivos}
    return {mid: razon for mid, razon in equivalentes.items()
            if mid.rsplit(":", 3)[0] in del_alcance}


def _ejecutar(proy, args) -> int:
    objetivos = resolver_objetivos(args.objetivo)
    comando_tests = comando_de_tests(objetivos, priorizar=bool(args.objetivo))
    silencioso = args.hechos

    def progreso(fila):
        if not silencioso:
            if fila["tests_fallaron"]:
                marca = "·"
            elif fila["timeout"]:
                marca = "TIEMPO"
            elif fila["error_arnes"]:
                marca = "ARNÉS"
            else:
                marca = "VIVO"
            print(f"  {marca:>4}  {fila['id']:<52} {fila['cambio']}", flush=True)

    if not silencioso:
        print("objetivos: " + ", ".join(p.relative_to(RAIZ).as_posix() for p in objetivos) + "\n")

    try:
        equivalentes = equivalentes_del_alcance(
            cargar_equivalentes(EQUIVALENTES), objetivos)
        evidencia = correr(
            RAIZ, objetivos, comando_tests, equivalentes, al_terminar_uno=progreso,
            timeout_por_ejecucion=args.timeout,
            limite_salida=args.limite_salida_kb * 1024,
            manifiesto=args.manifiesto, reanudar=args.reanudar,
            dependencias=dependencias_de_ronda())
    except (LineaBaseFallida, CacheNoLimpio, EquivalenteInvalido, AislamientoRoto,
            ManifiestoInvalido, RondaEnCurso, OSError, ValueError) as e:
        error = {"tipo": type(e).__name__, "mensaje": str(e)}
        if isinstance(e, LineaBaseFallida):
            salida = e.resultado.salida
            error.update({
                "baseline_verde": False,
                "tests_fallaron": e.resultado.tests_fallaron,
                "error_arnes": e.resultado.error_arnes,
                "timeout": e.resultado.timeout,
                "codigo_salida": e.resultado.codigo_salida,
                "salida": salida[:16_384],
                "salida_truncada": (len(salida) > 16_384 or e.resultado.stdout_truncado
                                     or e.resultado.stderr_truncado),
            })
        if silencioso:
            print(json.dumps({"error_mutacion": [error]}, ensure_ascii=False, indent=2))
        else:
            print(f"\nMUTACIÓN NO CONFIABLE — {type(e).__name__}\n{e}", file=sys.stderr)
        return 2

    corrida = evidencia["corrida_mutacion"][0]
    muertos = sum(m["tests_fallaron"] for m in evidencia["mutante"])
    vivos = [m for m in evidencia["mutante"] if m["estado"] == "pasaron"]
    ronda_inconclusa = (not corrida["baseline_verde"]
                        or not corrida["bytecode_frio"]
                        or corrida["mutantes"] <= 0
                        or corrida["errores_arnes"] > 0
                        or corrida["timeouts"] > 0)

    if silencioso:
        print(json.dumps(evidencia, ensure_ascii=False, indent=2))
        if ronda_inconclusa:
            return 2
        return 1 if vivos else 0

    eq = evidencia["mutante_equivalente"]
    print(f"\nmutantes: {len(evidencia['mutante'])} · murieron "
          f"{muertos} · sobrevivieron {len(vivos)} · "
          f"timeout {corrida['timeouts']} · errores de arnés {corrida['errores_arnes']} · "
          f"equivalentes declarados: {len(eq)}")

    catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
    # `medidas_aplicables` filtra por RELACIÓN presente, no por campo. Un mutante de código y uno de
    # medida son las dos cosas `mutante`, pero no tienen los mismos campos: el de código no trae
    # `detecciones_conductuales`. Así, una medida escrita para la mutación de MEDIDAS se declaraba
    # aplicable acá y reventaba dentro del `donde`.
    #
    # El error escapaba sin atajar y la ronda entera terminaba en un traceback de Python, después de
    # una hora de trabajo y con el informe a medio imprimir. Eso es peor que un rojo: la herramienta
    # que juzga a todas las demás era la única que no sabía informar su propio fracaso. Su contrato
    # dice «sale 1 si algún mutante sobrevivió y 2 si la ronda fue inconclusa» — un traceback no es
    # ninguno de los dos.
    #
    # Una medida que no puede juzgar esta evidencia se declara y se cuenta; no se saltea en silencio
    # ni se lleva puesta la ronda.
    no_juzgaron = []
    for medida in medidas_aplicables(catalogo.values(), evidencia):
        try:
            v = medida.evaluar(evidencia)
        except ErrorDeAlgebra as e:
            no_juzgaron.append((medida.id, str(e)))
            continue
        print(f"  {'✓' if v.ok else '✗'} {v.id:<44} valor {v.valor} ({v.umbral})")
    if no_juzgaron:
        print(f"\n  {len(no_juzgaron)} medida(s) NO pudieron juzgar esta evidencia — la relación "
              "estaba, los campos no:")
        for mid, motivo in no_juzgaron:
            print(f"    · {mid}: {motivo}")

    if ronda_inconclusa:
        print("\nRONDA INCONCLUSA: un timeout o error del arnés no mata un mutante.")
        if corrida["primer_inconcluso_id"]:
            print(f"  {corrida['primer_inconcluso_id']} · "
                  f"{corrida['primer_inconcluso_estado']}")
            print(corrida["primer_inconcluso_salida"])
        return 2

    if vivos:
        print("\nCÓDIGO QUE NINGÚN TEST FIJA:")
        for m in vivos:
            print(f"  · {m['id']}\n      {m['cambio']}")
        print("\nCada uno es un test que falta, o un mutante equivalente que hay que DECLARAR en")
        print("equivalentes.json con su razón escrita. Declararlo sin razón es una excusa.")
        return 1

    print("\nTodos los mutantes murieron: los tests fijan el código del núcleo.")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    args = argumentos(sin_bandera(argv))
    if args.reapuntar_equivalentes:
        # La reubicación opera directo sobre las fuentes sin requerir proyecto ni escalares.
        return reapuntar_equivalentes(EQUIVALENTES, RAIZ)
    proy = resolver_cli(argv)
    if proy is None:
        return 2
    try:
        with escalares_del_proyecto(proy, confiar=args.confiar_escalares):
            return _ejecutar(proy, args)
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
