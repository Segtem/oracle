"""Ejecución confinada de `escalares.py` externos.

El proceso principal sólo conserva proxies con metadatos. El código del proyecto vive en un
trabajador separado, con entorno mínimo, canal JSON y una política de auditoría que niega **leer el
CONTENIDO** de archivos fuera del proyecto, escribir fuera, abrir red y crear procesos.

## Lo que este confinamiento NO detiene, y no es una omisión

**Los METADATOS del sistema de archivos se leen sin restricción.** `os.stat`, `os.path.exists`,
`os.path.isdir`, `os.access` y todo lo que se apoya en ellos funcionan sobre cualquier ruta. Una UDF
hostil puede averiguar si existe `/etc/shadow` o `~/.ssh/id_rsa`, leer tamaños, permisos y fechas, y
enumerar qué directorios hay en el disco — y devolver todo eso como resultado, que viaja por el canal
JSON como cualquier otro valor.

No es un descuido del hook: **`os.stat` no emite ningún evento auditable en CPython**. PEP 578 cubre
`open`, `os.listdir`, `os.scandir`, los que mutan el árbol, los procesos y los sockets, pero no la
consulta de metadatos. Un `sys.addaudithook` no puede interceptar lo que nunca se anuncia.

Se podría poner un `os.stat` sombra en el trabajador, y sería teatro: `from posix import stat` lo
esquiva en una línea. Este repositorio prefiere un límite DECLARADO a una defensa que aparenta. La
frontera real, en una línea:

    lo que una UDF hostil NO puede: leer contenido afuera, escribir afuera, red, procesos, ctypes
    lo que SÍ puede:                fichar el disco por metadatos, y contártelo en su resultado

Si eso no alcanza para tu caso, la respuesta no es endurecer este hook: es no correr esa `escalares.py`
—`--confiar-escalares` es opt-in a propósito— o encerrar el proceso entero con algo del sistema
operativo (namespaces, seccomp), que está fuera de lo que Oracle hace.

Shi, Zhang y Cui, *A Programming Paradigm for Spatiotemporal Composability*, §6.3, ponen el mismo
límite: el control de acceso a nivel del lenguaje no alcanza si el componente hostil puede llegar al
runtime anfitrión; el sandbox necesita una frontera de ejecución por fuera del lenguaje y un puente
hacia lo que el host provee. Oracle toma la mitad correcta de esa arquitectura —proceso aparte y
canal JSON—. Lo que NO toma todavía es el borde del sistema operativo: no hay namespaces, seccomp ni
contenedor que esconda los metadatos del disco.

Hay un test que fija ESTE límite, incluida la fuga: `test_los_metadatos_se_filtran_y_esta_declarado`.
Si algún día se cierra de verdad, ese test falla y obliga a actualizar esta declaración en vez de
dejarla envejecer diciendo de menos.
"""

from __future__ import annotations

import atexit
import contextlib
import json
import os
import selectors
import signal
import subprocess
import sys
import threading
import weakref
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nucleo import algebra

RAIZ_ORACLE = Path(__file__).resolve().parents[2]
TIEMPO_MAXIMO_SEGUNDOS = 10


class ErrorEscalarAislada(RuntimeError):
    pass


@dataclass(frozen=True)
class EscalarDeclarada:
    nombre: str
    unidad: str
    unidades_argumentos: tuple[str, ...]
    aridad_min: int
    aridad_max: int | None
    procedencia: str


_TRABAJADORES = weakref.WeakSet()


def _dentro_de(ruta: Path, raiz: Path) -> bool:
    try:
        ruta.resolve().relative_to(raiz)
    except (OSError, ValueError):
        return False
    return True


def _cerrar_proceso(proc: subprocess.Popen | None) -> None:
    if proc is None:
        return
    try:
        if proc.poll() is None and os.name == "posix":
            with contextlib.suppress(ProcessLookupError):
                os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=1)
        elif proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=1)
    finally:
        for canal in (proc.stdin, proc.stdout):
            if canal is not None:
                with contextlib.suppress(OSError):
                    canal.close()


def cerrar_trabajadores() -> None:
    for trabajador in tuple(_TRABAJADORES):
        trabajador.cerrar()


atexit.register(cerrar_trabajadores)


