"""Sensor de `openspec validate`: arma proyectos de prueba, corre la CLI real y emite hechos.

Cada fixture ejerce un escenario de `openspec/specs/cli-validate/spec.md` (OpenSpec 79b6aa9).
El sensor no juzga nada: registra código de salida, ítems, problemas y texto. El juicio está en
`catalogos/`.

    python3 sensor.py --openspec <ruta al binario> [--exportar hechos.json]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PURPOSE = "Esta capacidad existe para probar el validador de OpenSpec con un caso chico y real."
WHY = "Hace falta un cambio de prueba para ejercer el validador de OpenSpec contra su propia spec."


def spec(req_body="The system SHALL do foo.", escenarios=("Works",), titulo="Foo", purpose=True):
    partes = ["# cap Specification", ""]
    if purpose:
        partes += ["## Purpose", PURPOSE, ""]
    partes += ["## Requirements", f"### Requirement: {titulo}"]
    if req_body:
        partes += [req_body, ""]
    for e in escenarios:
        partes += [f"#### Scenario: {e}", "- **WHEN** x", "- **THEN** y", ""]
    return "\n".join(partes)


def delta(op, reqs):
    """reqs: [(titulo, cuerpo, escenarios)]"""
    partes = [f"## {op} Requirements"]
    for titulo, cuerpo, escenarios in reqs:
        partes += [f"### Requirement: {titulo}", cuerpo, ""]
        for e in escenarios:
            partes += [f"#### Scenario: {e}", "- **WHEN** x", "- **THEN** y", ""]
    return "\n".join(partes)


def propuesta(nl="\n"):
    return nl.join(["# Change", "", "## Why", WHY, "", "## What Changes", "- Agrega algo de prueba.", ""])


def escribir(raiz: Path, archivos: dict[str, str]):
    for ruta, texto in archivos.items():
        p = raiz / "openspec" / ruta
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(texto.encode())


ADDED_OK = delta("ADDED", [("Bar", "The system SHALL bar.", ["Works"])])

# fixture -> (archivos, [(modo, argumentos, entorno extra)])
FIXTURES = {
    "spec_valida": (
        {"specs/cap/spec.md": spec()},
        [("normal", ["validate", "cap", "--json"], {})],
    ),
    "cambio_valido": (
        {"changes/ch/proposal.md": propuesta(), "changes/ch/specs/cap/spec.md": ADDED_OK},
        [("normal", ["validate", "ch", "--json"], {})],
    ),
    "cambio_sin_deltas": (
        {"changes/ch/proposal.md": propuesta()},
        [("normal", ["validate", "ch", "--json"], {}), ("humano", ["validate", "ch"], {})],
    ),
    "spec_sin_purpose": (
        {"specs/cap/spec.md": spec(purpose=False)},
        [("normal", ["validate", "cap", "--json"], {})],
    ),
    "requisito_sin_cuerpo": (
        {"specs/cap/spec.md": spec(req_body="")},
        [("normal", ["validate", "cap", "--json"], {})],
    ),
    "escenarios_en_vinetas": (
        {"specs/cap/spec.md": spec(escenarios=()) + "\n- **WHEN** x\n- **THEN** y\n"},
        [("normal", ["validate", "cap", "--json"], {})],
    ),
    "spec_sin_palabra_clave": (
        {"specs/cap/spec.md": spec(req_body="El sistema hace foo cuando corresponde.")},
        [("normal", ["validate", "cap", "--json"], {}), ("estricto", ["validate", "cap", "--json", "--strict"], {})],
    ),
    "delta_sin_palabra_clave": (
        {
            "changes/ch/proposal.md": propuesta(),
            "changes/ch/specs/cap/spec.md": delta("ADDED", [("Bar", "El sistema hace bar.", ["Works"])]),
        },
        [("normal", ["validate", "ch", "--json"], {}), ("estricto", ["validate", "ch", "--json", "--strict"], {})],
    ),
    "modified_omite_escenario": (
        {
            "specs/cap/spec.md": spec(escenarios=("A", "B")),
            "changes/ch/proposal.md": propuesta(),
            "changes/ch/specs/cap/spec.md": delta("MODIFIED", [("Foo", "The system SHALL do foo.", ["A"])]),
        },
        [("normal", ["validate", "ch", "--json"], {}), ("humano", ["validate", "ch"], {})],
    ),
    "modified_tras_rename": (
        {
            "specs/cap/spec.md": spec(escenarios=("S1", "S2"), titulo="A"),
            "changes/ch/proposal.md": propuesta(),
            "changes/ch/specs/cap/spec.md": "## RENAMED Requirements\n- FROM: `### Requirement: A`\n- TO: `### Requirement: B`\n\n"
            + delta("MODIFIED", [("B", "The system SHALL do foo.", ["S1"])]),
        },
        [("normal", ["validate", "ch", "--json"], {})],
    ),
    "modified_sin_base": (
        {
            "specs/cap/spec.md": spec(),
            "changes/ch/proposal.md": propuesta(),
            "changes/ch/specs/cap/spec.md": delta("MODIFIED", [("Inexistente", "The system SHALL x.", ["A"])]),
        },
        [("normal", ["validate", "ch", "--json"], {})],
    ),
    "sin_argumentos": (
        {"specs/cap/spec.md": spec()},
        [
            ("no_interactivo", ["validate", "--no-interactive"], {}),
            ("no_interactivo", ["validate"], {"OPEN_SPEC_INTERACTIVE": "0"}),
            ("no_interactivo", ["validate"], {}),
        ],
    ),
    "proyecto_mixto": (
        {
            "specs/cap/spec.md": spec(),
            "specs/rota/spec.md": spec(req_body=""),
            "specs/vacia/README.md": "sin spec.md\n",
            "changes/ch/proposal.md": propuesta(),
            "changes/ch/specs/cap/spec.md": ADDED_OK,
            "changes/archive/2026-01-01-viejo/proposal.md": "# roto\n",
        },
        [
            ("normal", ["validate", "--all", "--json"], {}),
            ("normal", ["validate", "--changes", "--json"], {}),
            ("normal", ["validate", "--specs", "--json"], {}),
        ],
    ),
    "solo_avisos": (
        {"specs/cap/spec.md": spec(req_body="El sistema hace foo cuando corresponde.")},
        [("normal", ["validate", "--all", "--json"], {}), ("estricto", ["validate", "--all", "--json", "--strict"], {})],
    ),
    "nombre_ambiguo": (
        {"specs/dup/spec.md": spec(), "changes/dup/proposal.md": propuesta(), "changes/dup/specs/cap/spec.md": ADDED_OK},
        [
            ("normal", ["validate", "dup", "--json"], {}),
            ("humano", ["validate", "dup"], {}),
            ("tipo_cambio", ["validate", "dup", "--type", "change", "--json"], {}),
            ("tipo_spec", ["validate", "dup", "--type", "spec", "--json"], {}),
        ],
    ),
    "nombre_desconocido": (
        {"specs/cap/spec.md": spec()},
        [("normal", ["validate", "cpa", "--json"], {}), ("humano", ["validate", "cpa"], {})],
    ),
    "propuesta_crlf": (
        {"changes/ch/proposal.md": propuesta("\r\n"), "changes/ch/specs/cap/spec.md": ADDED_OK.replace("\n", "\r\n")},
        [("normal", ["validate", "ch", "--json"], {})],
    ),
}

# Lo que hay en disco, para que las medidas de alcance comparen contra algo que no dijo la CLI.
EN_DISCO = {
    "proyecto_mixto": [("cap", "spec", False), ("rota", "spec", False), ("ch", "change", False), ("2026-01-01-viejo", "change", True)],
}


def correr(binario, fixture, archivos, corridas):
    hechos = {"corrida": [], "item": [], "problema": [], "resumen": [], "salida": [], "estado": [], "pie": []}
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        escribir(raiz, archivos)
        for n, (modo, args, extra) in enumerate(corridas):
            caso = f"{fixture}#{n}"
            entorno = {**os.environ, "NO_COLOR": "1", "OPENSPEC_TELEMETRY": "0", **extra}
            r = subprocess.run(
                [binario, *args], cwd=raiz, env=entorno, stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=60,
            )
            texto = (r.stdout + r.stderr).replace(tmp, "<tmp>")
            try:
                datos = json.loads(r.stdout)
            except ValueError:
                datos = None
            hechos["corrida"].append({
                "caso": caso, "fixture": fixture, "modo": modo, "comando": " ".join(["openspec", *args]),
                "entorno": " ".join(f"{k}={v}" for k, v in extra.items()), "codigo": r.returncode,
                "alcance": next((v for b, v in (("--all", "all"), ("--changes", "change"), ("--specs", "spec")) if b in args), "item"),
                "es_json": isinstance(datos, dict),
            })
            hechos["salida"].append({"caso": caso, "texto": texto})
            lineas = texto.splitlines()
            if "Next steps:" in lineas:
                resto = lineas[lineas.index("Next steps:") + 1:]
                vinetas = 0
                for linea in resto:
                    if not linea.startswith("  - "):
                        break
                    vinetas += 1
                hechos["pie"].append({"caso": caso, "vinetas": vinetas})
            if not isinstance(datos, dict):
                continue
            for e in datos.get("status", []):
                hechos["estado"].append({"caso": caso, "severidad": e.get("severity"), "codigo": e.get("code"),
                                         "mensaje": e.get("message")})
            for it in datos.get("items", []):
                hechos["item"].append({"caso": caso, "id": it.get("id"), "tipo": it.get("type"), "valido": it.get("valid") is True,
                                       "tiene_duracion": isinstance(it.get("durationMs"), (int, float))})
                for p in it.get("issues", []):
                    hechos["problema"].append({"caso": caso, "id": it.get("id"), "nivel": p.get("level"),
                                               "ruta": p.get("path"), "mensaje": p.get("message")})
            tot = datos.get("summary", {}).get("totals")
            if isinstance(tot, dict):
                hechos["resumen"].append({"caso": caso, "items": tot.get("items"), "aprobados": tot.get("passed"),
                                          "fallados": tot.get("failed"), "version": str(datos.get("version"))})
    return hechos


def medir(binario):
    hechos = {"corrida": [], "item": [], "problema": [], "resumen": [], "salida": [], "estado": [], "pie": [], "en_disco": []}
    for fixture, (archivos, corridas) in FIXTURES.items():
        for k, v in correr(binario, fixture, archivos, corridas).items():
            hechos[k].extend(v)
    for fixture, filas in EN_DISCO.items():
        hechos["en_disco"] += [{"fixture": fixture, "id": i, "tipo": t, "archivado": a} for i, t, a in filas]
    return hechos


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--openspec", required=True)
    ap.add_argument("--exportar")
    a = ap.parse_args(argv)
    salida = json.dumps(medir(a.openspec), indent=2, ensure_ascii=False)
    if a.exportar:
        Path(a.exportar).write_text(salida + "\n", encoding="utf-8")
    else:
        print(salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
