"""Escribir una medida sin pedirle permiso a nadie.

    python tools/medida.py --relaciones            qué hechos hay para medir, y sus campos
    python tools/medida.py --escalares             qué funciones de dominio se pueden usar
    python tools/medida.py --nueva dominio.nombre  crea el archivo con la forma puesta
    python tools/medida.py --listar                lista las medidas con umbral, alcance y fijación
    python tools/medida.py <archivo.json>          la revisa y la corre contra el corpus
    python tools/medida.py --expandir <archivo>     ve en qué forma canónica se convierte la macro

Para ejecutar `escalares.py` de otro proyecto hace falta `--confiar-escalares`. Ayuda,
`--relaciones`, `--nueva`, `--listar` y el inventario base de `--escalares` nunca ejecutan ese archivo.

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
from nucleo.algebra import AGREGADOS, COMPARADORES, ESCALARES, separar_clave  # noqa: E402
from nucleo.caso import CasoMalDeclarado, cargar_casos  # noqa: E402
from nucleo.fixtures import cargar_fixtures, evidencias as evidencias_fixture  # noqa: E402
from nucleo.medida import (Medida, MedidaMalDeclarada, cargar_catalogo,  # noqa: E402
                           cargar_fuente_medida)
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables, ProyectoInvalido,
                             catalogos_a_cargar, confiar_escalares, escalares_del_proyecto,
                             macros_del_proyecto, presentar_ruta, problemas_estructura,
                             ruta_de_medida_nueva, sin_banderas_comunes)  # noqa: E402
from tools.sesion import resolver_cli  # noqa: E402

# La plantilla usa la macro `ninguno`, que es la forma del 80% de las medidas. `--expandir` muestra
# en qué se convierte; y si el caso no encaja, la forma canónica sigue siendo válida.
# En superficie infija, no en JSON. La plantilla es lo primero que ve alguien que escribe su primera
# medida, y hasta hoy le decía «tu trabajo es anidar corchetes». Se guarda como `.oracle`, que el
# catálogo carga igual que un `.json`.
PLANTILLA = """\
ninguno {mid}:
    de RELACION x
    donde x.CAMPO == false
    umbral <= 0 porque "POR QUE ese numero y no otro. Un umbral sin defensa es una metrica esperando a volverse objetivo."
    alcance "QUE NO VE esta medida. Obligatorio: un verde que no dice lo que no mira se lee como «esta bien»."
