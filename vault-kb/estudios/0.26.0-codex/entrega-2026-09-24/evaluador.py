"""Evaluador independiente de la forma canónica del álgebra 0.8."""

import math

VERSION_ALGEBRA = "0.8"
__all__ = ["VERSION_ALGEBRA", "ErrorDeAlgebra", "evaluar"]


class ErrorDeAlgebra(ValueError):
    """Todo error del álgebra se informa con esta excepción, y con ninguna otra."""


_AGREGADOS = {"contar", "suma", "promedio", "min", "max"}
_COMPARADORES = {"==", "!=", "<", "<=", ">", ">="}
_SEGUN = {"medicion", "contrato", "convencion", "tanteo", "sin_declarar"}
_AMBITOS = {"universal", "del_origen", "sin_declarar"}
_MAX_FILAS = 10000
_MAX_PRODUCTO = 100000
_MAX_PROFUNDIDAD = 100


def _error(mensaje):
    raise ErrorDeAlgebra(mensaje)


def _nombre(valor):
    return isinstance(valor, str) and bool(valor)


def _numero(valor):
    return type(valor) in (int, float) and math.isfinite(valor)


def _escalar(valor):
    return type(valor) in (str, bool) or _numero(valor)


def _forma(nodo, nombre, minimo=None, maximo=None):
    if not isinstance(nodo, list) or not nodo or nodo[0] != nombre:
        _error(f"se esperaba {nombre}")
    if minimo is not None and len(nodo) < minimo or maximo is not None and len(nodo) > maximo:
        _error(f"aridad inválida de {nombre}")


def _expresion(expr, escalares, profundidad=0):
    if profundidad > _MAX_PROFUNDIDAD:
        _error("profundidad de expresión excedida")
    if not isinstance(expr, list):
        if not _escalar(expr):
            _error("literal inválido")
        return
    if not expr or not isinstance(expr[0], str):
        _error("expresión inválida")
    op = expr[0]
    if op == "campo":
        _forma(expr, op, 3, 3)
        if not _nombre(expr[1]) or not _nombre(expr[2]):
            _error("acceso a campo inválido")
    elif op in ("hecho", "col"):
        _forma(expr, op, 2, 2)
        if not _nombre(expr[1]):
            _error("acceso inválido")
    elif op in _COMPARADORES | {"y", "o"}:
        _forma(expr, op, 3, 3)
    elif op == "no":
        _forma(expr, op, 2, 2)
    elif op in escalares and callable(escalares[op]):
        if len(expr) < 2:
            _error("función escalar sin argumentos")
    else:
        _error(f"operador o escalar desconocido: {op}")
    if op not in ("campo", "hecho", "col"):
        for arg in expr[1:]:
            _expresion(arg, escalares, profundidad + 1)


def _referencias(expr, aliases, columnas):
    if not isinstance(expr, list):
        return
    if expr[0] in ("campo", "hecho") and expr[1] not in aliases:
        _error(f"alias no declarado: {expr[1]}")
    if expr[0] == "col" and expr[1] not in columnas:
        _error(f"columna no declarada: {expr[1]}")
    if expr[0] not in ("campo", "hecho", "col"):
        for arg in expr[1:]:
            _referencias(arg, aliases, columnas)


def _compatibles(a, b, orden=False):
    if type(a) is bool or type(b) is bool:
        return type(a) is type(b)
    if _numero(a) and _numero(b):
        return True
    return type(a) is type(b) and (type(a) is str or not orden)


def _comparar(op, a, b):
    if not _compatibles(a, b, op not in ("==", "!=")):
        _error("escalares incompatibles")
    if op in ("==", "!=") and (type(a) is float or type(b) is float):
        _error("igualdad exacta de flotantes")
    try:
        return {"==": lambda: a == b, "!=": lambda: a != b,
                "<": lambda: a < b, "<=": lambda: a <= b,
                ">": lambda: a > b, ">=": lambda: a >= b}[op]()
    except (TypeError, ValueError, OverflowError) as exc:
        raise ErrorDeAlgebra("comparación inválida") from exc


