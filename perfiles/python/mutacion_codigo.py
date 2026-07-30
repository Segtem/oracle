"""Perfil Python de mutación de CÓDIGO — la otra mitad del sensor.

`mutacion.py` muta medidas, que son datos. Esto copia el proyecto y muta allí el árbol sintáctico de
archivos `.py`; nunca escribe sobre las fuentes activas. Es más caro y hace falta igual: los tests que
no discriminan sólo se ven rompiendo el código que dicen cubrir.

## Los mutantes se GENERAN, no se declaran

Es la decisión de diseño del módulo. Si el autor elige qué romper, elige —sin querer— lo que sus
tests ya atrapan, que es el sesgo del que todo este repositorio intenta salir. Un recorrido del AST
no tiene opinión: propone todo lo que puede proponer, y los sobrevivientes son la lista honesta de lo
que nadie está fijando.

Cinco operadores, deliberadamente pocos:

  · `comparador`  <  ↔  <=   ·  >  ↔  >=   ·  ==  ↔  !=   ·  is ↔ is not   ·  in ↔ not in
  · `booleano`    and ↔ or
  · `negacion`    se borra un `not`
  · `constante`   n → n+1  ·  True ↔ False
  · `retorno`     `return <algo>` → `return None`

## El caché

Cada ejecución limpia `__pycache__` en la copia, usa un prefijo de caché temporal y vuelve a
inspeccionar el árbol después de correr los tests. No es prolijidad: `max` y `min` ocupan lo mismo y CPython invalida
el `.pyc` por (mtime, tamaño), así que mutar y restaurar dentro del mismo segundo deja al intérprete
corriendo bytecode vencido. Si un caché reaparece, la ronda falla antes de borrarlo: limpiar después
no puede borrar también la evidencia del incidente. Es el caso `006` del corpus.

## Mutantes equivalentes

Algunos mutantes no cambian el comportamiento y no se pueden matar (un `<` que sólo compara enteros
donde el borde es imposible, un mensaje de error). Se pueden declarar en `equivalentes.json`, pero
**con una razón escrita**, igual que un umbral lleva su defensa. Un equivalente sin razón es una
excusa, y el número de equivalentes declarados es una métrica que hay que mirar.
"""

from __future__ import annotations

import ast
import fcntl
import hashlib
import json
import math
import os
import shutil
import signal
import subprocess
import tempfile
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class LineaBaseFallida(RuntimeError):
    """Los tests ya fallan sobre el código original, así que la mutación no puede dar evidencia."""

    def __init__(self, resultado: "ResultadoTests"):
        self.resultado = resultado
        diagnostico = resultado.salida.strip() or "(sin salida diagnóstica)"
        super().__init__(
            f"la línea base no fue verde ({resultado.estado.value}, "
            f"código {resultado.codigo_salida!r}):\n{diagnostico}")


class CacheNoLimpio(RuntimeError):
    """No se pudo garantizar que la próxima corrida lea bytecode nuevo."""


class EquivalenteInvalido(ValueError):
    """Una exclusión de mutación no tiene sitio vigente o razón defendible."""


class ObjetivoInvalido(ValueError):
    """Una fuente a mutar no es un archivo físico confinado dentro de la raíz."""


class RondaEnCurso(RuntimeError):
    """Otra ronda ya posee el bloqueo estable de esta raíz."""


class AislamientoRoto(RuntimeError):
    """La raíz original cambió mientras la ronda debía operar sólo sobre su copia."""


class ManifiestoInvalido(ValueError):
    """Un estado reanudable no corresponde exactamente a esta ronda."""


ESQUEMA_MANIFIESTO = "oracle.mutacion-codigo/v1"


class EstadoTests(str, Enum):
    """Resultado observable de una invocación del arnés.

    El código 1 significa fallo discriminante sólo porque el comando acuerda ese protocolo. Cualquier
    otro no-cero es un error del arnés: analizar texto de pytest/unittest sería hardcodear otro caso
    particular y volver a confundir una colección rota con un mutante muerto.
    """

    PASARON = "pasaron"
    TESTS_FALLARON = "tests_fallaron"
    ERROR_ARNES = "error_arnes"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class ResultadoTests:
    estado: EstadoTests
    codigo_salida: int | None
    stdout: str = ""
    stderr: str = ""
    stdout_truncado: bool = False
    stderr_truncado: bool = False

    @property
    def salida(self) -> str:
        partes = []
        if self.stdout:
            partes.append(self.stdout.rstrip())
        if self.stderr:
            partes.append(self.stderr.rstrip())
        return "\n".join(partes)

    @property
    def pasaron(self) -> bool:
        return self.estado is EstadoTests.PASARON

    @property
    def tests_fallaron(self) -> bool:
        return self.estado is EstadoTests.TESTS_FALLARON

    @property
    def error_arnes(self) -> bool:
        return self.estado is EstadoTests.ERROR_ARNES

    @property
    def timeout(self) -> bool:
        return self.estado is EstadoTests.TIMEOUT


