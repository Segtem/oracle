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

Lo que **no** hace todavía: mutar el código Python del núcleo. Eso hace falta igual —tres de los once
casos del corpus salieron de ahí— y necesita el arnés con caché frío. Se hace cuando exista, y hasta
entonces esa mutación se corre a mano.
"""

from __future__ import annotations

from copy import deepcopy

from .medida import Medida

GRANDE = 1e12

_INVERSO = {"<=": ">", "<": ">=", ">=": "<", ">": "<=", "==": "!=", "!=": "=="}


def _umbral(datos: list) -> list:
    return datos[4]


def aflojar_umbral(datos: list) -> list | None:
    """El umbral pasa a ser imposible de violar. Si el caso sigue en rojo, el número no importa."""
    d = deepcopy(datos)
    op = _umbral(d)[1]
    if op in ("==", "!="):
        return None
    _umbral(d)[2] = GRANDE if op in ("<=", "<") else -GRANDE
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


def negar_filtro(datos: list) -> list | None:
    d = deepcopy(datos)
    hubo = False
    for paso in d[2][1:]:
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
    "negar_filtro": negar_filtro,
}


def mutantes(datos: list) -> list[tuple[str, list]]:
    """[(nombre del mutador, medida mutada)] — sólo los aplicables a esta medida."""
    salida = []
    for nombre, fn in MUTADORES.items():
        mutada = fn(datos)
        if mutada is not None:
            salida.append((nombre, mutada))
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
            try:
                v = Medida.de_datos(datos).evaluar(caso["evidencia"])
                if v.ok != esperado_ok:
                    murio, como = True, "invirtio_el_veredicto"
                elif _huella(v.testigos) != _huella(base.testigos):
                    # El informe también es contrato: los testigos son lo que una persona LEE para
                    # actuar. En el patrón «donde tol → max → umbral tol» quitar el filtro no puede
                    # cambiar el veredicto (es un mutante equivalente en el veredicto), y sí cambia
                    # los testigos. Mirando sólo `ok` esa mutación era invisible.
                    murio, como = True, "cambio_los_testigos"
                else:
                    murio, como = False, "sin_efecto"
            except Exception as e:        # noqa: BLE001  un mutante inválido no es un hallazgo
                murio, como = True, f"error:{type(e).__name__}"
            detecciones.append({
                "mutante": f"{mid}·{nombre}",
                "caso": caso["id"],
                "polaridad": "verde" if esperado_ok else "rojo",
                "invirtio": murio,
                "como": como,
            })

    # el hecho que juzga la medida: un mutante y si algún caso lo agarró
    por_mutante: dict[str, dict] = {}
    for d in detecciones:
        f = por_mutante.setdefault(d["mutante"], {
            "id": d["mutante"],
            "apunta_a": d["mutante"].split("·")[0],
            "cambio": d["mutante"].split("·")[1],
            "murio": False,
            "casos_que_lo_detectan": 0,
        })
        if d["invirtio"]:
            f["murio"] = True
            f["casos_que_lo_detectan"] += 1

    return {
        "mutante": list(por_mutante.values()),
        "deteccion": detecciones,
        "corrida_mutacion": [{
            "id": "mutacion_de_medidas",
            "mutantes": len(por_mutante),
            # verdadero por construcción: no se toca ningún archivo, así que no hay .pyc que rancie
            "bytecode_frio": True,
            "resultado_confiable": True,
        }],
    }