def _evaluar_expr(expr, fila, escalares):
    if not isinstance(expr, list):
        return expr
    op = expr[0]
    if op == "campo":
        if expr[1] not in fila["aliases"] or expr[2] not in fila["aliases"][expr[1]]:
            _error(f"campo ausente: {expr[1]}.{expr[2]}")
        return fila["aliases"][expr[1]][expr[2]]
    if op == "hecho":
        if expr[1] not in fila["aliases"]:
            _error(f"alias ausente: {expr[1]}")
        return fila["aliases"][expr[1]]
    if op == "col":
        if expr[1] not in fila["cols"]:
            _error(f"columna ausente: {expr[1]}")
        return fila["cols"][expr[1]]
    args = [_evaluar_expr(arg, fila, escalares) for arg in expr[1:]]
    if op in _COMPARADORES:
        return _comparar(op, *args)
    if op in ("y", "o", "no"):
        if any(type(arg) is not bool for arg in args):
            _error("operación lógica no booleana")
        return all(args) if op == "y" else any(args) if op == "o" else not args[0]
    try:
        resultado = escalares[op](*args)
    except Exception as exc:
        raise ErrorDeAlgebra(f"falló escalar {op}: {exc}") from exc
    if not _escalar(resultado):
        _error(f"resultado inválido de escalar {op}")
    return resultado


def _agregar(agg, expr, filas, escalares):
    if agg == "contar":
        return len(filas)
    valores = [_evaluar_expr(expr, fila, escalares) for fila in filas]
    if not valores:
        return 0
    if agg in ("suma", "promedio"):
        if any(type(v) is not bool and not _numero(v) for v in valores):
            _error("agregado numérico con valor inválido")
        resultado = (math.fsum(valores) if any(type(v) is float for v in valores)
                     else sum(valores))
        if agg == "promedio":
            resultado /= len(valores)
        if not math.isfinite(resultado):
            _error("agregado no finito")
        return resultado
    if any(not _compatibles(valores[0], v, True) for v in valores[1:]):
        _error("agregado con valores heterogéneos")
    if not (_numero(valores[0]) or type(valores[0]) in (str, bool)):
        _error("agregado con valores no comparables")
    return min(valores) if agg == "min" else max(valores)


def _validar_evidencia(evidencia):
    if not isinstance(evidencia, dict):
        _error("evidencia inválida")
    relaciones = {}
    for nombre, entrada in evidencia.items():
        if not _nombre(nombre) or not isinstance(entrada, list) or len(entrada) > _MAX_FILAS:
            _error("relación inválida o demasiado grande")
        clave = None
        filas = entrada
        if entrada and isinstance(entrada[0], list):
            _forma(entrada[0], "clave", 2, 2)
            clave = entrada[0][1]
            if not isinstance(clave, list) or not clave or len(set(map(str, clave))) != len(clave) or not all(_nombre(c) for c in clave):
                _error("clave inválida")
            filas = entrada[1:]
        vistos = []
        for fila in filas:
            if not isinstance(fila, dict) or not all(_nombre(k) and _escalar(v) for k, v in fila.items()):
                _error("fila inválida")
            if clave is not None:
                if any(c not in fila for c in clave):
                    _error(f"campo ausente en clave {clave}: {fila}")
                identidad = tuple(fila[c] for c in clave)
                if identidad in vistos:
                    _error(f"clave duplicada {clave}: {fila}")
                vistos.append(identidad)
        relaciones[nombre] = filas
    return relaciones


def _validar_fuente(fuente, escalares):
    if not isinstance(fuente, list) or not fuente:
        _error("fuente inválida")
    if fuente[0] == "de":
        _forma(fuente, "de", 3, 3)
        if not _nombre(fuente[1]) or not _nombre(fuente[2]):
            _error("relación o alias inválido")
        return {fuente[2]}
    if fuente[0] == "unir":
        _forma(fuente, "unir", 3, 3)
        a = _validar_fuente(fuente[1], escalares)
        b = _validar_fuente(fuente[2], escalares)
        if a & b:
            _error("alias repetido en unir")
        return a | b
    _error("fuente desconocida")