_PROCESOS_ACTIVOS: set[subprocess.Popen] = set()
_PROCESOS_GUARDA = threading.Lock()

CAMBIOS_COMPARADOR = {
    ast.Lt: ast.LtE, ast.LtE: ast.Lt,
    ast.Gt: ast.GtE, ast.GtE: ast.Gt,
    ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
    ast.Is: ast.IsNot, ast.IsNot: ast.Is,
    ast.In: ast.NotIn, ast.NotIn: ast.In,
}


@dataclass(frozen=True)
class Sitio:
    """Un lugar mutable del archivo. El `id` tiene que ser estable entre corridas."""

    archivo: str
    linea: int
    columna: int
    operador: str
    descripcion: str

    @property
    def id(self) -> str:
        return f"{self.archivo}:{self.linea}:{self.columna}:{self.operador}"


class _Recolector(ast.NodeVisitor):
    def __init__(self, archivo: str):
        self.archivo = archivo
        self.sitios: list[Sitio] = []

    def _añadir(self, nodo, operador, descripcion):
        self.sitios.append(Sitio(self.archivo, getattr(nodo, "lineno", 0),
                                 getattr(nodo, "col_offset", 0), operador, descripcion))

    def visit_Compare(self, nodo):
        for op in nodo.ops:
            if type(op) in CAMBIOS_COMPARADOR:
                self._añadir(nodo, "comparador",
                             f"{type(op).__name__} → {CAMBIOS_COMPARADOR[type(op)].__name__}")
                break
        self.generic_visit(nodo)

    def visit_BoolOp(self, nodo):
        self._añadir(nodo, "booleano", "and ↔ or")
        self.generic_visit(nodo)

    def visit_UnaryOp(self, nodo):
        if isinstance(nodo.op, ast.Not):
            self._añadir(nodo, "negacion", "se borra el `not`")
        self.generic_visit(nodo)

    def visit_Constant(self, nodo):
        if isinstance(nodo.value, bool):
            self._añadir(nodo, "constante", f"{nodo.value} → {not nodo.value}")
        elif isinstance(nodo.value, (int, float)):
            self._añadir(nodo, "constante", f"{nodo.value} → {nodo.value + 1}")

    def visit_Return(self, nodo):
        if nodo.value is not None and not (
                isinstance(nodo.value, ast.Constant) and nodo.value.value is None):
            self._añadir(nodo, "retorno", "return <algo> → return None")
        self.generic_visit(nodo)


class _Aplicador(ast.NodeTransformer):
    """Aplica UN solo sitio. Un mutante = un cambio, o no se sabe cuál mató al test."""

    def __init__(self, objetivo: Sitio):
        self.objetivo = objetivo
        self.aplicado = False

    def _es(self, nodo, operador) -> bool:
        return (not self.aplicado
                and getattr(nodo, "lineno", -1) == self.objetivo.linea
                and getattr(nodo, "col_offset", -1) == self.objetivo.columna
                and operador == self.objetivo.operador)

    def visit_Compare(self, nodo):
        self.generic_visit(nodo)
        if self._es(nodo, "comparador"):
            for i, op in enumerate(nodo.ops):
                if type(op) in CAMBIOS_COMPARADOR:
                    nodo.ops[i] = CAMBIOS_COMPARADOR[type(op)]()
                    self.aplicado = True
                    break
        return nodo

    def visit_BoolOp(self, nodo):
        self.generic_visit(nodo)
        if self._es(nodo, "booleano"):
            nodo.op = ast.Or() if isinstance(nodo.op, ast.And) else ast.And()
            self.aplicado = True
        return nodo

    def visit_UnaryOp(self, nodo):
        self.generic_visit(nodo)
        if isinstance(nodo.op, ast.Not) and self._es(nodo, "negacion"):
            self.aplicado = True
            return nodo.operand
        return nodo

    def visit_Constant(self, nodo):
        if self._es(nodo, "constante"):
            if isinstance(nodo.value, bool):
                nodo = ast.Constant(value=not nodo.value)
            elif isinstance(nodo.value, (int, float)):
                nodo = ast.Constant(value=nodo.value + 1)
            self.aplicado = True
        return nodo

    def visit_Return(self, nodo):
        self.generic_visit(nodo)
        if self._es(nodo, "retorno"):
            nodo.value = ast.Constant(value=None)
            self.aplicado = True
        return nodo


def sitios_de(ruta: Path, raiz: Path) -> list[Sitio]:
    rel = str(ruta.relative_to(raiz))
    r = _Recolector(rel)
    r.visit(ast.parse(ruta.read_text(encoding="utf-8")))
    return r.sitios


def mutar_fuente(fuente: str, sitio: Sitio) -> str | None:
    arbol = ast.parse(fuente)
    ap = _Aplicador(sitio)
    nuevo = ap.visit(arbol)
    if not ap.aplicado:
        return None
    ast.fix_missing_locations(nuevo)
    return ast.unparse(nuevo)


