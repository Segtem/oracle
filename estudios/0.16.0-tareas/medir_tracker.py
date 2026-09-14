"""Rondas explícitas del tracker con los perfiles declarados para su custodia en CI.

Ejemplo: python3 -B estudios/0.16.0-tareas/medir_tracker.py tareas_git --salida /tmp/ronda-git
Usa el motor de mutación existente y la suite completa, con módulos propios primero.
--diagnostico corre sólo los módulos propios para localizar huecos; no cierra la verificación.
No declara equivalentes ni cambia el conjunto de mutadores.
"""

import argparse
import json
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from perfiles.python.mutacion_codigo import correr  # noqa: E402
from tools.mutar_codigo import dependencias_de_ronda  # noqa: E402

from tools.mutar_codigo import PRIORIDADES as PRIORIDADES_CI  # noqa: E402

PRIORIDADES = {
    nombre: PRIORIDADES_CI[f"tools/{nombre}.py"]
    for nombre in ("tareas", "tareas_contexto", "tareas_git", "tareas_hechos")
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("objetivo", choices=PRIORIDADES)
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument("--diagnostico", action="store_true")
    args = parser.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    comando = [sys.executable, "-B", str(RAIZ / "tools/ejecutar_suite_mutacion.py")]
    for modulo in PRIORIDADES[args.objetivo]:
        comando.extend(("--prioridad", modulo))
    if args.diagnostico:
        # La fachada no contiene test*.py: no añade la suite general tras las prioridades.
        # Se conserva el runner oficial, que distingue error de carga (2) de fallo de test (1).
        comando.extend(("--inicio", "oracle_metalenguaje"))
    print("Alcance: " + ("diagnóstico con módulos propios" if args.diagnostico
                        else "suite completa con prioridades"), flush=True)
    dependencias = set(dependencias_de_ronda())
    dependencias.update((RAIZ / "tools").glob("*.py"))
    dependencias.add(Path(__file__).resolve())
    dependencias.update(p for p in (RAIZ / "ejemplo/seguimiento-tareas").rglob("*")
                        if p.is_file() and "__pycache__" not in p.parts)

    def progreso(fila):
        estado = ("muerto" if fila["tests_fallaron"] else "timeout" if fila["timeout"]
                  else "error_arnes" if fila["error_arnes"] else "vivo")
        print(f'{estado}: {fila["id"]} {fila["cambio"]}', flush=True)

    evidencia = correr(
        RAIZ, [RAIZ / "tools" / f"{args.objetivo}.py"], comando, {},
        al_terminar_uno=progreso, timeout_por_ejecucion=120,
        manifiesto=args.salida / "manifiesto.json", dependencias=sorted(dependencias))
    (args.salida / "hechos.json").write_text(
        json.dumps(evidencia, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    corrida = evidencia["corrida_mutacion"][0]
    print(json.dumps(corrida, ensure_ascii=False), flush=True)
    return int(corrida["tests_fallaron"] != corrida["mutantes"]
               or corrida["timeouts"] or corrida["errores_arnes"])


if __name__ == "__main__":
    raise SystemExit(main())