"""


def _evidencias(proy, *, comprobar_frescura: bool) -> list[tuple[str, dict]]:
    """(de dónde salió, evidencia) — del corpus y de los fixtures diferenciales."""
    salida = []
    for c in cargar_casos(proy.corpus):
        salida.append((c["id"], c["evidencia"]))
    rutas = sorted(proy.diferencial.glob("*.json"))
    if comprobar_frescura:
        catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
        fixtures, fallas = cargar_fixtures(rutas, raiz=proy.raiz, catalogo=catalogo)
    else:
        fixtures, fallas = cargar_fixtures(rutas)
    if fallas:
        raise ValueError("fixtures diferenciales inválidos o vencidos:\n  · " + "\n  · ".join(fallas))
    for fixture in fixtures:
        salida.extend(evidencias_fixture(fixture))
    return salida


def relaciones(proy) -> int:
    """Los hechos disponibles, DERIVADOS de la evidencia que existe. No es una lista a mano."""
    campos: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
    dondes: dict[str, set] = defaultdict(set)
    try:
        disponibles = _evidencias(proy, comprobar_frescura=False)
    except (OSError, ValueError, json.JSONDecodeError, CasoMalDeclarado) as e:
        print(f"no se pudo inventariar la evidencia: {e}")
        return 1
    for origen, ev in disponibles:
        for rel, filas in ev.items():
            dondes[rel].add(origen.split("/")[0])
            _clave, hechos = separar_clave(filas)
            for fila in hechos:
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


def escalares(proy, *, externas_omitidas: bool = False) -> int:
    print("FUNCIONES ESCALARES declaradas (el mecanismo de UDF):\n")
    for nombre in sorted(ESCALARES):
        fn = ESCALARES[nombre]
        unidad = f" → {fn.unidad}" if getattr(fn, "unidad", "") else ""
        maximo = getattr(fn, "aridad_max", "?")
        aridad = (f"{fn.aridad_min}+" if maximo is None else
                  str(fn.aridad_min) if fn.aridad_min == maximo else f"{fn.aridad_min}..{maximo}")
        doc = (fn.__doc__ or "").strip().split("\n")[0]
        print(f"  {nombre}/{aridad}{unidad}\n      {doc}")
    print(f"\nCOMPARADORES: {' '.join(COMPARADORES)}")
    print(f"LÓGICOS: y  o  no")
    print(f"AGREGADOS: {' '.join(sorted(AGREGADOS))}")
    print("ACCESORES: [\"campo\", alias, nombre] · [\"hecho\", alias] · [\"col\", nombre]")
    print("OPERADORES: de · donde · unir · resumen   (con y agrupar todavía no tienen usuario)")
    if externas_omitidas:
        print(f"\n⚠ {proy.raiz / 'escalares.py'} no se ejecutó. Para incluir sus UDF: "
              "`--confiar-escalares`.")
    return 0


def nueva(proy, mid: str) -> int:
    try:
        destino = ruta_de_medida_nueva(proy, mid)
    except ProyectoInvalido as e:
        print(f"id inválido: {e}")
        return 1
    if destino.exists():
        print(f"ya existe: {presentar_ruta(proy, destino)}")
        return 1
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(PLANTILLA.format(mid=mid), encoding="utf-8")
    print(f"creada: {presentar_ruta(proy, destino)}\n")
    print("Reemplazá RELACION, CAMPO y los dos textos en MAYÚSCULAS. Después:")
    print(f"  oracle revisar {presentar_ruta(proy, destino)}")
    return 0


def expandir_archivo(ruta: Path, macros=None) -> int:
    datos = cargar_fuente_medida(ruta, macros=macros)
    from nucleo.macro import es_macro
    if not es_macro(datos, macros):
        print(f"«{datos[1] if len(datos) > 1 else '?'}» ya está en forma canónica.")
    m = Medida.de_datos(datos, macros=macros)
    print(json.dumps(m.a_datos(), ensure_ascii=False, indent=1))
    return 0


def revisar(proy, ruta: Path) -> int:
    macros = macros_del_proyecto(proy)
    try:
        datos = cargar_fuente_medida(ruta, macros=macros)
    except MedidaMalDeclarada as e:
        print(f"✗ {e}")
        return 1
    try:
        medida = Medida.de_datos(datos, macros=macros)
    except MedidaMalDeclarada as e:
        print(f"✗ {e}")
        return 1

    forma = datos[0] if datos[0] in macros else "canónica"
    print(f"✓ bien declarada: {medida.id}   (forma: {forma})")
    print(f"    umbral   {medida.op} {medida.limite}")
    print(f"    porque   {medida.porque}")
    print(f"    alcance  {medida.alcance}\n")

    # correrla contra toda la evidencia que hay, para que no se estrene a ciegas
    rojos = verdes = errores = 0
    primer_error = ""
    ejemplos = []
    try:
        disponibles = _evidencias(proy, comprobar_frescura=True)
    except (OSError, ValueError, json.JSONDecodeError, CasoMalDeclarado) as e:
        print(f"✗ no se pudo cargar la evidencia: {e}")
        return 1
    for origen, ev in disponibles:
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


def _evaluadas_aparte(proy, catalogo) -> set[str]:
    """Las medidas que ejercita el ARNÉS y no un caso que las nombre.

    Son las que corren sobre el catálogo mismo —el nivel L2—: `aceptacion.py` las evalúa contra los
    hechos del propio marco. Que ningún caso las nombre no las deja sin ejercitar, y decir lo
    contrario en una vista de auditoría es un falso rojo.
    """
    # Una medida se ejercita aparte si TODAS las relaciones que consume las produce el propio marco:
    # es decir, si su evidencia no sale del mundo sino del catálogo. Es la misma pregunta que se hace
    # `nucleo/marco.py`, sin duplicar su política.
    from nucleo.medida import relaciones_de_medida, relaciones_del_lenguaje_declaradas
    # Sin `try`, y a propósito. Este `except Exception: return set()` estaba acá y se llevaba puesta
    # justo la corrección que esta vista existe para tener: si la pregunta «¿qué relaciones son del
    # lenguaje?» falla, el conjunto vacío hace que las seis medidas L2 salgan «⚠ SIN FIJAR» —seis
    # falsos rojos, en la herramienta de auditoría, con la causa real escondida—. Que reviente con
    # el motivo es peor de leer y mucho mejor de arreglar.
    del_lenguaje = set(relaciones_del_lenguaje_declaradas())
    aparte = set()
    for m in catalogo.values():
        usadas = set(relaciones_de_medida(m))
        if usadas and usadas <= del_lenguaje:
            aparte.add(m.id)
    return aparte


def listar(proy, argv: list[str] | None = None) -> int:
    estructura = problemas_estructura(proy, ("catalogos",))
    if estructura:
        print("PROYECTO INVÁLIDO — " + "; ".join(estructura))
        return 1

    argv = argv or []
    confiar = confiar_escalares(argv)
    # El listado carga lo MISMO que se carga al medir. Antes cargaba las raíces completas sólo
    # cuando Oracle se juzgaba a sí mismo, y a un consumidor le mostraba nada más sus propias
    # medidas: en un consumidor medido decía «41 medidas» y ni una `meta.*`, mientras al medir se
    # cargaban tres raíces. No veía las medidas universales que lo estaban juzgando —incluida la que
    # lo tenía en rojo—. La herramienta de auditoría le ocultaba al auditado quién lo audita.
    directorios = catalogos_a_cargar(proy)

    try:
        with escalares_del_proyecto(proy, confiar=confiar):
            catalogo = cargar_catalogo(directorios, macros=macros_del_proyecto(proy))
            del_proyecto = cargar_catalogo([proy.catalogos], macros=macros_del_proyecto(proy))
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
        return 1
    except Exception as e:
        print(f"CATÁLOGO INVÁLIDO — {e}")
        return 1

    if not catalogo:
        print(f"CATÁLOGO: 0 medidas en {presentar_ruta(proy, proy.catalogos)}")
        return 0

    conteo: defaultdict[str, int] = defaultdict(int)
    if proy.corpus.is_dir():
        try:
            for c in cargar_casos(proy.corpus):
                mid = c.get("medida")
                if mid:
                    conteo[mid] += 1
        except Exception:
            pass

    # «Sin fijar» NO es «ningún caso la nombra». Oracle ya distingue las dos cosas y esta vista
    # inventaba una tercera, más pobre: reportaba como SIN FIJAR a las seis medidas meta que juzgan
    # al catálogo mismo —incluida `meta.toda_medida_esta_fijada`, que pasa en verde—. Eran seis
    # falsos rojos en la herramienta que existe justamente para auditar.
    #
    # La noción buena está en `nucleo/marco.py`: una medida puede estar **evaluada aparte** —el arnés
    # la ejercita sobre el catálogo, no un caso que la nombre— y eso cuenta como ejercicio. Se usa
    # esa, no una copia.
    aparte = _evaluadas_aparte(proy, catalogo)
    # Un proyecto responde por SUS medidas. Las heredadas —el catálogo base y el del perfil— las
    # fija Oracle en su propio corpus; marcarlas «sin fijar» acá sería pedirle al consumidor que
    # escriba casos para medidas que no escribió. Se muestran, porque lo juzgan, pero aparte.
    ids_heredados = set(catalogo) - set(del_proyecto)
    propias = {mid: m for mid, m in catalogo.items() if mid in del_proyecto}
    fijadas = [m for m in propias.values() if conteo[m.id] > 0 or m.id in aparte]
    sin_fijar = [m for m in propias.values() if conteo[m.id] == 0 and m.id not in aparte]

    n_medidas = len(propias)
    txt_medidas = "1 medida" if n_medidas == 1 else f"{n_medidas} medidas"
    if not sin_fijar:
        print(f"CATÁLOGO ({txt_medidas} · todas fijadas):\n")
    else:
        txt_fijadas = "1 fijada" if len(fijadas) == 1 else f"{len(fijadas)} fijadas"
        txt_sin_fijar = "1 sin fijar" if len(sin_fijar) == 1 else f"{len(sin_fijar)} sin fijar"
        print(f"CATÁLOGO ({txt_medidas} · {txt_fijadas} · {txt_sin_fijar}):\n")

    for mid in sorted(propias):
        m = propias[mid]
        n = conteo[mid]
        if n > 0:
            fijacion = f"{n} caso" if n == 1 else f"{n} casos"
        elif mid in aparte:
            fijacion = "0 casos · la ejercita el arnés sobre el catálogo"
        else:
            fijacion = "0 casos  ⚠ SIN FIJAR — ninguna evidencia la pone a prueba"
        print(f"  {m.id}")
        print(f"    umbral:   {m.op} {m.limite}")
        print(f"    fijación: {fijacion}")
        alcance_lineas = (m.alcance or "").strip().splitlines()
        if not alcance_lineas:
            print("    alcance:  (no declarado)")
        elif len(alcance_lineas) == 1:
            print(f"    alcance:  {alcance_lineas[0]}")
        else:
            print(f"    alcance:  {alcance_lineas[0]}")
            for l in alcance_lineas[1:]:
                print(f"              {l}")
        print()

    if ids_heredados:
        n = len(ids_heredados)
        txt = "1 medida heredada" if n == 1 else f"{n} medidas heredadas"
        print(f"{txt.upper()} — no salen de tu catálogo, pero te juzgan:\n")
        for mid in sorted(ids_heredados):
            print(f"  {mid}")
        print()
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    args = sin_banderas_comunes(argv)
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    proy = resolver_cli(argv)
    if proy is None:
        return 1
    requeridos = (("catalogos",) if args[0] in ("--nueva", "--escalares", "--expandir", "--listar", "listar")
                  else ("catalogos", "corpus", "diferencial"))
    estructura = problemas_estructura(proy, requeridos)
    if estructura:
        print("PROYECTO INVÁLIDO — " + "; ".join(estructura))
        return 1
    if args[0] in ("--listar", "listar"):
        return listar(proy, argv)
    if args[0] == "--relaciones":
        return relaciones(proy)
    if args[0] == "--escalares":
        externas = not proy.es_el_propio_oracle and (proy.raiz / "escalares.py").exists()
        if externas and not confiar_escalares(argv):
            return escalares(proy, externas_omitidas=True)
        try:
            with escalares_del_proyecto(proy, confiar=confiar_escalares(argv)):
                return escalares(proy)
        except (EscalaresNoConfiables, EscalaresInvalidas) as e:
            print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
            return 1
    if args[0] == "--expandir":
        if len(args) < 2:
            print("falta el archivo: --expandir <archivo.json>")
            return 1
        entrada = Path(args[1])
        accion = lambda: expandir_archivo(
            entrada if entrada.exists() else proy.raiz / entrada,
            macros_del_proyecto(proy))
    elif args[0] == "--nueva":
        if len(args) < 2:
            print("falta el id: --nueva dominio.nombre")
            return 1
        return nueva(proy, args[1])
    else:
        ruta = Path(args[0])
        if not ruta.exists():
            ruta = proy.raiz / args[0]
        if not ruta.exists():
            print(f"no existe: {args[0]}")
            return 1
        accion = lambda: revisar(proy, ruta)
    try:
        with escalares_del_proyecto(proy, confiar=confiar_escalares(argv)):
            return accion()
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
