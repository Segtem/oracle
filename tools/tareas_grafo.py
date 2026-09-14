"""Generación del grafo de referencias entre tareas en formato DOT y JSON."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from tools import tareas
from tools.tareas import ParserDeSubcomando, auditar_tareas, resolver_raiz_tracker


PATRON_CANDIDATO_ID = re.compile(
    r"(?<![A-Za-z0-9_-])[0-9]{8}-[0-9]{6}[A-Za-z0-9_-]*"
)


def cmd_grafo(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea grafo",
        description="Emite el grafo de referencias entre tareas en formato DOT o JSON",
    )
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parsed = parser.parse_args(args)

    try:
        raiz = resolver_raiz_tracker(argv, ruta_explicita=parsed.proyecto)
    except (tareas.TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    raiz_tareas = raiz / "tareas"
    tareas_validas, problemas = auditar_tareas(raiz_tareas)

    if problemas:
        print(
            f"ERROR: se detectaron {len(problemas)} registro(s) inválido(s) en {raiz_tareas}:",
            file=sys.stderr,
        )
        for p in problemas:
            print(f"  · {p}", file=sys.stderr)
        return 1

    tareas_map = {t.id: t for t in tareas_validas}
    ids_validos_set = set(tareas_map.keys())

    aristas_set: set[tuple[str, str]] = set()

    for t in tareas_validas:
        try:
            texto = t.ruta.read_text(encoding="utf-8")
        except OSError as e:
            print(f"ERROR: no se pudo leer {t.ruta}: {e}", file=sys.stderr)
            return 1

        for m in PATRON_CANDIDATO_ID.finditer(texto):
            otro_id = m.group(0)
            if otro_id != t.id and otro_id in ids_validos_set:
                aristas_set.add((t.id, otro_id))

    aristas = sorted(aristas_set)

    # Nodos participantes: un nodo por tarea que participa en alguna arista
    nodos_ids = sorted({u for u, v in aristas} | {v for u, v in aristas})
    nodos = [tareas_map[nid] for nid in nodos_ids]

    if parsed.json:
        resultado = {
            "nodos": [
                {"id": t.id, "titulo": t.titulo, "estado": t.estado}
                for t in nodos
            ],
            "aristas": [
                {"origen": u, "destino": v}
                for u, v in aristas
            ],
        }
        print(json.dumps(resultado))
        return 0

    # Formato DOT determinista
    lineas = ["digraph tareas {"]
    for t in nodos:
        titulo_esc = t.titulo.replace("\\", "\\\\").replace('"', '\\"')
        label = f"{titulo_esc} ({t.estado})"
        lineas.append(f'  "{t.id}" [label="{label}"];')
    for u, v in aristas:
        lineas.append(f'  "{u}" -> "{v}";')
    lineas.append("}")

    print("\n".join(lineas))
    return 0
