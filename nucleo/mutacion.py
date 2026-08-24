"""Mutación de MEDIDAS — la prueba de si el corpus alcanza para fijarlas.

Si una medida es un dato, mutarla es transformar el dato: no se toca ningún archivo, no hay
`__pycache__` que invalidar y no hay forma de que el resultado dependa de bytecode viejo. Ésa es la
diferencia concreta entre esto y el `sed` a mano que produjo el caso `006` del corpus.

## Qué se está midiendo, exactamente

Para cada caso del corpus que declara una medida, el caso **espera rojo** (es un defecto real). Se
muta la medida y se vuelve a evaluar contra la misma evidencia:

  · si el caso pasa a **verde** ⇒ el mutante **murió**: el caso sí fija ese aspecto de la medida;
  · si el caso **sigue en rojo** ⇒ el mutante **sobrevivió**: el caso NO fija ese aspecto. Se podría
    escribir la medida de otra forma y el corpus no se daría cuenta.

Los sobrevivientes son la lista de lo que el corpus deja libre — y por lo tanto lo que puedo escribir
mal sin que nada me frene. Es el mismo argumento que la mutación de tests, un nivel más arriba.

El denominador se declara en `mutantes`: además de umbral y filtros completos, recorre fuentes,
expresiones, agregados y referencias de campo. La mutación del código Python es otro sensor,
`perfiles.python.mutacion_codigo`; no se mezcla con ésta porque su arnés y sus fallos posibles son
distintos.
"""

from __future__ import annotations

from copy import deepcopy
import math

from .medida import Medida

_INVERSO = {"<=": ">", "<": ">=", ">=": "<", ">": "<=", "==": "!=", "!=": "=="}


def _umbral(datos: list) -> list:
    return datos[4]


def aflojar_umbral(datos: list) -> list | None:
    """Mueve el límite al siguiente valor más permisivo sin imponer una escala universal.

    Los enteros avanzan una unidad y los flotantes un valor representable. A diferencia del antiguo
    centinela `1e12`, el cambio conserva la dirección incluso cuando el dominio trabaja por encima o
    por debajo de esa magnitud.
    """
    d = deepcopy(datos)
    op, limite = _umbral(d)[1], _umbral(d)[2]
    if op in ("==", "!="):
        return None
    if isinstance(limite, bool) or not isinstance(limite, (int, float)):
        return None
    ascendente = op in ("<=", "<")
    direccion = math.inf if ascendente else -math.inf
    nuevo = limite + (1 if ascendente else -1) if isinstance(limite, int) else math.nextafter(
        limite, direccion)
    if isinstance(nuevo, float) and not math.isfinite(nuevo):
        return None
    _umbral(d)[2] = nuevo
    return d


def invertir_comparador(datos: list) -> list | None:
    d = deepcopy(datos)
    _umbral(d)[1] = _INVERSO[_umbral(d)[1]]
    return d


def quitar_filtro(datos: list) -> list | None:
    """Sin `donde`, la medida cuenta la relación entera. Si el caso sigue en rojo, es porque su
    evidencia sólo tiene filas que ofenden — y entonces no está probando que el filtro filtre."""
    d = deepcopy(datos)
    tuberia = [p for p in d[2][1:] if p[0] != "donde"]
    if len(tuberia) == len(d[2]) - 1:
        return None
    d[2] = ["desde", *tuberia]
    return d


def quitar_requiere(datos: list) -> list | None:
    """Sin la precondición, una relación necesaria y vacía vuelve a leerse como un mundo en orden.

    `requiere` no es como `alcance` ni como la defensa del umbral —esos se validan al cargar o se
    juzgan en L2—: éste **cambia el veredicto**, así que tiene que estar en el denominador. Un
    mutador que nadie escribió no puede producir un sobreviviente, y sacar esta línea reabre el
    falso verde de la ausencia sin que nada lo note.
    """
    d = deepcopy(datos)
    if len(d) != 7:
        return None
    return [*d[:5], d[6]]


