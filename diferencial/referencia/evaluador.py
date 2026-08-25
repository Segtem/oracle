from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Callable


class ErrorDeAlgebra(ValueError):
    """Todo error del algebra publica se informa con esta excepcion."""


Scalar = bool | int | float | str
Row = dict[str, Any]


_AGREGADOS = {"max", "min", "suma", "promedio", "contar"}
_COMPARADORES = {"==", "!=", "<", "<=", ">", ">="}
_SIN_EVIDENCIA = "SIN EVIDENCIA"

# Contra que version de la especificacion se escribio esta implementacion. El arnes del diferencial
# la compara con la que declara el nucleo (nucleo/version.py) y falla cerrado si no coinciden: una
# extension del lenguaje que este evaluador no conoce no debe publicar "0 desacuerdos".
VERSION_ALGEBRA = "0.3"


@dataclass(frozen=True)
class LimitesAlgebra:
    filas_por_relacion: int = 100_000
    filas_materializadas: int = 1_000_000
    profundidad_expr: int = 100

    def __post_init__(self) -> None:
        for nombre, valor in (
            ("filas_por_relacion", self.filas_por_relacion),
            ("filas_materializadas", self.filas_materializadas),
            ("profundidad_expr", self.profundidad_expr),
        ):
            if not isinstance(valor, int) or isinstance(valor, bool) or valor < 1:
                raise ErrorDeAlgebra(f"{nombre} debe ser un entero positivo")


_LIMITES = LimitesAlgebra()


def evaluar(medida: list, evidencia: dict, escalares: dict | None = None) -> dict:
    """
    Evalua una medida del algebra descripta en ESPECIFICACION.md.

    La unica API publica es esta funcion y ErrorDeAlgebra.
    """

    escalares = {} if escalares is None else escalares
    _validar_escalares(escalares)
    medida_id, desde, resumen, umbral, requiere, alcance = _parsear_medida(medida)
    _ = alcance
    evidencia = _normalizar_evidencia(evidencia, _LIMITES)

    if _sin_evidencia_requerida(requiere, evidencia):
        return {
            "id": medida_id,
            "valor": _SIN_EVIDENCIA,
            "ok": False,
            "testigos": [],
        }

    filas, testigos = _evaluar_desde(desde, evidencia, escalares, _LIMITES)

    _, agregado, expr_resumen = resumen
    valor = _agregar(filas, agregado, expr_resumen, escalares, _LIMITES)

    _, op_umbral, valor_umbral, _porque = umbral
    valor_umbral = _validar_escalar(valor_umbral, "valor de umbral")
    ok = _comparar(op_umbral, valor, valor_umbral)

    return {
        "id": medida_id,
        "valor": valor,
        "ok": ok,
        "testigos": _copiar_filas(testigos),
    }


def _parsear_medida(medida: Any) -> tuple[str, list, list, list, list[str], list]:
    if not isinstance(medida, list) or len(medida) not in {6, 7}:
        raise ErrorDeAlgebra("una medida debe tener seis o siete elementos")
    if medida[0] != "medida":
        raise ErrorDeAlgebra("la medida debe empezar con 'medida'")
    medida_id = medida[1]
    if not isinstance(medida_id, str):
        raise ErrorDeAlgebra("el id de medida debe ser texto")

    desde, resumen, umbral = medida[2], medida[3], medida[4]
    if len(medida) == 6:
        requiere: list[str] = []
        alcance = medida[5]
    else:
        requiere = _parsear_requiere(medida[5])
        alcance = medida[6]
    if not _es_lista_con_tag(desde, "desde") or len(desde) < 2:
        raise ErrorDeAlgebra("seccion desde invalida")
    if not _es_lista_con_tag(resumen, "resumen") or len(resumen) != 3:
        raise ErrorDeAlgebra("seccion resumen invalida")
    if resumen[1] not in _AGREGADOS:
        raise ErrorDeAlgebra(f"agregado desconocido: {resumen[1]}")
    if not _es_lista_con_tag(umbral, "umbral") or len(umbral) != 4:
        raise ErrorDeAlgebra("seccion umbral invalida")
    if umbral[1] not in _COMPARADORES:
        raise ErrorDeAlgebra(f"comparador desconocido: {umbral[1]}")
    _validar_escalar(umbral[2], "valor de umbral")
    if not isinstance(umbral[3], str):
        raise ErrorDeAlgebra("la defensa del umbral debe ser texto")
    if not _es_lista_con_tag(alcance, "alcance") or len(alcance) != 2:
        raise ErrorDeAlgebra("seccion alcance invalida")
    if not isinstance(alcance[1], str):
        raise ErrorDeAlgebra("el alcance debe ser texto")
    return medida_id, desde, resumen, umbral, requiere, alcance