def _caches_bajo(raiz: Path) -> list[Path]:
    """Encuentra caches sin seguir symlinks y falla cerrado si no puede recorrer el árbol.

    Un enlace llamado `__pycache__` cuenta, incluso roto. Un cache oculto detrás de otro enlace de
    directorio queda fuera del árbol físico de `raiz`: seguirlo permitiría borrar fuera del proyecto.
    """
    encontrados: list[Path] = []

    def fallar(error: OSError) -> None:
        raise error

    try:
        for actual, directorios, archivos in os.walk(
                raiz, topdown=True, followlinks=False, onerror=fallar):
            base = Path(actual)
            for nombre in (*directorios, *archivos):
                if nombre == "__pycache__":
                    encontrados.append(base / nombre)
            # No hace falta entrar a un cache para borrarlo y hacerlo ampliaría la superficie de
            # recorrido. Los demás enlaces de directorio tampoco se siguen (`followlinks=False`).
            directorios[:] = [d for d in directorios if d != "__pycache__"]
    except OSError as e:
        raise CacheNoLimpio(f"no se pudo inspeccionar el árbol de caché «{raiz}»: {e}") from e
    return sorted(encontrados, key=lambda p: len(p.parts), reverse=True)


def limpiar_cache(raiz: Path) -> int:
    """Borra y COMPRUEBA todo `__pycache__` bajo `raiz`.

    Un intento de borrado no es evidencia de caché frío. Los symlinks se desenlazan sin seguirlos: un
    proyecto no puede hacer que limpiar su caché borre un directorio ajeno.
    """
    try:
        raiz_fisica = raiz.resolve(strict=True)
    except OSError as e:
        raise CacheNoLimpio(f"no se pudo resolver la raíz de caché «{raiz}»: {e}") from e

    encontrados = _caches_bajo(raiz)
    for d in encontrados:
        # `_caches_bajo` también es código mutable. La enumeración nunca obtiene autoridad de
        # borrado por sí sola: una segunda guarda independiente evita que mutar `==` a `!=` convierta
        # cada entrada del proyecto en supuesto caché. Se comprueba el padre físico para poder
        # desenlazar con seguridad un `__pycache__` symlink sin seguir su destino.
        if d.name != "__pycache__":
            raise CacheNoLimpio(f"se rechazó borrar una ruta que no es caché: «{d}»")
        try:
            d.parent.resolve(strict=True).relative_to(raiz_fisica)
        except (OSError, ValueError) as e:
            raise CacheNoLimpio(
                f"se rechazó borrar un caché fuera de la raíz «{raiz}»: «{d}»") from e
        if not d.exists() and not d.is_symlink():
            continue
        try:
            if d.is_symlink() or not d.is_dir():
                d.unlink()
            else:
                shutil.rmtree(d)
        except OSError as e:
            raise CacheNoLimpio(f"no se pudo borrar el caché «{d}»: {e}") from e

    restantes = _caches_bajo(raiz)
    if restantes:
        muestra = ", ".join(str(p) for p in restantes[:3])
        raise CacheNoLimpio(f"siguen presentes cachés después de limpiar: {muestra}")
    return len(encontrados)


def cache_esta_frio(raiz: Path) -> bool:
    """La afirmación que se publica como hecho, derivada del árbol en vez de fijada a mano."""
    return not _caches_bajo(raiz)


