"""`oracle cambios --desde <ref>`: lo que un cambio al catálogo afloja, comparado contra git.

Un verificador se debilita sin que nada falle: se sube un umbral, se quita un `requiere`, se borra
el caso que lo ponía rojo. En un diff se ve como una línea más. OpenSpec hace esto con sus deltas —un
MODIFIED que pierde un escenario es un error— y acá se hace sobre las medidas, el corpus y la sombra.

La regla: **aflojar no se prohíbe, se declara**. Un umbral que se afloja reescribiendo su `porque`
es una decisión escrita y sale como aviso; uno que se afloja con el mismo `porque` sale como error,
porque la defensa que queda ya no defiende el número que tiene al lado. Lo mismo con la cota de una
sombra. Quitar un `requiere` es siempre error: vuelve verde lo que no midió nada.

Compara el árbol de trabajo contra `<ref>` (por omisión `HEAD`) y sale con 1 si hay algún error.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from nucleo.caso import leer as leer_caso
from nucleo.medida import cargar_catalogo
from nucleo.proyecto import ProyectoInvalido, _sombra_declarada, macros_del_proyecto

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
        for nombre in _git(raiz, "ls-tree", "-r", "--name-only", ref, "--", ruta).splitlines():
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


def main(proy, ref: str = "HEAD") -> int:
    raiz = proy.raiz
    try:
        _git(raiz, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"✗ «{ref}» no es un commit de git en {raiz}")
        return 1
    macros = macros_del_proyecto(proy)
    with tempfile.TemporaryDirectory() as tmp:
        viejo = Path(tmp)
        _extraer(raiz, ref, viejo, [*_directorios_de_medidas(proy), "corpus", "oracle.json"])
        try:
            # ponytail: el ref se expande con las macros de HOY; si usaba una macro del proyecto que
            # ya se borró, no carga y se dice, en vez de comparar contra otra cosa.
            antes = _medidas(viejo, proy, macros)
            casos_antes, sombra_antes = _casos(viejo), _sombra(viejo)
        except (ValueError, ProyectoInvalido) as e:
            print(f"✗ no se pudo leer el catálogo de {ref}: {e}")
            return 1
    errores, avisos = comparar(antes, _medidas(raiz, proy, macros), casos_antes, _casos(raiz),
                               sombra_antes, _sombra(raiz))
    print(f"cambios desde {ref}:")
    for linea in errores:
        print(f"✗ {linea}")
    for linea in avisos:
        print(f"· {linea}")
    if not errores and not avisos:
        print("  nada se aflojó")
    print(f"\n{len(errores)} errores · {len(avisos)} avisos")
    return 1 if errores else 0