def _parsear_requiere(requiere: Any) -> list[str]:
    if not _es_lista_con_tag(requiere, "requiere") or len(requiere) < 2:
        raise ErrorDeAlgebra("seccion requiere invalida")
    relaciones: list[str] = []
    for nombre in requiere[1:]:
        if not isinstance(nombre, str) or nombre == "":
            raise ErrorDeAlgebra("requiere espera nombres de relacion no vacios")
        relaciones.append(nombre)
    return relaciones


def _sin_evidencia_requerida(
    requiere: list[str], evidencia: dict[str, list[dict[str, Scalar]]]
) -> bool:
    return any(not evidencia.get(nombre) for nombre in requiere)


def _normalizar_evidencia(
    evidencia: Any, limites: LimitesAlgebra
) -> dict[str, list[dict[str, Scalar]]]:
    if not isinstance(evidencia, dict):
        raise ErrorDeAlgebra("la evidencia debe ser un diccionario")

    normalizada: dict[str, list[dict[str, Scalar]]] = {}
    for nombre, relacion in evidencia.items():
        if not isinstance(nombre, str) or nombre == "":
            raise ErrorDeAlgebra("los nombres de relacion deben ser texto no vacio")
        normalizada[nombre] = _normalizar_relacion(nombre, relacion, limites)
    return normalizada


def _normalizar_relacion(
    nombre: str, relacion: Any, limites: LimitesAlgebra
) -> list[dict[str, Scalar]]:
    if not isinstance(relacion, list):
        raise ErrorDeAlgebra(f"la relacion {nombre} debe ser una lista")

    clave, comienzo_hechos = _extraer_clave(nombre, relacion)
    hechos_brutos = relacion[comienzo_hechos:]
    if len(hechos_brutos) > limites.filas_por_relacion:
        raise ErrorDeAlgebra(f"la relacion {nombre} supera el limite de filas")

    hechos: list[dict[str, Scalar]] = []
    for indice, hecho in enumerate(hechos_brutos, start=comienzo_hechos):
        if not isinstance(hecho, dict):
            raise ErrorDeAlgebra(f"la relacion {nombre} contiene un hecho no dict en fila {indice}")
        hecho_copiado: dict[str, Scalar] = {}
        for campo, valor in hecho.items():
            if not isinstance(campo, str):
                raise ErrorDeAlgebra("los nombres de campo deben ser texto")
            hecho_copiado[campo] = _validar_escalar(valor, f"campo {campo}")
        hechos.append(hecho_copiado)

    if clave is not None:
        _validar_clave_unica(nombre, clave, hechos, comienzo_hechos)
    return hechos


def _extraer_clave(nombre: str, relacion: list) -> tuple[list[str] | None, int]:
    if not relacion or not _es_lista_con_tag(relacion[0], "clave"):
        return None, 0
    nodo = relacion[0]
    if len(nodo) != 2 or not isinstance(nodo[1], list):
        raise ErrorDeAlgebra(f"clave invalida en relacion {nombre}")
    campos: list[str] = []
    vistos: set[str] = set()
    for campo in nodo[1]:
        if not isinstance(campo, str) or campo == "":
            raise ErrorDeAlgebra(f"clave invalida en relacion {nombre}")
        if campo in vistos:
            raise ErrorDeAlgebra(f"campo duplicado en clave de relacion {nombre}: {campo}")
        vistos.add(campo)
        campos.append(campo)
    if not campos:
        raise ErrorDeAlgebra(f"clave vacia en relacion {nombre}")
    return campos, 1


