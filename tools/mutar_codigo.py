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
from nucleo.medida import cargar_catalogo  # noqa: E402
from perfiles.python.mutacion_codigo import (CacheNoLimpio, EquivalenteInvalido,
                                              LineaBaseFallida, AislamientoRoto,
                                              ManifiestoInvalido, RondaEnCurso, correr)  # noqa: E402
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables, catalogos_a_cargar,
                             escalares_del_proyecto, resolver, sin_bandera)  # noqa: E402

PROY = resolver(sys.argv[1:])

TESTS = [sys.executable, str(RAIZ / "tools" / "ejecutar_suite_mutacion.py")]
EQUIVALENTES = RAIZ / "equivalentes.json"

PRIORIDADES = {
    "nucleo/algebra.py": ("tests.test_nucleo",),
    "nucleo/diferencial.py": ("tests.test_dominio", "tests.test_herramientas"),
    "nucleo/dominio.py": ("tests.test_dominio",),
    "nucleo/fixtures.py": ("tests.test_fixtures", "tests.test_herramientas"),
    "nucleo/grafo.py": ("tests.test_nucleo",),
    "nucleo/macro.py": ("tests.test_macro",),
    "nucleo/marco.py": ("tests.test_marco",),
    "nucleo/medida.py": ("tests.test_medida", "tests.test_nucleo"),
    "nucleo/mutacion.py": ("tests.test_mutacion",),
    "nucleo/proyecto.py": ("tests.test_proyecto", "tests.test_herramientas",
                            "tests.test_perfiles"),
    "nucleo/simulacion.py": ("tests.test_simulacion",),
    "perfiles/python/marco.py": ("tests.test_perfiles",),
    "perfiles/python/mutacion_codigo.py": ("tests.test_mutacion_codigo",),
}


def objetivos_disponibles() -> dict[str, Path]:
    rutas = [*(RAIZ / "nucleo").glob("*.py"), *(RAIZ / "perfiles" / "python").glob("*.py")]
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
    carpetas = ("nucleo", "perfiles", "tests", "catalogos", "corpus", "diferencial")
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
    return p.parse_args(argv)


def cargar_equivalentes(ruta: Path) -> dict[str, str]:
    if not ruta.exists():
        return {}
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise EquivalenteInvalido(f"no se pudo leer {ruta.name}: {e}") from e
    if not isinstance(datos, list):
        raise EquivalenteInvalido(f"{ruta.name} tiene que contener una lista")

    salida: dict[str, str] = {}
    for i, entrada in enumerate(datos):
        if not isinstance(entrada, dict):
            raise EquivalenteInvalido(f"{ruta.name}[{i}] tiene que ser un objeto")
        mid, razon = entrada.get("id"), entrada.get("razon")
        if not isinstance(mid, str) or not mid.strip():
            raise EquivalenteInvalido(f"{ruta.name}[{i}].id tiene que ser texto no vacío")
        if not isinstance(razon, str) or not razon.strip():
            raise EquivalenteInvalido(f"{ruta.name}[{i}].razon tiene que ser texto no vacío")
        if mid in salida:
            raise EquivalenteInvalido(f"id equivalente duplicado en {ruta.name}: {mid}")
        salida[mid] = razon
    return salida


def _ejecutar(args) -> int:
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
        equivalentes = cargar_equivalentes(EQUIVALENTES)
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

    catalogo = cargar_catalogo(catalogos_a_cargar(PROY))
    for mid in ("proceso.test_con_mutante_que_lo_mata", "proceso.arnes_con_bytecode_frio",
                "proceso.ronda_mutacion_concluyente"):
        v = catalogo[mid].evaluar(evidencia)
        print(f"  {'✓' if v.ok else '✗'} {mid:<44} valor {v.valor} ({v.umbral})")

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


def main() -> int:
    args = argumentos(sin_bandera(sys.argv[1:]))
    try:
        with escalares_del_proyecto(PROY, confiar=args.confiar_escalares):
            return _ejecutar(args)
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
