"""Mutadores independientes para medidas del álgebra Oracle.

Cada función conserva ``datos`` intacto y devuelve una copia mutada, o ``None``
cuando la forma o la dirección del veredicto no permiten justificar que la
transformación sea un debilitamiento.
"""


def _copiar(valor):
    """Copia recursivamente los valores admitidos por la forma de datos."""
    if isinstance(valor, list):
        return [_copiar(elemento) for elemento in valor]
    if isinstance(valor, dict):
        return {clave: _copiar(elemento) for clave, elemento in valor.items()}
    return valor


def _partes(datos):
    """Obtiene las partes estables de una medida o informa una forma ajena."""
    if not isinstance(datos, list) or len(datos) not in (6, 7, 8):
        return None
    if not datos or datos[0] != "medida":
        return None
    tuberia, resumen, umbral = datos[2], datos[3], datos[4]
    if not (isinstance(tuberia, list) and tuberia and tuberia[0] == "desde"):
        return None
    if not (isinstance(resumen, list) and len(resumen) == 3 and resumen[0] == "resumen"):
        return None
    if not (isinstance(umbral, list) and len(umbral) >= 3 and umbral[0] == "umbral"):
        return None
    indice_requiere = None
    siguiente = 5
    if (siguiente < len(datos) - 1 and isinstance(datos[siguiente], list)
            and datos[siguiente] and datos[siguiente][0] == "requiere"):
        indice_requiere = 5
        siguiente += 1
    if (siguiente < len(datos) - 1 and isinstance(datos[siguiente], list)
            and datos[siguiente] and datos[siguiente][0] == "ambito"):
        siguiente += 1
    if siguiente != len(datos) - 1:
        return None
    if not (isinstance(datos[-1], list) and datos[-1] and datos[-1][0] == "alcance"):
        return None
    return tuberia, resumen, umbral, indice_requiere