def _validar_clave_unica(
    nombre: str, campos: list[str], hechos: list[dict[str, Scalar]], comienzo_hechos: int
) -> None:
    vistos: dict[tuple[tuple[type, Scalar], ...], int] = {}
    clave_texto = ", ".join(campos)
    for offset, hecho in enumerate(hechos):
        indice = comienzo_hechos + offset
        valores: list[tuple[type, Scalar]] = []
        for campo in campos:
            if campo not in hecho:
                raise ErrorDeAlgebra(
                    f"campo de clave ausente en relacion {nombre} ({clave_texto}) fila {indice}: {campo}"
                )
            valores.append((type(hecho[campo]), hecho[campo]))
        valor_clave = tuple(valores)
        if valor_clave in vistos:
            raise ErrorDeAlgebra(
                f"clave duplicada en relacion {nombre} ({clave_texto}) fila {indice}; "
                f"primera fila {vistos[valor_clave]}"
            )
        vistos[valor_clave] = indice


def _evaluar_desde(
    desde: list,
    evidencia: dict[str, list[dict[str, Scalar]]],
    escalares: dict[str, Callable[..., Any]],
    limites: LimitesAlgebra,
) -> tuple[list[Row], list[Row]]:
    filas = _evaluar_relacion(desde[1], evidencia, escalares, limites)
    ultimos_testigos: list[Row] | None = None

    for paso in desde[2:]:
        if not isinstance(paso, list) or not paso:
            raise ErrorDeAlgebra("paso de tuberia invalido")
        operador = paso[0]
        if operador == "donde":
            filas = _aplicar_donde(filas, paso, escalares, limites)
            ultimos_testigos = _copiar_filas(filas)
        elif operador == "agrupar":
            filas = _aplicar_agrupar(filas, paso, escalares, limites)
        elif operador in {"de", "unir", "resumen"}:
            raise ErrorDeAlgebra(f"{operador} no es un paso valido de desde")
        else:
            raise ErrorDeAlgebra(f"operador desconocido: {operador}")

    if ultimos_testigos is None:
        ultimos_testigos = _copiar_filas(filas)
    return filas, ultimos_testigos


def _evaluar_relacion(
    expr: Any,
    evidencia: dict[str, list[dict[str, Scalar]]],
    escalares: dict[str, Callable[..., Any]],
    limites: LimitesAlgebra,
) -> list[Row]:
    if not isinstance(expr, list) or not expr:
        raise ErrorDeAlgebra("relacion invalida")

    operador = expr[0]
    if operador == "de":
        if len(expr) != 3:
            raise ErrorDeAlgebra("de espera relacion y alias")
        return _relacion_de(expr[1], expr[2], evidencia)
    if operador == "unir":
        if len(expr) != 3:
            raise ErrorDeAlgebra("unir espera dos relaciones")
        izquierda = _evaluar_relacion(expr[1], evidencia, escalares, limites)
        derecha = _evaluar_relacion(expr[2], evidencia, escalares, limites)
        return _unir(izquierda, derecha, limites)
    if operador == "desde":
        filas, _testigos = _evaluar_desde(expr, evidencia, escalares, limites)
        return filas
    if operador in {"donde", "agrupar"}:
        raise ErrorDeAlgebra(f"{operador} solo puede aparecer como paso de desde")
    if operador == "resumen":
        raise ErrorDeAlgebra("resumen no produce una relacion en desde")
    raise ErrorDeAlgebra(f"operador desconocido: {operador}")