def _terminar_proceso(proceso: subprocess.Popen) -> None:
    try:
        os.killpg(proceso.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proceso.wait(timeout=1)
    except subprocess.TimeoutExpired:
        pass
    # El líder puede salir con SIGTERM mientras un nieto lo ignora. El grupo sigue existiendo aunque
    # `wait()` del líder ya haya terminado; se lo mata completo antes de devolver control.
    try:
        os.killpg(proceso.pid, 0)
    except ProcessLookupError:
        return
    else:
        try:
            os.killpg(proceso.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            proceso.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass


def _terminar_activos() -> None:
    with _PROCESOS_GUARDA:
        activos = list(_PROCESOS_ACTIVOS)
    for proceso in activos:
        _terminar_proceso(proceso)


def _leer_acotado(canal, limite: int, salida: list[bytes], estado: dict) -> None:
    total = 0
    try:
        while bloque := canal.read(8192):
            disponible = max(0, limite - total)
            if disponible:
                salida.append(bloque[:disponible])
            total += len(bloque)
    finally:
        estado["truncado"] = total > limite
        canal.close()


def ejecutar_tests(comando: list[str], raiz: Path, *, timeout: float,
                   codigos_fallo_tests=frozenset({1}), entorno=None,
                   limite_salida: int = 1_048_576) -> ResultadoTests:
    """Ejecuta un comando y conserva su categoría y diagnóstico.

    El protocolo por defecto reserva 0 para verde y 1 para tests que discriminaron. Otros códigos,
    señales y errores al lanzar son fallos del arnés. Un runner con otra convención debe declarar
    `codigos_fallo_tests`; inferirlo del texto haría esta función dependiente de un framework.
    """
    if (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout) or timeout <= 0):
        raise ValueError("timeout tiene que ser un número finito mayor que cero")
    codigos = frozenset(codigos_fallo_tests)
    if any(type(c) is not int or c <= 0 for c in codigos):
        raise ValueError("los códigos de fallo de tests tienen que ser enteros estrictamente positivos")
    if not comando:
        return ResultadoTests(EstadoTests.ERROR_ARNES, None, stderr="comando de tests vacío")
    if type(limite_salida) is not int or limite_salida <= 0:
        raise ValueError("limite_salida tiene que ser un entero positivo")

    try:
        proceso = subprocess.Popen(
            comando, cwd=str(raiz), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=entorno, start_new_session=True)
    except (OSError, ValueError) as e:
        return ResultadoTests(EstadoTests.ERROR_ARNES, None, stderr=f"{type(e).__name__}: {e}")

    stdout_b, stderr_b = [], []
    estado_out, estado_err = {}, {}
    lectores = [
        threading.Thread(target=_leer_acotado,
                         args=(proceso.stdout, limite_salida, stdout_b, estado_out), daemon=True),
        threading.Thread(target=_leer_acotado,
                         args=(proceso.stderr, limite_salida, stderr_b, estado_err), daemon=True),
    ]
    with _PROCESOS_GUARDA:
        _PROCESOS_ACTIVOS.add(proceso)
    for lector in lectores:
        lector.start()
    agotado = False
    try:
        try:
            codigo = proceso.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            agotado = True
            _terminar_proceso(proceso)
            codigo = None
    finally:
        for lector in lectores:
            lector.join(timeout=3)
        with _PROCESOS_GUARDA:
            _PROCESOS_ACTIVOS.discard(proceso)

    stdout = b"".join(stdout_b).decode("utf-8", errors="replace")
    stderr = b"".join(stderr_b).decode("utf-8", errors="replace")
    truncado_out = estado_out.get("truncado", False)
    truncado_err = estado_err.get("truncado", False)
    if agotado:
        return ResultadoTests(
            EstadoTests.TIMEOUT, None, stdout, stderr, truncado_out, truncado_err)

    if codigo == 0:
        estado = EstadoTests.PASARON
    elif codigo in codigos:
        estado = EstadoTests.TESTS_FALLARON
    else:
        estado = EstadoTests.ERROR_ARNES
    return ResultadoTests(estado, codigo, stdout, stderr, truncado_out, truncado_err)


def correr_tests(comando: list[str], raiz: Path, timeout: float = 60.0) -> bool:
    """Wrapper booleano histórico; la ronda usa `ejecutar_tests` para no perder estados."""
    return ejecutar_tests(comando, raiz, timeout=timeout).pasaron


def _ejecutar_ronda(comando: list[str], raiz: Path, *, timeout: float,
                    codigos_fallo_tests, etapa: str,
                    permitir_cache_preexistente: bool = False,
                    limite_salida: int = 1_048_576) -> ResultadoTests:
    """Ejecuta una ronda entre dos fronteras comprobadas de caché frío.

    `PYTHONPYCACHEPREFIX` apunta a un directorio temporal fresco para que CPython tampoco lea un pyc
    local que aparezca en la ventana entre la comprobación y el `exec`. Además se desactiva la
    escritura de bytecode. Si aun así el comando crea un `__pycache__` explícito, se detecta ANTES de
    borrarlo y la ronda se invalida. No se afirma vigilancia continua frente a un proceso adversario
    que cree y borre un cache entre ambos escaneos.
    """
    if not permitir_cache_preexistente:
        reaparecidos_antes = _caches_bajo(raiz)
        if reaparecidos_antes:
            muestra = ", ".join(
                str(p.relative_to(raiz)) for p in reaparecidos_antes[:3])
            try:
                raise CacheNoLimpio(
                    f"reapareció caché antes de ejecutar {etapa}: {muestra}")
            finally:
                limpiar_cache(raiz)
    limpiar_cache(raiz)
    resultado: ResultadoTests | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="oracle-pyc-") as prefijo:
            entorno = os.environ.copy()
            entorno["PYTHONPYCACHEPREFIX"] = prefijo
            entorno["PYTHONDONTWRITEBYTECODE"] = "1"
            resultado = ejecutar_tests(
                comando, raiz, timeout=timeout,
                codigos_fallo_tests=codigos_fallo_tests, entorno=entorno,
                limite_salida=limite_salida)

        reaparecidos = _caches_bajo(raiz)
        if reaparecidos:
            muestra = ", ".join(str(p.relative_to(raiz)) for p in reaparecidos[:3])
            error = CacheNoLimpio(
                f"reapareció caché después de ejecutar {etapa}: {muestra}")
            error.resultado = resultado
            raise error
        return resultado
    finally:
        # También deja el árbol recuperado cuando la comprobación anterior acaba de demostrar una
        # reaparición. La excepción conserva el hecho; limpiar después no lo convierte en verde.
        limpiar_cache(raiz)


