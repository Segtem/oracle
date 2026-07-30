"""Sensores del propio marco: hechos sobre los casos y sobre el uso de cada medida.

El norte de oracle es el universo de problemas de **crear una herramienta**, y una parte de ese
universo es la herramienta misma: si el corpus fija las medidas, si alguna quedó sin ejercitar, si un
caso reclama algo que no existe. Eso hasta ahora se decidía con `if`s dentro de `tools/` — o sea que
el veredicto sobre el marco estaba en código imperativo mientras el resto del proyecto exige que los
veredictos sean datos. Es el mismo pecado que un sensor que juzga, un nivel más arriba.

Acá se producen los hechos; el juicio queda en `catalogos/meta/`.

    caso(id, medida, tiene_medida, medida_existe, esperado_ok, dio_ok, explica_el_hueco)
    medida_en_uso(id, casos_que_la_evaluan, mutantes, mutantes_vivos)

## Por qué no hay nulos

Un caso sin medida usable **no tiene veredicto que comparar**. La tentación es poner `null` en
`esperado_ok`/`dio_ok`, y eso choca de frente con una decisión del álgebra: comparar contra un valor
ausente **levanta un error**, porque un `False` silencioso convierte un campo mal escrito en un verde.

Así que en esos casos los dos campos se igualan a propósito: la medida de coincidencia no tiene nada
que decir ahí, y de la falta se ocupa otra medida (`meta.el_caso_reclama_una_medida_que_existe`). Cada
pregunta a la medida que le corresponde, en vez de un nulo que todas tienen que esquivar.

Eso también es el síntoma de un hueco declarado del álgebra: la **ausencia** todavía no se expresa, y
hasta que `agrupar` exista se rodea así.
"""

from __future__ import annotations


def hechos_de_casos(catalogo: dict, casos: list[dict]) -> dict:
    """Un hecho por caso del corpus: qué esperaba, qué dio, y si su medida existe."""
    filas = []
    for c in casos:
        mid = c.get("medida") or ""
        existe = bool(mid) and mid in catalogo
        esperado = c.get("etiqueta") == "verde_correcto"

        if existe:
            dio = catalogo[mid].evaluar(c["evidencia"]).ok
        else:
            # nada que comparar: se igualan y de la falta se ocupa otra medida (ver el docstring)
            dio = esperado

        filas.append({
            "id": c["id"],
            "medida": mid,
            "tiene_medida": bool(mid),
            "medida_existe": existe,
            "esperado_ok": esperado,
            "dio_ok": dio,
            "explica_el_hueco": bool(str(c.get("sin_medida_todavia", "")).strip()),
        })
    return {"caso": filas}