def _relacion_de(
    nombre: Any, alias: Any, evidencia: dict[str, list[dict[str, Scalar]]]
) -> list[Row]:
    if not isinstance(nombre, str) or not isinstance(alias, str):
        raise ErrorDeAlgebra("de espera nombres de texto")
    if alias == "":
        raise ErrorDeAlgebra("el alias no puede ser vacio")
    if nombre not in evidencia:
        raise ErrorDeAlgebra(f"relacion ausente: {nombre}")
    relacion = evidencia[nombre]

    filas: list[Row] = []
    for hecho in relacion:
        filas.append({alias: dict(hecho)})
    return filas


def _unir(izquierda: list[Row], derecha: list[Row], limites: LimitesAlgebra) -> list[Row]:
    if len(izquierda) * len(derecha) > limites.filas_materializadas:
        raise ErrorDeAlgebra("unir supera el limite de filas materializadas")
    filas: list[Row] = []
    for fila_izq in izquierda:
        for fila_der in derecha:
            choque = set(fila_izq).intersection(fila_der)
            if choque:
                nombres = ", ".join(sorted(choque))
                raise ErrorDeAlgebra(f"alias o columna duplicada en unir: {nombres}")
            combinada: Row = {}
            combinada.update(_copiar_fila(fila_izq))
            combinada.update(_copiar_fila(fila_der))
            filas.append(combinada)
    return filas


def _aplicar_donde(
    filas: list[Row],
    paso: list,
    escalares: dict[str, Callable[..., Any]],
    limites: LimitesAlgebra,
) -> list[Row]:
    if len(paso) != 2:
        raise ErrorDeAlgebra("donde espera un predicado")
    predicado = paso[1]
    filtradas: list[Row] = []
    for fila in filas:
        valor = _evaluar_expr(predicado, fila, escalares, limites)
        if not isinstance(valor, bool):
            raise ErrorDeAlgebra("donde espera un predicado booleano")
        if valor:
            filtradas.append(_copiar_fila(fila))
    return filtradas


def _aplicar_agrupar(
    filas: list[Row],
    paso: list,
    escalares: dict[str, Callable[..., Any]],
    limites: LimitesAlgebra,
) -> list[Row]:
    if len(paso) != 3:
        raise ErrorDeAlgebra("agrupar espera claves y agregados")
    claves = _parsear_claves(paso[1])
    agregados = _parsear_agregados_grupo(paso[2])

    grupos: dict[tuple[tuple[type, Scalar], ...], list[Row]] = {}
    valores_por_grupo: dict[tuple[tuple[type, Scalar], ...], list[Scalar]] = {}
    orden: list[tuple[tuple[type, Scalar], ...]] = []

    for fila in filas:
        valores_clave: list[Scalar] = []
        for _nombre, expr in claves:
            valores_clave.append(_validar_escalar(_evaluar_expr(expr, fila, escalares, limites), "clave"))
        clave = tuple((type(valor), valor) for valor in valores_clave)
        if clave not in grupos:
            grupos[clave] = []
            valores_por_grupo[clave] = valores_clave
            orden.append(clave)
        grupos[clave].append(_copiar_fila(fila))

    salida: list[Row] = []
    for clave in orden:
        fila_salida: Row = {}
        for (nombre, _expr), valor in zip(claves, valores_por_grupo[clave]):
            if nombre in fila_salida:
                raise ErrorDeAlgebra(f"columna duplicada en agrupar: {nombre}")
            fila_salida[nombre] = valor
        for nombre, agregado, expr in agregados:
            if nombre in fila_salida:
                raise ErrorDeAlgebra(f"columna duplicada en agrupar: {nombre}")
            fila_salida[nombre] = _agregar(grupos[clave], agregado, expr, escalares, limites)
        salida.append(fila_salida)
    return salida


