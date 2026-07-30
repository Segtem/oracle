"""Mutación de CÓDIGO — la otra mitad del sensor, y la que atrapó 3 de los casos del corpus.

`mutacion.py` muta medidas, que son datos. Esto muta el árbol sintáctico de archivos `.py` reales,
que es más caro y más incómodo, y hace falta igual: los tests que no discriminan sólo se ven
rompiendo el código que dicen cubrir.

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

Cada ejecución limpia `__pycache__` antes, usa un prefijo de caché temporal y vuelve a inspeccionar el
árbol después de correr los tests. No es prolijidad: `max` y `min` ocupan lo mismo y CPython invalida
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
import atexit
import math
import os
import shutil
import signal
import subprocess
import tempfile
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


# Archivos con su contenido original mientras están mutados. Un `finally` NO alcanza: `timeout` manda
# SIGTERM y Python termina sin ejecutarlo, así que una corrida cortada dejaba el archivo mutado en el
# árbol de trabajo. Pasó de verdad, y el daño lo salvó git — no la herramienta.
_EN_VUELO: dict[Path, str] = {}


def _restaurar_todo(*_args) -> None:
    for ruta, original in list(_EN_VUELO.items()):
        try:
            ruta.write_text(original, encoding="utf-8")
        except Exception:  # noqa: BLE001  restaurar es lo último que se intenta, nunca lo que falla
            pass
        _EN_VUELO.pop(ruta, None)


atexit.register(_restaurar_todo)
for _sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    try:
        signal.signal(_sig, lambda s, f: (_restaurar_todo(), raise_exit(s)))
    except (ValueError, OSError):
        pass


def raise_exit(sig):
    raise SystemExit(128 + sig)

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


def _texto(salida) -> str:
    if salida is None:
        return ""
    if isinstance(salida, bytes):
        return salida.decode("utf-8", errors="replace")
    return str(salida)


def ejecutar_tests(comando: list[str], raiz: Path, *, timeout: float,
                   codigos_fallo_tests=frozenset({1}), entorno=None) -> ResultadoTests:
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

    try:
        r = subprocess.run(comando, cwd=str(raiz), capture_output=True, text=True,
                           timeout=timeout, env=entorno)
    except subprocess.TimeoutExpired as e:
        return ResultadoTests(EstadoTests.TIMEOUT, None,
                              stdout=_texto(e.stdout), stderr=_texto(e.stderr))
    except (OSError, ValueError) as e:
        return ResultadoTests(EstadoTests.ERROR_ARNES, None, stderr=f"{type(e).__name__}: {e}")

    if r.returncode == 0:
        estado = EstadoTests.PASARON
    elif r.returncode in codigos:
        estado = EstadoTests.TESTS_FALLARON
    else:
        estado = EstadoTests.ERROR_ARNES
    return ResultadoTests(estado, r.returncode, _texto(r.stdout), _texto(r.stderr))


def correr_tests(comando: list[str], raiz: Path, timeout: float = 60.0) -> bool:
    """Wrapper booleano histórico; la ronda usa `ejecutar_tests` para no perder estados."""
    return ejecutar_tests(comando, raiz, timeout=timeout).pasaron


def _ejecutar_ronda(comando: list[str], raiz: Path, *, timeout: float,
                    codigos_fallo_tests, etapa: str,
                    permitir_cache_preexistente: bool = False) -> ResultadoTests:
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
                codigos_fallo_tests=codigos_fallo_tests, entorno=entorno)

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
    if len(salida) <= limite:
        return salida, False
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


def correr(raiz: Path, objetivos: list[Path], comando: list[str],
           equivalentes: dict[str, str] | None = None, al_terminar_uno=None, *,
           timeout_por_ejecucion: float = 60.0,
           codigos_fallo_tests=frozenset({1}), limite_diagnostico: int = 16_384) -> dict:
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
        permitir_cache_preexistente=True)
    baseline_verde = baseline.pasaron
    if not baseline_verde:
        raise LineaBaseFallida(baseline)

    filas: list[dict] = []
    primer_fallo: tuple[Sitio, ResultadoTests] | None = None
    primer_inconcluso: tuple[Sitio, ResultadoTests] | None = None

    for ruta in objetivos:
        original = originales[ruta]
        for sitio in sitios_por_ruta[ruta]:
            mutado = mutar_fuente(original, sitio)
            if mutado is None:
                continue
            try:
                _EN_VUELO[ruta] = original      # red de seguridad si nos matan a mitad
                ruta.write_text(mutado, encoding="utf-8")
                resultado = _ejecutar_ronda(
                    comando, raiz, timeout=timeout_por_ejecucion,
                    codigos_fallo_tests=codigos_fallo_tests, etapa=f"el mutante {sitio.id}")
            finally:
                ruta.write_text(original, encoding="utf-8")
                _EN_VUELO.pop(ruta, None)

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
            "rondas_ejecutadas": 1 + len(filas),
            "rondas_cache_verificadas": 1 + len(filas),
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
