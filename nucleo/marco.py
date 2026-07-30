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
                  evaluadas_aparte: set[str] | None = None) -> dict:
    """Un hecho por medida del catálogo: cuántos casos la evalúan y cuántos mutantes le sobreviven.

    `mutantes` son las filas que produce `nucleo.mutacion`; sin ellas, la cuenta de sobrevivientes
    queda en cero y `meta.toda_medida_esta_fijada` no puede decir nada — por eso el informe aclara
    cuándo se corrió sin mutación.
    """
    # Las medidas de nivel meta no las evalúa ningún caso del corpus: se evalúan sobre el catálogo
    # mismo. Se declaran acá en vez de exceptuarlas, para que «ejercitada» siga significando lo mismo
    # para todas.
    evalua: dict[str, int] = {mid: (1 if mid in (evaluadas_aparte or set()) else 0)
                              for mid in catalogo}
    for c in casos:
        mid = c.get("medida") or ""
        if mid in evalua:
            evalua[mid] += 1

    total: dict[str, int] = {mid: 0 for mid in catalogo}
    vivos: dict[str, int] = {mid: 0 for mid in catalogo}
    for m in (mutantes or []):
        mid = m.get("apunta_a", "")
        if mid in total:
            total[mid] += 1
            if not m.get("murio", True):
                vivos[mid] += 1

    return {"medida_en_uso": [
        {"id": mid, "casos_que_la_evaluan": evalua[mid], "mutantes": total[mid],
         "mutantes_vivos": vivos[mid]}
        for mid in sorted(catalogo)]}
