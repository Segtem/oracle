"""Casos del corpus a partir de una corrida real del sensor.

Por cada medida escribe dos casos:
  1xx  observado: los hechos reales que la medida lee, recortados a los fixtures que nombra. La
       etiqueta sale del veredicto real: rojo → falso_verde (OpenSpec no cumple su spec),
       verde → verde_correcto.
  2xx  sin evidencia: la relación que la medida requiere, vacía. Fija `requiere`.

    PYTHONPATH=<raíz de Oracle> python3 corpus.py <hechos.json> <salida de oracle juzgar> <sha de OpenSpec> <versión de la CLI>
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
from nucleo.caso import imprimir  # PYTHONPATH=<raíz de Oracle>


def main(hechos_ruta, juicio_ruta, commit, version):
    hechos = json.loads(Path(hechos_ruta).read_text())
    sha = "sha256:" + hashlib.sha256(Path(hechos_ruta).read_bytes()).hexdigest()
    rojas = set(re.findall(r"^✗ (\S+)", Path(juicio_ruta).read_text(), re.M))
    fixtures = {c["fixture"] for c in hechos["corrida"]}
    hoy = datetime.now(timezone.utc)
    destino = RAIZ / "corpus" / "openspec"
    for n, medida in enumerate(sorted(RAIZ.glob("catalogos/openspec/*.oracle"))):
        texto = medida.read_text()
        mid = medida.stem
        corto = mid.removeprefix("openspec.").replace("_", "-")
        relaciones = sorted(set(re.findall(r"^\s*(?:de|unir|sin) (\w+) ", texto, re.M)))
        requiere = re.search(r"^\s*requiere (\w+)", texto, re.M).group(1)
        nombrados = {f for f in re.findall(r'"(\w+)"', texto) if f in fixtures}
        casos = {c["caso"] for c in hechos["corrida"] if c["fixture"] in (nombrados or fixtures)}
        # La corrida entera, sin recortar: un filtro de la medida que se afloje ve las demás.
        evidencia = {rel: hechos[rel] for rel in relaciones}
        rojo = mid in rojas
        comun = {
            "fecha": hoy.date().isoformat(),
            "medida": mid,
            "como_se_detecto": "observacion",
        }
        imprimir_en(destino / f"{101 + n}-{corto}.caso", {
            "id": f"{101 + n}-{corto}",
            **comun,
            "origen": {
                "repo": "Fission-AI/OpenSpec",
                "commit": commit,
                "cuando_utc": hoy.isoformat(timespec="seconds"),
                "comando": f"python3 sensor.py --openspec <@fission-ai/openspec {version}>",
                "evidencia_sha256": sha,
            },
            "procedencia": "observada",
            "titulo": f"openspec validate {version}, corrido contra los fixtures que {mid} nombra",
            "etiqueta": "falso_verde" if rojo else "verde_correcto",
            "sintoma": ("La CLI real no cumple la cláusula de cli-validate que esta medida vuelve falsable."
                        if rojo else "Ninguno: la CLI real cumple la cláusula de cli-validate que esta medida vuelve falsable."),
            "evidencia": evidencia,
            "leccion": ("Una spec escrita en prosa normativa dejó de coincidir con la herramienta que la valida; "
                        "ni `openspec validate` ni `/opsx:verify` lo ven porque ninguno corre la CLI contra la spec."
                        if rojo else "La medida queda fijada contra la salida real, no sólo contra evidencia fabricada."),
        })
        negado = re.search(r"^\s*sin (\w+) ", texto, re.M)
        rotos = []
        if negado and not rojo:
            # La CLI cumple: se rompe UNA corrida por fixture, quitando las filas que la salvan.
            rel = negado.group(1)
            for fx in sorted(nombrados):
                caso = min(c["caso"] for c in hechos["corrida"] if c["fixture"] == fx)
                if rel == "item":
                    quitar = lambda f: f["caso"] == caso
                else:
                    quitar = lambda f: f.get("caso") == caso or f.get("fixture") == fx
                rotos.append((fx, {**evidencia, rel: [f for f in evidencia[rel] if not quitar(f)]}))
        for sufijo, cambio in ROMPER.get(mid, []):
            rotos.append((sufijo, cambio(json.loads(json.dumps(evidencia)))))
        for k, (sufijo, roto) in enumerate(rotos):
            cid = f"{301 + n}-{corto}-roto-{k + 1}"
            imprimir_en(destino / f"{cid}.caso", construido(
                comun, cid, "falso_verde",
                f"La corrida observada con una sola violación en {sufijo}",
                "Una sola corrida deja de cumplir la cláusula y la medida tiene que ponerse roja con valor 1.", roto))
        if rojo and mid in ARREGLOS:
            arreglado = {**evidencia, "problema": evidencia["problema"] + [
                {"caso": c, "id": "cap", "nivel": nivel, "ruta": "cap/spec.md", "mensaje": aguja}
                for c in sorted(casos) for nivel, aguja in [ARREGLOS[mid]]]}
            imprimir_en(destino / f"{301 + n}-{corto}-cumplido.caso", construido(
                comun, f"{301 + n}-{corto}-cumplido", "verde_correcto",
                "Los mismos hechos observados con el mensaje que la spec pide",
                "Si la CLI emitiera el texto literal de la spec, la medida tiene que quedar verde.", arreglado))
        imprimir_en(destino / f"{201 + n}-{corto}-sin-evidencia.caso", {
            "id": f"{201 + n}-{corto}-sin-evidencia",
            **comun,
            "origen": {"repo": "Segtem/oracle", "commit": "sin-commit"},
            "procedencia": "construida",
            "como_se_detecto": "mutacion",
            "titulo": f"El sensor no emitió {requiere}",
            "etiqueta": "falso_verde",
            "espera": "sin_evidencia",
            "sintoma": f"Sin filas de {requiere} la medida no midió nada y no puede dar verde.",
            "evidencia": {requiere: []},
            "leccion": "Un verde por relación vacía es el falso verde más barato; `requiere` lo cierra.",
        })


# Las tres medidas que la CLI real incumple por un mensaje: el nivel y el texto que la spec pide.
ARREGLOS = {
    "openspec.sin_deltas_advierte_titulos_antes_de_operaciones":
        ("ERROR", "Spec delta files cannot start with titles before the operation headers"),
    "openspec.error_de_estructura_remite_a_agents_md": ("ERROR", "See openspec/AGENTS.md"),
    "openspec.vinetas_avisan_con_el_texto_de_la_spec": ("WARNING", "Scenarios must use '#### Scenario:' headers"),
}


def _primera(filas, **donde):
    return next(f for f in filas if all(f.get(k) == v for k, v in donde.items()))


def _set(fila, **cambios):
    fila.update(cambios)


# Medidas sin `sin` que la CLI cumple y el generador no cubrió: la violación, escrita a mano.
ROMPER = {
    "openspec.el_filtro_no_mezcla_tipos": [
        ("--changes", lambda e: (_set(_primera(e["item"], caso="proyecto_mixto#1"), tipo="spec"), e)[1]),
        ("--specs", lambda e: (_set(_primera(e["item"], caso="proyecto_mixto#2"), tipo="change"), e)[1]),
    ],
    "openspec.pie_trae_dos_a_tres_pasos": [
        ("un pie de una viñeta", lambda e: (_set(e["pie"][0], vinetas=1), e)[1]),
        ("un pie de cuatro viñetas", lambda e: (_set(e["pie"][0], vinetas=4), e)[1]),
    ],
    "openspec.resumen_cuadra": [
        ("totales que no suman", lambda e: (_set(e["resumen"][0], items=e["resumen"][0]["items"] + 1), e)[1]),
        ("sin versión", lambda e: (_set(e["resumen"][0], version="None"), e)[1]),
    ],
}


def _sacar(filas, **donde):
    fila = _primera(filas, **donde)
    filas.remove(fila)


def _texto(e, caso, quitar):
    fila = _primera(e["salida"], caso=caso)
    fila["texto"] = fila["texto"].replace(quitar, "")


def _agregar(rel, **fila):
    return lambda e: (e[rel].append(fila), e)[1]


def _cambiar(rel, donde, **cambios):
    return lambda e: (_set(_primera(e[rel], **donde), **cambios), e)[1]


def _quitar(rel, **donde):
    return lambda e: (_sacar(e[rel], **donde), e)[1]


def _borrar_texto(caso, quitar):
    return lambda e: (_texto(e, caso, quitar), e)[1]


# Una violación por rama de cada disyunción, para que ninguna rama quede sin caso que la decida.
ROMPER |= {
    "openspec.todo_lo_vivo_se_valida": [
        ("--all", _quitar("item", caso="proyecto_mixto#0", id="rota")),
        ("--changes", _quitar("item", caso="proyecto_mixto#1", id="ch")),
        ("--specs", _quitar("item", caso="proyecto_mixto#2", id="cap")),
    ],
    "openspec.cambio_invalido_muestra_el_pie": [
        ("el pie del MODIFIED", _borrar_texto("modified_omite_escenario#1", "Next steps")),
        ("la bandera del cambio sin deltas", _borrar_texto("cambio_sin_deltas#1", "--deltas-only")),
    ],
    "openspec.error_de_estructura_remite_a_agents_md": [
        ("sólo el requisito sin cuerpo", _agregar("problema", caso="spec_sin_purpose#0", id="cap", nivel="ERROR",
                                                  ruta="cap/spec.md", mensaje="See openspec/AGENTS.md")),
    ],
    "openspec.item_directo_detecta_su_tipo": [
        ("la spec", _cambiar("item", {"caso": "spec_valida#0"}, tipo="change")),
        ("el cambio", _cambiar("item", {"caso": "cambio_valido#0"}, tipo="spec")),
    ],
    "openspec.nada_archivado_se_valida": [
        ("el archivado", _agregar("item", caso="proyecto_mixto#0", id="2026-01-01-viejo", tipo="change",
                                  valido=False, tiene_duracion=True)),
    ],
    "openspec.nombre_ambiguo_no_valida": [
        ("--json", _agregar("item", caso="nombre_ambiguo#0", id="dup", tipo="spec", valido=True, tiene_duracion=True)),
        ("la salida humana", _agregar("item", caso="nombre_ambiguo#1", id="dup", tipo="spec", valido=True,
                                      tiene_duracion=True)),
    ],
    "openspec.nombre_no_resuelto_sale_con_1_sin_validar": [
        ("el desconocido", _cambiar("corrida", {"caso": "nombre_desconocido#0"}, codigo=0)),
        ("el ambiguo en JSON", _cambiar("corrida", {"caso": "nombre_ambiguo#0"}, codigo=0)),
        ("el ambiguo en salida humana", _cambiar("corrida", {"caso": "nombre_ambiguo#1"}, codigo=0)),
    ],
    "openspec.sin_argumentos_lista_las_banderas": [
        ("--all", _borrar_texto("sin_argumentos#0", "--all")),
        ("--changes", _borrar_texto("sin_argumentos#1", "--changes")),
        ("--specs", _borrar_texto("sin_argumentos#2", "--specs")),
    ],
    "openspec.sin_palabra_clave_no_falla": [
        ("la spec", _cambiar("corrida", {"caso": "spec_sin_palabra_clave#0"}, codigo=1)),
        ("el delta", _cambiar("corrida", {"caso": "delta_sin_palabra_clave#0"}, codigo=1)),
    ],
    "openspec.tipo_explicito_manda": [
        ("--type change", _cambiar("item", {"caso": "nombre_ambiguo#2"}, tipo="spec")),
        ("--type spec", _cambiar("item", {"caso": "nombre_ambiguo#3"}, tipo="change")),
    ],
}


def construido(comun, cid, etiqueta, titulo, sintoma, evidencia):
    return {
        "id": cid, **comun, "origen": {"repo": "Segtem/oracle", "commit": "sin-commit"},
        "procedencia": "construida", "como_se_detecto": "mutacion", "titulo": titulo,
        "etiqueta": etiqueta, "sintoma": sintoma, "evidencia": evidencia,
        "leccion": "Deriva de la corrida real cambiando sólo lo que decide la cláusula.",
    }


def imprimir_en(ruta: Path, datos: dict):
    ruta.write_text(imprimir(datos), encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:])