def negar_filtro(datos: list) -> list | None:
    d = deepcopy(datos)
    hubo = False
    for paso in d[2][2:]:
        if paso[0] == "donde":
            paso[1] = ["no", paso[1]]
            hubo = True
    return d if hubo else None


def _huella(testigos) -> tuple:
    """Forma canónica de los testigos, para comparar informes. Ordenada: el orden de las filas no es
    parte del contrato, pero QUIÉNES son sí."""
    return tuple(sorted(
        tuple(sorted((alias, tuple(sorted(hecho.items()))) for alias, hecho in fila.items()))
        for fila in testigos))


MUTADORES = {
    "aflojar_umbral": aflojar_umbral,
    "invertir_comparador": invertir_comparador,
    "quitar_filtro": quitar_filtro,
    "quitar_requiere": quitar_requiere,
    "negar_filtro": negar_filtro,
}


_AGREGADO_ALTERNO = {
    "max": "min",
    "min": "max",
    "suma": "promedio",
    "promedio": "suma",
}


def _en(datos, ruta: tuple[int, ...]):
    actual = datos
    for indice in ruta:
        actual = actual[indice]
    return actual


def _reemplazar(datos, ruta: tuple[int, ...], valor):
    copia = deepcopy(datos)
    padre = _en(copia, ruta[:-1])
    padre[ruta[-1]] = valor
    return copia


def _ruta(ruta: tuple[int, ...]) -> str:
    return ".".join(map(str, ruta))


def _fuentes(fuente, ruta: tuple[int, ...]):
    if fuente[0] == "de":
        yield ruta, fuente
    elif fuente[0] == "unir":
        yield from _fuentes(fuente[1], (*ruta, 1))
        yield from _fuentes(fuente[2], (*ruta, 2))


def _raices_de_expresion(datos: list):
    for indice, paso in enumerate(datos[2][2:], start=2):
        if paso[0] == "donde":
            yield (2, indice, 1)
        elif paso[0] == "agrupar":
            for posicion in range(len(paso[1])):
                yield (2, indice, 1, posicion, 1)
            for posicion in range(len(paso[2])):
                yield (2, indice, 2, posicion, 2)
    yield (3, 2)


def _nodos_de_expresion(expr, ruta: tuple[int, ...]):
    yield ruta, expr
    if isinstance(expr, list):
        for indice, argumento in enumerate(expr[1:], start=1):
            yield from _nodos_de_expresion(argumento, (*ruta, indice))


def _mutantes_de_fuentes(datos: list):
    fuentes = list(_fuentes(datos[2][1], (2, 1)))
    relaciones = sorted({fuente[1] for _ruta_fuente, fuente in fuentes})
    for ruta_fuente, fuente in fuentes:
        for relacion in relaciones:
            if relacion != fuente[1]:
                ruta_relacion = (*ruta_fuente, 1)
                nombre = f"fuente:{_ruta(ruta_relacion)}:{fuente[1]}→{relacion}"
                yield nombre, _reemplazar(datos, ruta_relacion, relacion)


def _mutantes_de_expresiones(datos: list):
    for raiz in _raices_de_expresion(datos):
        for ruta_nodo, nodo in _nodos_de_expresion(_en(datos, raiz), raiz):
            if isinstance(nodo, bool):
                yield (f"expresion:booleano@{_ruta(ruta_nodo)}",
                       _reemplazar(datos, ruta_nodo, not nodo))
            elif isinstance(nodo, list) and nodo:
                cabeza = nodo[0]
                if cabeza in _INVERSO:
                    yield (f"expresion:comparador@{_ruta(ruta_nodo)}:{cabeza}→{_INVERSO[cabeza]}",
                           _reemplazar(datos, (*ruta_nodo, 0), _INVERSO[cabeza]))
                elif cabeza in ("y", "o"):
                    alterno = "o" if cabeza == "y" else "y"
                    yield (f"expresion:logico@{_ruta(ruta_nodo)}:{cabeza}→{alterno}",
                           _reemplazar(datos, (*ruta_nodo, 0), alterno))
                elif cabeza == "no":
                    yield (f"expresion:quitar_no@{_ruta(ruta_nodo)}",
                           _reemplazar(datos, ruta_nodo, deepcopy(nodo[1])))


