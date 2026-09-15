"""Verbo `oracle juzgar` (y `oracle proyecto juzgar`).

Juzga evidencia real —un JSON de hechos— contra el catálogo efectivo del proyecto.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from nucleo.algebra import ErrorDeAlgebra
from nucleo.medida import (Catalogo, Medida, MedidaMalDeclarada, evaluar,
                           medidas_aplicables, relaciones_de_medida)
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables,
                             Proyecto, ProyectoInvalido, catalogo_efectivo,
                             configuracion, confiar_escalares,
                             escalares_del_proyecto, macros_del_proyecto,
                             problemas_estructura, resolver)

# Límite superior para la lectura de evidencia en memoria (50 MiB).
LIMITE_TAMANO_EVIDENCIA = 50 * 1024 * 1024


def ayuda() -> None:
    print("""oracle juzgar — evalúa evidencia contra las medidas del proyecto

Uso:
  oracle proyecto juzgar --con <hechos.json> [--proyecto <ruta>]
                         [--confiar-escalares] [--medida <id>]... [--json]
  oracle juzgar --con <hechos.json> ...    (alias directo)

Opciones:
  --con <archivo>        Ruta al archivo JSON con la evidencia (obligatorio)
  --proyecto <ruta>      Ruta al proyecto (por defecto: directorio actual o $ORACLE_PROYECTO)
  --confiar-escalares    Autoriza la ejecución de funciones en escalares.py
  --medida <id>          Evalúa sólo esta medida (repetible, sin duplicados)
  --json                 Emite el informe como JSON en stdout""")


def catalogo_para_juzgar(proy: Proyecto) -> Catalogo:
    """Selección de medidas idéntica a la que usa oracle test en aceptación.

    Aplica `catalogo_efectivo`, respetando el ámbito (`universal` o `del_origen` con
    identidad lógica de proyecto) y descartando medidas heredadas del catálogo base
    o de bibliotecas que no obligan a este proyecto.
    """
    return catalogo_efectivo(proy, macros=macros_del_proyecto(proy))


def _leer_evidencia(ruta_str: str) -> tuple[dict | None, str | None]:
    """Lee y valida la forma de la evidencia.

    Devuelve (evidencia, None) si es válida; (None, mensaje_error) si es inválida.
    """
    ruta = Path(ruta_str).expanduser()
    if not ruta.exists():
        return None, f"el archivo de evidencia no existe: «{ruta}»"
    if ruta.is_dir():
        return None, f"la ruta de evidencia es un directorio, no un archivo: «{ruta}»"

    try:
        tamano = ruta.stat().st_size
    except OSError as e:
        return None, f"no se pudo consultar el archivo «{ruta}»: {e}"

    if tamano > LIMITE_TAMANO_EVIDENCIA:
        return None, (f"el archivo supera el límite de tamaño de 50 MiB "
                      f"({tamano} bytes): «{ruta}»")

    try:
        crudo = ruta.read_bytes()
    except OSError as e:
        return None, f"no se pudo leer el archivo «{ruta}»: {e}"

    try:
        texto = crudo.decode("utf-8")
    except UnicodeDecodeError as e:
        return None, f"el archivo «{ruta}» no es UTF-8 válido: {e}"

    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as e:
        return None, f"JSON inválido en «{ruta}»: {e}"

    if not isinstance(datos, dict):
        return None, (f"se esperaba un objeto JSON (relación → lista de filas) "
                      f"en «{ruta}»")

    for relacion, filas in datos.items():
        if not relacion.strip():
            return None, (f"nombre de relación inválido en «{ruta}»: debe ser un texto "
                          f"no vacío")
        if not isinstance(filas, list):
            return None, (f"el valor de la relación «{relacion}» debe ser una lista de filas "
                          f"en «{ruta}»")
        for i, fila in enumerate(filas):
            if not isinstance(fila, dict):
                return None, (f"la fila {i} de la relación «{relacion}» debe ser un objeto "
                              f"(recibido {type(fila).__name__}) en «{ruta}»")

    return datos, None


def cmd_juzgar(argv: list[str]) -> int:
    """Implementa el verbo `juzgar` / `proyecto juzgar`."""
    if "-h" in argv or "--help" in argv:
        ayuda()
        return 0

    args = list(argv)

    # 1. Parseo de banderas CLI
    ruta_evidencia_str: str | None = None
    es_json = False
    medidas_pedidas: list[str] = []
    sobrantes: list[str] = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--con":
            if ruta_evidencia_str is not None:
                print("bandera repetida: `--con`", file=sys.stderr)
                return 2
            if i + 1 >= len(args) or args[i + 1].startswith("--"):
                print("falta la ruta: `--con <archivo.json>`", file=sys.stderr)
                return 2
            ruta_evidencia_str = args[i + 1]
            i += 2
        elif arg == "--medida":
            if i + 1 >= len(args) or args[i + 1].startswith("--"):
                print("falta el id: `--medida <id>`", file=sys.stderr)
                return 2
            mid = args[i + 1]
            if mid in medidas_pedidas:
                print(f"id de medida repetido en `--medida`: «{mid}»", file=sys.stderr)
                return 2
            medidas_pedidas.append(mid)
            i += 2
        elif arg == "--json":
            es_json = True
            i += 1
        elif arg == "--confiar-escalares":
            i += 1
        elif arg == "--proyecto":
            if i + 1 >= len(args) or args[i + 1].startswith("--"):
                print("falta la ruta: `--proyecto <ruta>`", file=sys.stderr)
                return 2
            i += 2
        else:
            sobrantes.append(arg)
            i += 1

    if sobrantes:
        print(f"argumento desconocido para `oracle juzgar`: {sobrantes[0]}", file=sys.stderr)
        return 2

    if ruta_evidencia_str is None:
        print("falta la evidencia: indicá `--con <archivo.json>`", file=sys.stderr)
        return 2

    # 2. Resolución del proyecto
    try:
        proy = resolver(argv)
        fallas_estructura = problemas_estructura(proy, ("catalogos",))
        if fallas_estructura:
            print(f"PROYECTO INVÁLIDO — {'; '.join(fallas_estructura)}", file=sys.stderr)
            return 2
    except ProyectoInvalido as e:
        print(f"PROYECTO INVÁLIDO — {e}", file=sys.stderr)
        return 2

    # 3. Comprobación de escalares no confiadas
    confiar = confiar_escalares(argv)
    if (proy.raiz / "escalares.py").exists() and not proy.es_el_propio_oracle and not confiar:
        print(
            f"ESCALARES EXTERNAS NO EJECUTADAS — {proy.raiz / 'escalares.py'} es código Python "
            "externo; repetí con `--confiar-escalares` para ejecutarlo",
            file=sys.stderr,
        )
        return 2

    # 4. Lectura de evidencia
    evidencia, error_evidencia = _leer_evidencia(ruta_evidencia_str)
    if error_evidencia is not None or evidencia is None:
        print(f"EVIDENCIA INVÁLIDA — {error_evidencia}", file=sys.stderr)
        return 2

    # 5. Carga de catálogo y evaluación en el contexto de escalares
    try:
        with escalares_del_proyecto(proy, confiar=confiar):
            catalogo = catalogo_para_juzgar(proy)

            # 6. Selección y verificación de aplicabilidad de medidas
            if medidas_pedidas:
                medidas_a_evaluar: list[Medida] = []
                for mid in medidas_pedidas:
                    if mid not in catalogo:
                        print(
                            f"MEDIDA DESCONOCIDA — «{mid}» no existe en el catálogo efectivo del proyecto",
                            file=sys.stderr,
                        )
                        return 2
                    m = catalogo[mid]
                    if not medidas_aplicables([m], evidencia):
                        relaciones = relaciones_de_medida(m)
                        print(
                            f"MEDIDA NO APLICABLE — «{mid}» requiere las relaciones "
                            f"{list(relaciones)}, no presentes en la evidencia",
                            file=sys.stderr,
                        )
                        return 2
                    medidas_a_evaluar.append(m)
            else:
                medidas_a_evaluar = medidas_aplicables(catalogo.values(), evidencia)
                if not medidas_a_evaluar:
                    relaciones = sorted(evidencia.keys())
                    print(
                        f"SIN MEDIDAS APLICABLES — ninguna medida del catálogo aplica a "
                        f"las relaciones de la evidencia: {relaciones}",
                        file=sys.stderr,
                    )
                    return 1

            # 7. Evaluación
            informe = evaluar(medidas_a_evaluar, evidencia)

    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}", file=sys.stderr)
        return 2
    except ProyectoInvalido as e:
        print(f"PROYECTO INVÁLIDO — {e}", file=sys.stderr)
        return 2
    except (MedidaMalDeclarada, ErrorDeAlgebra, KeyError) as e:
        print(f"ERROR AL EVALUAR — {e}", file=sys.stderr)
        return 2

    # 8. Tratamiento de sombras y emisión de resultados
    mapa_sombra = {e.medida: e for e in configuracion(proy).sombra}
    rojos_fuera_de_sombra = [v for v in informe.veredictos if (not v.ok) and v.id not in mapa_sombra]
    rojos_en_sombra = [v for v in informe.veredictos if (not v.ok) and v.id in mapa_sombra]
    es_aprobado = (len(rojos_fuera_de_sombra) == 0)

    if es_json:
        medidas_json = []
        for v in informe.veredictos:
            d = v.a_dict()
            d["en_sombra"] = (v.id in mapa_sombra)
            medidas_json.append(d)
        salida_json = {
            "ok": es_aprobado,
            "medidas": medidas_json,
        }
        print(json.dumps(salida_json, ensure_ascii=False))
    else:
        lineas: list[str] = []
        for v in informe.veredictos:
            linea_base = v.linea()
            if v.id in mapa_sombra:
                s = mapa_sombra[v.id]
                detalles = []
                if s.desde:
                    detalles.append(f"desde {s.desde}")
                if s.porque:
                    detalles.append(f"porque: {s.porque}")
                texto_detalle = f" ({'; '.join(detalles)})" if detalles else ""
                primer_renglon, salto, resto = linea_base.partition("\n")
                lineas.append(f"{primer_renglon}   [EN SOMBRA]{texto_detalle}{salto}{resto}")
            else:
                lineas.append(linea_base)

        if not es_aprobado:
            lineas.append(f"\nVEREDICTO: {len(rojos_fuera_de_sombra)} de {len(informe.veredictos)} medidas en rojo")
        else:
            if len(rojos_en_sombra) == len(informe.veredictos) and len(informe.veredictos) > 0:
                lineas.append(
                    f"\nVEREDICTO: verde por sombra en {len(informe.veredictos)} medidas "
                    f"({len(rojos_en_sombra)} en sombra en rojo). SIN MIRAR:"
                )
            elif rojos_en_sombra:
                lineas.append(
                    f"\nVEREDICTO: verde en {len(informe.veredictos)} medidas "
                    f"({len(rojos_en_sombra)} en sombra perdonadas). SIN MIRAR:"
                )
            else:
                lineas.append(f"\nVEREDICTO: verde en {len(informe.veredictos)} medidas. SIN MIRAR:")
            lineas += [f"  · {v.id}: {v.alcance}" for v in informe.veredictos]

        print("\n".join(lineas))

    return 0 if es_aprobado else 1