def _es_numero_finito(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    if isinstance(valor, float):
        return valor == valor and valor not in (float("inf"), float("-inf"))
    return True


def _numero_mayor(valor):
    if not _es_numero_finito(valor):
        return None
    if isinstance(valor, int):
        return valor + 1
    candidatos = (valor + 1.0, valor / 2.0 if valor < 0 else valor * 2.0)
    for candidato in candidatos:
        if _es_numero_finito(candidato) and candidato > valor:
            return candidato
    return None


def _numero_menor(valor):
    if not _es_numero_finito(valor):
        return None
    if isinstance(valor, int):
        return valor - 1
    candidatos = (valor - 1.0, valor * 2.0 if valor < 0 else valor / 2.0)
    for candidato in candidatos:
        if _es_numero_finito(candidato) and candidato < valor:
            return candidato
    return None


def _aprueba(valor, comparador, limite):
    if not isinstance(limite, (bool, int, float)):
        return False
    try:
        if comparador == "<":
            return valor < limite
        if comparador == "<=":
            return valor <= limite
        if comparador == ">":
            return valor > limite
        if comparador == ">=":
            return valor >= limite
        if comparador == "==":
            return valor == limite
        if comparador == "!=":
            return valor != limite
    except TypeError:
        return False
    return False


def _es_predicado(expresion):
    if isinstance(expresion, bool):
        return True
    return (
        isinstance(expresion, list)
        and bool(expresion)
        and expresion[0] in {"<", "<=", ">", ">=", "==", "!=", "y", "o", "no"}
    )


def _reemplazar_primero(nodo, transformador):
    """Reemplaza en profundidad la primera expresión aceptada."""
    reemplazo = transformador(nodo)
    if reemplazo is not None:
        return reemplazo, True
    if not isinstance(nodo, list):
        return nodo, False
    for indice, hijo in enumerate(nodo):
        nuevo_hijo, cambio = _reemplazar_primero(hijo, transformador)
        if cambio:
            nodo[indice] = nuevo_hijo
            return nodo, True
    return nodo, False


def _direccion_monotona(partes, direccion):
    _, resumen, umbral, _ = partes
    if direccion == "superior" and umbral[1] not in {"<", "<="}:
        return False
    if direccion == "inferior" and umbral[1] not in {">", ">="}:
        return False
    if resumen[1] == "contar":
        return True
    return resumen[1] == "suma" and _es_predicado(resumen[2])


def _mutar_predicado(datos, direccion, transformador):
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None or not _direccion_monotona(partes, direccion):
        return None
    tuberia, resumen, _, _ = partes
    ultimo_agrupamiento = 1
    for indice in range(2, len(tuberia)):
        paso = tuberia[indice]
        if isinstance(paso, list) and paso and paso[0] == "agrupar":
            ultimo_agrupamiento = indice
    for indice in range(ultimo_agrupamiento + 1, len(tuberia)):
        paso = tuberia[indice]
        if isinstance(paso, list) and len(paso) == 2 and paso[0] == "donde":
            nuevo, cambio = _reemplazar_primero(paso[1], transformador)
            if cambio:
                paso[1] = nuevo
                return copia
    if resumen[1] == "suma" and _es_predicado(resumen[2]):
        nuevo, cambio = _reemplazar_primero(resumen[2], transformador)
        if cambio:
            resumen[2] = nuevo
            return copia
    return None


def aflojar_cota_superior(datos: list) -> list | None:
    """Eleva una cota final superior; un exceso pequeño podría dejar de ser rojo sin que el corpus pruebe el borde."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None:
        return None
    umbral = partes[2]
    if umbral[1] not in {"<", "<="}:
        return None
    nuevo = _numero_mayor(umbral[2])
    if nuevo is None:
        return None
    umbral[2] = nuevo
    return copia


def aflojar_cota_inferior(datos: list) -> list | None:
    """Baja una cota final inferior; una carencia leve podría aprobar si los casos sólo ejercitan valores extremos."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None:
        return None
    umbral = partes[2]
    if umbral[1] not in {">", ">="}:
        return None
    nuevo = _numero_menor(umbral[2])
    if nuevo is None:
        return None
    umbral[2] = nuevo
    return copia


def incluir_limite_superior(datos: list) -> list | None:
    """Cambia una cota superior estricta por inclusiva; puede pasar inadvertido si ningún caso cae exactamente en el límite."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None or partes[2][1] != "<":
        return None
    partes[2][1] = "<="
    return copia


def incluir_limite_inferior(datos: list) -> list | None:
    """Cambia una cota inferior estricta por inclusiva; sobrevive si el corpus no contiene el valor de frontera."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None or partes[2][1] != ">":
        return None
    partes[2][1] = ">="
    return copia


def igualdad_como_cota_superior(datos: list) -> list | None:
    """Reemplaza igualdad final por una cota superior; acepta todo lo que quede por debajo y puede ocultar mediciones demasiado bajas."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None or partes[2][1] != "==":
        return None
    partes[2][1] = "<="
    return copia


def igualdad_como_cota_inferior(datos: list) -> list | None:
    """Reemplaza igualdad final por una cota inferior; acepta todo lo que quede por encima y prueba el lado opuesto del valor esperado."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None or partes[2][1] != "==":
        return None
    partes[2][1] = ">="
    return copia


def quitar_requisitos_de_evidencia(datos: list) -> list | None:
    """Elimina ``requiere``; la ausencia total vuelve a poder colapsar a cero y parecer verde si no hay un caso sin evidencia."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None or partes[3] is None or len(copia[partes[3]]) < 2:
        return None
    del copia[partes[3]]
    return copia


def vaciar_tuberia_si_cero_aprueba(datos: list) -> list | None:
    """Descarta todas las filas justo antes del resumen; explota el cero de los agregados vacíos cuando el corpus no exige testigos."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None:
        return None
    tuberia, _, umbral, _ = partes
    if not _aprueba(0, umbral[1], umbral[2]):
        return None
    tuberia.append(["donde", False])
    return copia


def convertir_conteo_en_existencia(datos: list) -> list | None:
    """Reduce un conteo a cero o uno; pierde la multiplicidad y puede sobrevivir si sólo se prueba la presencia de algún defecto."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None:
        return None
    _, resumen, umbral, _ = partes
    if resumen[1] != "contar" or umbral[1] not in {"<", "<="}:
        return None
    if not (_aprueba(0, umbral[1], umbral[2]) or _aprueba(1, umbral[1], umbral[2])):
        return None
    resumen[1:] = ["max", 1]
    return copia


def maximo_por_minimo(datos: list) -> list | None:
    """Usa el mejor valor en vez del peor bajo una cota superior; un caso con filas homogéneas no distingue ambos agregados."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None or partes[1][1] != "max" or partes[2][1] not in {"<", "<="}:
        return None
    partes[1][1] = "min"
    return copia


def minimo_por_maximo(datos: list) -> list | None:
    """Usa el mejor valor en vez del peor bajo una cota inferior; puede pasar si cada caso aporta un único valor."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None or partes[1][1] != "min" or partes[2][1] not in {">", ">="}:
        return None
    partes[1][1] = "max"
    return copia


def suma_de_indicadores_por_maximo(datos: list) -> list | None:
    """Convierte cantidad de coincidencias en mera existencia; varias infracciones pesan como una y la falta de casos múltiples puede ocultarlo."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None:
        return None
    _, resumen, umbral, _ = partes
    if resumen[1] != "suma" or not _es_predicado(resumen[2]):
        return None
    if umbral[1] not in {"<", "<="} or not _aprueba(0, umbral[1], umbral[2]):
        return None
    resumen[1] = "max"
    return copia


def promedio_por_minimo(datos: list) -> list | None:
    """Sustituye el promedio de indicadores por su mínimo bajo una cota superior; una sola fila favorable puede tapar al resto."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None:
        return None
    _, resumen, umbral, _ = partes
    if resumen[1] != "promedio" or not _es_predicado(resumen[2]) or umbral[1] not in {"<", "<="}:
        return None
    resumen[1] = "min"
    return copia


def promedio_por_maximo(datos: list) -> list | None:
    """Sustituye el promedio de indicadores por su máximo bajo una cota inferior; una sola fila favorable puede aprobar el conjunto."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None:
        return None
    _, resumen, umbral, _ = partes
    if resumen[1] != "promedio" or not _es_predicado(resumen[2]) or umbral[1] not in {">", ">="}:
        return None
    resumen[1] = "max"
    return copia


def conservar_una_rama_de_disyuncion(datos: list) -> list | None:
    """Quita clases de defectos de una disyunción contada con cota superior; sobrevive si los casos sólo cubren la rama conservada."""
    def transformar(nodo):
        if isinstance(nodo, list) and len(nodo) >= 3 and nodo[0] == "o":
            return _copiar(nodo[1])
        return None

    return _mutar_predicado(datos, "superior", transformar)


def hacer_estricta_comparacion_interna(datos: list) -> list | None:
    """Excluye la frontera de un predicado de defectos; puede pasar inadvertido cuando ningún testigo interno está justo en el borde."""
    def transformar(nodo):
        if isinstance(nodo, list) and len(nodo) == 3 and nodo[0] in {"<=", ">="}:
            copia = _copiar(nodo)
            copia[0] = "<" if nodo[0] == "<=" else ">"
            return copia
        return None

    return _mutar_predicado(datos, "superior", transformar)


def alejar_limite_de_defecto(datos: list) -> list | None:
    """Estrecha numéricamente un predicado de defectos; omite casos cercanos al límite si el corpus sólo contiene anomalías grandes."""
    def transformar(nodo):
        if not (isinstance(nodo, list) and len(nodo) == 3):
            return None
        if nodo[0] in {">", ">="}:
            nuevo = _numero_mayor(nodo[2])
        elif nodo[0] in {"<", "<="}:
            nuevo = _numero_menor(nodo[2])
        else:
            return None
        if nuevo is None:
            return None
        copia = _copiar(nodo)
        copia[2] = nuevo
        return copia

    return _mutar_predicado(datos, "superior", transformar)


def quitar_un_termino_de_conjuncion(datos: list) -> list | None:
    """Amplía una selección que alimenta una exigencia mínima; una condición necesaria desaparece y puede faltar un caso que la aísle."""
    def transformar(nodo):
        if isinstance(nodo, list) and len(nodo) >= 3 and nodo[0] == "y":
            return _copiar(nodo[1])
        return None

    return _mutar_predicado(datos, "inferior", transformar)


def incluir_frontera_interna(datos: list) -> list | None:
    """Amplía un predicado que sostiene una cota inferior incluyendo su frontera; sobrevive si faltan ejemplos exactos del borde."""
    def transformar(nodo):
        if isinstance(nodo, list) and len(nodo) == 3 and nodo[0] in {"<", ">"}:
            copia = _copiar(nodo)
            copia[0] = "<=" if nodo[0] == "<" else ">="
            return copia
        return None

    return _mutar_predicado(datos, "inferior", transformar)


def acercar_limite_de_requisito(datos: list) -> list | None:
    """Amplía numéricamente un predicado contado como requisito mínimo; valores marginales podrían aprobar sin casos de frontera."""
    def transformar(nodo):
        if not (isinstance(nodo, list) and len(nodo) == 3):
            return None
        if nodo[0] in {">", ">="}:
            nuevo = _numero_menor(nodo[2])
        elif nodo[0] in {"<", "<="}:
            nuevo = _numero_mayor(nodo[2])
        else:
            return None
        if nuevo is None:
            return None
        copia = _copiar(nodo)
        copia[2] = nuevo
        return copia

    return _mutar_predicado(datos, "inferior", transformar)


def eliminar_filtro_de_requisito(datos: list) -> list | None:
    """Elimina una selección antes de un conteo o suma mínimos; filas irrelevantes pueden satisfacer la exigencia si no hay evidencia distractora."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None or not _direccion_monotona(partes, "inferior"):
        return None
    tuberia = partes[0]
    ultimo_agrupamiento = 1
    for indice in range(2, len(tuberia)):
        paso = tuberia[indice]
        if isinstance(paso, list) and paso and paso[0] == "agrupar":
            ultimo_agrupamiento = indice
    for indice in range(ultimo_agrupamiento + 1, len(tuberia)):
        paso = tuberia[indice]
        if isinstance(paso, list) and len(paso) == 2 and paso[0] == "donde":
            del tuberia[indice]
            return copia
    return None


def quitar_clave_de_agrupamiento(datos: list) -> list | None:
    """Fusiona grupos antes de contarlos con cota superior; pierde una dimensión y puede sobrevivir si los casos usan una sola categoría."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None:
        return None
    tuberia, resumen, umbral, _ = partes
    if resumen[1] != "contar" or umbral[1] not in {"<", "<="} or len(tuberia) < 3:
        return None
    paso = tuberia[-1]
    if not (isinstance(paso, list) and len(paso) >= 3 and paso[0] == "agrupar"):
        return None
    claves = paso[1]
    if not isinstance(claves, list) or len(claves) < 2:
        return None
    del claves[-1]
    return copia


def eliminar_agrupamiento_de_requisito(datos: list) -> list | None:
    """Cuenta filas en vez de grupos bajo una cota inferior; la multiplicidad puede fingir variedad si los casos no repiten una clave."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None:
        return None
    tuberia, resumen, umbral, _ = partes
    if resumen[1] != "contar" or umbral[1] not in {">", ">="} or len(tuberia) < 3:
        return None
    paso = tuberia[-1]
    if not (isinstance(paso, list) and paso and paso[0] == "agrupar"):
        return None
    del tuberia[-1]
    return copia


def _alias_de_fuente(fuente):
    if not isinstance(fuente, list) or not fuente:
        return set()
    if fuente[0] == "de" and len(fuente) == 3 and isinstance(fuente[2], str):
        return {fuente[2]}
    if fuente[0] == "unir" and len(fuente) == 3:
        return _alias_de_fuente(fuente[1]) | _alias_de_fuente(fuente[2])
    return set()


def _relaciones_de_fuente(fuente):
    if not isinstance(fuente, list) or not fuente:
        return set()
    if fuente[0] == "de" and len(fuente) == 3 and isinstance(fuente[1], str):
        return {fuente[1]}
    if fuente[0] == "unir" and len(fuente) == 3:
        return _relaciones_de_fuente(fuente[1]) | _relaciones_de_fuente(fuente[2])
    return set()


def _alias_referidos(nodo):
    encontrados = set()
    if isinstance(nodo, list):
        if len(nodo) >= 2 and nodo[0] in {"campo", "hecho"} and isinstance(nodo[1], str):
            encontrados.add(nodo[1])
        for hijo in nodo:
            encontrados |= _alias_referidos(hijo)
    elif isinstance(nodo, dict):
        for hijo in nodo.values():
            encontrados |= _alias_referidos(hijo)
    return encontrados


def quitar_factor_no_observado_del_producto(datos: list) -> list | None:
    """Quita un factor no consultado de un producto y conserva su precondición de presencia; pierde multiplicidad que puede no estar cubierta."""
    copia = _copiar(datos)
    partes = _partes(copia)
    if partes is None:
        return None
    tuberia, resumen, umbral, indice_requiere = partes
    if resumen[1] != "contar" or umbral[1] not in {"<", "<="} or indice_requiere is None:
        return None
    if any(isinstance(paso, list) and paso and paso[0] == "agrupar" for paso in tuberia[2:]):
        return None
    if len(tuberia) < 2:
        return None
    fuente = tuberia[1]
    if not (isinstance(fuente, list) and len(fuente) == 3 and fuente[0] == "unir"):
        return None
    requeridas = {nombre for nombre in copia[indice_requiere][1:] if isinstance(nombre, str)}
    referencias = _alias_referidos(tuberia[2:]) | _alias_referidos(resumen)
    for indice_descartado, indice_conservado in ((2, 1), (1, 2)):
        descartado = fuente[indice_descartado]
        if _alias_de_fuente(descartado) & referencias:
            continue
        relaciones = _relaciones_de_fuente(descartado)
        if relaciones and relaciones <= requeridas:
            tuberia[1] = _copiar(fuente[indice_conservado])
            return copia
    return None


MUTADORES = [
    aflojar_cota_superior,
    aflojar_cota_inferior,
    incluir_limite_superior,
    incluir_limite_inferior,
    igualdad_como_cota_superior,
    igualdad_como_cota_inferior,
    quitar_requisitos_de_evidencia,
    vaciar_tuberia_si_cero_aprueba,
    convertir_conteo_en_existencia,
    maximo_por_minimo,
    minimo_por_maximo,
    suma_de_indicadores_por_maximo,
    promedio_por_minimo,
    promedio_por_maximo,
    conservar_una_rama_de_disyuncion,
    hacer_estricta_comparacion_interna,
    alejar_limite_de_defecto,
    quitar_un_termino_de_conjuncion,
    incluir_frontera_interna,
    acercar_limite_de_requisito,
    eliminar_filtro_de_requisito,
    quitar_clave_de_agrupamiento,
    eliminar_agrupamiento_de_requisito,
    quitar_factor_no_observado_del_producto,
]