def _sitios_de_agregado(datos: list):
    yield (3, 1), (3, 2), datos[3][1]
    for indice, paso in enumerate(datos[2][2:], start=2):
        if paso[0] == "agrupar":
            for posicion, agregado in enumerate(paso[2]):
                yield ((2, indice, 2, posicion, 1),
                       (2, indice, 2, posicion, 2), agregado[1])


def _mutantes_de_agregados(datos: list):
    for ruta_agregado, ruta_expresion, agregado in _sitios_de_agregado(datos):
        if agregado == "contar":
            # La expresión de `contar` no tiene semántica. Para que el mutante no sea el equivalente
            # universal contar→suma(1), lo reemplaza por el agregado nulo suma(0): «no medir».
            mutada = _reemplazar(datos, ruta_agregado, "suma")
            mutada = _reemplazar(mutada, ruta_expresion, 0)
            yield f"agregado:{_ruta(ruta_agregado)}:contar→suma(0)", mutada
        else:
            alterno = _AGREGADO_ALTERNO[agregado]
            yield (f"agregado:{_ruta(ruta_agregado)}:{agregado}→{alterno}",
                   _reemplazar(datos, ruta_agregado, alterno))


def _mutantes_de_campos(datos: list):
    accesos = []
    nombres_por_espacio: dict[tuple, set[str]] = {}
    for raiz in _raices_de_expresion(datos):
        for ruta_nodo, nodo in _nodos_de_expresion(_en(datos, raiz), raiz):
            if not (isinstance(nodo, list) and nodo and nodo[0] in ("campo", "col")):
                continue
            espacio = ("campo", nodo[1]) if nodo[0] == "campo" else ("col",)
            posicion_nombre = 2 if nodo[0] == "campo" else 1
            accesos.append((ruta_nodo, nodo, espacio, posicion_nombre))
            nombres_por_espacio.setdefault(espacio, set()).add(nodo[posicion_nombre])

    # Una columna derivada puede ser una alternativa aunque todavía no aparezca en otro `col`.
    for paso in datos[2]:
        if paso[0] == "agrupar":
            nombres_por_espacio.setdefault(("col",), set()).update(
                nombre for nombre, _expr in paso[1])
            nombres_por_espacio.setdefault(("col",), set()).update(
                agregado[0] for agregado in paso[2])

    for ruta_nodo, nodo, espacio, posicion_nombre in accesos:
        actual = nodo[posicion_nombre]
        for alterno in sorted(nombres_por_espacio[espacio] - {actual}):
            ruta_nombre = (*ruta_nodo, posicion_nombre)
            yield (f"campo:{_ruta(ruta_nombre)}:{actual}→{alterno}",
                   _reemplazar(datos, ruta_nombre, alterno))


def _mutantes_estructurales(datos: list):
    yield from _mutantes_de_fuentes(datos)
    yield from _mutantes_de_expresiones(datos)
    yield from _mutantes_de_agregados(datos)
    yield from _mutantes_de_campos(datos)


def mutantes(datos: list) -> list[tuple[str, list]]:
    """Mutantes aplicables, con un id estable por categoría y ruta dentro de la medida.

    El denominador cubre umbral, filtros completos, fuentes intercambiables, nodos de expresión,
    agregados y referencias de campo. No muta UDF, aridad, defensa ni alcance: esos contratos se
    validan al cargar o se juzgan con medidas meta.
    """
    salida = []
    for nombre, fn in MUTADORES.items():
        mutada = fn(datos)
        if mutada is not None:
            salida.append((nombre, mutada))
    salida.extend(_mutantes_estructurales(datos))
    return salida


