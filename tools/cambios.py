"""`oracle cambios --desde <ref>`: lo que un cambio al catálogo afloja, comparado contra git.

Un verificador se debilita sin que nada falle: se sube un umbral, se quita un `requiere`, se borra
el caso que lo ponía rojo. En un diff se ve como una línea más. OpenSpec hace esto con sus deltas —un
MODIFIED que pierde un escenario es un error— y acá se hace sobre las medidas, el corpus y la sombra.

La regla: **aflojar no se prohíbe, se declara**. Un umbral que se afloja reescribiendo su `porque`
es una decisión escrita y sale como aviso; uno que se afloja con el mismo `porque` sale como error,
porque la defensa que queda ya no defiende el número que tiene al lado. Lo mismo con la cota de una
sombra. Quitar un `requiere` es siempre error: vuelve verde lo que no midió nada.

Un agente que no puede aflojar la medida puede aflojar lo que la alimenta (SpecBench, EvilGenie y el
Reward Hacking Benchmark lo documentan): una escalar, una relación, el sensor que emite el hecho.
Eso no se puede juzgar sin correrlo, así que se nombra: qué escalar o relación cambió y qué medidas
la usan, y qué archivo de los `sensores` que declara `oracle.json` se tocó. Dejar de vigilar una
ruta de `sensores` es error: es la forma de que todo lo anterior deje de avisar.

Compara el árbol de trabajo contra `<ref>` (por omisión `HEAD`) y sale con 1 si hay algún error.
"""

from __future__ import annotations

import ast
import json
import subprocess
import tempfile
from pathlib import Path

from nucleo.caso import leer as leer_caso
from nucleo.medida import cargar_catalogo, relaciones_de_medida
from nucleo.relacion import Relacion, cargar_fuente_relacion, rutas_de_relaciones
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables, ProyectoInvalido,
                             _sombra_declarada, escalares_del_proyecto, macros_del_proyecto)

SUPERIORES = ("<", "<=")
INFERIORES = (">", ">=")


def _git(raiz: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(raiz), *args], check=True, capture_output=True, text=True).stdout


def _directorios_de_medidas(proy) -> list[str]:
    extra = ["perfiles/python/catalogos"] if proy.es_el_propio_oracle else []
    return ["catalogos", *extra]


def _extraer(raiz: Path, ref: str, destino: Path, rutas: list[str]) -> None:
    """Copia a `destino` los archivos que `rutas` tenían en `ref`, relativos al proyecto."""
    prefijo = _git(raiz, "rev-parse", "--show-prefix").strip()
    for ruta in rutas:
        # `--full-name`: sin él, git devuelve rutas relativas al directorio actual, y a un proyecto
        # que vive en un subdirectorio del repositorio (el `medidas/` de un consumidor) se le quitaba
        # el prefijo dos veces. Lo encontró la adopción en LyraGASP.
        for nombre in _git(raiz, "ls-tree", "-r", "--name-only", "--full-name", ref, "--", ruta).splitlines():
            relativo = nombre[len(prefijo):]
            salida = destino / relativo
            salida.parent.mkdir(parents=True, exist_ok=True)
            salida.write_bytes(subprocess.run(["git", "-C", str(raiz), "show", f"{ref}:{nombre}"],
                                              check=True, capture_output=True).stdout)


def _medidas(raiz: Path, proy, macros) -> dict:
    dirs = [raiz / d for d in _directorios_de_medidas(proy) if (raiz / d).is_dir()]
    return dict(cargar_catalogo(dirs, macros=macros)) if dirs else {}


def _casos(raiz: Path) -> dict[str, str]:
    corpus = raiz / "corpus"
    if not corpus.is_dir():
        return {}
    casos = {}
    for ruta in sorted(corpus.rglob("*.caso")):
        datos = leer_caso(ruta.read_text(encoding="utf-8"))
        casos[datos["id"]] = datos.get("etiqueta", "")
    return casos


def _sombra(raiz: Path) -> dict:
    ruta = raiz / "oracle.json"
    if not ruta.is_file():
        return {}
    return {e.medida: e for e in _sombra_declarada(json.loads(ruta.read_text(encoding="utf-8")))}


