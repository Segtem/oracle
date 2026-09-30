from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from nucleo.requisito import (RequisitoMalDeclarado, cargar_requisitos, hechos_de_requisitos, imprimir,
                              leer)

MEDIDO = """requisito cli_validate.rutas_de_archivo:
    texto "Todo error SHALL incluir la ruta del archivo fuente"
    fuente "openspec/specs/cli-validate/spec.md"
    medido_por openspec.a, openspec.b
"""

SIN_MEDIDA = """requisito cli_validate.progreso:
    texto "Muestra el progreso"
    sin_medir "la barra de progreso sólo se ve en una terminal"
"""

PARCIAL = """requisito cli_validate.opciones:
    texto "Acepta --strict y --json y muestra el progreso"
    medido_por openspec.a
    sin_medir "el progreso sólo se ve en una terminal"
"""


class SuperficieTests(unittest.TestCase):
    def test_ida_y_vuelta(self) -> None:
        for texto in (MEDIDO, SIN_MEDIDA, PARCIAL):
            with self.subTest(texto=texto.splitlines()[0]):
                self.assertEqual(imprimir(leer(texto)), texto)

    def test_arbol(self) -> None:
        self.assertEqual(leer(MEDIDO), [
            "requisito", "cli_validate.rutas_de_archivo",
            ["texto", "Todo error SHALL incluir la ruta del archivo fuente"],
            ["fuente", "openspec/specs/cli-validate/spec.md"],
            ["medido_por", "openspec.a", "openspec.b"]])
        self.assertEqual(leer(SIN_MEDIDA)[-1], ["sin_medir", "la barra de progreso sólo se ve en una terminal"])
        self.assertEqual([c[0] for c in leer(PARCIAL)[2:]], ["texto", "medido_por", "sin_medir"])

    def test_comentarios_no_son_parte_del_arbol(self) -> None:
        self.assertEqual(leer("# nota\n" + MEDIDO), leer(MEDIDO))

    def test_rechaza(self) -> None:
        cabecera = 'requisito a.b:\n    texto "t"\n'
        malos = {
            "ni medido_por ni sin_medir": cabecera,
            "orden cambiado": cabecera + '    sin_medir "p"\n    medido_por x.y\n',
            "fuente después de medido_por": cabecera + '    medido_por x.y\n    fuente "f"\n',
            "medido_por dos veces": cabecera + '    medido_por x.y\n    medido_por x.z\n',
            "medida repetida": cabecera + "    medido_por x.y, x.y\n",
            "id de medida inválido": cabecera + "    medido_por Mala\n",
            "id no ASCII": 'requisito a.dueño:\n    texto "t"\n    medido_por x.y\n',
            "id sin dominio": 'requisito ab:\n    texto "t"\n    medido_por x.y\n',
            "texto vacío": 'requisito a.b:\n    texto ""\n    medido_por x.y\n',
            "sin_medir vacío": 'requisito a.b:\n    texto "t"\n    sin_medir ""\n',
            "fuente vacía": 'requisito a.b:\n    texto "t"\n    fuente ""\n    medido_por x.y\n',
            "sin texto": 'requisito a.b:\n    medido_por x.y\n',
            "cláusula desconocida": cabecera + '    prioridad "alta"\n    medido_por x.y\n',
            "sin cabecera": '    texto "t"\n',
        }
        for motivo, texto in malos.items():
            with self.subTest(motivo=motivo), self.assertRaises(RequisitoMalDeclarado):
                leer(texto)


