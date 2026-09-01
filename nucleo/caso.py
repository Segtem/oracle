"""Superficie de autoría para casos del corpus.

El almacenamiento histórico del corpus es JSON: un objeto con prosa y evidencia L0. Esta superficie
mantiene ese contrato y sólo cambia la forma de escribirlo: la prosa queda como prosa y la evidencia
homogénea queda como tabla.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .proyecto import ID_CASO_RE
from .sintaxis import ErrorSintaxis, fragmento_de_error

IND = "    "
IND2 = IND * 2
IND3 = IND * 3
EXTENSIONES_DE_CASO = frozenset({".json", ".caso"})
ENCABEZADO_RE = re.compile(r"caso\s+(\S+):")
# El vocabulario cerrado DECLARA su significado donde se define, no en un `.md` aparte.
#
# Hasta el 2026-09-01 eran nombres sueltos en un `frozenset`, y qué querían decir vivía repartido
# entre cuatro documentos distintos —el tutorial, `corpus/README.md`, `PLAN-LENGUAJE.md` y una
# guía—. Cuatro copias que nadie podía mantener sincronizadas, para cinco palabras.
#
# Acá el significado es DATO, así que el CLI puede explicarlo en el momento en que hace falta
# —cuando alguien escribe una etiqueta inválida— y la referencia se genera en vez de escribirse.
# No hace falta una medida que lo vigile: no hay dos copias que puedan divergir.

ETIQUETAS = {
    "falso_verde":
        "la medida pasó y no debía: el defecto estaba ahí y no lo vio. Es el caso que más "
        "enseña, porque un verificador que calla es peor que no tenerlo",
    "falso_rojo":
        "la medida falló sobre algo que estaba bien. Enseña a ignorar el verificador, que es "
        "la forma más rápida de perderlo",
    "deuda_de_diseño":
        "el defecto es real y el lenguaje todavía no puede expresarlo. Se guarda para que la "
        "falta quede escrita en vez de olvidarse",
    "medida_correcta_conclusion_errada":
        "la medida hizo lo que declara y aun así la conclusión fue equivocada: el error está "
        "en lo que se decidió medir, no en cómo se midió",
    "verde_correcto":
        "la medida pasó y correspondía. Hace falta tanto como un rojo: sin él, el mutador que "
        "quita el filtro sobrevive y nadie se entera",
}

DETECCIONES = {
    "mutacion": "lo encontró el arnés al romper la medida a propósito",
    "persona": "lo vio alguien leyendo el código o la salida, sin que ninguna "
               "herramienta lo señalara",
    "accidente": "apareció haciendo otra cosa, y nadie lo estaba buscando. Vale igual: dice "
                 "que en el camino donde sí se buscaba no estaba",
    "herramienta_ajena": "lo señaló una herramienta de afuera de Oracle",
    "observacion": "salió de mirar de frente una corrida real, con la intención de "
                   "encontrar algo",
}

PROCEDENCIAS = {
    "observada":
        "la evidencia es lo que devolvió una corrida que ocurrió. Es una afirmación sobre el "
        "pasado, y Oracle NO puede verificarla: ante la duda, `construida`",
    "construida":
        "la evidencia se escribió a mano para ejercer la medida. Es honesto y no cierra nada "
        "que no deba cerrarse",
    "generada":
        "la produjo un generador a partir de una especificación, no una corrida del mundo",
}


def opciones(vocabulario: dict) -> str:
    """Las opciones de un vocabulario cerrado, cada una con lo que significa.

    Antes el error decía sólo la lista de nombres. Quien escribe `falso_rojo` donde iba
    `falso_verde` no necesita saber que existen cinco: necesita saber cuál es cuál, y el momento
    en que lo necesita es exactamente ése.
    """
    return "\n".join(f"        {nombre}: {sentido}" for nombre, sentido in
                     sorted(vocabulario.items()))


class CasoMalDeclarado(ValueError):
    pass


def _fallar(linea: int, columna: int, esperado: str, encontrado: object = "",
            *, literal: bool = False) -> None:
    raise ErrorSintaxis(linea, columna, esperado,
                        repr(encontrado) if encontrado != "" else "", literal)


def _indentada(linea: str, nivel: int, n: int) -> str:
    esperado = IND * nivel
    if not linea.startswith(esperado) or linea.startswith(esperado + " "):
        col = len(linea) - len(linea.lstrip()) + 1
        _fallar(n, col, f"indentación de {len(esperado)} espacios", linea[:col])
    return linea[len(esperado):]


def _json_valor(texto: str, linea: int, columna: int):
    try:
        valor, fin = json.JSONDecoder().raw_decode(texto)
    except json.JSONDecodeError as e:
        _fallar(linea, columna + e.pos, "texto entre comillas", texto)
    if texto[fin:].strip():
        _fallar(linea, columna + fin, "texto entre comillas", texto[fin:].strip())
    return valor


def _json_objeto(texto: str, linea: int, columna: int) -> dict:
    valor = _json_valor(texto, linea, columna)
    if not isinstance(valor, dict):
        _fallar(linea, columna, "objeto JSON", valor)
    return valor


def _valores_fila(texto: str, linea: int, columna: int) -> list:
    valores = []
    i = 0
    decodificador = json.JSONDecoder()
    while i < len(texto):
        while i < len(texto) and texto[i].isspace():
            i += 1
        if i >= len(texto):
            break
        try:
            valor, fin = decodificador.raw_decode(texto[i:])
        except json.JSONDecodeError as e:
            _fallar(linea, columna + i + e.pos, "valor JSON de fila", texto[i:])
        valores.append(valor)
        i += fin
        while i < len(texto) and texto[i].isspace():
            i += 1
        if i >= len(texto):
            break
        if texto[i] != ",":
            _fallar(linea, columna + i, "',' entre valores de fila", texto[i:])
        i += 1
    if not valores:
        _fallar(linea, columna, "valores de fila", texto)
    return valores


def _escalar(valor) -> str:
    return json.dumps(valor, ensure_ascii=False)


def _campo_bloque(nombre: str, valor: str) -> list[str]:
    lineas = str(valor).split("\n")
    return [f"{IND}{nombre}:", *(f"{IND2}{linea}" for linea in lineas)]


def _lineas_relacion(nombre: str, filas: list) -> list[str]:
    if not isinstance(filas, list):
        raise ValueError(f"la relación «{nombre}» no es una lista")
    clave = None
    hechos = list(filas)
    if hechos and isinstance(hechos[0], list) and len(hechos[0]) == 2 and hechos[0][0] == "clave":
        clave = hechos[0][1]
        hechos = hechos[1:]
    prefijo_clave = ""
    if clave is not None:
        if not isinstance(clave, list) or not all(isinstance(c, str) for c in clave):
            raise ValueError(f"clave no imprimible en «{nombre}»: {clave!r}")
        prefijo_clave = f" clave({', '.join(clave)})"
    if not hechos:
        return [f"{IND2}{nombre}:{prefijo_clave}"]

    campos = list(hechos[0].keys()) if isinstance(hechos[0], dict) else []
    imprimible_como_tabla = (
        bool(campos)
        and all(isinstance(f, dict) and list(f.keys()) == campos for f in hechos)
        and all(c and c.strip() == c and "," not in c for c in campos)
    )
    if not imprimible_como_tabla:
        lineas = [f"{IND2}{nombre}:{prefijo_clave}"]
        for hecho in hechos:
            if not isinstance(hecho, dict):
                raise ValueError(f"fila no imprimible en «{nombre}»: {hecho!r}")
            lineas.append(f"{IND3}fila {json.dumps(hecho, ensure_ascii=False, separators=(', ', ': '))}")
        return lineas

    cabeza = f"{IND2}{nombre}: "
    if clave is not None:
        cabeza += f"clave({', '.join(clave)}); "
    cabeza += ", ".join(campos)
    return [cabeza, *(
        f"{IND3}{', '.join(_escalar(hecho[c]) for c in campos)}" for hecho in hechos
    )]


class _Parser:
    def __init__(self, texto: str) -> None:
        self.texto = texto
        self.lineas = texto.splitlines()
        self.i = 0

    def _saltar_vacios(self) -> None:
        while self.i < len(self.lineas):
            linea = self.lineas[self.i]
            if linea.strip() and not linea.lstrip().startswith("#"):
                break
            self.i += 1

    def _actual(self) -> tuple[int, str]:
        if self.i >= len(self.lineas):
            linea = len(self.lineas) + 1
            return linea, ""
        return self.i + 1, self.lineas[self.i]

    def _tomar_campo(self, nombre: str, nivel: int = 1) -> tuple[str, int, int] | None:
        self._saltar_vacios()
        n, linea = self._actual()
        if not linea.startswith(IND * nivel):
            return None
        cuerpo = _indentada(linea, nivel, n)
        prefijo = f"{nombre}:"
        if not cuerpo.startswith(prefijo):
            return None
        resto = cuerpo[len(prefijo):]
        if resto.startswith(" "):
            resto = resto[1:]
            col = len(IND * nivel) + len(prefijo) + 2
        elif resto == "":
            col = len(IND * nivel) + len(prefijo) + 1
        else:
            _fallar(n, len(IND * nivel) + len(prefijo) + 1, "espacio o fin tras ':'", resto)
        self.i += 1
        return resto, n, col

    def _exigir_campo(self, nombre: str, nivel: int = 1) -> tuple[str, int, int]:
        tomado = self._tomar_campo(nombre, nivel)
        if tomado is None:
            n, linea = self._actual()
            col = len(linea) - len(linea.lstrip()) + 1 if linea else 1
            _fallar(n, col, f"línea «{nombre}:»", linea.strip())
        return tomado

    def _leer_bloque(self, nombre: str) -> str:
        resto, n, col = self._exigir_campo(nombre)
        if resto:
            _fallar(n, col, "bloque de prosa en la línea siguiente", resto)
        partes = []
        while self.i < len(self.lineas):
            linea = self.lineas[self.i]
            if not linea.startswith(IND2):
                break
            partes.append(linea[len(IND2):])
            self.i += 1
        if not partes:
            _fallar(n + 1, 1, f"prosa para «{nombre}»")
        return "\n".join(partes)

    def _leer_origen(self) -> dict:
        resto, n, col = self._exigir_campo("origen")
        if resto:
            _fallar(n, col, "origen en bloque", resto)
        origen = {}
        while self.i < len(self.lineas):
            n2, linea = self._actual()
            if not linea.startswith(IND2):
                break
            cuerpo = _indentada(linea, 2, n2)
            clave, sep, valor = cuerpo.partition(":")
            if not sep or not clave.strip():
                _fallar(n2, len(IND2) + 1, "campo de origen «nombre: valor»", cuerpo)
            if not valor.startswith(" "):
                _fallar(n2, len(IND2) + len(clave) + 2, "espacio tras ':'", cuerpo)
            if clave in origen:
                _fallar(n2, len(IND2) + 1, f"campo de origen sin repetir, no «{clave}»", cuerpo)
            origen[clave] = _json_valor(valor[1:], n2, len(IND2) + len(clave) + 3)
            self.i += 1
        if not origen:
            _fallar(n + 1, 1, "origen con al menos un campo")
        return origen

    def _parsear_cabecera_relacion(self, texto_crudo: str, linea: int, columna: int):
        texto = texto_crudo.strip()
        clave = None
        if texto.startswith("clave("):
            fin = texto.find(")")
            if fin < 0:
                _fallar(linea, columna, "')' de clave", texto)
            crudo = texto[len("clave("):fin]
            trozos_clave = [c.strip() for c in crudo.split(",") if c.strip()]
            if not trozos_clave:
                _fallar(linea, columna + len("clave("), "campos de clave", crudo)
            for trozo in crudo.split(","):
                palabras = trozo.split()
                if len(palabras) > 1:
                    idx0 = texto_crudo.find(palabras[0])
                    idx1 = texto_crudo.find(palabras[1], idx0 + len(palabras[0]))
                    _fallar(linea, columna + idx1, "',' entre campos de clave", palabras[1])
            clave = trozos_clave
            texto = texto[fin + 1:].strip()
            if texto:
                if not texto.startswith(";"):
                    _fallar(linea, columna + fin + 1, "';' antes de campos", texto)
                texto = texto[1:].strip()
        for trozo in texto.split(","):
            palabras = trozo.split()
            if len(palabras) > 1:
                punto_inicio = texto_crudo.find(";") + 1 if clave is not None else 0
                idx0 = texto_crudo.find(palabras[0], punto_inicio)
                idx1 = texto_crudo.find(palabras[1], idx0 + len(palabras[0]))
                _fallar(linea, columna + idx1, "',' entre campos", palabras[1])
        campos = [c.strip() for c in texto.split(",") if c.strip()] if texto else []
        if len(set(campos)) != len(campos):
            _fallar(linea, columna, "campos sin repetir", texto)
        return clave, campos

    def _leer_evidencia(self) -> dict:
        resto, n, col = self._exigir_campo("evidencia")
        if resto:
            _fallar(n, col, "evidencia en bloque", resto)
        evidencia = {}
        while self.i < len(self.lineas):
            n_rel, linea_rel = self._actual()
            if not linea_rel.startswith(IND2):
                break
            if linea_rel.startswith(IND3):
                _fallar(n_rel, len(IND2) + 1, "relación", linea_rel.strip())
            cuerpo = _indentada(linea_rel, 2, n_rel)
            relacion, sep, resto_rel = cuerpo.partition(":")
            if not sep or not relacion.strip():
                _fallar(n_rel, len(IND2) + 1, "relación «nombre: campos»", cuerpo)
            relacion = relacion.strip()
            if relacion in evidencia:
                _fallar(n_rel, len(IND2) + 1, f"relación sin repetir, no «{relacion}»", cuerpo)
            col_resto = len(IND2) + cuerpo.find(":") + 2
            clave, campos = self._parsear_cabecera_relacion(resto_rel, n_rel, col_resto)
            self.i += 1
            hechos = []
            while self.i < len(self.lineas):
                n_fila, linea_fila = self._actual()
                if not linea_fila.startswith(IND3):
                    break
                cuerpo_fila = _indentada(linea_fila, 3, n_fila)
                if cuerpo_fila.startswith("fila "):
                    if campos:
                        _fallar(n_fila, len(IND3) + 1,
                                "fila de tabla, no escape JSON, porque hay campos", cuerpo_fila)
                    hechos.append(_json_objeto(cuerpo_fila[len("fila "):], n_fila,
                                               len(IND3) + len("fila ")+ 1))
                else:
                    if not campos:
                        _fallar(n_fila, len(IND3) + 1,
                                "«fila { ... }» o relación nueva", cuerpo_fila)
                    valores = _valores_fila(cuerpo_fila, n_fila, len(IND3) + 1)
                    if len(valores) != len(campos):
                        n_campos = len(campos)
                        nom_campos = (
                            f"1 campo ({campos[0]})"
                            if n_campos == 1
                            else f"{n_campos} campos ({', '.join(campos)})"
                        )
                        _fallar(
                            n_fila,
                            len(IND3) + 1,
                            f"la relación «{relacion}» declara {nom_campos} y esta fila trae {len(valores)}",
                            cuerpo_fila,
                            literal=True,
                        )
                    hechos.append(dict(zip(campos, valores)))
                self.i += 1
            if campos and not hechos:
                _fallar(n_rel, len(IND2) + len(relacion) + 2,
                        "filas para una relación con encabezado de campos", cuerpo)
            filas = ([["clave", clave]] if clave is not None else []) + hechos
            evidencia[relacion] = filas
        if not evidencia:
            _fallar(n + 1, 1, "al menos una relación de evidencia")
        return evidencia

    def leer(self) -> dict:
        self._saltar_vacios()
        n, encabezado = self._actual()
        m = ENCABEZADO_RE.fullmatch(encabezado)
        if not m:
            _fallar(n, 1, "encabezado «caso <id>:»", encabezado)
        cid = m.group(1)
        if ID_CASO_RE.fullmatch(cid) is None:
            _fallar(n, encabezado.find(cid) + 1,
                    "id «NNN-descripcion», sólo con minúsculas ASCII, dígitos y `-`", cid)
        datos = {"id": cid}
        self.i += 1

        datos["fecha"] = _json_valor(*self._exigir_campo("fecha"))
        datos["origen"] = self._leer_origen()
        procedencia = self._tomar_campo("procedencia")
        if procedencia is not None:
            valor, n_proc, col_proc = procedencia
            if valor not in PROCEDENCIAS:
                _fallar(n_proc, col_proc,
                        f"una procedencia declarada\n{opciones(PROCEDENCIAS)}", valor)
            datos["procedencia"] = valor
        datos["titulo"] = _json_valor(*self._exigir_campo("titulo"))
        etiqueta, n_etiqueta, col_etiqueta = self._exigir_campo("etiqueta")
        if etiqueta not in ETIQUETAS:
            _fallar(n_etiqueta, col_etiqueta,
                    f"una etiqueta declarada\n{opciones(ETIQUETAS)}", etiqueta)
        datos["etiqueta"] = etiqueta
        datos["sintoma"] = self._leer_bloque("sintoma")
        como_se_detecto, n_det, col_det = self._exigir_campo("como_se_detecto")
        if como_se_detecto not in DETECCIONES:
            _fallar(n_det, col_det,
                    f"un como_se_detecto declarado\n{opciones(DETECCIONES)}", como_se_detecto)
        datos["como_se_detecto"] = como_se_detecto
        medida, n_medida, col_medida = self._exigir_campo("medida")
        datos["medida"] = None if medida == "null" else medida

        estado = self._tomar_campo("estado_sin_medida")
        if estado is not None:
            datos["estado_sin_medida"] = estado[0]
        for opcional in ("resuelto", "limite_humano", "sin_medida_todavia"):
            if self._tomar_campo(opcional) is not None:
                self.i -= 1
                datos[opcional] = self._leer_bloque(opcional)

        datos["evidencia"] = self._leer_evidencia()
        datos["leccion"] = self._leer_bloque("leccion")
        self._saltar_vacios()
        if self.i != len(self.lineas):
            n_extra, linea_extra = self._actual()
            _fallar(n_extra, len(linea_extra) - len(linea_extra.lstrip()) + 1,
                    "fin de caso", linea_extra.strip())
        return datos


def leer(texto: str) -> dict:
    return _Parser(texto).leer()


def imprimir(datos: dict) -> str:
    if not isinstance(datos, dict):
        raise ValueError("un caso tiene que ser un objeto JSON")
    if "id" not in datos:
        raise ValueError("un caso necesita `id`")
    if not isinstance(datos["id"], str) or ID_CASO_RE.fullmatch(datos["id"]) is None:
        raise ValueError(
            f"id inválido: «{datos['id']}» — debe ser `NNN-descripcion`, sólo con minúsculas "
            "ASCII, dígitos y `-`")
    lineas = [f"caso {datos['id']}:"]
    lineas.append(f"{IND}fecha: {_escalar(datos['fecha'])}")
    lineas.append(f"{IND}origen:")
    for clave, valor in datos["origen"].items():
        lineas.append(f"{IND2}{clave}: {_escalar(valor)}")
    if "procedencia" in datos:
        lineas.append(f"{IND}procedencia: {datos['procedencia']}")
    lineas.append(f"{IND}titulo: {_escalar(datos['titulo'])}")
    lineas.append(f"{IND}etiqueta: {datos['etiqueta']}")
    lineas.extend(_campo_bloque("sintoma", datos["sintoma"]))
    lineas.append(f"{IND}como_se_detecto: {datos['como_se_detecto']}")
    lineas.append(f"{IND}medida: {datos['medida'] if datos['medida'] is not None else 'null'}")
    if "estado_sin_medida" in datos:
        lineas.append(f"{IND}estado_sin_medida: {datos['estado_sin_medida']}")
    for opcional in ("resuelto", "limite_humano", "sin_medida_todavia"):
        if opcional in datos:
            lineas.extend(_campo_bloque(opcional, datos[opcional]))
    lineas.append(f"{IND}evidencia:")
    for relacion, filas in datos["evidencia"].items():
        lineas.extend(_lineas_relacion(relacion, filas))
    lineas.extend(_campo_bloque("leccion", datos["leccion"]))
    return "\n".join(lineas) + "\n"


def _rutas_en_corpus(raiz: Path) -> list[Path]:
    base = Path(raiz)
    if not base.exists():
        return []
    if base.is_symlink() or not base.is_dir():
        raise CasoMalDeclarado(f"el corpus debe ser un directorio físico: {base}")
    try:
        base_fisica = base.resolve()
    except OSError as e:
        raise CasoMalDeclarado(f"no se pudo resolver el corpus {base}: {e}") from e
    rutas = []
    for ruta in base.rglob("*"):
        if ruta.suffix not in EXTENSIONES_DE_CASO:
            continue
        if ruta.is_symlink():
            raise CasoMalDeclarado(f"un caso de corpus no puede ser symlink: {ruta}")
        try:
            fisica = ruta.resolve()
            fisica.relative_to(base_fisica)
        except (OSError, ValueError) as e:
            raise CasoMalDeclarado(f"el caso {ruta} no está confinado en {base_fisica}") from e
        if not fisica.is_file():
            raise CasoMalDeclarado(f"el caso debe ser un archivo físico: {ruta}")
        rutas.append(ruta)
    return sorted(rutas)


def rutas_de_corpus(raiz: Path) -> list[Path]:
    return _rutas_en_corpus(Path(raiz))


def cargar_fuente_caso(ruta: Path) -> dict:
    ruta = Path(ruta)
    try:
        texto = ruta.read_text(encoding="utf-8")
    except OSError as e:
        raise CasoMalDeclarado(f"no se pudo leer el caso {ruta}: {e}") from e
    if ruta.suffix == ".json":
        try:
            datos = json.loads(texto)
        except json.JSONDecodeError as e:
            raise CasoMalDeclarado(f"{ruta}: JSON inválido — {e}") from e
    elif ruta.suffix == ".caso":
        try:
            datos = leer(texto)
        except ErrorSintaxis as e:
            raise CasoMalDeclarado(f"{ruta}: {fragmento_de_error(e, texto)}") from e
    else:
        raise CasoMalDeclarado(
            f"formato de caso no soportado: {ruta} (esperaba .json o .caso)")
    if not isinstance(datos, dict):
        raise CasoMalDeclarado(f"{ruta}: la raíz del caso debe ser un objeto")
    cid = datos.get("id")
    if not isinstance(cid, str) or ID_CASO_RE.fullmatch(cid) is None:
        raise CasoMalDeclarado(
            f"{ruta}: id inválido: «{cid}» — debe ser `NNN-descripcion`, sólo con minúsculas "
            "ASCII, dígitos y `-`")
    return datos


def cargar_casos(raiz: Path) -> list[dict]:
    salida = []
    fuentes: dict[str, Path] = {}
    for ruta in rutas_de_corpus(raiz):
        datos = cargar_fuente_caso(ruta)
        cid = datos.get("id")
        if isinstance(cid, str):
            if cid in fuentes:
                raise CasoMalDeclarado(
                    f"el id «{cid}» está dos veces: {fuentes[cid]} y {ruta}")
            fuentes[cid] = ruta
        salida.append(datos)
    return salida