def _sensores(raiz: Path) -> list[str]:
    ruta = raiz / "oracle.json"
    datos = json.loads(ruta.read_text(encoding="utf-8")) if ruta.is_file() else {}
    sensores = datos.get("sensores", [])
    if not isinstance(sensores, list) or not all(isinstance(s, str) and s for s in sensores):
        raise ProyectoInvalido("`sensores` de `oracle.json` debe ser una lista de rutas")
    return sensores


def _escalares(raiz: Path) -> dict[str, str]:
    """Cada escalar declarada con la forma de su código. Si cambia lo que comparten (un ayudante,
    un import, una constante), cambia la forma de todas: no se sigue quién llama a quién."""
    ruta = raiz / "escalares.py"
    if not ruta.is_file():
        return {}
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    propias, comun = {}, []
    for nodo in arbol.body:
        nombres = [d.args[0].value for d in getattr(nodo, "decorator_list", ())
                   if isinstance(d, ast.Call) and getattr(d.func, "id", "") == "escalar"
                   and d.args and isinstance(d.args[0], ast.Constant)]
        if nombres:
            propias.update(dict.fromkeys(nombres, ast.dump(nodo)))
        elif not (isinstance(nodo, ast.Expr) and isinstance(nodo.value, ast.Constant)):
            comun.append(ast.dump(nodo))   # la docstring del módulo no cuenta
    return {n: forma + "".join(comun) for n, forma in propias.items()}


def _relaciones(raiz: Path) -> dict[str, list]:
    directorio = raiz / "relaciones"
    if not directorio.is_dir():
        return {}
    relaciones = {}
    for ruta in rutas_de_relaciones(directorio):
        datos = cargar_fuente_relacion(ruta)
        relaciones[Relacion.de_datos(datos).nombre] = datos
    return relaciones


def _quienes(medidas: dict, usa) -> str:
    ids = sorted(mid for mid, m in medidas.items() if usa(m))
    return f"  (la usan: {', '.join(ids)})" if ids else "  (ninguna medida la usa)"


def comparar_fuentes(escalares_antes: dict, escalares_despues: dict, relaciones_antes: dict,
                     relaciones_despues: dict, medidas: dict, sensores_antes: list[str],
                     sensores_despues: list[str], sensores_tocados: list[str]) -> tuple[list[str], list[str]]:
    """Lo que alimenta a las medidas sin ser una medida: escalares, relaciones y sensores."""
    errores, avisos = [], []
    for nombre in sorted(escalares_antes):
        if escalares_despues.get(nombre, escalares_antes[nombre]) != escalares_antes[nombre]:
            avisos.append(f"escalar cambiada  {nombre}" + _quienes(
                medidas, lambda m: f'"{nombre}"' in json.dumps([m.tuberia, m.resumen])))
    for nombre in sorted(relaciones_antes):
        if relaciones_despues.get(nombre, relaciones_antes[nombre]) != relaciones_antes[nombre]:
            avisos.append(f"relación cambiada  {nombre}" + _quienes(
                medidas, lambda m: nombre in relaciones_de_medida(m)))
    for ruta in sorted(set(sensores_antes) - set(sensores_despues)):
        errores.append(f"sensor que se deja de vigilar  {ruta}")
    avisos.extend(f"sensor cambiado  {ruta}" for ruta in sensores_tocados)
    return errores, avisos


def endurece_o_iguala(op_antes: str, lim_antes, op_despues: str, lim_despues) -> bool:
    """¿El umbral nuevo admite lo mismo o menos que el viejo? Cambiar de sentido nunca endurece."""
    igual_o_estricto = lim_despues == lim_antes and op_despues in (op_antes, "<", ">")
    if op_antes in SUPERIORES and op_despues in SUPERIORES:
        return lim_despues < lim_antes or igual_o_estricto
    if op_antes in INFERIORES and op_despues in INFERIORES:
        return lim_despues > lim_antes or igual_o_estricto
    return (op_antes, lim_antes) == (op_despues, lim_despues)


