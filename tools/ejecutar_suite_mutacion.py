"""Runner `unittest` con un protocolo de salida inequívoco para mutación de código.

0 significa que la suite pasó; 1, que un test falló o terminó con una excepción; 2, que el arnés no
pudo establecer una suite (descubrimiento inválido, runner roto o cero tests). La línea base verde es
la que permite atribuir al mutante un error posterior dentro del código ejercitado.
"""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path


class _RastreadorCobertura:
    def __init__(self, objetivos: list[str], tope: Path):
        self.tope = tope.resolve()
        self.archivos_seguidos: dict[str, str] = {}
        if objetivos:
            for obj in objetivos:
                p = Path(obj) if Path(obj).is_absolute() else (self.tope / obj)
                res = p.resolve()
                try:
                    rel = res.relative_to(self.tope).as_posix()
                except ValueError:
                    rel = Path(obj).as_posix()
                self.archivos_seguidos[str(res)] = rel
        else:
            for p in self.tope.rglob("*.py"):
                if "tests" not in p.parts and ".git" not in p.parts and "__pycache__" not in p.parts:
                    try:
                        self.archivos_seguidos[str(p.resolve())] = p.resolve().relative_to(self.tope).as_posix()
                    except ValueError:
                        pass
        self.mapa: dict[str, dict[int, set[str]]] = {}
        self.test_actual: list[str | None] = [None]
        self.usando_monitoring = hasattr(sys, "monitoring") and hasattr(sys.monitoring, "COVERAGE_ID")
        self.tool_id = getattr(sys.monitoring, "COVERAGE_ID", None) if self.usando_monitoring else None
        self._prev_trace = None

    def activar(self):
        if self.usando_monitoring:
            try:
                sys.monitoring.use_tool_id(self.tool_id, "oracle_suite_cobertura")
            except ValueError:
                pass
            def _line_cb(code, line_number):
                rel = self.archivos_seguidos.get(code.co_filename)
                if rel is not None and self.test_actual[0] is not None:
                    self.mapa.setdefault(rel, {}).setdefault(line_number, set()).add(self.test_actual[0])
                # Cada línea se informa una vez por test: DISABLE la apaga hasta el próximo
                # restart_events (en fijar_test). Sin esto el callback corre en cada línea de todo
                # el intérprete, stdlib incluida, y la línea base pasaba de 2 a más de 5 minutos.
                return sys.monitoring.DISABLE
            sys.monitoring.register_callback(self.tool_id, sys.monitoring.events.LINE, _line_cb)
            sys.monitoring.set_events(self.tool_id, sys.monitoring.events.LINE)
        else:
            def _trace(frame, event, arg):
                if event == "line":
                    fname = frame.f_code.co_filename
                    if fname in self.archivos_seguidos and self.test_actual[0] is not None:
                        rel = self.archivos_seguidos[fname]
                        self.mapa.setdefault(rel, {}).setdefault(frame.f_lineno, set()).add(self.test_actual[0])
                return _trace
            self._prev_trace = sys.gettrace()
            sys.settrace(_trace)

    def desactivar(self):
        if self.usando_monitoring:
            try:
                sys.monitoring.set_events(self.tool_id, 0)
                sys.monitoring.free_tool_id(self.tool_id)
            except Exception:
                pass
        else:
            sys.settrace(self._prev_trace)

    def fijar_test(self, test_id: str | None):
        self.test_actual[0] = test_id
        if self.usando_monitoring:
            sys.monitoring.restart_events()

    def serializar(self) -> dict[str, dict[str, list[str]]]:
        return {
            rel: {str(linea): sorted(tests) for linea, tests in sorted(lineas.items())}
            for rel, lineas in sorted(self.mapa.items())
        }

    def guardar(self, ruta: Path):
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(self.serializar(), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def argumentos(argv: list[str] | None = None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inicio", default="tests", help="directorio inicial de descubrimiento")
    p.add_argument("--tope", default=".", help="directorio superior importable")
    p.add_argument("--prioridad", action="append", default=[], metavar="MODULO",
                   help="módulo unittest que discrimina primero; repetible")
    p.add_argument("--solo-prioridad", action="store_true",
                   help="ejecutar únicamente los módulos prioritarios declarados")
    p.add_argument("--guardar-cobertura", type=Path, metavar="RUTA",
                   help="guardar mapa línea->tests como JSON")
    p.add_argument("--objetivo-cobertura", action="append", default=[], metavar="RUTA",
                   help="archivo objetivo a trazar; repetible")
    return p.parse_args(argv)


def _correr_suite(suite, rastreador: _RastreadorCobertura | None = None) -> unittest.TestResult:
    if rastreador is None:
        return unittest.TextTestRunner(verbosity=1, failfast=True).run(suite)

    class CoberturaResult(unittest.TextTestResult):
        def startTest(self, test):
            super().startTest(test)
            rastreador.fijar_test(test.id())

        def stopTest(self, test):
            super().stopTest(test)
            rastreador.fijar_test(None)

    class CoberturaRunner(unittest.TextTestRunner):
        def _makeResult(self):
            return CoberturaResult(self.stream, self.descriptions, self.verbosity)

    rastreador.activar()
    try:
        return CoberturaRunner(verbosity=1, failfast=True).run(suite)
    finally:
        rastreador.desactivar()


def _sin_modulos(suite: unittest.TestSuite, modulos: list[str]) -> unittest.TestSuite:
    """Quita del descubrimiento lo que ya corrió como prioridad."""
    prefijos = tuple(f"{modulo}." for modulo in modulos)

    def casos(contenedor):
        for caso in contenedor:
            if isinstance(caso, unittest.TestSuite):
                yield from casos(caso)
            elif not modulos or not caso.id().startswith(prefijos):
                yield caso

    return unittest.TestSuite(casos(suite))


def main(argv: list[str] | None = None) -> int:
    args = argumentos(argv)
    rastreador = None
    try:
        tope = str(Path(args.tope).resolve())
        if tope not in sys.path:
            sys.path.insert(0, tope)
        if args.guardar_cobertura:
            rastreador = _RastreadorCobertura(args.objetivo_cobertura, Path(tope))
        cargador = unittest.TestLoader()
        tests_prioritarios = 0
        for modulo in args.prioridad:
            suite_prioritaria = cargador.loadTestsFromName(modulo)
            if cargador.errors or any(isinstance(caso, unittest.loader._FailedTest)
                                      for caso in suite_prioritaria):
                print("error del arnés durante carga prioritaria:", file=sys.stderr)
                if cargador.errors:
                    print(cargador.errors[0], file=sys.stderr)
                return 2
            resultado_prioritario = _correr_suite(suite_prioritaria, rastreador)
            tests_prioritarios += resultado_prioritario.testsRun
            if (resultado_prioritario.failures or resultado_prioritario.errors
                    or resultado_prioritario.unexpectedSuccesses):
                return 1
        if args.solo_prioridad:
            if tests_prioritarios == 0:
                print("error del arnés: se descubrieron cero tests", file=sys.stderr)
                return 2
            return 0
        suite = _sin_modulos(cargador.discover(
            start_dir=args.inicio, top_level_dir=args.tope), args.prioridad)
        if cargador.errors:
            print("error del arnés durante descubrimiento:", file=sys.stderr)
            print(cargador.errors[0], file=sys.stderr)
            return 2
        # Una sola discriminación alcanza para matar el mutante. Seguir ejecutando puede activar
        # caminos rotos posteriores (incluso otra mutación recursiva) y convertir un fallo ya probado
        # en timeout inconcluso.
        resultado = _correr_suite(suite, rastreador)
    except SystemExit as e:
        print(f"error del arnés durante descubrimiento: SystemExit: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001  descubrir/importar es parte del arnés observado
        print(f"error del arnés durante descubrimiento: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    finally:
        if rastreador and args.guardar_cobertura:
            rastreador.guardar(args.guardar_cobertura)

    if tests_prioritarios + resultado.testsRun == 0:
        print("error del arnés: se descubrieron cero tests", file=sys.stderr)
        return 2
    if any(isinstance(caso, unittest.loader._FailedTest)
           for caso, _traza in resultado.errors):  # defensa si un loader futuro no llena `errors`
        print("error del arnés: falló la importación durante el descubrimiento", file=sys.stderr)
        return 2
    if resultado.failures or resultado.errors or resultado.unexpectedSuccesses:
        return 1
    return 0 if resultado.wasSuccessful() else 2


if __name__ == "__main__":
    sys.exit(main())