def hechos_de_uso(catalogo: dict, casos: list[dict], mutantes: list[dict] | None = None,
                  evaluadas_aparte: set[str] | None = None,
                  heredadas: set[str] | None = None) -> dict:
    """Un hecho por medida del catálogo: cuántos casos la evalúan y cuántos mutantes le sobreviven.

    `debe_tener_mutantes` declara la política: una medida propia y ordinaria tiene que generar al
    menos uno; una heredada responde ante el corpus de origen, y una evaluada aparte queda fuera de
    esta ronda. Así «cero mutantes» no se confunde con «todos sus mutantes murieron».
    """
    evaluadas_aparte = evaluadas_aparte or set()
    heredadas = heredadas or set()

    # Las medidas de nivel meta no las evalúa ningún caso del corpus: se evalúan sobre el catálogo
    # mismo. Se declaran acá en vez de exceptuarlas, para que «ejercitada» siga significando lo mismo
    # para todas.
    evalua: dict[str, int] = {mid: (1 if mid in evaluadas_aparte else 0)
                              for mid in catalogo}
    for c in casos:
        mid = c.get("medida") or ""
        if mid in evalua:
            evalua[mid] += 1

    total: dict[str, int] = {mid: 0 for mid in catalogo}
    vivos: dict[str, int] = {mid: 0 for mid in catalogo}
    for i, m in enumerate(mutantes or []):
        if not isinstance(m, dict):
            raise ValueError(f"mutante[{i}] tiene que ser un hecho")
        mid = m.get("apunta_a")
        if not isinstance(mid, str) or mid not in total:
            raise ValueError(f"mutante[{i}].apunta_a no identifica una medida del catálogo: {mid!r}")
        if type(m.get("murio")) is not bool:
            raise ValueError(f"mutante[{i}].murio tiene que ser booleano")
        total[mid] += 1
        if not m["murio"]:
            vivos[mid] += 1

    # `es_heredada`: vino del catálogo BASE de oracle, no del proyecto. Sin este campo, apuntar la
    # herramienta a un proyecto ajeno daba falso rojo en «sin ejercitar» para todas las medidas
    # universales — que están fijadas por el corpus de oracle, no por el del proyecto. Un proyecto
    # responde por SUS medidas.
    return {"medida_en_uso": [
        {"id": mid, "casos_que_la_evaluan": evalua[mid], "mutantes": total[mid],
         "mutantes_vivos": vivos[mid], "es_heredada": mid in heredadas,
         "debe_tener_mutantes": mid not in heredadas and mid not in evaluadas_aparte}
        for mid in sorted(catalogo)]}


def hechos_de_modulos(raiz, paquetes, entradas) -> dict:
    """`modulo`, `importa` y `alcanzable` de un árbol de Python.

    Es el sensor del código propio: qué módulos hay, quién importa a quién, y a qué se llega desde las
    entradas. La alcanzabilidad se calcula acá —es un hecho— y no en el álgebra, que no sabe de grafos.

    Un módulo puede tener importadores y estar muerto igual: si su racimo entero no se alcanza desde
    ninguna entrada, nadie lo va a ejecutar nunca. Eso es lo que `modulo_con_consumidor` no puede ver
    y sí ve una medida sobre `alcanzable`.
    """
    import ast
    from pathlib import Path

    from .grafo import cierre

    raiz = Path(raiz)
    modulos, importa = [], []
    for paquete in paquetes:
        for p in sorted((raiz / paquete).rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            nombre = ".".join(p.relative_to(raiz).with_suffix("").parts).removesuffix(".__init__")
            es_test = "test" in p.name or "tests" in p.parts
            fuente = p.read_text(encoding="utf-8")
            arbol = ast.parse(fuente)
            # un `__init__.py` sin sentencias es un marcador de paquete, no un módulo. Es un HECHO,
            # así que va como campo y la medida decide qué hacer con él — el sensor no excluye nada.
            modulos.append({"nombre": nombre, "es_test": es_test,
                            "lineas": len(fuente.splitlines()),
                            "es_paquete_vacio": p.name == "__init__.py" and not arbol.body})
            for n in ast.walk(arbol):
                objetivos = []
                if isinstance(n, ast.Import):
                    objetivos = [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom):
                    if n.level:
                        base = ".".join(nombre.split(".")[:-n.level] or [nombre.split(".")[0]])
                        # `from . import x` no trae `module`: el nombre está en `names`, y sin esto
                        # ese import quedaba invisible y el módulo importado salía «no alcanzable»
                        objetivos = ([f"{base}.{n.module}"] if n.module
                                     else [f"{base}.{a.name}" for a in n.names])
                    elif n.module:
                        objetivos = [n.module]
                for o in objetivos:
                    if o.split(".")[0] in paquetes:
                        importa.append({"a": nombre, "b": o, "es_test": es_test})

    conocidos = {m["nombre"] for m in modulos}
    aristas = [e for e in importa if e["b"] in conocidos]
    return {"modulo": modulos, "importa": aristas,
            "alcanzable": cierre(aristas, [e for e in entradas if e in conocidos])}