class TrabajadorEscalares:
    """Proceso propietario de las UDF de un proyecto."""

    def __init__(self, raiz: Path, archivo: Path) -> None:
        self.raiz = raiz
        self.archivo = archivo
        self.declaradas: tuple[EscalarDeclarada, ...] = ()
        self._proc: subprocess.Popen | None = None
        self._selector: selectors.BaseSelector | None = None
        self._lock = threading.RLock()
        self._finalizador = None

    def iniciar(self) -> tuple[EscalarDeclarada, ...]:
        entorno = {
            "PYTHONPATH": str(RAIZ_ORACLE),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONIOENCODING": "utf-8",
            "LC_ALL": "C.UTF-8",
            "LANG": "C.UTF-8",
        }
        self._proc = subprocess.Popen(
            [sys.executable, "-B", "-m", "nucleo.aislamiento.escalares",
             "--trabajador", str(self.raiz), str(self.archivo)],
            cwd=RAIZ_ORACLE,
            env=entorno,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            start_new_session=(os.name == "posix"),
        )
        if self._proc.stdout is None:
            self.cerrar()
            raise ErrorEscalarAislada("no se pudo abrir el canal del trabajador de escalares")
        self._selector = selectors.DefaultSelector()
        self._selector.register(self._proc.stdout, selectors.EVENT_READ)
        self._finalizador = weakref.finalize(self, _cerrar_proceso, self._proc)
        _TRABAJADORES.add(self)

        respuesta = self._leer()
        if not respuesta.get("ok"):
            self.cerrar()
            tipo = respuesta.get("tipo", "Error")
            mensaje = respuesta.get("mensaje", "falló la carga de escalares.py")
            raise ErrorEscalarAislada(f"{tipo}: {mensaje}")
        declaradas = []
        for datos in respuesta.get("escalares", []):
            declaradas.append(EscalarDeclarada(
                nombre=datos["nombre"],
                unidad=datos["unidad"],
                unidades_argumentos=tuple(datos["unidades_argumentos"]),
                aridad_min=datos["aridad_min"],
                aridad_max=datos["aridad_max"],
                procedencia=datos["procedencia"],
            ))
        self.declaradas = tuple(declaradas)
        return self.declaradas

    def llamar(self, nombre: str, argumentos: tuple[Any, ...]) -> Any:
        try:
            cuerpo = json.dumps(
                {"op": "llamar", "nombre": nombre, "argumentos": list(argumentos)},
                ensure_ascii=False,
                allow_nan=False,
            )
        except (TypeError, ValueError) as e:
            raise algebra.ErrorDeAlgebra(
                f"los argumentos de la escalar externa «{nombre}» deben ser JSON finito") from e
        with self._lock:
            if self._proc is None or self._proc.stdin is None or self._proc.poll() is not None:
                raise algebra.ErrorDeAlgebra(
                    f"el trabajador de la escalar externa «{nombre}» no está activo")
            try:
                self._proc.stdin.write(cuerpo + "\n")
                self._proc.stdin.flush()
            except (BrokenPipeError, OSError) as e:
                raise algebra.ErrorDeAlgebra(
                    f"el trabajador de la escalar externa «{nombre}» cerró el canal") from e
            respuesta = self._leer()
        if respuesta.get("ok"):
            return respuesta.get("resultado")
        tipo = respuesta.get("tipo", "Error")
        mensaje = respuesta.get("mensaje", "sin detalle")
        raise algebra.ErrorDeAlgebra(
            f"falló la escalar externa «{nombre}»: {tipo}: {mensaje}")

    def cerrar(self) -> None:
        with self._lock:
            proc = self._proc
            if proc is None:
                return
            if proc.poll() is None and proc.stdin is not None:
                with contextlib.suppress(BrokenPipeError, OSError):
                    proc.stdin.write(json.dumps({"op": "cerrar"}) + "\n")
                    proc.stdin.flush()
            _cerrar_proceso(proc)
            if self._selector is not None:
                self._selector.close()
                self._selector = None
            for canal in (proc.stdin, proc.stdout):
                if canal is not None:
                    with contextlib.suppress(OSError):
                        canal.close()
            if self._finalizador is not None:
                self._finalizador.detach()
                self._finalizador = None
            self._proc = None
            _TRABAJADORES.discard(self)

    def _leer(self) -> dict[str, Any]:
        if self._proc is None or self._proc.stdout is None or self._selector is None:
            raise ErrorEscalarAislada("el trabajador de escalares no tiene canal de lectura")
        eventos = self._selector.select(TIEMPO_MAXIMO_SEGUNDOS)
        if not eventos:
            self.cerrar()
            raise ErrorEscalarAislada(
                f"el trabajador de escalares no respondió en {TIEMPO_MAXIMO_SEGUNDOS}s")
        linea = self._proc.stdout.readline()
        if not linea:
            codigo = self._proc.poll()
            self.cerrar()
            raise ErrorEscalarAislada(
                f"el trabajador de escalares terminó sin respuesta (código {codigo})")
        try:
            datos = json.loads(linea)
        except json.JSONDecodeError as e:
            self.cerrar()
            raise ErrorEscalarAislada("el trabajador de escalares emitió datos inválidos") from e
        if not isinstance(datos, dict):
            self.cerrar()
            raise ErrorEscalarAislada("el trabajador de escalares no emitió un objeto JSON")
        return datos