def _diagnostico(resultado: ResultadoTests, limite: int) -> tuple[str, bool]:
    salida = resultado.salida.strip() or "(sin salida diagnóstica)"
    truncada_en_captura = resultado.stdout_truncado or resultado.stderr_truncado
    if len(salida) <= limite:
        sufijo = "\n… salida acotada durante la ejecución …" if truncada_en_captura else ""
        return salida + sufijo, truncada_en_captura
    return salida[:limite] + "\n… salida truncada …", True


def _comprobar_cierre_frio(raiz: Path) -> None:
    reaparecidos = _caches_bajo(raiz)
    if not reaparecidos:
        return
    muestra = ", ".join(str(p.relative_to(raiz)) for p in reaparecidos[:3])
    try:
        raise CacheNoLimpio(f"reapareció caché antes de cerrar la ronda: {muestra}")
    finally:
        limpiar_cache(raiz)


def _validar_objetivos(raiz: Path, objetivos: list[Path]) -> None:
    """Resuelve cada fuente antes de leerla y rechaza enlaces o escapes de la raíz.

    `write_text` sigue symlinks. Sin esta frontera, un `nucleo/modulo.py` enlazado podía hacer que la
    ronda mutara temporalmente un archivo ajeno al proyecto y que una interrupción lo dejara roto.
    """
    try:
        raiz_fisica = raiz.resolve(strict=True)
    except (OSError, RuntimeError) as e:
        raise ObjetivoInvalido(f"no se pudo resolver la raíz «{raiz}»: {e}") from e
    if not raiz_fisica.is_dir():
        raise ObjetivoInvalido(f"la raíz de mutación no es un directorio: «{raiz}»")

    for ruta in objetivos:
        if ruta.is_symlink():
            raise ObjetivoInvalido(f"el objetivo de mutación no puede ser un symlink: «{ruta}»")
        try:
            fisica = ruta.resolve(strict=True)
        except (OSError, RuntimeError) as e:
            raise ObjetivoInvalido(f"no se pudo resolver el objetivo «{ruta}»: {e}") from e
        try:
            fisica.relative_to(raiz_fisica)
        except ValueError as e:
            raise ObjetivoInvalido(
                f"el objetivo de mutación escapa de la raíz «{raiz}»: «{ruta}»") from e
        if not fisica.is_file():
            raise ObjetivoInvalido(f"el objetivo de mutación no es un archivo: «{ruta}»")


