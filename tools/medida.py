"""Escribir una medida sin pedirle permiso a nadie.

    python tools/medida.py --relaciones            qué hechos hay para medir, y sus campos
    python tools/medida.py --escalares             qué funciones de dominio se pueden usar
    python tools/medida.py --nueva dominio.nombre  crea el archivo con la forma puesta
    python tools/medida.py <archivo.json>          la revisa y la corre contra el corpus

Existe porque sin esto el lenguaje tiene dueño. Todo el argumento de este repositorio es que quien
ve un defecto pueda escribir la regla que lo atrapa; si para eso hay que escribir s-expresiones en
JSON a mano y adivinar qué relaciones existen, el único que puede hacerlo es quien escribió el
evaluador — y ahí volvemos al problema del principio.

`--relaciones` no es una lista mantenida a mano: sale de la evidencia que hay en el corpus y en los
fixtures. Si aparece un hecho nuevo, aparece acá solo.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos  # noqa: F401,E402
from nucleo.algebra import AGREGADOS, COMPARADORES, ESCALARES  # noqa: E402
from nucleo.medida import Medida, MedidaMalDeclarada, cargar_catalogo  # noqa: E402

PLANTILLA = """\
["medida", "{mid}",
  ["desde", ["de", "RELACION", "x"],
            ["donde", ["==", ["campo", "x", "CAMPO"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0,
   "POR QUE ese numero y no otro. Un umbral sin defensa es una metrica esperando a volverse objetivo."],
  ["alcance",
   "QUE NO VE esta medida. Obligatorio: un verde que no dice lo que no mira se lee como «esta bien»."]]
"""


def _evidencias() -> list[tuple[str, dict]]:
    """(de dónde salió, evidencia) — del corpus y de los fixtures diferenciales."""
    salida = []
    for p in sorted((RAIZ / "corpus").rglob("*.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        salida.append((c["id"], c["evidencia"]))
    for p in sorted((RAIZ / "diferencial").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        for mid, casos in d["grupos"].items():
            for i, caso in enumerate(casos):
                salida.append((f"{p.stem}/{mid}[{i}]", caso["evidencia"]))
    return salida


def relaciones() -> int:
    """Los hechos disponibles, DERIVADOS de la evidencia que existe. No es una lista a mano."""
    campos: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
    dondes: dict[str, set] = defaultdict(set)
    for origen, ev in _evidencias():
        for rel, filas in ev.items():
            dondes[rel].add(origen.split("/")[0])
            for fila in filas:
                for k, v in fila.items():
                    campos[rel][k].add(type(v).__name__)

    print("RELACIONES que se pueden medir hoy:\n")
    for rel in sorted(campos):
        print(f"  {rel}")
        for campo, tipos in sorted(campos[rel].items()):
            print(f"      {campo:<28} {'/'.join(sorted(tipos))}")
        print(f"      · aparece en: {', '.join(sorted(dondes[rel])[:3])}\n")
    print("Un hecho nuevo se agrega desde su SENSOR, no acá: el sensor produce, el álgebra juzga.")
    return 0


def escalares() -> int:
    print("FUNCIONES ESCALARES declaradas (el mecanismo de UDF):\n")
    for nombre in sorted(ESCALARES):
        fn = ESCALARES[nombre]
        unidad = f" → {fn.unidad}" if getattr(fn, "unidad", "") else ""
        doc = (fn.__doc__ or "").strip().split("\n")[0]
        print(f"  {nombre}{unidad}\n      {doc}")
    print(f"\nCOMPARADORES: {' '.join(COMPARADORES)}")
    print(f"LÓGICOS: y  o  no")
    print(f"AGREGADOS: {' '.join(sorted(AGREGADOS))}")
    print("ACCESORES: [\"campo\", alias, nombre] · [\"hecho\", alias] · [\"col\", nombre]")
    print("OPERADORES: de · donde · unir · resumen   (con y agrupar todavía no tienen usuario)")
    return 0


def nueva(mid: str) -> int:
    if "." not in mid:
        print(f"el id va «dominio.nombre» (p. ej. `colocacion.{mid}`), para que se agrupe solo")
        return 1
    dominio = mid.split(".")[0]
    destino = RAIZ / "catalogos" / dominio / f"{mid}.json"
    if destino.exists():
        print(f"ya existe: {destino}")
        return 1
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(PLANTILLA.format(mid=mid), encoding="utf-8")
    print(f"creada: {destino}\n")
    print("Reemplazá RELACION, CAMPO y los dos textos en MAYÚSCULAS. Después:")
    print(f"  python tools/medida.py {destino.relative_to(RAIZ)}")
    return 0


def revisar(ruta: Path) -> int:
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"✗ JSON inválido: {e}")
        return 1
    try:
        medida = Medida.de_datos(datos)
    except MedidaMalDeclarada as e:
        print(f"✗ {e}")
        return 1

    print(f"✓ bien declarada: {medida.id}")
    print(f"    umbral   {medida.op} {medida.limite}")
    print(f"    porque   {medida.porque}")
    print(f"    alcance  {medida.alcance}\n")

    # correrla contra toda la evidencia que hay, para que no se estrene a ciegas
    rojos = verdes = errores = 0
    primer_error = ""
    ejemplos = []
    for origen, ev in _evidencias():
        try:
            v = medida.evaluar(ev)
        except Exception as e:  # noqa: BLE001
            errores += 1
            primer_error = primer_error or f"{origen}: {type(e).__name__}: {e}"
            continue
        if v.ok:
            verdes += 1
        else:
            rojos += 1
            if len(ejemplos) < 2:
                ejemplos.append((origen, v))

    print(f"contra la evidencia que hay: {verdes} verde · {rojos} rojo · {errores} error")
    if errores:
        print(f"    ⚠ el primero: {primer_error}")
        print("    (suele ser un campo mal escrito: mirá `--relaciones`)")
    for origen, v in ejemplos:
        print(f"\n  se pone roja con «{origen}»:")
        print("   ", v.linea())

    if rojos == 0:
        print("\n⚠ nunca se pone roja. Una medida que no puede fallar no mide nada — hace falta")
        print("  evidencia donde el defecto exista. Agregá un caso al corpus con esa evidencia.")
        return 1
    if verdes == 0:
        print("\n⚠ nunca se pone verde. Probablemente la condición esté invertida: el `donde` tiene")
        print("  que seleccionar lo que OFENDE, no lo que está bien.")
        return 1

    print("\n✓ discrimina: hay evidencia que la pone roja y evidencia que la pone verde.")
    print("  Para que quede fijada, agregá al corpus un caso de cada polaridad.")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if args[0] == "--relaciones":
        return relaciones()
    if args[0] == "--escalares":
        return escalares()
    if args[0] == "--nueva":
        if len(args) < 2:
            print("falta el id: --nueva dominio.nombre")
            return 1
        return nueva(args[1])
    ruta = Path(args[0])
    if not ruta.exists():
        ruta = RAIZ / args[0]
    if not ruta.exists():
        print(f"no existe: {args[0]}")
        return 1
    return revisar(ruta)


if __name__ == "__main__":
    sys.exit(main())