def _parsear_claves(claves: Any) -> list[tuple[str, Any]]:
    if not isinstance(claves, list):
        raise ErrorDeAlgebra("las claves de agrupar deben ser una lista")
    resultado: list[tuple[str, Any]] = []
    for clave in claves:
        if not isinstance(clave, list) or len(clave) != 2:
            raise ErrorDeAlgebra("cada clave de agrupar debe ser [nombre, expr]")
        nombre = clave[0]
        if not isinstance(nombre, str) or nombre == "":
            raise ErrorDeAlgebra("el nombre de clave debe ser texto no vacio")
        resultado.append((nombre, clave[1]))
    return resultado


def _parsear_agregados_grupo(agregados: Any) -> list[tuple[str, str, Any]]:
    if _parece_agregado_grupo(agregados):
        candidatos = [agregados]
    elif isinstance(agregados, list):
        candidatos = agregados
    else:
        raise ErrorDeAlgebra("los agregados de agrupar deben ser una lista")

    resultado: list[tuple[str, str, Any]] = []
    for agregado in candidatos:
        if not _parece_agregado_grupo(agregado):
            raise ErrorDeAlgebra("cada agregado debe ser [nombre, agg, expr]")
        nombre, agg, expr = agregado
        if not isinstance(nombre, str) or nombre == "":
            raise ErrorDeAlgebra("el nombre de agregado debe ser texto no vacio")
        if agg not in _AGREGADOS:
            raise ErrorDeAlgebra(f"agregado desconocido: {agg}")
        resultado.append((nombre, agg, expr))
    return resultado


def _parece_agregado_grupo(valor: Any) -> bool:
    return isinstance(valor, list) and len(valor) == 3 and isinstance(valor[1], str)


def _agregar(
    filas: list[Row],
    agregado: str,
    expr: Any,
    escalares: dict[str, Callable[..., Any]],
    limites: LimitesAlgebra,
) -> Scalar:
    if agregado not in _AGREGADOS:
        raise ErrorDeAlgebra(f"agregado desconocido: {agregado}")
    if agregado == "contar":
        return len(filas)
    if not filas:
        return 0

    valores = [_evaluar_expr(expr, fila, escalares, limites) for fila in filas]
    if agregado == "suma":
        return _sumar(valores)
    if agregado == "promedio":
        return _promediar(valores)
    if agregado in {"min", "max"}:
        return _min_max(valores, agregado)
    raise ErrorDeAlgebra(f"agregado desconocido: {agregado}")


def _sumar(valores: list[Any]) -> Scalar:
    total: int | float = 0
    for valor in valores:
        if isinstance(valor, bool):
            total += int(valor)
        elif _es_numero_no_bool(valor):
            total += valor
        else:
            raise ErrorDeAlgebra("suma espera numeros finitos o booleanos")
    return _validar_escalar(total, "resultado de suma")


def _promediar(valores: list[Any]) -> Scalar:
    total = _sumar(valores)
    return _validar_escalar(total / len(valores), "resultado de promedio")


def _min_max(valores: list[Any], agregado: str) -> Scalar:
    primer_tipo = _tipo_escalar_comparable(valores[0])
    for valor in valores:
        if _tipo_escalar_comparable(valor) is not primer_tipo:
            raise ErrorDeAlgebra("min/max exige escalares homogeneos")
    try:
        resultado = min(valores) if agregado == "min" else max(valores)
    except TypeError as exc:
        raise ErrorDeAlgebra("min/max exige valores comparables") from exc
    return _validar_escalar(resultado, f"resultado de {agregado}")