def _proxy(trabajador: TrabajadorEscalares, declarada: EscalarDeclarada):
    def llamar(*argumentos):
        return trabajador.llamar(declarada.nombre, argumentos)

    llamar.__name__ = declarada.nombre
    llamar.nombre_escalar = declarada.nombre
    llamar.unidad = declarada.unidad
    llamar.unidades_argumentos = declarada.unidades_argumentos
    llamar.aridad_min = declarada.aridad_min
    llamar.aridad_max = declarada.aridad_max
    llamar.procedencia_escalar = declarada.procedencia
    return llamar


def registrar_escalares_aisladas(
        raiz: Path, archivo: Path, registro: algebra.RegistroEscalares) -> TrabajadorEscalares:
    trabajador = TrabajadorEscalares(raiz, archivo)
    declaradas = trabajador.iniciar()
    repetidas = sorted(d.nombre for d in declaradas if d.nombre in registro)
    if repetidas:
        trabajador.cerrar()
        raise ErrorEscalarAislada(f"escalares.py alteró registros existentes: {repetidas}")
    for declarada in declaradas:
        registro[declarada.nombre] = _proxy(trabajador, declarada)
    return trabajador


def _respuesta_error(e: BaseException) -> dict[str, Any]:
    return {"ok": False, "tipo": type(e).__name__, "mensaje": str(e)}


def _enviar(datos: dict[str, Any]) -> None:
    sys.__stdout__.write(json.dumps(datos, ensure_ascii=False, allow_nan=False) + "\n")
    sys.__stdout__.flush()


def _escritura(modo: Any, banderas: Any) -> bool:
    if isinstance(modo, str) and any(c in modo for c in "wax+"):
        return True
    if isinstance(banderas, int):
        mascara = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
        return bool(banderas & mascara)
    return False


def _ruta(valor: Any) -> Path | None:
    if isinstance(valor, int) or valor is None:
        return None
    try:
        return Path(valor)
    except TypeError:
        return None


def _instalar_auditoria(raiz: Path) -> None:
    lectura = tuple(dict.fromkeys((
        raiz,
        RAIZ_ORACLE.resolve(),
        Path(sys.base_prefix).resolve(),
        Path(sys.prefix).resolve(),
        Path(sys.exec_prefix).resolve(),
        Path(sys.base_exec_prefix).resolve(),
    )))

    def puede_leer(ruta: Path) -> bool:
        return any(_dentro_de(ruta, permitida) for permitida in lectura)

    def puede_escribir(ruta: Path) -> bool:
        return _dentro_de(ruta, raiz)

    def exigir_lectura(valor: Any) -> None:
        ruta = _ruta(valor)
        if ruta is not None and not puede_leer(ruta):
            raise PermissionError(f"lectura fuera del proyecto bloqueada: {ruta}")

    def exigir_escritura(valor: Any) -> None:
        ruta = _ruta(valor)
        if ruta is not None and not puede_escribir(ruta):
            raise PermissionError(f"escritura fuera del proyecto bloqueada: {ruta}")

    def auditar(evento: str, args: tuple[Any, ...]) -> None:
        if evento == "open":
            ruta = args[0] if args else None
            modo = args[1] if len(args) > 1 else "r"
            banderas = args[2] if len(args) > 2 else None
            if _escritura(modo, banderas):
                exigir_escritura(ruta)
            else:
                exigir_lectura(ruta)
        elif evento in {"os.listdir", "os.scandir"}:
            exigir_lectura(args[0] if args else None)
        elif evento in {
                "os.mkdir", "os.rmdir", "os.remove", "os.unlink", "os.rename",
                "os.replace", "os.symlink", "os.link", "shutil.copyfile",
                "shutil.copymode", "shutil.copystat", "shutil.copytree",
                "shutil.move"}:
            for valor in args[:2]:
                exigir_escritura(valor)
        elif evento == "os.chdir":
            exigir_lectura(args[0] if args else None)
        elif evento in {
                "subprocess.Popen", "os.system", "os.fork", "os.forkpty",
                "os.posix_spawn", "os.posix_spawnp", "pty.spawn", "os.kill",
                "os.killpg", "socket.__new__", "socket.connect", "socket.bind"}:
            raise PermissionError(f"operación externa bloqueada: {evento}")
        elif evento == "import" and args and args[0] == "ctypes":
            raise PermissionError("ctypes no está disponible para escalares externas")

    sys.addaudithook(auditar)