class ArbolTests(unittest.TestCase):
    def test_de_datos_rechaza_lo_que_no_es_un_requisito(self) -> None:
        from nucleo.requisito import Requisito
        for datos in ("requisito", ["requisito", "a.b"], ["otro", "a.b", ["texto", "t"]],
                      ("requisito", "a.b", ["texto", "t"], ["medido_por", "x.y"])):
            with self.subTest(datos=datos), self.assertRaisesRegex(RequisitoMalDeclarado, "se esperaba"):
                Requisito.de_datos(datos)

    def test_el_minimo_es_id_texto_y_una_clausula(self) -> None:
        from nucleo.requisito import Requisito
        r = Requisito.de_datos(["requisito", "a.b", ["texto", "t"], ["sin_medir", "p"]])
        self.assertEqual((r.cobertura, r.sin_medir), ("ninguna", "p"))
        with self.assertRaisesRegex(RequisitoMalDeclarado, "al menos una"):
            Requisito.de_datos(["requisito", "a.b", ["texto", "t"]])

    def test_es_inmutable(self) -> None:
        from dataclasses import FrozenInstanceError
        from nucleo.requisito import Requisito
        with self.assertRaises(FrozenInstanceError):
            Requisito.de_datos(leer(MEDIDO)).texto = "otro"

    def test_el_error_nombra_la_linea(self) -> None:
        with self.assertRaisesRegex(RequisitoMalDeclarado, "^línea 3: "):
            leer('requisito a.b:\n    texto "t"\n    prioridad "alta"\n')


class CargaTests(unittest.TestCase):
    def _dir(self, archivos: dict[str, str]) -> Path:
        base = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(base))
        for nombre, texto in archivos.items():
            (base / nombre).write_text(texto, encoding="utf-8")
        return base

    def test_carga_y_hechos(self) -> None:
        base = self._dir({"cli_validate.rutas_de_archivo.requisito": MEDIDO,
                          "cli_validate.progreso.requisito": SIN_MEDIDA,
                          "cli_validate.opciones.requisito": PARCIAL})
        hechos = hechos_de_requisitos(cargar_requisitos(base).values())
        self.assertEqual(hechos["requisito_medido_por"], [
            {"requisito": "cli_validate.opciones", "medida": "openspec.a"},
            {"requisito": "cli_validate.rutas_de_archivo", "medida": "openspec.a"},
            {"requisito": "cli_validate.rutas_de_archivo", "medida": "openspec.b"}])
        por_id = {f["requisito"]: f for f in hechos["requisito_declarado"]}
        self.assertEqual(por_id["cli_validate.progreso"],
                         {"requisito": "cli_validate.progreso", "texto": "Muestra el progreso", "fuente": "",
                          "medidas": 0, "cobertura": "ninguna",
                          "sin_medir": "la barra de progreso sólo se ve en una terminal"})
        self.assertEqual(por_id["cli_validate.rutas_de_archivo"]["cobertura"], "total")
        self.assertEqual(por_id["cli_validate.rutas_de_archivo"]["medidas"], 2)
        self.assertEqual(por_id["cli_validate.opciones"]["cobertura"], "parcial")

    def test_sin_directorio_no_hay_requisitos(self) -> None:
        self.assertEqual(cargar_requisitos(Path(tempfile.gettempdir()) / "no-existe-requisitos"), {})

    def test_el_archivo_se_llama_como_su_id(self) -> None:
        base = self._dir({"otro.nombre.requisito": MEDIDO})
        with self.assertRaisesRegex(RequisitoMalDeclarado, "se llama como su id"):
            cargar_requisitos(base)

    def test_fuera_de_forma_unica_no_carga(self) -> None:
        base = self._dir({"cli_validate.rutas_de_archivo.requisito": MEDIDO.replace("a, openspec.b", "a,openspec.b")})
        with self.assertRaises(RequisitoMalDeclarado):
            cargar_requisitos(base)