def _evaluar_expr(
    expr: Any,
    fila: Row,
    escalares: dict[str, Callable[..., Any]],
    limites: LimitesAlgebra,
    profundidad: int = 0,
) -> Any:
    if profundidad > limites.profundidad_expr:
        raise ErrorDeAlgebra("expresion supera el limite de profundidad")
    if not isinstance(expr, list):
        return _validar_escalar(expr, "literal")
    if not expr:
        raise ErrorDeAlgebra("lista vacia en posicion de expresion")

    cabeza = expr[0]
    if cabeza == "campo":
        return _expr_campo(expr, fila)
    if cabeza == "hecho":
        return _expr_hecho(expr, fila)
    if cabeza == "col":
        return _expr_col(expr, fila)
    if cabeza in _COMPARADORES:
        if len(expr) != 3:
            raise ErrorDeAlgebra(f"{cabeza} espera dos operandos")
        return _comparar(
            cabeza,
            _evaluar_expr(expr[1], fila, escalares, limites, profundidad + 1),
            _evaluar_expr(expr[2], fila, escalares, limites, profundidad + 1),
        )
    if cabeza == "y":
        if len(expr) < 3:
            raise ErrorDeAlgebra("y espera al menos dos operandos")
        valores = [_evaluar_expr(arg, fila, escalares, limites, profundidad + 1) for arg in expr[1:]]
        _validar_booleanos(valores, "y")
        return all(valores)
    if cabeza == "o":
        if len(expr) < 3:
            raise ErrorDeAlgebra("o espera al menos dos operandos")
        valores = [_evaluar_expr(arg, fila, escalares, limites, profundidad + 1) for arg in expr[1:]]
        _validar_booleanos(valores, "o")
        return any(valores)
    if cabeza == "no":
        if len(expr) != 2:
            raise ErrorDeAlgebra("no espera un operando")
        valor = _evaluar_expr(expr[1], fila, escalares, limites, profundidad + 1)
        if not isinstance(valor, bool):
            raise ErrorDeAlgebra("no espera un booleano")
        return not valor
    if isinstance(cabeza, str) and cabeza in escalares:
        argumentos = [_evaluar_expr(arg, fila, escalares, limites, profundidad + 1) for arg in expr[1:]]
        try:
            resultado = escalares[cabeza](*argumentos)
        except Exception as exc:  # noqa: BLE001 - se normaliza la API publica
            raise ErrorDeAlgebra(f"fallo la funcion escalar {cabeza}") from exc
        return _validar_escalar(resultado, f"resultado de {cabeza}")
    if isinstance(cabeza, str):
        raise ErrorDeAlgebra(f"operador o funcion escalar desconocida: {cabeza}")
    raise ErrorDeAlgebra("literal no escalar en posicion de expresion")


def _expr_campo(expr: list, fila: Row) -> Scalar:
    if len(expr) != 3:
        raise ErrorDeAlgebra("campo espera alias y nombre")
    alias, nombre = expr[1], expr[2]
    if not isinstance(alias, str) or not isinstance(nombre, str):
        raise ErrorDeAlgebra("campo espera textos")
    if alias not in fila:
        raise ErrorDeAlgebra(f"alias ausente: {alias}")
    hecho = fila[alias]
    if not isinstance(hecho, dict):
        raise ErrorDeAlgebra(f"{alias} no es un hecho")
    if nombre not in hecho:
        raise ErrorDeAlgebra(f"campo ausente: {alias}.{nombre}")
    return _validar_escalar(hecho[nombre], f"campo {alias}.{nombre}")


def _expr_hecho(expr: list, fila: Row) -> dict[str, Scalar]:
    if len(expr) != 2:
        raise ErrorDeAlgebra("hecho espera alias")
    alias = expr[1]
    if not isinstance(alias, str):
        raise ErrorDeAlgebra("hecho espera texto")
    if alias not in fila:
        raise ErrorDeAlgebra(f"alias ausente: {alias}")
    hecho = fila[alias]
    if not isinstance(hecho, dict):
        raise ErrorDeAlgebra(f"{alias} no es un hecho")
    return dict(hecho)


