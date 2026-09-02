"""Regresiones para la reubicación y validación de mutantes equivalentes."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from perfiles.python.mutacion_codigo import EquivalenteInvalido, sitios_de
from tools.mutar_codigo import (
    EQUIVALENTES,
    RAIZ,
    cargar_equivalentes,
    equivalentes_del_alcance,
    leer_declaraciones_equivalentes,
    reapuntar_equivalentes,
)

class EquivalentesReubicacionTests(unittest.TestCase):
    """Fija la reubicación automática de equivalentes posicionales.

    Un id `archivo:linea:columna:tipo` es frágil ante inserciones de líneas previas.
    Los tests comprueban que el mecanismo reubique usando contenido y ordinal, sin
    confundir líneas repetidas y fallando cerrado ante contenidos desaparecidos o mutados.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_reubicacion_encuentra_el_sitio_cuando_se_agregan_lineas_arriba(self) -> None:
        # Creamos un archivo inicial donde el mutante está en la línea 4
        codigo_inicial = (
            "def foo(x):\n"
            "    # línea previa\n"
            "    # otra línea\n"
            "    while x < 10:\n"
            "        x += 1\n"
            "    return x\n"
        )
        ruta_archivo = self.raiz / "modulo.py"
        ruta_archivo.write_text(codigo_inicial, encoding="utf-8")

        # Se lee del AST y no se afirma de memoria: si el sitio no estuviera donde se cree, el
        # resto del test mediría otra cosa y pasaría igual.
        sitios = sitios_de(ruta_archivo, self.raiz)
        sitio_inicial = next(s for s in sitios if s.operador == "comparador")
        self.assertEqual(sitio_inicial.linea, 4)

        declaraciones = [
            {
                "id": sitio_inicial.id,
                "linea_texto": "while x < 10:",
                "ordinal": 1,
                "razon": "explicación necesaria",
            }
        ]
        ruta_eq = self.raiz / "equivalentes.json"
        ruta_eq.write_text(json.dumps(declaraciones), encoding="utf-8")

        # El caso real: se agregan líneas ARRIBA. Es lo que rompió estos ids cinco veces en una
        # sola sesión.
        codigo_modificado = (
            "# comentario 1\n"
            "# comentario 2\n"
            "# comentario 3\n"
            "# comentario 4\n"
            "# comentario 5\n"
            + codigo_inicial
        )
        ruta_archivo.write_text(codigo_modificado, encoding="utf-8")

        with redirect_stdout(io.StringIO()):
            codigo_salida = reapuntar_equivalentes(ruta_eq, self.raiz)

        self.assertEqual(codigo_salida, 0)
        datos_actualizados = json.loads(ruta_eq.read_text(encoding="utf-8"))
        self.assertEqual(datos_actualizados[0]["id"], "modulo.py:9:10:comparador")
        self.assertEqual(datos_actualizados[0]["linea_texto"], "while x < 10:")
        self.assertEqual(datos_actualizados[0]["ordinal"], 1)

    def test_reubicacion_no_confunde_dos_lineas_identicas_con_distinto_ordinal(self) -> None:
        # Archivo con dos bucles while idénticos en distintas funciones
        # Dos bucles con el texto EXACTAMENTE igual: el contenido solo no alcanza para decir
        # cuál es cuál, y ahí es donde el ordinal hace el trabajo.
        ruta_archivo = self.raiz / "modulo.py"
        codigo_repetido = (
            "def primero(i):\n"
            "    while i < 10:\n"
            "        i += 1\n"
            "    return i\n"
            "\n"
            "def segundo(i):\n"
            "    while i < 10:\n"
            "        i += 1\n"
            "    return i\n"
        )
        ruta_archivo.write_text(codigo_repetido, encoding="utf-8")

        declaraciones_repetidas = [
            {
                "id": "modulo.py:2:10:comparador",
                "linea_texto": "while i < 10:",
                "ordinal": 1,
                "razon": "primer bucle",
            },
            {
                "id": "modulo.py:7:10:comparador",
                "linea_texto": "while i < 10:",
                "ordinal": 2,
                "razon": "segundo bucle",
            },
        ]
        ruta_eq = self.raiz / "equivalentes.json"
        ruta_eq.write_text(json.dumps(declaraciones_repetidas), encoding="utf-8")

        # Las líneas nuevas van ENTRE las dos, así que los dos ids se corren distinto: el
        # primero uno, el segundo cuatro. Un mapeo por posición los confunde; por ordinal, no.
        codigo_con_espaciado = (
            "# encabezado\n"
            "def primero(i):\n"
            "    while i < 10:\n"
            "        i += 1\n"
            "    return i\n"
            "\n"
            "# comentario separador 1\n"
            "# comentario separador 2\n"
            "# comentario separador 3\n"
            "def segundo(i):\n"
            "    while i < 10:\n"
            "        i += 1\n"
            "    return i\n"
        )
        ruta_archivo.write_text(codigo_con_espaciado, encoding="utf-8")

        with redirect_stdout(io.StringIO()):
            codigo_salida = reapuntar_equivalentes(ruta_eq, self.raiz)

        self.assertEqual(codigo_salida, 0)
        datos = json.loads(ruta_eq.read_text(encoding="utf-8"))

        self.assertEqual(datos[0]["id"], "modulo.py:3:10:comparador")
        self.assertEqual(datos[0]["ordinal"], 1)
        self.assertEqual(datos[1]["id"], "modulo.py:11:10:comparador")
        self.assertEqual(datos[1]["ordinal"], 2)

    def test_contenido_desaparecido_no_se_reubica_en_silencio(self) -> None:
        codigo = (
            "def foo(x):\n"
            "    return x + 1\n"
        )
        ruta_archivo = self.raiz / "modulo.py"
        ruta_archivo.write_text(codigo, encoding="utf-8")

        declaraciones = [
            {
                "id": "modulo.py:10:10:comparador",
                "linea_texto": "while no_existe < 5:",
                "ordinal": 1,
                "razon": "código eliminado",
            }
        ]
        ruta_eq = self.raiz / "equivalentes.json"
        ruta_eq.write_text(json.dumps(declaraciones), encoding="utf-8")

        buf_err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(buf_err):
            codigo_salida = reapuntar_equivalentes(ruta_eq, self.raiz)

        # Falla cerrado y NO toca el id: un contenido que ya no está significa que el
        # equivalente hay que volver a mirarlo, no reubicarlo a cualquier lado.
        self.assertEqual(codigo_salida, 1)
        self.assertIn("ya no existe", buf_err.getvalue())
        datos = json.loads(ruta_eq.read_text(encoding="utf-8"))
        self.assertEqual(datos[0]["id"], "modulo.py:10:10:comparador")

    def test_sitio_ast_inexistente_en_linea_coincidente_falla_cerrado(self) -> None:
        # El texto de la línea coincide, pero en esa columna el AST ya no tiene ese tipo de
        # sitio. Reubicar por contenido sin mirar el AST declararía equivalente OTRO mutante.
        codigo = (
            "def foo(x):\n"
            "    while x == 10:\n"
            "        pass\n"
        )
        ruta_archivo = self.raiz / "modulo.py"
        ruta_archivo.write_text(codigo, encoding="utf-8")

        declaraciones = [
            {
                "id": "modulo.py:2:10:constante",
                "linea_texto": "while x == 10:",
                "ordinal": 1,
                "razon": "esperaba constante pero en col 10 hay comparador",
            }
        ]
        ruta_eq = self.raiz / "equivalentes.json"
        ruta_eq.write_text(json.dumps(declaraciones), encoding="utf-8")

        buf_err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(buf_err):
            codigo_salida = reapuntar_equivalentes(ruta_eq, self.raiz)

        self.assertEqual(codigo_salida, 1)
        self.assertIn("no existe el sitio mutante", buf_err.getvalue())

    def test_poblado_automatico_de_metadatos_en_sitio_vigente(self) -> None:
        codigo = (
            "def foo(x):\n"
            "    while x < 10:\n"
            "        x += 1\n"
            "    return x\n"
        )
        ruta_archivo = self.raiz / "modulo.py"
        ruta_archivo.write_text(codigo, encoding="utf-8")

        declaraciones = [
            {
                "id": "modulo.py:2:10:comparador",
                "razon": "sin linea_texto previa",
            }
        ]
        ruta_eq = self.raiz / "equivalentes.json"
        ruta_eq.write_text(json.dumps(declaraciones), encoding="utf-8")

        with redirect_stdout(io.StringIO()):
            codigo_salida = reapuntar_equivalentes(ruta_eq, self.raiz)

        self.assertEqual(codigo_salida, 0)
        datos = json.loads(ruta_eq.read_text(encoding="utf-8"))
        self.assertEqual(datos[0]["linea_texto"], "while x < 10:")
        self.assertEqual(datos[0]["ordinal"], 1)

    def test_equivalentes_del_alcance_sigue_fallando_cerrado_con_id_roto(self) -> None:
        # La reubicación es una herramienta, no una amnistía: el validador sigue cerrado.
        with self.assertRaises(EquivalenteInvalido):
            equivalentes_del_alcance(
                {"nucleo/caso.py:99999:0:constante": "fuera de rango"},
                [RAIZ / "nucleo/caso.py"],
            )

    def test_todas_las_entradas_del_repo_estan_vigentes_y_pobladas(self) -> None:
        # Sobre el archivo REAL del repo. Sin esto, alguien agrega una entrada a mano sin
        # metadatos y la reubicación deja de poder ayudarla justo cuando haga falta.
        declaraciones = leer_declaraciones_equivalentes(EQUIVALENTES)
        self.assertTrue(len(declaraciones) > 0, "debe haber equivalentes declarados")

        for d in declaraciones:
            self.assertIn("linea_texto", d, f"entrada {d['id']} sin linea_texto")
            self.assertIsInstance(d["linea_texto"], str)
            self.assertTrue(d["linea_texto"].strip())
            self.assertIn("ordinal", d, f"entrada {d['id']} sin ordinal")
            self.assertIsInstance(d["ordinal"], int)
            self.assertGreaterEqual(d["ordinal"], 1)

        mapeo = cargar_equivalentes(EQUIVALENTES)
        self.assertEqual(len(mapeo), len(declaraciones))