def comparar(antes: dict, despues: dict, casos_antes: dict, casos_despues: dict,
             sombra_antes: dict, sombra_despues: dict) -> tuple[list[str], list[str]]:
    errores, avisos = [], []
    for mid in sorted(antes):
        a = antes[mid]
        if mid not in despues:
            avisos.append(f"medida borrada  {mid}")
            continue
        d = despues[mid]
        umbral = f"{a.op} {a.limite:g} → {d.op} {d.limite:g}"
        if not endurece_o_iguala(a.op, a.limite, d.op, d.limite):
            if a.porque == d.porque:
                errores.append(f"umbral aflojado sin nueva defensa  {mid}  {umbral}  (el `porque` no cambió)")
            else:
                avisos.append(f"umbral aflojado con nueva defensa  {mid}  {umbral}")
        quitados = sorted({str(r) for r in a.requiere} - {str(r) for r in d.requiere})
        if quitados:
            errores.append(f"requiere quitado  {mid}  {', '.join(quitados)}")
        if a.alcance != d.alcance:
            avisos.append(f"alcance cambiado  {mid}")
    for cid in sorted(casos_antes):
        if cid not in casos_despues:
            avisos.append(f"caso borrado  {cid}")
        elif casos_antes[cid] != casos_despues[cid]:
            avisos.append(f"caso con otra etiqueta  {cid}  {casos_antes[cid]} → {casos_despues[cid]}")
    for mid in sorted(sombra_despues):
        d = sombra_despues[mid]
        if mid not in sombra_antes:
            avisos.append(f"sombra nueva  {mid}")
            continue
        a = sombra_antes[mid]
        if d.cota > a.cota:
            linea = f"cota de sombra subida  {mid}  {a.cota} → {d.cota}"
            if a.porque == d.porque:
                errores.append(f"{linea}  (el `porque` no cambió)")
            else:
                avisos.append(linea)
    return errores, avisos


def main(proy, ref: str = "HEAD", *, confiar: bool = False) -> int:
    # Las medidas de un proyecto pueden usar sus escalares: sin registrarlas, el catálogo no carga.
    try:
        with escalares_del_proyecto(proy, confiar=confiar):
            return _main(proy, ref)
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
        return 1


def _main(proy, ref: str) -> int:
    raiz = proy.raiz
    try:
        _git(raiz, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"✗ «{ref}» no es un commit de git en {raiz}")
        return 1
    macros = macros_del_proyecto(proy)
    with tempfile.TemporaryDirectory() as tmp:
        viejo = Path(tmp)
        _extraer(raiz, ref, viejo, [*_directorios_de_medidas(proy), "corpus", "oracle.json",
                                    "escalares.py", "relaciones"])
        try:
            # ponytail: el ref se expande con las macros de HOY; si usaba una macro del proyecto que
            # ya se borró, no carga y se dice, en vez de comparar contra otra cosa.
            antes = _medidas(viejo, proy, macros)
            casos_antes, sombra_antes = _casos(viejo), _sombra(viejo)
            fuentes_antes = _escalares(viejo), _relaciones(viejo), _sensores(viejo)
        except (ValueError, SyntaxError, ProyectoInvalido) as e:
            print(f"✗ no se pudo leer el catálogo de {ref}: {e}")
            return 1
    try:
        despues, casos_despues, sombra_despues = _medidas(raiz, proy, macros), _casos(raiz), _sombra(raiz)
        escalares, relaciones, sensores = _escalares(raiz), _relaciones(raiz), _sensores(raiz)
    except (ValueError, SyntaxError, ProyectoInvalido) as e:
        print(f"✗ no se pudo leer el catálogo del árbol de trabajo: {e}")
        return 1
    # Lo vigilado es lo que se vigilaba en el ref: sacar una ruta no la esconde de este mismo cambio.
    vigiladas = sorted(set(fuentes_antes[2]) | set(sensores))
    try:
        tocados = _git(raiz, "diff", "--name-only", ref, "--", *vigiladas).splitlines() if vigiladas else []
    except subprocess.CalledProcessError as e:
        print(f"✗ `sensores` de `oracle.json` nombra una ruta que git no puede mirar: {e.stderr.strip()}")
        return 1
    errores, avisos = comparar(antes, despues, casos_antes, casos_despues, sombra_antes, sombra_despues)
    e2, a2 = comparar_fuentes(fuentes_antes[0], escalares, fuentes_antes[1], relaciones, despues,
                              fuentes_antes[2], sensores, tocados)
    errores, avisos = errores + e2, avisos + a2
    print(f"cambios desde {ref}:")
    for linea in errores:
        print(f"✗ {linea}")
    for linea in avisos:
        print(f"· {linea}")
    if not errores and not avisos:
        print("  nada se aflojó")
    print(f"\n{len(errores)} errores · {len(avisos)} avisos")
    return 1 if errores else 0