def _validar_medida(medida, escalares):
    _forma(medida, "medida", 6, 8)
    if not _nombre(medida[1]):
        _error("id inválido")
    tuberia, resumen, umbral = medida[2:5]
    _forma(tuberia, "desde", 2)
    aliases = _validar_fuente(tuberia[1], escalares)
    columnas = set()
    for paso in tuberia[2:]:
        if not isinstance(paso, list) or not paso:
            _error("paso inválido")
        op = paso[0]
        if op == "donde":
            _forma(paso, op, 2, 2)
            _expresion(paso[1], escalares)
            _referencias(paso[1], aliases, columnas)
        elif op == "sin":
            _forma(paso, op, 3, 3)
            nuevo = _validar_fuente(paso[1], escalares)
            if paso[1][0] != "de" or aliases & nuevo:
                _error("derecha o alias inválido en sin")
            _expresion(paso[2], escalares)
            _referencias(paso[2], aliases | nuevo, columnas)
        elif op == "agrupar":
            _forma(paso, op, 3, 3)
            if not isinstance(paso[1], list) or not isinstance(paso[2], list):
                _error("grupo inválido")
            nombres = []
            for clave in paso[1]:
                if not isinstance(clave, list) or len(clave) != 2 or not _nombre(clave[0]):
                    _error("clave de grupo inválida")
                nombres.append(clave[0]); _expresion(clave[1], escalares)
                _referencias(clave[1], aliases, columnas)
            for agregado in paso[2]:
                if not isinstance(agregado, list) or len(agregado) != 3 or not _nombre(agregado[0]) or agregado[1] not in _AGREGADOS:
                    _error("agregado de grupo inválido")
                nombres.append(agregado[0]); _expresion(agregado[2], escalares)
                _referencias(agregado[2], aliases, columnas)
            if len(set(nombres)) != len(nombres):
                _error("columnas de grupo repetidas")
            aliases = set()
            columnas = set(nombres)
        else:
            _error(f"paso desconocido: {op}")
    _forma(resumen, "resumen", 3, 3)
    if resumen[1] not in _AGREGADOS:
        _error("agregado de resumen desconocido")
    _expresion(resumen[2], escalares)
    _referencias(resumen[2], aliases, columnas)
    _forma(umbral, "umbral", 4, 5)
    if umbral[1] not in _COMPARADORES or not _escalar(umbral[2]) or not isinstance(umbral[3], str) or not umbral[3]:
        _error("umbral inválido")
    if len(umbral) == 5 and umbral[4] not in _SEGUN:
        _error("procedencia de umbral inválida")
    extras = medida[5:]
    if extras and isinstance(extras[0], list) and extras[0] and extras[0][0] == "requiere":
        requiere = extras.pop(0)
        _forma(requiere, "requiere", 2)
        nombres = []
        for entrada in requiere[1:]:
            if isinstance(entrada, str):
                nombre = entrada
            else:
                _forma(entrada, "filas", 4, 4)
                nombre = entrada[1]
                if not _nombre(entrada[2]):
                    _error("alias de requiere inválido")
                _expresion(entrada[3], escalares)
                _referencias(entrada[3], {entrada[2]}, set())
            if not _nombre(nombre) or nombre in nombres:
                _error("relación repetida o inválida en requiere")
            nombres.append(nombre)
    else:
        requiere = None
    if len(extras) not in (1, 2):
        _error("alcance inválido")
    _forma(extras[0], "alcance", 2, 2)
    if not isinstance(extras[0][1], str) or not extras[0][1]:
        _error("alcance vacío")
    if len(extras) == 2:
        _forma(extras[1], "ambito", 2, 2)
        if extras[1][1] not in _AMBITOS:
            _error("ámbito inválido")
    return tuberia, resumen, umbral, requiere


def _fuente(fuente, relaciones):
    if fuente[0] == "de":
        if fuente[1] not in relaciones:
            _error(f"relación ausente: {fuente[1]}")
        return [{"aliases": {fuente[2]: fila}, "cols": {}} for fila in relaciones[fuente[1]]]
    a, b = _fuente(fuente[1], relaciones), _fuente(fuente[2], relaciones)
    if len(a) * len(b) > _MAX_PRODUCTO:
        _error("límite de producto excedido")
    return [{"aliases": x["aliases"] | y["aliases"], "cols": {}} for x in a for y in b]


