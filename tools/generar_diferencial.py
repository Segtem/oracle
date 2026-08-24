"""Emite los fixtures `oracle.diferencial/v1` desde la implementación de referencia.

    python tools/generar_diferencial.py            → comprueba que lo versionado esté al día
    python tools/generar_diferencial.py --escribir → reescribe los fixtures

Quién decide `referencia_ok` es `diferencial/referencia/evaluador.py`, escrito por otro autor que
nunca vio `nucleo/` (ver `diferencial/referencia/PROCEDENCIA.md`). Oracle no se copia a sí mismo: si
las dos implementaciones ya discrepan al generar, **no se emite el fixture**, porque un fixture que
nace en desacuerdo congela el desacuerdo en vez de exponerlo.

Regenerar dos veces con las mismas entradas produce exactamente los mismos bytes: la serialización es
JSON canónico con orden estable y sin `NaN`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos.escalares  # noqa: F401,E402  registra las UDF declaradas
from nucleo.diferencial import Procedencia, crear_frescura  # noqa: E402
from nucleo.fixtures import validar_fixture  # noqa: E402
from nucleo.medida import cargar_catalogo  # noqa: E402
from nucleo.proyecto import (Proyecto, catalogos_a_cargar,  # noqa: E402
                             macros_del_proyecto)

REFERENCIA = RAIZ / "diferencial" / "referencia" / "evaluador.py"

# Los escenarios son el material del fixture, y se escriben acá y no en un JSON suelto para que la
# huella del emisor los cubra: un mundo que cambia sin que cambie su huella es un fixture que miente.
#
# El contrato del esquema pide ambas polaridades GLOBALES y ambas por MEDIDA. No es burocracia: un
# fixture de puros verdes no distingue una implementación correcta de una que devuelve `True`.
MUNDOS = [
    ("todo-en-orden", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "termino", "determinista": True, "presupuesto_agotado": False}],
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 1, "actor": "a", "que": "sigue"},
                   {"corrida": "c1", "t": 2, "actor": "a", "que": "termina"}],
    }),
    ("corrida-que-no-se-reproduce", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "termino", "determinista": False, "presupuesto_agotado": False}],
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 1, "actor": "a", "que": "termina"}],
    }),
    ("presupuesto-agotado", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "sin_pasos", "determinista": True, "presupuesto_agotado": True}],
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 1, "actor": "a", "que": "termina"}],
    }),
    ("traza-con-un-hueco", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "termino", "determinista": True, "presupuesto_agotado": False}],
        # falta el instante 1: hay dos eventos y el último es t=2
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 2, "actor": "a", "que": "termina"}],
    }),
]

MEDIDAS = [
    "simulacion.corrida_reproducible",
    "simulacion.la_traza_no_tiene_huecos",
    "simulacion.no_se_agoto_el_presupuesto",
]

SALIDA = RAIZ / "diferencial" / "simulacion.json"


def cargar_referencia():
    spec = importlib.util.spec_from_file_location("referencia_diferencial", REFERENCIA)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def construir(catalogo: dict) -> dict:
    from nucleo.algebra import ESCALARES

    referencia = cargar_referencia()
    medidas = [catalogo[mid] for mid in MEDIDAS]
    escenarios = []
    for nombre, evidencia in MUNDOS:
        ref_por_medida, oracle_por_medida = {}, {}
        for medida in medidas:
            ref_por_medida[medida.id] = bool(
                referencia.evaluar(medida.a_datos(), evidencia, dict(ESCALARES))["ok"])
            oracle_por_medida[medida.id] = bool(medida.evaluar(evidencia).ok)
        # El desacuerdo se informa acá y aborta: fijarlo en un archivo lo convertiría en el nuevo
        # esperado, que es exactamente la manera de perder el hallazgo.
        difieren = [mid for mid in ref_por_medida
                    if ref_por_medida[mid] != oracle_por_medida[mid]]
        if difieren:
            raise SystemExit(
                f"NO SE EMITE — en «{nombre}» la referencia y Oracle ya discrepan: {difieren}.\n"
                "Un fixture que nace en desacuerdo congela el desacuerdo. Resolvé cuál de las dos "
                "tiene razón (y si la especificación lo decide) antes de versionarlo.")
        escenarios.append({
            "id": nombre,
            "evidencia": evidencia,
            "referencia_ok": all(ref_por_medida.values()),
            "oracle_al_generar": {
                "global_ok": all(oracle_por_medida.values()),
                "por_medida": oracle_por_medida,
            },
        })

    procedencia = Procedencia(
        raiz=RAIZ,
        emisor=("tools/generar_diferencial.py",),
        referencia=("diferencial/referencia/evaluador.py",),
        desde_proyecto=".")
    return {
        "esquema": "oracle.diferencial/v1",
        "origen": "implementación independiente (Codex gpt-5.5) escrita sólo desde ESPECIFICACION.md",
        "medidas": list(MEDIDAS),
        "mundos": len(MUNDOS),
        "escenarios": escenarios,
        "frescura": crear_frescura(procedencia, medidas, {"dominio": "simulacion"}),
    }


def serializar(datos: dict) -> str:
    return json.dumps(datos, ensure_ascii=False, sort_keys=True, indent=2,
                      allow_nan=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    proy = Proyecto(RAIZ)
    catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
    datos = construir(catalogo)

    fallas = validar_fixture(datos, SALIDA.name)
    if fallas:
        print("FIXTURE INVÁLIDO — no se escribe:")
        for f in fallas:
            print(f"  · {f}")
        return 1

    texto = serializar(datos)
    if "--escribir" in argv:
        SALIDA.write_text(texto, encoding="utf-8")
        print(f"{SALIDA.relative_to(RAIZ)} escrito · {len(MUNDOS)} mundos · "
              f"{len(MEDIDAS)} medidas")
        return 0
    if not SALIDA.exists():
        print(f"falta {SALIDA.relative_to(RAIZ)}; ejecutá "
              "`python tools/generar_diferencial.py --escribir`")
        return 1
    if SALIDA.read_text(encoding="utf-8") != texto:
        print(f"{SALIDA.relative_to(RAIZ)} no coincide con lo que emite la referencia hoy; "
              "ejecutá `python tools/generar_diferencial.py --escribir`")
        return 1
    print(f"DIFERENCIAL AL DÍA — {len(MUNDOS)} mundos × {len(MEDIDAS)} medidas, "
          "referencia y Oracle de acuerdo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
