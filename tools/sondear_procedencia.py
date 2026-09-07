"""Emite la relación `caso` sobre corpus reales y la juzga con la medida de procedencia.

    python tools/sondear_procedencia.py
    python tools/sondear_procedencia.py --hechos

Existe por una razón concreta: `meta.todo_caso_observado_declara_de_donde_salio` exige que un caso
`observada` diga de dónde salió, y sus PROPIOS casos tienen que poder decirlo. Un `comando` que
nombra un script que no está en el repositorio es exactamente el puntero a la nada que la medida
persigue, así que el comando vive acá.

Cada sonda escribe un corpus de verdad en un directorio temporal, lo carga con el cargador real y
le pasa `hechos_de_casos`. Lo observado es qué emite el marco sobre esos casos; las entradas son
construidas y esto no dice nada sobre ningún dominio externo. No escribe en el corpus del proyecto
ni toca el catálogo.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path = [str(RAIZ), *sys.path]

from nucleo.caso import cargar_casos  # noqa: E402
from nucleo.marco import hechos_de_casos  # noqa: E402
from nucleo.medida import cargar  # noqa: E402

MID = "meta.todo_caso_observado_declara_de_donde_salio"

# La prosa no importa acá: lo que se sondea es qué sale de `origen` y `procedencia`.
BASE = {"fecha": "2026-09-07", "titulo": "t", "etiqueta": "falso_verde", "sintoma": "s",
        "como_se_detecto": "observacion", "medida": "dominio.algo",
        "evidencia": {"pieza": [{"nombre": "a"}]}, "leccion": "l"}

COMMIT = "abc1234"
REGISTRO = "medidas/observaciones/2026-09-07-dataset/registro.json"
COMANDO = "python3 tools/observar.py capturar --plan p.json --destino d"

# Dos corpus, y la diferencia entre los dos es UN campo de UN caso. El segundo conserva un caso
# `construida` sin nada en `origen` a propósito: es lo que distingue «este caso no dice de dónde
# salió» de «esta medida mira todos los casos». Sin él, quitarle el filtro de procedencia a la
# medida no cambiaría el veredicto y el mutante viviría.
SONDAS = {
    "un_caso_observado_no_dice_de_donde_salio": (
        [("001-corrida-sin-registro", "observada", {"repo": "Segtem/oracle", "commit": COMMIT}),
         ("002-corrida-con-registro", "observada",
          {"repo": "Segtem/oracle", "commit": COMMIT, "registro": REGISTRO}),
         ("003-escrito-a-mano", "construida", {"repo": "Segtem/oracle", "commit": COMMIT})],
        False),
    "todos_los_observados_dicen_de_donde_salieron": (
        [("001-corrida-con-comando", "observada",
          {"repo": "Segtem/oracle", "commit": COMMIT, "comando": COMANDO}),
         ("002-corrida-con-registro", "observada",
          {"repo": "Segtem/oracle", "commit": COMMIT, "registro": REGISTRO}),
         ("003-escrito-a-mano", "construida", {"repo": "Segtem/oracle", "commit": COMMIT})],
        True),
}


def escribir_corpus(entradas: list[tuple]) -> Path:
    raiz = Path(tempfile.mkdtemp(prefix="oracle-sonda-procedencia-")) / "corpus" / "dominio"
    raiz.mkdir(parents=True)
    for cid, procedencia, origen in entradas:
        # Sin `indent` ni `ensure_ascii`: este archivo vive milisegundos en un temporal y lo lee
        # `cargar_casos`, para el que sangría y escapes son indistinguibles. Estaban puestos por
        # costumbre y la mutación los encontró vivos, que es lo que son: decoración.
        (raiz / f"{cid}.json").write_text(
            json.dumps({**BASE, "id": cid, "procedencia": procedencia, "origen": origen}),
            encoding="utf-8")
    return raiz.parent


def hechos(nombre: str) -> dict:
    """Los hechos de UNA sonda, cargados del disco con el cargador real del corpus."""
    entradas, _debe_pasar = SONDAS[nombre]
    return hechos_de_casos({}, cargar_casos(escribir_corpus(entradas)))


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    medida = cargar(RAIZ / "catalogos" / "meta" / f"{MID}.oracle")
    salida = {}
    discordancias = []
    for nombre, (_entradas, debe_pasar) in SONDAS.items():
        evidencia = hechos(nombre)
        salida[nombre] = evidencia
        # La expectativa está declarada arriba, en la sonda; no se lee del veredicto.
        if medida.evaluar(evidencia).ok != debe_pasar:
            discordancias.append(nombre)
    if "--hechos" in args:
        print(json.dumps(salida))
        return 1 if discordancias else 0
    print(f"PROCEDENCIA — {len(SONDAS)} sondas sobre corpus reales, juzgadas por {MID}")
    for nombre in SONDAS:
        marca = "✗" if nombre in discordancias else "✓"
        print(f"  {marca} {nombre}")
    return 1 if discordancias else 0


_entrada_directa = {"__main__": main}.get(__name__)
if _entrada_directa:
    raise SystemExit(_entrada_directa())