def _testigos(filas):
    return [fila["cols"].copy() if not fila["aliases"] else
            {k: v.copy() for k, v in fila["aliases"].items()} for fila in filas]


def _juzgar(medida, evidencia, escalares):
    if not isinstance(escalares, dict) or not all(_nombre(k) and callable(v) for k, v in escalares.items()):
        _error("registro de escalares inválido")
    tuberia, resumen, umbral, requiere = _validar_medida(medida, escalares)
    relaciones = _validar_evidencia(evidencia)
    falta = False
    ausentes = []
    if requiere:
        for entrada in requiere[1:]:
            nombre = entrada if isinstance(entrada, str) else entrada[1]
            if nombre not in relaciones:
                ausentes.append(nombre)
                continue
            filas = relaciones[nombre]
            if isinstance(entrada, str):
                falta |= not filas
            else:
                coinciden = []
                for fila in filas:
                    valor = _evaluar_expr(entrada[3], {"aliases": {entrada[2]: fila}, "cols": {}}, escalares)
                    if type(valor) is not bool:
                        _error("condición de requiere no booleana")
                    coinciden.append(valor)
                falta |= not any(coinciden)
    if ausentes:
        _error(f"relación requerida ausente: {ausentes[0]}")
    if falta:
        return {"id": medida[1], "valor": "SIN EVIDENCIA", "ok": False, "testigos": []}
    filas = _fuente(tuberia[1], relaciones)
    for paso in tuberia[2:]:
        if paso[0] == "donde":
            nuevas = []
            for fila in filas:
                valor = _evaluar_expr(paso[1], fila, escalares)
                if type(valor) is not bool:
                    _error("predicado no booleano")
                if valor:
                    nuevas.append(fila)
            filas = nuevas
        elif paso[0] == "sin":
            relacion, alias = paso[1][1:]
            if relacion not in relaciones:
                _error(f"relación ausente: {relacion}")
            derecha = relaciones[relacion]
            if len(filas) * len(derecha) > _MAX_PRODUCTO:
                _error("límite de producto excedido")
            nuevas = []
            for fila in filas:
                coincide = False
                for hecho in derecha:
                    extendida = {"aliases": fila["aliases"] | {alias: hecho}, "cols": fila["cols"]}
                    valor = _evaluar_expr(paso[2], extendida, escalares)
                    if type(valor) is not bool:
                        _error("condición de sin no booleana")
                    coincide |= valor
                if not coincide:
                    nuevas.append(fila)
            filas = nuevas
        else:
            grupos = []
            for fila in filas:
                clave = [_evaluar_expr(c[1], fila, escalares) for c in paso[1]]
                grupo = next((g for g in grupos if g[0] == clave), None)
                if grupo is None:
                    grupo = (clave, [])
                    grupos.append(grupo)
                grupo[1].append(fila)
            nuevas = []
            for clave, miembros in grupos:
                cols = {c[0]: valor for c, valor in zip(paso[1], clave)}
                for nombre, agg, expr in paso[2]:
                    cols[nombre] = _agregar(agg, expr, miembros, escalares)
                nuevas.append({"aliases": {}, "cols": cols})
            filas = nuevas
    valor = _agregar(resumen[1], resumen[2], filas, escalares)
    if not _numero(valor):
        _error("el resumen final no produjo un número")
    ok = _comparar(umbral[1], valor, umbral[2])
    return {"id": medida[1], "valor": valor, "ok": ok, "testigos": _testigos(filas)}


def evaluar(medida: list, evidencia: dict, escalares: dict | None = None) -> dict:
    """Evalúa una medida canónica sobre evidencia de relaciones."""
    try:
        return _juzgar(medida, evidencia, {} if escalares is None else escalares)
    except ErrorDeAlgebra:
        raise
    except Exception as exc:
        raise ErrorDeAlgebra(f"evaluación inválida: {exc}") from exc