def _escribir_atomico(ruta: Path, contenido: str) -> None:
    """Reemplaza un archivo completo sin exponer una escritura parcial dentro de la copia."""
    modo = ruta.stat().st_mode
    descriptor, temporal = tempfile.mkstemp(prefix=f".{ruta.name}.", dir=ruta.parent)
    temporal = Path(temporal)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as archivo:
            archivo.write(contenido)
            archivo.flush()
            os.fsync(archivo.fileno())
        os.chmod(temporal, modo)
        os.replace(temporal, ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def _json_canonico(datos) -> str:
    return json.dumps(datos, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _huella_json(datos) -> str:
    return hashlib.sha256(_json_canonico(datos).encode("utf-8")).hexdigest()


def _escribir_manifiesto(ruta: Path, datos: dict) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporal = tempfile.mkstemp(prefix=f".{ruta.name}.", dir=ruta.parent)
    temporal = Path(temporal)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, sort_keys=True, indent=2)
            archivo.write("\n")
            archivo.flush()
            os.fsync(archivo.fileno())
        os.replace(temporal, ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def _identidad_ronda(raiz: Path, objetivos: list[Path], comando: list[str], equivalentes: dict,
                     timeout: float, codigos, limite_salida: int) -> dict:
    fuentes = [{"ruta": ruta.resolve().relative_to(raiz).as_posix(),
                "sha256": hashlib.sha256(ruta.read_bytes()).hexdigest()}
               for ruta in objetivos]
    motor = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return {"raiz": str(raiz), "fuentes": fuentes, "comando": comando,
            "equivalentes": equivalentes, "timeout": timeout,
            "codigos_fallo_tests": sorted(codigos), "limite_salida": limite_salida,
            "motor_sha256": motor}


def _cargar_reanudacion(ruta: Path, identidad: dict, sitios: dict[str, Sitio]) -> tuple[dict, list[dict]]:
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ManifiestoInvalido(f"no se pudo leer {ruta}: {e}") from e
    if not isinstance(datos, dict) or datos.get("esquema") != ESQUEMA_MANIFIESTO:
        raise ManifiestoInvalido("esquema de manifiesto ausente o desconocido")
    if datos.get("identidad") != identidad or datos.get("huella") != _huella_json(identidad):
        raise ManifiestoInvalido("el manifiesto pertenece a otras fuentes, motor o configuración")
    filas = datos.get("completados")
    if not isinstance(filas, list) or datos.get("huella_completados") != _huella_json(filas):
        raise ManifiestoInvalido("los resultados completados no tienen una huella válida")
    ids = [fila.get("id") for fila in filas if isinstance(fila, dict)]
    if len(ids) != len(filas) or len(set(ids)) != len(ids) or not set(ids) <= set(sitios):
        raise ManifiestoInvalido("el manifiesto contiene ids inválidos, duplicados o vencidos")
    requeridos = {"apunta_a", "cambio", "murio", "estado", "tests_fallaron", "error_arnes",
                  "timeout", "codigo_salida", "equivalente_declarado", "razon_equivalente"}
    for fila in filas:
        sitio = sitios[fila["id"]]
        if (not requeridos <= set(fila)
                or fila["apunta_a"] != sitio.archivo
                or fila["cambio"] != f"{sitio.operador}: {sitio.descripcion}"
                or fila["estado"] not in {estado.value for estado in EstadoTests}
                or type(fila["murio"]) is not bool
                or fila["murio"] != fila["tests_fallaron"]
                or fila["equivalente_declarado"] != (fila["id"] in identidad["equivalentes"])
                or fila["razon_equivalente"] != identidad["equivalentes"].get(fila["id"], "")):
            raise ManifiestoInvalido(f"resultado inválido para {fila.get('id')}")
    return datos, filas


@contextmanager
def _bloqueo_de_ronda(raiz: Path):
    identificador = hashlib.sha256(str(raiz.resolve()).encode("utf-8")).hexdigest()[:24]
    ruta = Path(tempfile.gettempdir()) / f"oracle-mutacion-{identificador}.lock"
    archivo = ruta.open("a+", encoding="utf-8")
    try:
        try:
            fcntl.flock(archivo.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as e:
            archivo.seek(0)
            duenio = archivo.read().strip() or "desconocido"
            raise RondaEnCurso(f"ya hay una ronda para {raiz} (pid {duenio})") from e
        archivo.seek(0)
        archivo.truncate()
        archivo.write(str(os.getpid()))
        archivo.flush()
        yield
    finally:
        try:
            fcntl.flock(archivo.fileno(), fcntl.LOCK_UN)
        finally:
            archivo.close()


@contextmanager
def _senales_de_ronda():
    """Instala handlers sólo mientras una ronda posee recursos y los restaura al salir."""
    if threading.current_thread() is not threading.main_thread():
        yield
        return
    anteriores = {}

    def terminar(sig, _marco):
        _terminar_activos()
        raise SystemExit(128 + sig)

    try:
        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            anteriores[sig] = signal.getsignal(sig)
            signal.signal(sig, terminar)
        yield
    finally:
        _terminar_activos()
        for sig, anterior in anteriores.items():
            signal.signal(sig, anterior)


def _copiar_proyecto(raiz: Path, destino: Path) -> None:
    shutil.copytree(
        raiz, destino, symlinks=True,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))


def _comando_en_copia(comando: list[str], raiz: Path, copia: Path) -> list[str]:
    salida = []
    raiz_fisica = raiz.resolve()
    for argumento in comando:
        reemplazo = argumento
        try:
            ruta = Path(argumento)
            if ruta.is_absolute():
                relativa = ruta.resolve(strict=False).relative_to(raiz_fisica)
                reemplazo = str(copia / relativa)
        except (OSError, ValueError):
            pass
        salida.append(reemplazo)
    return salida


def _correr_en_raiz(raiz: Path, objetivos: list[Path], comando: list[str],
                     equivalentes: dict[str, str] | None = None, al_terminar_uno=None, *,
                     timeout_por_ejecucion: float = 60.0,
                     codigos_fallo_tests=frozenset({1}), limite_diagnostico: int = 16_384,
                     limite_salida: int = 1_048_576,
                     filas_previas: list[dict] | None = None) -> dict:
    """Genera y prueba todos los mutantes. Devuelve EVIDENCIA, no un informe.

    Restaura siempre el archivo original, incluso si el subproceso revienta: el `finally` es lo único
    que separa esta herramienta de un destructor de repositorios.
    """
    equivalentes = equivalentes or {}

    _validar_objetivos(raiz, objetivos)
    originales = {ruta: ruta.read_text(encoding="utf-8") for ruta in objetivos}
    sitios_por_ruta = {ruta: sitios_de(ruta, raiz) for ruta in objetivos}
    ids_vigentes = {sitio.id for sitios in sitios_por_ruta.values() for sitio in sitios}

    razones_invalidas = [mid for mid, razon in equivalentes.items()
                         if not isinstance(razon, str) or not razon.strip()]
    if razones_invalidas:
        raise EquivalenteInvalido(
            f"equivalentes sin razón no vacía: {sorted(map(str, razones_invalidas))}")
    ids_vencidos = set(equivalentes) - ids_vigentes
    if ids_vencidos:
        raise EquivalenteInvalido(
            f"equivalentes que no apuntan a un sitio vigente: {sorted(map(str, ids_vencidos))}")

    if type(limite_diagnostico) is not int or limite_diagnostico <= 0:
        raise ValueError("limite_diagnostico tiene que ser un entero positivo")

    baseline = _ejecutar_ronda(
        comando, raiz, timeout=timeout_por_ejecucion,
        codigos_fallo_tests=codigos_fallo_tests, etapa="la línea base",
        permitir_cache_preexistente=True, limite_salida=limite_salida)
    baseline_verde = baseline.pasaron
    if not baseline_verde:
        raise LineaBaseFallida(baseline)

    filas: list[dict] = list(filas_previas or [])
    completados = {fila["id"] for fila in filas}
    ejecutados_ahora = 0
    primer_fallo: tuple[Sitio, ResultadoTests] | None = None
    primer_inconcluso: tuple[Sitio, ResultadoTests] | None = None

    for ruta in objetivos:
        original = originales[ruta]
        for sitio in sitios_por_ruta[ruta]:
            if sitio.id in completados:
                continue
            mutado = mutar_fuente(original, sitio)
            if mutado is None:
                continue
            try:
                _escribir_atomico(ruta, mutado)
                resultado = _ejecutar_ronda(
                    comando, raiz, timeout=timeout_por_ejecucion,
                    codigos_fallo_tests=codigos_fallo_tests, etapa=f"el mutante {sitio.id}",
                    limite_salida=limite_salida)
            finally:
                _escribir_atomico(ruta, original)

            murio = resultado.tests_fallaron
            fila = {
                "id": sitio.id,
                "apunta_a": sitio.archivo,
                "cambio": f"{sitio.operador}: {sitio.descripcion}",
                "murio": murio,
                "estado": resultado.estado.value,
                "tests_fallaron": resultado.tests_fallaron,
                "error_arnes": resultado.error_arnes,
                "timeout": resultado.timeout,
                "codigo_salida": resultado.codigo_salida,
                "equivalente_declarado": sitio.id in equivalentes,
                "razon_equivalente": equivalentes.get(sitio.id, ""),
            }
            filas.append(fila)
            ejecutados_ahora += 1
            if not resultado.pasaron and primer_fallo is None:
                primer_fallo = (sitio, resultado)
            if (resultado.error_arnes or resultado.timeout) and primer_inconcluso is None:
                primer_inconcluso = (sitio, resultado)
            if al_terminar_uno:
                al_terminar_uno(fila)
                _comprobar_cierre_frio(raiz)

    # No limpiar antes de esta lectura: un callback o escritor concurrente no puede hacer reaparecer
    # un cache y confiar en que la limpieza final borre también la evidencia de la reaparición.
    _comprobar_cierre_frio(raiz)
    bytecode_frio = cache_esta_frio(raiz)
    if not bytecode_frio:
        raise CacheNoLimpio("el árbol conserva bytecode después de la limpieza final")

    reales = [f for f in filas if not f["equivalente_declarado"]]
    errores_arnes = sum(f["error_arnes"] for f in filas)
    timeouts = sum(f["timeout"] for f in filas)
    fallos_tests = sum(f["tests_fallaron"] for f in filas)
    if primer_fallo:
        sitio_fallo, resultado_fallo = primer_fallo
        primer_fallo_salida, salida_truncada = _diagnostico(resultado_fallo, limite_diagnostico)
        primer_fallo_id = sitio_fallo.id
        primer_fallo_estado = resultado_fallo.estado.value
        primer_fallo_codigo = resultado_fallo.codigo_salida
    else:
        primer_fallo_id = ""
        primer_fallo_estado = ""
        primer_fallo_codigo = None
        primer_fallo_salida = ""
        salida_truncada = False

    if primer_inconcluso:
        sitio_inconcluso, resultado_inconcluso = primer_inconcluso
        inconcluso_salida, inconcluso_truncado = _diagnostico(
            resultado_inconcluso, limite_diagnostico)
        primer_inconcluso_id = sitio_inconcluso.id
        primer_inconcluso_estado = resultado_inconcluso.estado.value
        primer_inconcluso_codigo = resultado_inconcluso.codigo_salida
    else:
        primer_inconcluso_id = ""
        primer_inconcluso_estado = ""
        primer_inconcluso_codigo = None
        inconcluso_salida = ""
        inconcluso_truncado = False

    return {
        "mutante": reales,
        "mutante_equivalente": [f for f in filas if f["equivalente_declarado"]],
        "corrida_mutacion": [{
            "id": "mutacion_de_codigo",
            "mutantes": len(reales),
            "baseline_verde": baseline_verde,
            "baseline_estado": baseline.estado.value,
            "bytecode_frio": bytecode_frio,
            "tests_fallaron": fallos_tests,
            "errores_arnes": errores_arnes,
            "timeouts": timeouts,
            "rondas_ejecutadas": 1 + ejecutados_ahora,
            "rondas_cache_verificadas": 1 + ejecutados_ahora,
            "mutantes_reutilizados": len(filas) - ejecutados_ahora,
            "primer_fallo_id": primer_fallo_id,
            "primer_fallo_estado": primer_fallo_estado,
            "primer_fallo_codigo_salida": primer_fallo_codigo,
            "primer_fallo_salida": primer_fallo_salida,
            "primer_fallo_salida_truncada": salida_truncada,
            "primer_inconcluso_id": primer_inconcluso_id,
            "primer_inconcluso_estado": primer_inconcluso_estado,
            "primer_inconcluso_codigo_salida": primer_inconcluso_codigo,
            "primer_inconcluso_salida": inconcluso_salida,
            "primer_inconcluso_salida_truncada": inconcluso_truncado,
        }],
    }


def correr(raiz: Path, objetivos: list[Path], comando: list[str],
           equivalentes: dict[str, str] | None = None, al_terminar_uno=None, *,
           timeout_por_ejecucion: float = 60.0,
           codigos_fallo_tests=frozenset({1}), limite_diagnostico: int = 16_384,
           limite_salida: int = 1_048_576, manifiesto: Path | None = None,
           reanudar: bool = False) -> dict:
    """Muta exclusivamente una copia temporal y comprueba que los objetivos originales no cambien."""
    raiz = Path(raiz).resolve(strict=True)
    objetivos = [Path(ruta) if Path(ruta).is_absolute() else raiz / ruta for ruta in objetivos]
    _validar_objetivos(raiz, objetivos)
    originales = {ruta.resolve(): ruta.read_bytes() for ruta in objetivos}
    equivalentes = equivalentes or {}
    sitios = {sitio.id: sitio for ruta in objetivos for sitio in sitios_de(ruta, raiz)}
    razones_invalidas = [mid for mid, razon in equivalentes.items()
                         if not isinstance(razon, str) or not razon.strip()]
    if razones_invalidas or not set(equivalentes) <= set(sitios):
        raise EquivalenteInvalido("equivalentes inválidos, vacíos o vencidos")
    if reanudar and manifiesto is None:
        raise ManifiestoInvalido("`reanudar` requiere una ruta de manifiesto")
    ruta_manifiesto = Path(manifiesto).expanduser().resolve() if manifiesto else None
    identidad = _identidad_ronda(
        raiz, objetivos, comando, equivalentes, timeout_por_ejecucion,
        codigos_fallo_tests, limite_salida)

    with _bloqueo_de_ronda(raiz), _senales_de_ronda():
        if reanudar:
            datos_manifiesto, filas_previas = _cargar_reanudacion(
                ruta_manifiesto, identidad, sitios)
            datos_manifiesto["estado"] = "en_curso"
        else:
            filas_previas = []
            datos_manifiesto = {
                "esquema": ESQUEMA_MANIFIESTO,
                "estado": "en_curso",
                "identidad": identidad,
                "huella": _huella_json(identidad),
                "completados": [],
                "huella_completados": _huella_json([]),
            }
        if ruta_manifiesto:
            _escribir_manifiesto(ruta_manifiesto, datos_manifiesto)

        def guardar(fila):
            if ruta_manifiesto:
                datos_manifiesto["completados"].append(fila)
                datos_manifiesto["huella_completados"] = _huella_json(
                    datos_manifiesto["completados"])
                _escribir_manifiesto(ruta_manifiesto, datos_manifiesto)
            if al_terminar_uno:
                al_terminar_uno(fila)

        with tempfile.TemporaryDirectory(prefix="oracle-mutacion-") as temporal:
            copia = Path(temporal) / "proyecto"
            _copiar_proyecto(raiz, copia)
            objetivos_copia = [copia / ruta.resolve().relative_to(raiz) for ruta in objetivos]
            comando_copia = _comando_en_copia(comando, raiz, copia)
            evidencia = _correr_en_raiz(
                copia, objetivos_copia, comando_copia, equivalentes,
                guardar if ruta_manifiesto or al_terminar_uno else None,
                timeout_por_ejecucion=timeout_por_ejecucion,
                codigos_fallo_tests=codigos_fallo_tests,
                limite_diagnostico=limite_diagnostico, limite_salida=limite_salida,
                filas_previas=filas_previas)
        if ruta_manifiesto:
            datos_manifiesto["estado"] = "completa"
            _escribir_manifiesto(ruta_manifiesto, datos_manifiesto)

    alterados = [str(ruta.relative_to(raiz)) for ruta, contenido in originales.items()
                 if not ruta.exists() or ruta.read_bytes() != contenido]
    if alterados:
        raise AislamientoRoto(f"cambiaron objetivos de la raíz original: {alterados}")
    evidencia["corrida_mutacion"][0]["aislada"] = True
    evidencia["corrida_mutacion"][0]["fuentes_originales_intactas"] = True
    return evidencia
