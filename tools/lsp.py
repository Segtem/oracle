"""Servidor LSP mínimo de Oracle: publica diagnósticos y completado por stdio."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

RAIZ = Path(__file__).resolve().parents[1]
sys.path = [str(RAIZ), *sys.path]

from nucleo.caso import (DETECCIONES, ETIQUETAS, PROCEDENCIAS, CasoMalDeclarado,  # noqa: E402
                         cargar_casos, leer as leer_caso)
from nucleo.medida import (ORIGENES_DE_UMBRAL, Medida, MedidaMalDeclarada,  # noqa: E402
                           cargar_catalogo)
from nucleo.proyecto import (Proyecto, catalogos_a_cargar, macros_del_proyecto,  # noqa: E402
                             relaciones_del_proyecto)
from nucleo.sintaxis import IDENT_RE, ErrorSintaxis, leer_con_mapa  # noqa: E402
from nucleo.version import exigir_sintaxis_compatible  # noqa: E402
from tools.medida import (_evaluadas_aparte, ejercicio_del_catalogo,  # noqa: E402
                          esta_ejercitada, relaciones_por_alias,
                          texto_de_fijacion)
from tools.sesion import resolver_cli  # noqa: E402

ERROR = 1
AVISO = 2

# Dos mensajes porque son dos afirmaciones distintas. Con evidencia completa el aviso es un
# hecho; con evidencia incompleta —el catálogo no carga sin ejecutar código del proyecto, o un
# fixture diferencial está vencido— el aviso dice además qué no pudo mirar, que es lo que exige
# el propio lenguaje de un `alcance`.
MENSAJE_SIN_FIJAR = {
    True: "SIN FIJAR — ninguna evidencia la pone a prueba",
    False: ("SIN FIJAR — ningún caso del corpus la evalúa. No se pudieron leer los "
            "diferenciales, así que podría estar fijada por uno"),
}


def _rango(texto: str, linea: int, columna: int) -> dict:
    """El rango que el editor va a subrayar, con ancho garantizado.

    Un error como «se esperaba segun o porque» señala el lugar donde faltaba algo,
    y ese lugar suele ser el final de la línea: columna 16 sobre una línea de 15
    caracteres. Un rango de ancho cero es legal —el protocolo recorta la posición
    contra el fin de la línea— pero no se ve: el editor lo cuenta y lo marca en la
    regla lateral, y en el texto no dibuja nada. Se midió en VS Code y el síntoma
    era exactamente ése.

    Cuando el punto señalado no deja ancho, se subraya la línea entera sin su
    sangría, que es donde el lector tiene que mirar de todos modos. Si esa línea
    está en blanco se sube a la última con contenido, porque marcar el vacío del
    final del archivo tampoco dice nada.
    """
    lineas = texto.split("\n") or [""]
    numero = min(max(linea - 1, 0), len(lineas) - 1)
    principio = max(columna - 1, 0)
    fin = min(principio + 1, len(lineas[numero]))
    if fin > principio:
        return {"start": {"line": numero, "character": principio},
                "end": {"line": numero, "character": fin}}
    while numero > 0 and not lineas[numero].strip():
        numero -= 1
    contenido = lineas[numero]
    sangria = len(contenido) - len(contenido.lstrip())
    return {"start": {"line": numero, "character": sangria},
            "end": {"line": numero, "character": max(len(contenido), sangria + 1)}}


def _diagnostico(texto: str, mensaje: str, severidad: int,
                 linea: int = 1, columna: int = 1) -> dict:
    return {
        "range": _rango(texto, linea, columna),
        "severity": severidad,
        "source": "oracle",
        "message": mensaje,
    }


def diagnosticar(proy: Proyecto, ruta: Path, texto: str) -> list[dict]:
    try:
        if ruta.suffix == ".caso":
            leer_caso(texto)
            return []
        if ruta.suffix != ".oracle":
            return []
        macros = macros_del_proyecto(proy)
        lectura = leer_con_mapa(texto, macros=macros)
        exigir_sintaxis_compatible(lectura.version)
        medida = Medida.de_datos(lectura.datos, macros=macros)
        try:
            ruta.resolve().relative_to(proy.catalogos.resolve())
        except ValueError:
            pass
        else:
            # Quién contesta «¿está ejercitada?» es `meta.toda_medida_esta_ejercitada`, no este
            # archivo. Acá había un `any(caso["medida"] == medida.id ...)` que decía en Python lo
            # mismo que esa medida ya dice en Oracle, y las dos podían separarse sin que nada
            # avisara: la medida cuenta también los casos que aportan los fixtures diferenciales,
            # y aquella línea no los miraba. Es el mismo movimiento que ya hizo `tools/mutar.py`
            # cuando sacó su `if vivos: return 1`.
            ejercitada, completa = esta_ejercitada(proy, medida, macros)
            if ejercitada is False:
                ubicacion = lectura.ubicacion("1")
                return [_diagnostico(texto, MENSAJE_SIN_FIJAR[completa], AVISO,
                                     ubicacion.linea, ubicacion.columna)]
        return []
    except ErrorSintaxis as e:
        return [_diagnostico(texto, str(e), ERROR, e.linea, e.columna)]
    except (MedidaMalDeclarada, CasoMalDeclarado, ValueError) as e:
        return [_diagnostico(texto, str(e), ERROR)]


def lentes(proy: Proyecto, ruta: Path, texto: str) -> list[dict]:
    """La línea que el editor dibuja ARRIBA de la medida: qué la pone a prueba y con qué umbral.

    Es la misma vista que `python tools/medida.py --listar` imprime en la terminal, por archivo.
    Se arma con `texto_de_fijacion`, la única línea escrita para decirlo: el editor no tiene una
    segunda opinión sobre cuándo una medida está ejercitada.

    Lo que muestra viene de dos sitios distintos a propósito. «SIN FIJAR» es un VEREDICTO, y lo da
    `meta.toda_medida_esta_ejercitada`; «3 casos · 1 verde · 2 rojos» es EVIDENCIA del sensor de
    `nucleo/marco.py`, que se presenta sin juzgarla. Contar filas de una relación no es
    reimplementar un reclamo; decidir si ese conteo alcanza, sí, y de eso sigue respondiendo la
    medida.
    """
    if ruta.suffix != ".oracle":
        return []
    try:
        macros = macros_del_proyecto(proy)
        lectura = leer_con_mapa(texto, macros=macros)
        exigir_sintaxis_compatible(lectura.version)
        medida = Medida.de_datos(lectura.datos, macros=macros)
    except (ErrorSintaxis, MedidaMalDeclarada, ValueError):
        # Una medida que no se puede leer ya tiene su diagnóstico. Un lens con datos a medias
        # sobre un archivo roto sería ruido encima del error que hay que arreglar primero.
        return []

    ejercicio = ejercicio_del_catalogo(proy, {medida.id: medida}, macros)
    partes = [texto_de_fijacion(medida.id, ejercicio)]
    verdes, rojos = ejercicio.polaridad_por_medida.get(medida.id, (0, 0))
    if verdes or rojos:
        partes.append(f"{verdes} verde" + ("s" if verdes != 1 else ""))
        partes.append(f"{rojos} rojo" + ("s" if rojos != 1 else ""))
    partes.append(f"umbral {medida.op} {medida.limite} segun {medida.segun}")

    ubicacion = lectura.ubicacion("1")
    linea = ubicacion.linea - 1
    return [{"range": {"start": {"line": linea, "character": 0},
                       "end": {"line": linea, "character": 0}},
             "command": {"title": " · ".join(partes), "command": ""}}]


def _contexto(texto: str, posicion: dict) -> tuple[str, int]:
    """Prefijo de línea e índice Python; LSP cuenta UTF-16, no puntos de código."""
    lineas = texto.split("\n")
    numero = posicion["line"]
    linea = lineas[numero]
    unidades = posicion["character"]
    usadas = 0
    columna = 0
    while usadas < unidades:
        usadas += 2 if ord(linea[columna]) > 0xFFFF else 1
        columna += 1
    if usadas != unidades:
        raise ValueError("la posición LSP parte un carácter UTF-16")
    indice = sum(len(anterior) + 1 for anterior in lineas[:numero]) + columna
    return linea[:columna], indice


def _items(valores) -> list[dict]:
    return [{"label": valor} for valor in sorted(valores)]


def _es_contexto(prefijo: str, clave: str) -> bool:
    return re.fullmatch(rf"\s*{re.escape(clave)}:\s*\S*", prefijo) is not None


def _datos_de_medida_incompleta(proy: Proyecto, texto: str, indice: int,
                                campo_parcial: str) -> list | None:
    insercion = "campo_completado" if not campo_parcial else ""
    candidato = texto[:indice] + insercion + texto[indice:]
    try:
        macros = macros_del_proyecto(proy)
        lectura = leer_con_mapa(candidato, macros=macros)
        exigir_sintaxis_compatible(lectura.version)
        return Medida.de_datos(lectura.datos, macros=macros).a_datos()
    except (ErrorSintaxis, MedidaMalDeclarada, ValueError):
        return None


def completar(proy: Proyecto, ruta: Path, texto: str, posicion: dict) -> list[dict]:
    prefijo, indice = _contexto(texto, posicion)

    # La prosa es una decisión humana. Tiene prioridad sobre cualquier palabra que aparezca dentro.
    if re.match(r"\s*alcance\b", prefijo):
        return []
    if re.search(r"(?:^|\s)porque(?:\s|$)", prefijo):
        return []

    if ruta.suffix == ".caso":
        for clave, valores in (
            ("etiqueta", ETIQUETAS),
            ("procedencia", PROCEDENCIAS),
            ("como_se_detecto", DETECCIONES),
        ):
            if _es_contexto(prefijo, clave):
                return _items(valores)
        if _es_contexto(prefijo, "medida"):
            try:
                catalogo = cargar_catalogo(
                    catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
            except (MedidaMalDeclarada, ValueError, OSError):
                return []
            return _items(catalogo)
        return []

    if ruta.suffix != ".oracle":
        return []
    if re.fullmatch(r"\s*umbral\b.*\bsegun\s+\S*", prefijo):
        return _items(ORIGENES_DE_UMBRAL)
    if re.fullmatch(r"\s*(?:de|unir)\s+\S*", prefijo):
        try:
            relaciones = relaciones_del_proyecto(proy)
        except (ValueError, OSError):
            return []
        return [
            {"label": nombre, "documentation": relacion.alcance}
            for nombre, relacion in sorted(relaciones.items())
        ]

    campo = re.search(rf"({IDENT_RE.pattern})\.(\S*)$", prefijo)
    if campo is None:
        return []
    datos = _datos_de_medida_incompleta(proy, texto, indice, campo.group(2))
    if datos is None:
        return []
    relacion_nombre = relaciones_por_alias(datos).get(campo.group(1))
    try:
        relacion = relaciones_del_proyecto(proy).get(relacion_nombre)
    except (ValueError, OSError):
        return []
    if relacion is None:
        return []
    return [
        {"label": c.nombre, "detail": f"{c.tipo} · {c.unidad}"}
        for c in relacion.campos
    ]


def _ruta_de_uri(uri: str) -> Path:
    partes = urlsplit(uri)
    if partes.scheme != "file" or partes.netloc not in ("", "localhost"):
        raise ValueError(f"URI de archivo inválida: {uri!r}")
    return Path(unquote(partes.path))


def _leer_mensaje(entrada) -> dict | None:
    cabeceras = {}
    while True:
        linea = entrada.readline()
        if not linea:
            if cabeceras:
                raise EOFError("cabecera truncada")
            return None
        if linea in (b"\r\n", b"\n"):
            break
        nombre, separador, valor = linea.decode("ascii").partition(":")
        if not separador:
            raise ValueError("cabecera LSP sin ':'")
        cabeceras[nombre.lower()] = valor.strip()
    largo = int(cabeceras["content-length"])
    cuerpo = entrada.read(largo)
    if len(cuerpo) != largo:
        raise EOFError("cuerpo LSP truncado")
    mensaje = json.loads(cuerpo.decode("utf-8"))
    if not isinstance(mensaje, dict):
        raise ValueError("el mensaje LSP debe ser un objeto JSON")
    return mensaje


def _enviar(salida, mensaje: dict) -> None:
    cuerpo = json.dumps(mensaje, separators=(",", ":")).encode("utf-8")
    salida.write(f"Content-Length: {len(cuerpo)}\r\n\r\n".encode("ascii") + cuerpo)
    salida.flush()


class Servidor:
    def __init__(self, proy: Proyecto, salida) -> None:
        self.proy = proy
        self.salida = salida
        self.apagado = False
        self.documentos: dict[str, str] = {}

    def _respuesta(self, mensaje: dict, resultado) -> None:
        _enviar(self.salida, {"jsonrpc": "2.0", "id": mensaje["id"], "result": resultado})

    def _publicar(self, uri: str, texto: str | None, version=None) -> None:
        parametros = {"uri": uri, "diagnostics": (
            [] if texto is None else diagnosticar(self.proy, _ruta_de_uri(uri), texto))}
        if version is not None:
            parametros["version"] = version
        _enviar(self.salida, {
            "jsonrpc": "2.0", "method": "textDocument/publishDiagnostics",
            "params": parametros,
        })

    def manejar(self, mensaje: dict) -> bool:
        metodo = mensaje.get("method")
        if metodo == "initialize":
            self._respuesta(mensaje, {"capabilities": {
                "textDocumentSync": {"openClose": True, "change": 1},
                "completionProvider": {"triggerCharacters": ["."]},
                "codeLensProvider": {"resolveProvider": False},
            }})
        elif metodo == "shutdown":
            self.apagado = True
            self._respuesta(mensaje, None)
        elif metodo == "exit":
            return False
        elif metodo == "textDocument/didOpen":
            documento = mensaje["params"]["textDocument"]
            self.documentos[documento["uri"]] = documento["text"]
            self._publicar(documento["uri"], documento["text"], documento.get("version"))
        elif metodo == "textDocument/didChange":
            params = mensaje["params"]
            cambios = params["contentChanges"]
            if len(cambios) != 1 or set(cambios[0]) != {"text"}:
                raise ValueError("didChange requiere un único cambio de texto completo")
            documento = params["textDocument"]
            self.documentos[documento["uri"]] = cambios[0]["text"]
            self._publicar(documento["uri"], cambios[0]["text"], documento.get("version"))
        elif metodo == "textDocument/didClose":
            uri = mensaje["params"]["textDocument"]["uri"]
            self.documentos.pop(uri, None)
            self._publicar(uri, None)
        elif metodo == "textDocument/codeLens":
            uri = mensaje["params"]["textDocument"]["uri"]
            texto = self.documentos.get(uri)
            self._respuesta(mensaje, [] if texto is None else lentes(
                self.proy, _ruta_de_uri(uri), texto))
        elif metodo == "textDocument/completion":
            params = mensaje["params"]
            uri = params["textDocument"]["uri"]
            texto = self.documentos.get(uri)
            resultado = ([] if texto is None else completar(
                self.proy, _ruta_de_uri(uri), texto, params["position"]))
            self._respuesta(mensaje, resultado)
        elif "id" in mensaje:
            _enviar(self.salida, {
                "jsonrpc": "2.0", "id": mensaje["id"],
                "error": {"code": -32601, "message": f"método no soportado: {metodo}"},
            })
        return True


def servir(proy: Proyecto, entrada, salida) -> int:
    servidor = Servidor(proy, salida)
    while True:
        mensaje = _leer_mensaje(entrada)
        if mensaje is None or not servidor.manejar(mensaje):
            return 0 if servidor.apagado else 1


def main(argv: list[str] | None = None) -> int:
    proy = resolver_cli(list(sys.argv[1:] if argv is None else argv))
    if proy is None:
        return 1
    return servir(proy, sys.stdin.buffer, sys.stdout.buffer)


for _punto_de_entrada in {"__main__": (main,)}.get(__name__, ()):
    sys.exit(_punto_de_entrada())
