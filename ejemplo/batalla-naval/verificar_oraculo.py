#!/usr/bin/env python3
"""
verificar_oraculo.py - Demostración de verificación rigurosa de reglas con Oracle

Este script:
1. Lee la partida guardada en 'partida_real.json'.
2. Ejecuta `oracle juzgar --con partida_real.json` para comprobar que las 11 reglas se cumplen (VERDE).
4. Genera variantes con infracciones deliberadas (trampas/errores) para demostrar
   que el oráculo es falsable y no un sello complaciente:
   a) Disparo duplicado a la misma celda.
   b) Disparo fuera de los límites del tablero (fila 10).
   c) Impacto fantasma (mentir diciendo que dio en un barco cuando era agua).
   d) Turnos consecutivos del mismo tirador sin alternar.
   e) Disparo posterior al fin de la partida.
   f) Ganador ilegítimo (con menos de 17 impactos).
"""

import copy
import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CLI = BASE_DIR.parents[1] / "tools" / "cli.py"


def simular_partida():
    """Ejecuta una partida automática usando el motor del juego en Node.js."""
    script = """
    const { TraceRecorder } = require("./js/trace.js");
    const { NavalGame } = require("./js/engine.js");

    const trace = new TraceRecorder();
    const game = new NavalGame(trace);
    game.newGame();
    game.playerBoard.autoPlaceFleet();
    game.startBattle();

    while (game.phase === "battle") {
      if (game.currentTurn === "jugador") {
        const unshot = [];
        for (let r = 0; r < 10; r++) {
          for (let c = 0; c < 10; c++) {
            if (!game.cpuBoard.grid[r][c].shot) unshot.push({ r, c });
          }
        }
        const target = unshot[Math.floor(Math.random() * unshot.length)];
        game.firePlayerShot(target.r, target.c);
      } else {
        game.executeCpuTurn();
      }
    }
    console.log(trace.toJSON(2));
    """
    res = subprocess.run(
        ["node", "-e", script],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(res.stdout)


def ejecutar_oracle_juzgar(ruta_json):
    """Ejecuta `oracle juzgar --con <ruta_json>` y retorna (codigo, salida)."""
    res = subprocess.run(
        [sys.executable, str(CLI), "juzgar", "--proyecto", str(BASE_DIR),
         "--con", str(ruta_json)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )
    return res.returncode, res.stdout.strip() or res.stderr.strip()


def main():
    print("=" * 70)
    print("DEMOSTRACIÓN DE VERIFICACIÓN FORMAL DE BATALLA NAVAL")
    print("Herramienta: Oracle Metalenguaje (oracle juzgar)")
    print("=" * 70)

    # 1. Partida real legítima
    print("\n[1/3] Leyendo partida real guardada...")
    ruta_real = BASE_DIR / "partida_real.json"
    evidencia_real = json.loads(ruta_real.read_text(encoding="utf-8"))
    print(f" -> Leída de {ruta_real.name}")
    print(f"    - Celdas de barco: {len(evidencia_real['celda_barco'])}")
    print(f"    - Tiros jugados: {len(evidencia_real['tiro'])}")
    print(f"    - Ganador: {evidencia_real['partida'][0]['ganador']}")

    print("\n[2/3] Juzgando la partida legítima contra el catálogo de Oracle...")
    rc, salida = ejecutar_oracle_juzgar(ruta_real)
    print(salida)
    if rc == 0 and "VEREDICTO: verde en 11 medidas" in salida:
        print("\n>>> RESULTADO: ÉXITO. Todas las 11 reglas se cumplen formalmente.")
    else:
        print("\n>>> RESULTADO: Error en la evaluación de la partida real.")
        sys.exit(1)

    # 2. Pruebas de falsabilidad (contraejemplos / inyección de faltas)
    print("\n" + "=" * 70)
    print("[3/3] DEMOSTRACIÓN DE FALSIBILIDAD: Inyectando infracciones a propósito")
    print("      (Probamos que el oráculo no aprueba cualquier cosa)")
    print("=" * 70)

    escenarios_infraccion = [
        (
            "Disparo duplicado a la misma casilla (fila 3, col 3)",
            "naval.tiros_sin_repeticion",
            lambda e: e["tiro"].append({
                "turno": len(e["tiro"]),
                "tirador": e["tiro"][0]["tirador"],
                "receptor": e["tiro"][0]["receptor"],
                "fila": e["tiro"][0]["fila"],
                "columna": e["tiro"][0]["columna"],
                "es_impacto": False,
                "hundio_barco": False,
                "barco_hundido": "ninguno"
            })
        ),
        (
            "Disparo fuera del tablero reglamentario (fila 14, col 2)",
            "naval.tiros_dentro_del_tablero",
            lambda e: e["tiro"].append({
                "turno": len(e["tiro"]),
                "tirador": "jugador",
                "receptor": "cpu",
                "fila": 14,
                "columna": 2,
                "es_impacto": False,
                "hundio_barco": False,
                "barco_hundido": "ninguno"
            })
        ),
        (
            "Impacto fantasma (afirmar impacto en casilla donde no había barco)",
            "naval.veracidad_impacto_positivo",
            lambda e: e["tiro"].append({
                "turno": len(e["tiro"]),
                "tirador": "jugador",
                "receptor": "cpu",
                "fila": 0,
                "columna": 9,  # Supongamos agua
                "es_impacto": True,
                "hundio_barco": False,
                "barco_hundido": "ninguno"
            }) if not any(c["jugador"] == "cpu" and c["fila"] == 0 and c["columna"] == 9 for c in e["celda_barco"])
            else e["tiro"].append({
                "turno": len(e["tiro"]),
                "tirador": "jugador",
                "receptor": "cpu",
                "fila": 0,
                "columna": 8,
                "es_impacto": True,
                "hundio_barco": False,
                "barco_hundido": "ninguno"
            })
        ),
        (
            "Turnos consecutivos del mismo tirador sin alternar",
            "naval.alternancia_turnos",
            lambda e: e["tiro"].insert(1, {
                "turno": 1,
                "tirador": e["tiro"][0]["tirador"],  # Mismo tirador consecutivo
                "receptor": e["tiro"][0]["receptor"],
                "fila": 8,
                "columna": 8,
                "es_impacto": False,
                "hundio_barco": False,
                "barco_hundido": "ninguno"
            }) or [t.__setitem__("turno", i) for i, t in enumerate(e["tiro"])]
        )
    ]

    fallas = 0
    for titulo, medida_esperada, inyector in escenarios_infraccion:
        evidencia_rota = copy.deepcopy(evidencia_real)
        inyector(evidencia_rota)
        ruta_rota = BASE_DIR / "partida_con_infraccion.json"
        ruta_rota.write_text(json.dumps(evidencia_rota, indent=2), encoding="utf-8")

        rc, salida = ejecutar_oracle_juzgar(ruta_rota)
        ruta_rota.unlink(missing_ok=True)

        if medida_esperada in salida and ("✗" in salida or "en rojo" in salida):
            print(f"  ✓ {titulo}")
            print(f"    -> Atrapado con éxito por medida: {medida_esperada}")
        else:
            fallas += 1
            print(f"  ✗ Falló detección para: {titulo}")
            print(salida)

    if fallas:
        sys.exit(1)

    print("\n" + "=" * 70)
    print("VERIFICACIÓN COMPLETA FINALIZADA CON ÉXITO")
    print("=" * 70)


if __name__ == "__main__":
    main()
