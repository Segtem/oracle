"""Verbo `oracle juzgar` (y `oracle proyecto juzgar`).

Juzga evidencia real —un JSON de hechos— contra el catálogo efectivo del proyecto.
"""

from __future__ import annotations

import json
import stat
import sys
from dataclasses import replace
from pathlib import Path

from nucleo.algebra import ErrorDeAlgebra
from nucleo.medida import (Catalogo, Informe, Medida, MedidaMalDeclarada, evaluar_conjunto,
                           medidas_aplicables, no_aplicadas, relaciones_de_medida)
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables,
                             Proyecto, ProyectoInvalido, catalogo_efectivo,
                             ORIGEN_PROYECTO, configuracion, confiar_escalares,
                             cotas_de_sombra,
                             escalares_del_proyecto, macros_del_proyecto,
                             resolver)

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
    # Una sola consulta al sistema de archivos, dentro del `try`: `exists()` e `is_dir()` también
    # llaman a `stat`, y un OSError que no sea «no existe» salía como traceback.
    try:
        info = ruta.stat()
    except FileNotFoundError:
        return None, f"el archivo de evidencia no existe: «{ruta}»"
    except OSError as e:
        return None, f"no se pudo consultar el archivo «{ruta}»: {e}"
    if stat.S_ISDIR(info.st_mode):
        return None, f"la ruta de evidencia es un directorio, no un archivo: «{ruta}»"
    tamano = info.st_size

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


class MedidaDesconocida(Exception):
    """Una medida pedida explícitamente no existe en el catálogo efectivo."""

    def __init__(self, mid: str) -> None:
        self.mid = mid
        super().__init__(f"MEDIDA DESCONOCIDA — «{mid}» no existe en el catálogo efectivo del proyecto")


class MedidaNoAplicable(Exception):
    """Una medida pedida explícitamente no aplica a las relaciones de la evidencia."""

    def __init__(self, mid: str, relaciones: list[str]) -> None:
        self.mid = mid
        self.relaciones = relaciones
        super().__init__(
            f"MEDIDA NO APLICABLE — «{mid}» requiere las relaciones "
            f"{relaciones}, no presentes en la evidencia"
        )


