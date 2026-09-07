"""Ejercita umbrales distintos de cero y juzga al generador con la medida de polaridad.

    python tools/sondear_generador.py
    python tools/sondear_generador.py --hechos

Las entradas son sondas construidas. La salida registra lo que el generador hizo al ejecutarlas;
no es evidencia sobre un dominio externo. No escribe casos ni modifica el catálogo.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path = [str(RAIZ), *sys.path]

from nucleo.generador import GeneracionNoPosible, fabricar_candidatos  # noqa: E402
from nucleo.medida import Medida, cargar  # noqa: E402

MID_POLARIDAD = "meta.el_caso_se_pone_como_debe"
MID_SOMBRAS = "meta.ninguna_sombra_envejece_sin_revisarse"


def sondas() -> list[tuple[Medida, bool]]:
    """El booleano declara si esta sonda requiere generación o una negativa explícita."""
    salida = []
    for nombre, op, limite, agregado, debe_generar in (
        ("conteo_inclusivo", "<=", 5, "contar", True),
        ("conteo_estricto", "<", 5, "contar", True),
        ("conteo_fraccionario", "<=", 5.5, "contar", True),
        ("magnitud_insuficiente", "<=", 10, "max", False),
    ):
        medida = Medida.de_datos([
            "medida", f"sonda.{nombre}",
            ["desde", ["de", "dato", "x"], ["donde", [">", ["campo", "x", "valor"], 0]]],
            ["resumen", agregado, ["campo", "x", "valor"]],
            ["umbral", op, limite, "Sonda construida del generador, no política del dominio"],
            ["alcance", "Sólo comprueba la fabricación de evidencia y su polaridad"],
        ])
        salida.append((medida, debe_generar))
    salida.append((cargar(RAIZ / "catalogos" / "meta" / f"{MID_SOMBRAS}.oracle"), True))
    return salida


def hechos() -> dict:
    """Reutiliza los campos de `caso`; las expectativas no se deducen del resultado."""
    filas = []
    for medida, debe_generar in sondas():
        try:
            candidatos = fabricar_candidatos(medida)
        except GeneracionNoPosible:
            filas.append({"id": f"{medida.id}:entrega", "esperado_ok": debe_generar,
                          "dio_ok": False})
            continue
        filas.append({"id": f"{medida.id}:entrega", "esperado_ok": debe_generar,
                      "dio_ok": True})
        filas.append({"id": f"{medida.id}:ambas_polaridades", "esperado_ok": True,
                      "dio_ok": {c["etiqueta"] for c in candidatos}
                      == {"falso_verde", "verde_correcto"}})
        for candidato in candidatos:
            v = medida.evaluar(candidato["evidencia"])
            filas.append({"id": candidato["id"],
                          "esperado_ok": candidato["etiqueta"] == "verde_correcto",
                          "dio_ok": v.ok})
    return {"caso": filas}


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    evidencia = hechos()
    if not evidencia["caso"]:
        print("GENERADOR NO COMPROBADO — no se ejecutó ninguna sonda")
        return 1
    medida = cargar(RAIZ / "catalogos" / "meta" / f"{MID_POLARIDAD}.oracle")
    v = medida.evaluar(evidencia)
    if "--hechos" in args:
        print(json.dumps(evidencia))
    else:
        print(f"GENERADOR — {len(evidencia['caso'])} comprobaciones de entrega y polaridad")
        print(v.linea())
    return 0 if v.ok else 1


_entrada_directa = {"__main__": main}.get(__name__)
if _entrada_directa:
    raise SystemExit(_entrada_directa())