def _expr_col(expr: list, fila: Row) -> Scalar:
    if len(expr) != 2:
        raise ErrorDeAlgebra("col espera nombre")
    nombre = expr[1]
    if not isinstance(nombre, str):
        raise ErrorDeAlgebra("col espera texto")
    if nombre not in fila:
        raise ErrorDeAlgebra(f"columna ausente: {nombre}")
    valor = fila[nombre]
    if isinstance(valor, dict):
        raise ErrorDeAlgebra(f"{nombre} no es una columna derivada")
    return _validar_escalar(valor, f"columna {nombre}")


def _comparar(op: str, izquierda: Any, derecha: Any) -> bool:
    if op not in _COMPARADORES:
        raise ErrorDeAlgebra(f"comparador desconocido: {op}")
    izquierda = _validar_escalar(izquierda, "operando izquierdo")
    derecha = _validar_escalar(derecha, "operando derecho")

    if op == "==" and isinstance(izquierda, float) and isinstance(derecha, float):
        raise ErrorDeAlgebra("la igualdad exacta entre flotantes esta prohibida")

    if op in {"==", "!="}:
        _validar_tipos_igualdad(izquierda, derecha)
        resultado = izquierda == derecha
        return resultado if op == "==" else not resultado

    _validar_tipos_orden(izquierda, derecha)
    if op == "<":
        return izquierda < derecha
    if op == "<=":
        return izquierda <= derecha
    if op == ">":
        return izquierda > derecha
    if op == ">=":
        return izquierda >= derecha
    raise ErrorDeAlgebra(f"comparador desconocido: {op}")


def _validar_tipos_igualdad(izquierda: Scalar, derecha: Scalar) -> None:
    if isinstance(izquierda, bool) or isinstance(derecha, bool):
        if not isinstance(izquierda, bool) or not isinstance(derecha, bool):
            raise ErrorDeAlgebra("igualdad entre tipos incompatibles")
        return
    if _es_numero_no_bool(izquierda) and _es_numero_no_bool(derecha):
        return
    if type(izquierda) is type(derecha):
        return
    raise ErrorDeAlgebra("igualdad entre tipos incompatibles")


def _validar_tipos_orden(izquierda: Scalar, derecha: Scalar) -> None:
    if _es_numero_no_bool(izquierda) and _es_numero_no_bool(derecha):
        return
    if isinstance(izquierda, str) and isinstance(derecha, str):
        return
    raise ErrorDeAlgebra("orden entre tipos incompatibles")


def _validar_booleanos(valores: list[Any], operador: str) -> None:
    for valor in valores:
        if not isinstance(valor, bool):
            raise ErrorDeAlgebra(f"{operador} espera booleanos")


def _validar_escalar(valor: Any, contexto: str) -> Scalar:
    if not isinstance(valor, (bool, int, float, str)):
        raise ErrorDeAlgebra(f"{contexto} no es escalar")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ErrorDeAlgebra(f"{contexto} no es finito")
    return valor


def _tipo_escalar_comparable(valor: Any) -> type:
    _validar_escalar(valor, "valor de min/max")
    if isinstance(valor, bool):
        raise ErrorDeAlgebra("min/max exige valores ordenables")
    return type(valor)


def _es_numero_no_bool(valor: Any) -> bool:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _validar_escalares(escalares: Any) -> None:
    if not isinstance(escalares, dict):
        raise ErrorDeAlgebra("escalares debe ser un diccionario")
    for nombre, funcion in escalares.items():
        if not isinstance(nombre, str) or nombre == "":
            raise ErrorDeAlgebra("los nombres de escalares deben ser texto no vacio")
        if not callable(funcion):
            raise ErrorDeAlgebra(f"escalar no callable: {nombre}")


def _es_lista_con_tag(valor: Any, tag: str) -> bool:
    return isinstance(valor, list) and bool(valor) and valor[0] == tag


def _copiar_filas(filas: list[Row]) -> list[Row]:
    return [_copiar_fila(fila) for fila in filas]


def _copiar_fila(fila: Row) -> Row:
    copia: Row = {}
    for clave, valor in fila.items():
        copia[clave] = dict(valor) if isinstance(valor, dict) else valor
    return copia