def juzgar_evidencia(
    proy: Proyecto,
    evidencia: dict,
    ids: tuple[str, ...] | list[str] = (),
) -> Informe:
    """Evalúa evidencia contra el catálogo efectivo del proyecto, con sombras y cotas.

    Aplica las sombras y cotas declaradas en `oracle.json`. Si se reciben `ids`, evalúa
    únicamente esas medidas (levantando MedidaDesconocida o MedidaNoAplicable si alguna
    no existe o no aplica). Si no se reciben `ids`, evalúa todas las aplicables y adjunta
    `no_aplicadas` con las medidas del catálogo propio cuyas relaciones faltaron.
    """
    catalogo = catalogo_para_juzgar(proy)

    if ids:
        medidas_a_evaluar: list[Medida] = []
        for mid in ids:
            if mid not in catalogo:
                raise MedidaDesconocida(mid)
            m = catalogo[mid]
            if not medidas_aplicables([m], evidencia):
                relaciones = relaciones_de_medida(m)
                raise MedidaNoAplicable(mid, list(relaciones))
            medidas_a_evaluar.append(m)
        faltantes: tuple = ()
    else:
        medidas_a_evaluar = medidas_aplicables(catalogo.values(), evidencia)
        # Sólo las del catálogo propio: las heredadas juzgan el catálogo, no esta evidencia,
        # y nombrarlas en cada corrida taparía la que de verdad faltó.
        faltantes = no_aplicadas(
            [catalogo[mid] for mid, entrada in catalogo.entradas.items()
             if entrada.origen == ORIGEN_PROYECTO], evidencia)

    sombra = configuracion(proy).sombra
    informe = evaluar_conjunto(medidas_a_evaluar, evidencia,
                               en_sombra=frozenset(e.medida for e in sombra),
                               cotas=cotas_de_sombra(sombra))
    return replace(informe, no_aplicadas=faltantes)


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
            print(f"argumento desconocido para `oracle juzgar`: {arg}", file=sys.stderr)
            return 2

    if ruta_evidencia_str is None:
        print("falta la evidencia: indicá `--con <archivo.json>`", file=sys.stderr)
        return 2

    # 2. Resolución del proyecto
    try:
        # `resolver` ya rechaza un proyecto sin `catalogos/`.
        proy = resolver(argv)
    except ProyectoInvalido as e:
        print(f"PROYECTO INVÁLIDO — {e}", file=sys.stderr)
        return 2

    # 3. Comprobación de escalares no confiadas
    confiar = confiar_escalares(argv)
    if (proy.raiz / "escalares.py").exists() and not confiar:
        print(
            f"ESCALARES EXTERNAS NO EJECUTADAS — {proy.raiz / 'escalares.py'} es código Python "
            "externo; repetí con `--confiar-escalares` para ejecutarlo",
            file=sys.stderr,
        )
        return 2

    # 4. Lectura de evidencia
    evidencia, error_evidencia = _leer_evidencia(ruta_evidencia_str)
    if error_evidencia is not None:
        print(f"EVIDENCIA INVÁLIDA — {error_evidencia}", file=sys.stderr)
        return 2

    # 5. Carga de catálogo y evaluación en el contexto de escalares
    try:
        with escalares_del_proyecto(proy, confiar=confiar):
            informe = juzgar_evidencia(proy, evidencia, ids=medidas_pedidas)
            # Primero lo que no se pudo juzgar: una medida que levantó tampoco dejó veredicto, y
            # contarla como «ninguna aplica» esconde el error.
            if informe.no_juzgaron:
                for mid, motivo in informe.no_juzgaron:
                    print(f"ERROR AL EVALUAR — «{mid}»: {motivo}", file=sys.stderr)
                return 2
            if not informe.veredictos:
                relaciones = sorted(evidencia.keys())
                print(
                    f"SIN MEDIDAS APLICABLES — ninguna medida del catálogo aplica a "
                    f"las relaciones de la evidencia: {relaciones}",
                    file=sys.stderr,
                )
                return 1

    except MedidaDesconocida as e:
        print(str(e), file=sys.stderr)
        return 2
    except MedidaNoAplicable as e:
        print(str(e), file=sys.stderr)
        return 2
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}", file=sys.stderr)
        return 2
    except ProyectoInvalido as e:
        print(f"PROYECTO INVÁLIDO — {e}", file=sys.stderr)
        return 2
    except (MedidaMalDeclarada, ErrorDeAlgebra, KeyError) as e:
        print(f"ERROR AL EVALUAR — {e}", file=sys.stderr)
        return 2

    sombra = configuracion(proy).sombra
    mapa_sombra = {e.medida: e for e in sombra}

    # 8. Emisión de resultados. Lo propio de `juzgar` es la prosa: el `desde` y el `porque` de cada
    # sombra, y el «verde por sombra» de cuando TODAS las aplicables estaban perdonadas. Quién está
    # en rojo lo decide el informe.
    rojos_fuera_de_sombra = informe.rojos
    rojos_en_sombra = informe.perdonados
    es_aprobado = informe.ok

    if es_json:
        medidas_json = []
        for v in informe.veredictos:
            d = v.a_dict()
            d["en_sombra"] = (v.id in mapa_sombra)
            d["supera_su_cota"] = informe.supera_su_cota(v)
            medidas_json.append(d)
        salida_json = {
            "ok": es_aprobado,
            "medidas": medidas_json,
            "no_aplicadas": [{"id": mid, "faltan": list(faltan)}
                             for mid, faltan in informe.no_aplicadas],
        }
        print(json.dumps(salida_json, ensure_ascii=False))
    else:
        lineas: list[str] = []
        for v in informe.veredictos:
            linea_base = v.linea()
            if v.id in mapa_sombra:
                s = mapa_sombra[v.id]
                detalles = []
                if informe.supera_su_cota(v):
                    detalles.append(f"SUPERA SU COTA {s.cota}: la sombra no la perdona")
                if s.desde:
                    detalles.append(f"desde {s.desde}")
                if s.porque:
                    detalles.append(f"porque: {s.porque}")
                texto_detalle = f" ({'; '.join(detalles)})" if detalles else ""
                primer_renglon, salto, resto = linea_base.partition("\n")
                lineas.append(f"{primer_renglon}   [EN SOMBRA]{texto_detalle}{salto}{resto}")
            else:
                lineas.append(linea_base)

        lineas += informe.lineas_no_aplicadas()
        if not es_aprobado:
            lineas.append(f"\nVEREDICTO: {len(rojos_fuera_de_sombra)} de {len(informe.veredictos)} medidas en rojo")
        else:
            if len(rojos_en_sombra) == len(informe.veredictos):
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