def _metadata(fn) -> dict[str, Any]:
    requeridos = ("nombre_escalar", "unidad", "unidades_argumentos", "aridad_min", "aridad_max",
                  "procedencia_escalar")
    faltantes = [campo for campo in requeridos if not hasattr(fn, campo)]
    if faltantes:
        raise RuntimeError(f"la escalar «{getattr(fn, '__name__', '?')}» evitó `@escalar`")
    return {
        "nombre": fn.nombre_escalar,
        "unidad": fn.unidad,
        "unidades_argumentos": fn.unidades_argumentos,
        "aridad_min": fn.aridad_min,
        "aridad_max": fn.aridad_max,
        "procedencia": fn.procedencia_escalar,
    }


def _cargar_en_trabajador(raiz: Path, archivo: Path) -> tuple[dict[str, Any],
                                                              algebra.RegistroEscalares]:
    import importlib.util
    import oracle_metalenguaje  # noqa: F401

    registro = algebra.RegistroEscalares()
    globales_anteriores = dict(algebra.ESCALARES)
    huella = str(abs(hash((str(raiz), str(archivo)))))
    spec = importlib.util.spec_from_file_location(f"oracle_escalares_aisladas_{huella}", archivo)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"no se pudo preparar la carga de {archivo}")
    modulo = importlib.util.module_from_spec(spec)
    with algebra.usar_registro(registro, procedencia=f"proyecto:{raiz}"):
        with contextlib.redirect_stdout(sys.stderr):
            spec.loader.exec_module(modulo)
    if dict(algebra.ESCALARES) != globales_anteriores:
        raise RuntimeError("escalares.py intentó alterar el registro global fuera de su motor")
    return {"ok": True, "escalares": [_metadata(fn) for fn in registro.values()]}, registro


def _ejecutar_trabajador(argv: list[str]) -> int:
    if len(argv) != 2:
        _enviar({"ok": False, "tipo": "UsoInvalido", "mensaje": "faltan raíz y archivo"})
        return 2
    raiz = Path(argv[0]).resolve()
    archivo = Path(argv[1]).resolve()
    try:
        _instalar_auditoria(raiz)
        datos, registro = _cargar_en_trabajador(raiz, archivo)
        _enviar(datos)
    except BaseException as e:
        _enviar(_respuesta_error(e))
        return 1

    for linea in sys.stdin:
        try:
            pedido = json.loads(linea)
            if pedido.get("op") == "cerrar":
                return 0
            if pedido.get("op") != "llamar":
                raise ValueError("operación desconocida")
            nombre = pedido["nombre"]
            argumentos = pedido.get("argumentos", [])
            if nombre not in registro:
                raise KeyError(f"escalar no registrada: {nombre}")
            with contextlib.redirect_stdout(sys.stderr):
                resultado = registro[nombre](*argumentos)
            json.dumps(resultado, ensure_ascii=False, allow_nan=False)
            _enviar({"ok": True, "resultado": resultado})
        except BaseException as e:
            _enviar(_respuesta_error(e))
    return 0


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "--trabajador":
        return _ejecutar_trabajador(sys.argv[2:])
    print("uso interno: python -m nucleo.aislamiento.escalares --trabajador <raiz> <archivo>",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