def correr(catalogo: dict, casos: list[dict]) -> dict:
    """Devuelve EVIDENCIA (relaciones), no un informe: la salida del sensor se mide con el álgebra.

    Es el punto del diseño — un sensor no juzga, produce hechos.
    """
    # Un mutante es un par (medida, mutador). Muere si ALGÚN caso lo detecta — no si lo detecta cada
    # caso. Es el error de análisis que tuvo la primera versión: `quitar_filtro` no lo puede detectar
    # un caso de defecto (contar sin filtro sigue dando >0), y sí lo detecta un caso verde.
    detecciones: list[dict] = []
    for caso in casos:
        mid = caso.get("medida")
        if not mid or mid not in catalogo:
            continue
        # Las DOS polaridades. Un caso `verde_correcto` espera verde, el resto espera rojo, y un
        # mutante muere cuando invierte lo esperado. Sin los casos verdes, `quitar_filtro` no puede
        # morir nunca: contar sin filtro sólo da verde con la relación vacía.
        esperado_ok = caso.get("etiqueta") == "verde_correcto"
        original = catalogo[mid]
        if original.evaluar(caso["evidencia"]).ok != esperado_ok:
            continue                      # el caso no está en su estado esperado: no fija nada
        base = original.evaluar(caso["evidencia"])
        for nombre, datos in mutantes(original.a_datos()):
            # Cuatro OBSERVACIONES crudas. Cuál cuenta como muerte, y por qué, lo declara y lo
            # defiende `proceso.test_con_mutante_que_lo_mata`: acá no se decide nada.
            try:
                v = Medida.de_datos(datos).evaluar(caso["evidencia"])
                invirtio = v.ok != esperado_ok
                cambio_testigos = _huella(v.testigos) != _huella(base.testigos)
                cambio_valor = v.valor != base.valor
                rechazado = False
            except Exception:             # noqa: BLE001  un mutante inválido no es un hallazgo
                invirtio = cambio_testigos = cambio_valor = False
                rechazado = True
            detecciones.append({
                "mutante": f"{mid}·{nombre}",
                "caso": caso["id"],
                "polaridad": "verde" if esperado_ok else "rojo",
                "invirtio_el_veredicto": invirtio,
                "cambio_los_testigos": cambio_testigos,
                "cambio_el_valor": cambio_valor,
                "rechazado_por_el_algebra": rechazado,
            })

    # El hecho por mutante: CUÁNTAS veces se lo observó de cada manera. Son conteos, no un dictamen.
    #
    # La distinción que los conteos preservan y `murio` aplastaba: un mutante que el álgebra rechaza
    # con una excepción —un campo que no existe en ese alias, una fuente que no casa— no lo
    # discriminó ningún caso; ni siquiera llegó a evaluar. Sumarlo a las muertes conductuales publica
    # una capacidad de detección que el corpus no tiene.
    por_mutante: dict[str, dict] = {}
    for d in detecciones:
        f = por_mutante.setdefault(d["mutante"], {
            "id": d["mutante"],
            "apunta_a": d["mutante"].split("·")[0],
            "cambio": d["mutante"].split("·")[1],
            "detecciones_conductuales": 0,
            "rechazos_del_algebra": 0,
        })
        if d["invirtio_el_veredicto"] or d["cambio_los_testigos"] or d["cambio_el_valor"]:
            f["detecciones_conductuales"] += 1
        if d["rechazado_por_el_algebra"]:
            f["rechazos_del_algebra"] += 1

    return {
        "mutante": list(por_mutante.values()),
        "deteccion": detecciones,
        "corrida_mutacion_medidas": [{
            "id": "mutacion_de_medidas",
            "mutantes": len(por_mutante),
        }],
    }
