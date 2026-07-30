"""Runner `unittest` con un protocolo de salida inequívoco para mutación de código.

0 significa que la suite pasó; 1, que un test falló o terminó con una excepción; 2, que el arnés no
pudo establecer una suite (descubrimiento inválido, runner roto o cero tests). La línea base verde es
la que permite atribuir al mutante un error posterior dentro del código ejercitado.
"""

from __future__ import annotations

import argparse
import sys
import unittest


def argumentos(argv: list[str] | None = None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inicio", default="tests", help="directorio inicial de descubrimiento")
    p.add_argument("--tope", default=".", help="directorio superior importable")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = argumentos(argv)
    try:
        cargador = unittest.TestLoader()
        suite = cargador.discover(
            start_dir=args.inicio, top_level_dir=args.tope)
        if cargador.errors:
            print("error del arnés durante descubrimiento:", file=sys.stderr)
            print(cargador.errors[0], file=sys.stderr)
            return 2
        # Una sola discriminación alcanza para matar el mutante. Seguir ejecutando puede activar
        # caminos rotos posteriores (incluso otra mutación recursiva) y convertir un fallo ya probado
        # en timeout inconcluso.
        resultado = unittest.TextTestRunner(verbosity=1, failfast=True).run(suite)
    except SystemExit as e:
        print(f"error del arnés durante descubrimiento: SystemExit: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001  descubrir/importar es parte del arnés observado
        print(f"error del arnés durante descubrimiento: {type(e).__name__}: {e}", file=sys.stderr)
        return 2

    if resultado.testsRun == 0:
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
