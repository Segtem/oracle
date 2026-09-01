"""Sensores del propio marco: hechos sobre los casos y sobre el uso de cada medida.

El norte de oracle es el universo de problemas de **crear una herramienta**, y una parte de ese
universo es la herramienta misma: si el corpus fija las medidas, si alguna quedó sin ejercitar, si un
caso reclama algo que no existe. Eso hasta ahora se decidía con `if`s dentro de `tools/` — o sea que
el veredicto sobre el marco estaba en código imperativo mientras el resto del proyecto exige que los
veredictos sean datos. Es el mismo pecado que un sensor que juzga, un nivel más arriba.

Acá se producen los hechos; el juicio queda en `catalogos/meta/`.

    caso(id, medida, procedencia, tiene_medida, medida_existe, esperado_ok, dio_ok,
         explica_el_hueco, es_heredado, biblioteca)
    medida_en_uso(id, casos_que_la_evaluan, mutantes, mutantes_vivos)
    sombra(medida, declara_desde, declara_porque, dias, dio_ok, existe)

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

from datetime import date


RELACIONES_DEL_LENGUAJE = frozenset({"caso", "medida_en_uso", "sombra",
                                     "relacion_documentada", "verbo_del_cli"})


def hechos_de_documentacion(relaciones, referencia: str) -> dict:
    """Un hecho por relación del lenguaje: si la referencia la nombra.

    La documentación es la única parte del proyecto SIN arnés. El código no puede quedar
    desactualizado sin que un mutante lo diga; la prosa sí, y por eso envejece sola: al 2026-09-01
    diez de diecinueve relaciones —incluidas todas las de L−1 y L−2— no estaban nombradas en la
    especificación, y nada lo había señalado nunca.

    Lo que se mide es la ÚNICA cosa falsable acá: que el nombre aparezca. Si la explicación es
    buena, si está actualizada o si alguien la entiende son preguntas que ninguna medida puede
    contestar, y el `alcance` de la medida que consume estos hechos lo dice.
    """
    # Sin referencia NO se emiten filas, y eso es deliberado. Un consumidor no tiene —ni tiene por
    # qué tener— la especificación de Oracle: el paquete instalado ni siquiera la incluye. Emitir
    # filas ahí pondría en rojo a todo proyecto ajeno por no documentar un lenguaje que no escribió.
    # Con la relación vacía, `requiere` hace que la medida salga SIN EVIDENCIA: no concluye, que es
    # la verdad, en vez de concluir mal.
    if not referencia.strip():
        # NO se emite ni la clave: `medidas_aplicables` elige juezas por las relaciones PRESENTES,
        # así que sin la clave la medida ni se evalúa. Emitirla vacía la haría aplicable y saldría
        # SIN EVIDENCIA, que la aceptación cuenta como falla — un rojo igual, por otro camino.
        return {}
    return {"relacion_documentada": [
        {"relacion": nombre, "nombrada_en_la_referencia": nombre in referencia}
        for nombre in sorted(relaciones)]}


def hechos_de_verbos(verbos_por_sustantivo, ayuda: str) -> dict:
    """Un hecho por verbo que el CLI acepta: si la ayuda lo nombra.

    Un verbo que existe y no está en la ayuda es una función que sólo encuentra quien lea el
    despacho. Al 2026-09-01 había tres —`medida probar`, `caso generar` y `biblioteca nueva`—, y
    el último lo había agregado yo ese mismo día: la ayuda es exactamente el lugar donde una
    novedad se olvida.

    Se compara contra la ayuda que imprime `oracle --help`, no contra la documentación entera: es
    lo primero y muchas veces lo único que alguien lee.
    """
    if not ayuda.strip():
        return {}
    return {"verbo_del_cli": [
        {"sustantivo": sustantivo, "verbo": verbo,
         "nombrado_en_la_ayuda": f"{sustantivo} {verbo}" in ayuda}
        for sustantivo in sorted(verbos_por_sustantivo)
        for verbo in sorted(verbos_por_sustantivo[sustantivo])]}


def hechos_de_sombra(en_sombra, veredictos_ok: dict, catalogo: dict,
                     hoy: date | None = None) -> dict:
    """Un hecho por medida puesta en sombra: qué declara, hace cuánto, y si ya está en verde.

    La sombra apaga la CONSECUENCIA de un rojo, no la medición. Estos hechos existen para que el
    apagado no sea gratis: que una sombra no declare su motivo, o que lleve meses puesta sobre una
    medida que hace rato da verde, son cosas que una medida del catálogo puede atrapar — y las
    atrapa, en `catalogos/meta/`.

    `dias` es -1 cuando `desde` no se declaró o no es una fecha ISO. No es un nulo disfrazado: el
    álgebra levanta error al comparar contra un valor ausente, y de la falta se ocupa
    `meta.toda_sombra_declara_desde_y_porque`, que mira `declara_desde`. Cada pregunta a la medida
    que le corresponde.
    """
    hoy = hoy or date.today()
    filas = []
    for entrada in en_sombra:
        try:
            dias = (hoy - date.fromisoformat(entrada.desde)).days
        except ValueError:
            dias = -1
        filas.append({
            "medida": entrada.medida,
            "declara_desde": bool(entrada.desde.strip()),
            "declara_porque": bool(entrada.porque.strip()),
            "dias": dias,
            # Una sombra sobre una medida que YA da verde no tiene motivo para seguir puesta.
            # `dio_ok` es falso cuando la medida no llegó a evaluarse: no se puede afirmar que
            # esté en verde algo que no corrió.
            "dio_ok": bool(veredictos_ok.get(entrada.medida, False)),
            "existe": entrada.medida in catalogo,
        })
    return {"sombra": filas}


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
            "procedencia": c.get("procedencia", "sin_declarar"),
            "tiene_medida": bool(mid),
            "medida_existe": existe,
            "esperado_ok": esperado,
            "dio_ok": dio,
            "es_hueco_abierto": c.get("estado_sin_medida") == "abierto",
            "explica_el_hueco": bool(str(c.get("sin_medida_todavia", "")).strip()),
            "es_heredado": bool(c.get("es_heredado", False)),
            "biblioteca": c.get("biblioteca", ""),
        })
    return {"caso": filas}


def hechos_de_uso(catalogo: dict, casos: list[dict], mutantes: list[dict] | None = None,
                  evaluadas_aparte: set[str] | None = None,
                  heredadas: set[str] | None = None) -> dict:
    """Un hecho por medida del catálogo: cuántos casos la evalúan y cuántos mutantes le sobreviven.

    `debe_tener_mutantes` declara la política: una medida propia y ordinaria tiene que generar al
    menos uno; una heredada responde ante el corpus de origen. Así «cero mutantes» no se confunde con
    «todos sus mutantes murieron».

    **Estar evaluada aparte NO exime de tener mutantes**, y confundir las dos cosas era un agujero
    del denominador. `evaluadas_aparte` responde «¿alguien la ejercita?» —y sí: las medidas meta las
    evalúa `tools/aceptacion.py` sobre el catálogo mismo—. Que deba tener mutantes es otra pregunta,
    y su respuesta es comprobable: **la tiene que tener si algún caso del corpus la declara**, porque
    ahí la mutación puede correr y significa algo. Mientras las dos iban juntas, escribir una medida
    con prefijo `meta.` la sacaba del denominador aunque tuviera casos, y una clase entera de medidas
    quedaba sin mutar por una convención de nombre en vez de por una propiedad verificable.
    """
    evaluadas_aparte = evaluadas_aparte or set()
    heredadas = heredadas or set()

    # Las medidas de nivel meta no las evalúa ningún caso del corpus: se evalúan sobre el catálogo
    # mismo. Se declaran acá en vez de exceptuarlas, para que «ejercitada» siga significando lo mismo
    # para todas.
    por_casos: dict[str, int] = {mid: 0 for mid in catalogo}
    for c in casos:
        mid = c.get("medida") or ""
        if mid in por_casos:
            por_casos[mid] += 1
    evalua = {mid: por_casos[mid] + (1 if mid in evaluadas_aparte else 0) for mid in catalogo}

    total: dict[str, int] = {mid: 0 for mid in catalogo}
    vivos: dict[str, int] = {mid: 0 for mid in catalogo}
    for i, m in enumerate(mutantes or []):
        if not isinstance(m, dict):
            raise ValueError(f"mutante[{i}] tiene que ser un hecho")
        mid = m.get("apunta_a")
        if not isinstance(mid, str) or mid not in total:
            raise ValueError(f"mutante[{i}].apunta_a no identifica una medida del catálogo: {mid!r}")
        conteos = (m.get("detecciones_conductuales"), m.get("rechazos_del_algebra"))
        if any(type(c) is not int or c < 0 for c in conteos):
            raise ValueError(
                f"mutante[{i}] tiene que traer `detecciones_conductuales` y "
                "`rechazos_del_algebra` como enteros no negativos")
        total[mid] += 1
        # Cero observaciones de cualquier tipo: nadie lo notó. Es aritmética, no la política de qué
        # cuenta como muerte — eso lo declara `proceso.test_con_mutante_que_lo_mata`, con defensa.
        if not any(conteos):
            vivos[mid] += 1

    # `es_heredada`: vino del catálogo BASE de oracle, no del proyecto. Sin este campo, apuntar la
    # herramienta a un proyecto ajeno daba falso rojo en «sin ejercitar» para todas las medidas
    # universales — que están fijadas por el corpus de oracle, no por el del proyecto. Un proyecto
    # responde por SUS medidas.
    return {"medida_en_uso": [
        {"id": mid, "casos_que_la_evaluan": evalua[mid], "mutantes": total[mid],
         "mutantes_vivos": vivos[mid], "es_heredada": mid in heredadas,
         "debe_tener_mutantes": mid not in heredadas and por_casos[mid] > 0}
        for mid in sorted(catalogo)]}