class CoberturaTests(unittest.TestCase):
    def _proyecto(self, requisitos: dict[str, str]) -> Path:
        raiz = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(raiz))
        (raiz / "oracle.json").write_text(
            '{"esquema": "oracle.proyecto/v1", "catalogo_base": false, "perfiles": []}\n', encoding="utf-8")
        for d in ("catalogos", "corpus", "diferencial", "requisitos"):
            (raiz / d).mkdir()
        (raiz / "catalogos" / "openspec.a.oracle").write_text(
            "ninguno openspec.a:\n    de corrida c\n    donde c.codigo != 0\n"
            '    umbral <= 0 segun contrato porque "cero"\n    ambito universal\n    alcance "prueba"\n',
            encoding="utf-8")
        for nombre, texto in requisitos.items():
            (raiz / "requisitos" / nombre).write_text(texto, encoding="utf-8")
        return raiz

    def _correr(self, raiz: Path) -> tuple[int, str]:
        from nucleo.proyecto import Proyecto
        from tools import cobertura
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = cobertura.main(Proyecto(raiz))
        return codigo, salida.getvalue()

    def test_informa_y_falla_ante_una_medida_inexistente(self) -> None:
        raiz = self._proyecto({"cli_validate.rutas_de_archivo.requisito": MEDIDO,
                               "cli_validate.progreso.requisito": SIN_MEDIDA})
        codigo, texto = self._correr(raiz)
        self.assertEqual(codigo, 1)
        self.assertIn("✗ cli_validate.rutas_de_archivo   nombra medidas que no existen: openspec.b", texto)
        self.assertIn("· cli_validate.progreso   SIN MEDIR: la barra de progreso sólo se ve en una terminal", texto)
        self.assertIn("2 requisitos: 0 medidos · 0 en parte · 1 sin medir · 1 con medidas inexistentes", texto)

    def test_verde_y_medidas_huerfanas(self) -> None:
        raiz = self._proyecto({"cli_validate.progreso.requisito": SIN_MEDIDA})
        codigo, texto = self._correr(raiz)
        self.assertEqual(codigo, 0)
        self.assertIn("1 de 1 medidas propias no cubren ningún requisito:\n  · openspec.a", texto)

    def test_medido_y_parcial(self) -> None:
        raiz = self._proyecto({"cli_validate.rutas_de_archivo.requisito": MEDIDO.replace(", openspec.b", ""),
                               "cli_validate.opciones.requisito": PARCIAL})
        codigo, texto = self._correr(raiz)
        self.assertEqual(codigo, 0)
        self.assertIn("✓ cli_validate.rutas_de_archivo   openspec.a\n", texto)
        self.assertIn("◐ cli_validate.opciones   openspec.a · SIN MEDIR: el progreso sólo se ve en una terminal", texto)
        self.assertIn("2 requisitos: 1 medidos · 1 en parte · 0 sin medir · 0 con medidas inexistentes", texto)
        self.assertNotIn("no cubren", texto)

    def test_un_requisito_mal_escrito_sale_con_1(self) -> None:
        raiz = self._proyecto({"cli_validate.malo.requisito": 'requisito cli_validate.malo:\n    texto "t"\n'})
        codigo, texto = self._correr(raiz)
        self.assertEqual(codigo, 1)
        self.assertTrue(texto.startswith("✗ "), texto)
        self.assertIn("cli_validate.malo.requisito", texto)

    def test_un_proyecto_con_escalares_propias_pide_confianza(self) -> None:
        # 2026-09-29: en LyraGASP `oracle cobertura` terminaba en una traza, porque cargaba el
        # catálogo sin registrar medidas/escalares.py.
        raiz = self._proyecto({"cli_validate.rutas_de_archivo.requisito": MEDIDO.replace(", openspec.b", "")})
        (raiz / "escalares.py").write_text(
            "from oracle_metalenguaje import escalar\n\n\n@escalar(\"es_grande\")\ndef es_grande(x):\n"
            "    return x > 10\n", encoding="utf-8")
        (raiz / "catalogos" / "openspec.a.oracle").write_text(
            "ninguno openspec.a:\n    de corrida c\n    donde es_grande(c.codigo)\n"
            '    umbral <= 0 segun contrato porque "cero"\n    ambito universal\n    alcance "prueba"\n',
            encoding="utf-8")
        from nucleo.proyecto import Proyecto
        from tools import cobertura
        salida = io.StringIO()
        with redirect_stdout(salida):
            self.assertEqual(cobertura.main(Proyecto(raiz)), 1)
        self.assertIn("ESCALARES EXTERNAS NO EJECUTADAS", salida.getvalue())
        self.assertIn("--confiar-escalares", salida.getvalue())
        salida = io.StringIO()
        with redirect_stdout(salida):
            self.assertEqual(cobertura.main(Proyecto(raiz), confiar=True), 0)
        self.assertIn("✓ cli_validate.rutas_de_archivo   openspec.a", salida.getvalue())
        from tools import cli
        with redirect_stdout(io.StringIO()) as cli_salida:
            self.assertEqual(cli.main(["cobertura", "--proyecto", str(raiz), "--confiar-escalares"]), 0)
        self.assertIn("1 requisitos: 1 medidos", cli_salida.getvalue())

    def _juzgar(self, raiz: Path, evidencia: dict, *, cli_argv: bool = False) -> tuple[int, str]:
        ruta = raiz / "hechos.json"
        ruta.write_text(json.dumps(evidencia), encoding="utf-8")
        from nucleo.proyecto import Proyecto
        from tools import cli, cobertura
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = (cli.main(["cobertura", "--con", str(ruta), "--proyecto", str(raiz)]) if cli_argv
                      else cobertura.main(Proyecto(raiz), con=str(ruta)))
        return codigo, salida.getvalue()

    def test_con_evidencia_dice_si_se_cumple(self) -> None:
        raiz = self._proyecto({"cli_validate.rutas_de_archivo.requisito": MEDIDO.replace(", openspec.b", ""),
                               "cli_validate.opciones.requisito": PARCIAL,
                               "cli_validate.progreso.requisito": SIN_MEDIDA})
        codigo, texto = self._juzgar(raiz, {"corrida": [{"codigo": 0}]})
        self.assertEqual(codigo, 0)
        self.assertIn("✓ cli_validate.rutas_de_archivo   cumple · openspec.a cumple\n", texto)
        self.assertIn("◐ cli_validate.opciones   cumple · openspec.a cumple · SIN MEDIR: el progreso", texto)
        self.assertIn("· cli_validate.progreso   sin medir · SIN MEDIR:", texto)
        self.assertIn("3 requisitos: 2 se cumplen (1 sólo en lo medido) · 0 no se cumplen · 0 sin juicio"
                      " · 1 sin medir · 0 con medidas inexistentes", texto)
        codigo, texto = self._juzgar(raiz, {"corrida": [{"codigo": 2}]}, cli_argv=True)
        self.assertEqual(codigo, 1)
        self.assertIn("✗ cli_validate.rutas_de_archivo   no cumple · openspec.a falla\n", texto)
        self.assertIn("0 se cumplen (0 sólo en lo medido) · 2 no se cumplen", texto)

    def test_en_sombra_no_se_cumple_pero_no_hace_fallar(self) -> None:
        raiz = self._proyecto({"cli_validate.rutas_de_archivo.requisito": MEDIDO.replace(", openspec.b", "")})
        (raiz / "oracle.json").write_text(json.dumps({
            "esquema": "oracle.proyecto/v1", "catalogo_base": False, "perfiles": [],
            "sombra": {"openspec.a": {"desde": "2026-09-30", "porque": "deuda", "cota": 5}}}), encoding="utf-8")
        codigo, texto = self._juzgar(raiz, {"corrida": [{"codigo": 2}]})
        self.assertEqual(codigo, 0)
        self.assertIn("✗ cli_validate.rutas_de_archivo   no cumple · openspec.a falla en sombra", texto)

    def test_sin_la_relacion_queda_sin_juicio(self) -> None:
        raiz = self._proyecto({"cli_validate.rutas_de_archivo.requisito": MEDIDO.replace(", openspec.b", "")})
        codigo, texto = self._juzgar(raiz, {"otra": [{"x": 1}]})
        self.assertEqual(codigo, 0)
        self.assertIn("? cli_validate.rutas_de_archivo   sin juicio · openspec.a no aplicada", texto)
        self.assertIn("0 se cumplen (0 sólo en lo medido) · 0 no se cumplen · 1 sin juicio", texto)

    def test_sin_evidencia_no_juzgo_e_inexistente(self) -> None:
        raiz = self._proyecto({"cli_validate.rutas_de_archivo.requisito": MEDIDO.replace(", openspec.b", ""),
                               "cli_validate.otro.requisito": MEDIDO.replace("cli_validate.rutas_de_archivo",
                                                                             "cli_validate.otro")})
        medida = raiz / "catalogos" / "openspec.a.oracle"
        medida.write_text("medida openspec.a:\n    de corrida c\n    donde c.codigo != 0\n    resumen contar(1)\n"
                          '    umbral <= 0 segun contrato porque "cero"\n    requiere corrida\n'
                          '    ambito universal\n    alcance "prueba"\n', encoding="utf-8")
        codigo, texto = self._juzgar(raiz, {"corrida": []})
        self.assertEqual(codigo, 1)
        self.assertIn("? cli_validate.rutas_de_archivo   sin juicio · openspec.a sin evidencia\n", texto)
        self.assertIn("✗ cli_validate.otro   nombra medidas que no existen: openspec.b", texto)
        self.assertIn("0 se cumplen (0 sólo en lo medido) · 0 no se cumplen · 1 sin juicio · 0 sin medir"
                      " · 1 con medidas inexistentes", texto)
        (raiz / "requisitos" / "cli_validate.otro.requisito").unlink()
        codigo, texto = self._juzgar(raiz, {"corrida": [{"otro": 1}]})
        self.assertEqual(codigo, 1)
        self.assertIn("? cli_validate.rutas_de_archivo   sin juicio · openspec.a no juzgó\n", texto)
        self.assertIn("✗ openspec.a no juzgó: ", texto)

    def test_un_proyecto_que_no_se_puede_juzgar_se_dice(self) -> None:
        raiz = self._proyecto({"cli_validate.progreso.requisito": SIN_MEDIDA})
        (raiz / "oracle.json").write_text(json.dumps({
            "esquema": "oracle.proyecto/v1", "catalogo_base": False, "perfiles": [],
            "sombra": {"openspec.a": {"desde": "2026-09-30", "porque": "deuda", "cota": "mucha"}}}),
            encoding="utf-8")
        codigo, texto = self._juzgar(raiz, {"corrida": [{"codigo": 0}]})
        self.assertEqual(codigo, 1)
        self.assertTrue(texto.startswith("✗ no se pudo juzgar la evidencia: "), texto)

    def test_evidencia_ilegible_o_uso_malo(self) -> None:
        raiz = self._proyecto({"cli_validate.progreso.requisito": SIN_MEDIDA})
        from nucleo.proyecto import Proyecto
        from tools import cli, cobertura
        with redirect_stdout(io.StringIO()) as salida:
            self.assertEqual(cobertura.main(Proyecto(raiz), con=str(raiz / "no-existe.json")), 1)
        self.assertIn("✗ el archivo de evidencia no existe", salida.getvalue())
        with redirect_stdout(io.StringIO()) as salida:
            self.assertEqual(cli.main(["cobertura", "--con", "--proyecto", str(raiz)]), 1)
        self.assertIn("uso: oracle cobertura [--con <hechos.json>]", salida.getvalue())

    def test_sin_requisitos(self) -> None:
        codigo, texto = self._correr(self._proyecto({}))
        self.assertEqual((codigo, texto), (0, "sin requisitos: el proyecto no tiene requisitos/*.requisito\n"))


if __name__ == "__main__":
    unittest.main()
