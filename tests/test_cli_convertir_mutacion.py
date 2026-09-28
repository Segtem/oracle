"""Pruebas para matar mutantes sobrevivientes de tools/cli.py (Lista A)."""

from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from nucleo import caso, sintaxis
from nucleo.proyecto import Proyecto
from nucleo.sintaxis import ErrorSintaxis
from tools import cli

RAIZ = Path(__file__).resolve().parents[1]


class CliConvertirMutacionTests(unittest.TestCase):
    def _proy(self, raiz: Path) -> Proyecto:
        (raiz / "oracle.json").write_text('{"esquema": "oracle.proyecto/v1"}\n', encoding="utf-8")
        return Proyecto(raiz)

    # Mutante 1: tools/cli.py:720:8:retorno (return False → return None)
    def test_mismo_arbol_distintos_tipos_devuelve_falso_no_none(self):
        self.assertIs(cli._mismo_arbol(True, 1), False)
        self.assertIs(cli._mismo_arbol(1, 1.0), False)
        self.assertIs(cli._mismo_arbol("texto", 123), False)

    # Mutante 3: tools/cli.py:766:7:booleano (and ↔ or)
    def test_reemplazar_destino_existente_archivo_regular_falla_con_mensaje_preciso(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            origen = t / "fuente.json"
            origen.write_bytes(b"original")
            destino = t / "destino.oracle"
            destino.write_bytes(b"existente")
            with self.assertRaises(FileExistsError) as cm:
                cli._reemplazar(origen, destino, "nuevo", b"original")
            self.assertTrue(str(cm.exception).startswith("ya existe el destino"))

    # Mutante 4: tools/cli.py:782:11:comparador (IsNot → Is)
    def test_reemplazar_exitoso_limpia_archivo_temporal(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            origen = t / "fuente.json"
            origen.write_bytes(b"original")
            destino = t / "destino.oracle"
            cli._reemplazar(origen, destino, "nuevo", b"original")
            temporales = [p for p in t.iterdir() if p.name.startswith(".destino.oracle.")]
            self.assertEqual(temporales, [])
            self.assertEqual(destino.read_text(encoding="utf-8"), "nuevo")

    # Mutante 6: tools/cli.py:786:64:constante (False → True)
    def test_convertir_lote_defecto_no_escribe(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "catalogos/demo").mkdir(parents=True)
            medida_datos = sintaxis.leer((RAIZ / "catalogos/proceso/proceso.verificador_sin_falsos_rojos.oracle")
                                         .read_text(encoding="utf-8"))
            fuente = raiz / "catalogos/demo/medida.json"
            fuente.write_text(json.dumps(medida_datos, ensure_ascii=False), encoding="utf-8")
            proy = self._proy(raiz)

            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = cli._convertir_lote(raiz, proy)
            self.assertEqual(codigo, 0)
            self.assertIn("Vista previa; no se escriben archivos", salida.getvalue())
            self.assertNotIn("Conversión con --escribir", salida.getvalue())
            self.assertFalse((raiz / "catalogos/demo/medida.oracle").exists())

    # Mutante 7: tools/cli.py:787:7:booleano (and ↔ or)
    def test_convertir_lote_rechaza_archivo_regular_como_directorio(self):
        with tempfile.TemporaryDirectory() as tmp:
            archivo = Path(tmp) / "archivo.txt"
            archivo.write_text("texto", encoding="utf-8")
            proy = self._proy(Path(tmp))
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = cli._convertir_lote(archivo, proy)
            self.assertEqual(codigo, 1)
            self.assertIn("se esperaba un directorio físico", salida.getvalue())

    # Mutante 8: tools/cli.py:789:8:retorno (return <algo> → return None)
    def test_convertir_lote_directorio_invalido_retorna_uno_no_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            archivo = Path(tmp) / "archivo.txt"
            archivo.write_text("texto", encoding="utf-8")
            proy = self._proy(Path(tmp))
            with redirect_stdout(io.StringIO()):
                codigo = cli._convertir_lote(archivo, proy)
            self.assertIs(codigo, 1)

    # Mutante 9: tools/cli.py:789:15:constante (1 → 2)
    def test_convertir_lote_directorio_invalido_retorna_uno_no_dos(self):
        with tempfile.TemporaryDirectory() as tmp:
            archivo = Path(tmp) / "archivo.txt"
            archivo.write_text("texto", encoding="utf-8")
            proy = self._proy(Path(tmp))
            with redirect_stdout(io.StringIO()):
                codigo = cli._convertir_lote(archivo, proy)
            self.assertEqual(codigo, 1)

    # Mutante 10: tools/cli.py:801:15:booleano (and ↔ or)
    def test_convertir_lote_rechaza_origen_que_es_enlace_simbolico(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "corpus/demo").mkdir(parents=True)
            real = raiz / "real.json"
            real.write_text("{}", encoding="utf-8")
            enlace = raiz / "corpus/demo/caso.json"
            enlace.symlink_to(real)
            proy = self._proy(raiz)
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = cli._convertir_lote(raiz, proy)
            self.assertEqual(codigo, 1)
            self.assertIn("el origen debe ser un archivo físico", salida.getvalue())

    # Mutante 11: tools/cli.py:803:15:booleano (and ↔ or)
    def test_convertir_lote_rechaza_destino_que_ya_existe_como_archivo_regular(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "catalogos/demo").mkdir(parents=True)
            medida_datos = sintaxis.leer((RAIZ / "catalogos/proceso/proceso.verificador_sin_falsos_rojos.oracle")
                                         .read_text(encoding="utf-8"))
            fuente = raiz / "catalogos/demo/medida.json"
            fuente.write_text(json.dumps(medida_datos, ensure_ascii=False), encoding="utf-8")
            (raiz / "catalogos/demo/medida.oracle").write_text("existente", encoding="utf-8")
            proy = self._proy(raiz)
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = cli._convertir_lote(raiz, proy)
            self.assertEqual(codigo, 1)
            self.assertIn("ya existe el destino", salida.getvalue())

    # Mutante 12: tools/cli.py:807:15:booleano (and ↔ or)
    def test_convertir_lote_solo_corpus_no_carga_macros(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "corpus/demo").mkdir(parents=True)
            caso_datos = caso.leer((RAIZ / "corpus/meta/477-medida-universal-depende-por-requiere-de-relacion-del-origen.caso")
                                   .read_text(encoding="utf-8"))
            fuente = raiz / "corpus/demo/caso.json"
            fuente.write_text(json.dumps(caso_datos, ensure_ascii=False), encoding="utf-8")
            proy = self._proy(raiz)
            with mock.patch("tools.cli.macros_del_proyecto") as mock_macros:
                with redirect_stdout(io.StringIO()):
                    cli._convertir_lote(raiz, proy)
                mock_macros.assert_not_called()

    # Mutante 13: tools/cli.py:807:15:comparador (Eq → NotEq)
    def test_convertir_lote_catalogo_carga_macros(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "catalogos/demo").mkdir(parents=True)
            medida_datos = sintaxis.leer((RAIZ / "catalogos/proceso/proceso.verificador_sin_falsos_rojos.oracle")
                                         .read_text(encoding="utf-8"))
            fuente = raiz / "catalogos/demo/medida.json"
            fuente.write_text(json.dumps(medida_datos, ensure_ascii=False), encoding="utf-8")
            proy = self._proy(raiz)
            with mock.patch("tools.cli.macros_del_proyecto", return_value={}) as mock_macros:
                with redirect_stdout(io.StringIO()):
                    cli._convertir_lote(raiz, proy)
                mock_macros.assert_called_once()

    # Mutante 14: tools/cli.py:807:39:comparador (Is → IsNot)
    def test_convertir_lote_catalogo_requiere_macros_inicialmente_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "catalogos/demo").mkdir(parents=True)
            medida_datos = sintaxis.leer((RAIZ / "catalogos/proceso/proceso.verificador_sin_falsos_rojos.oracle")
                                         .read_text(encoding="utf-8"))
            fuente = raiz / "catalogos/demo/medida.json"
            fuente.write_text(json.dumps(medida_datos, ensure_ascii=False), encoding="utf-8")
            proy = self._proy(raiz)
            with mock.patch("tools.cli.macros_del_proyecto", return_value={}) as mock_macros:
                with redirect_stdout(io.StringIO()):
                    cli._convertir_lote(raiz, proy)
                mock_macros.assert_called_once()

    # Mutante 15: tools/cli.py:818:31:constante (1 → 2)
    def test_convertir_lote_cuenta_exacta_no_convertibles(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "catalogos/demo").mkdir(parents=True)
            (raiz / "catalogos/demo/invalido.json").write_text("{invalido json", encoding="utf-8")
            proy = self._proy(raiz)
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = cli._convertir_lote(raiz, proy)
            self.assertEqual(codigo, 1)
            self.assertIn("Resumen: 0 convertibles; 1 no convertibles", salida.getvalue())
            self.assertNotIn("2 no convertibles", salida.getvalue())

    # Mutante 16: tools/cli.py:825:34:constante (False → True)
    def test_cmd_convertir_defecto_no_escribe(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "catalogos/demo").mkdir(parents=True)
            medida_datos = sintaxis.leer((RAIZ / "catalogos/proceso/proceso.verificador_sin_falsos_rojos.oracle")
                                         .read_text(encoding="utf-8"))
            fuente = raiz / "catalogos/demo/medida.json"
            fuente.write_text(json.dumps(medida_datos, ensure_ascii=False), encoding="utf-8")
            proy = self._proy(raiz)
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = cli.cmd_convertir(proy, str(raiz), a_superficie=True)
            self.assertEqual(codigo, 0)
            self.assertIn("Vista previa; no se escriben archivos", salida.getvalue())
            self.assertNotIn("Conversión con --escribir", salida.getvalue())
            self.assertFalse((raiz / "catalogos/demo/medida.oracle").exists())

    # Mutante 17: tools/cli.py:864:8:retorno (return <algo> → return None)
    def test_cmd_convertir_error_sintaxis_retorna_uno_no_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            archivo = raiz / "medida.json"
            archivo.write_text("{}", encoding="utf-8")
            proy = self._proy(raiz)
            with mock.patch("nucleo.medida.cargar_fuente_medida",
                            side_effect=ErrorSintaxis(1, 1, "esperado", "encontrado")):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    codigo = cli.cmd_convertir(proy, str(archivo))
                self.assertIs(codigo, 1)

    # Mutante 18: tools/cli.py:864:15:constante (1 → 2)
    def test_cmd_convertir_error_sintaxis_retorna_uno_no_dos(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            archivo = raiz / "medida.json"
            archivo.write_text("{}", encoding="utf-8")
            proy = self._proy(raiz)
            with mock.patch("nucleo.medida.cargar_fuente_medida",
                            side_effect=ErrorSintaxis(1, 1, "esperado", "encontrado")):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    codigo = cli.cmd_convertir(proy, str(archivo))
                self.assertEqual(codigo, 1)

    # Mutante 19: tools/cli.py:874:7:negacion (se borra el `not`)
    def test_cmd_formatear_ruta_relativa_a_raiz_proyecto(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "catalogos").mkdir(parents=True)
            medida = raiz / "catalogos/medida.oracle"
            medida.write_text((RAIZ / "catalogos/proceso/proceso.verificador_sin_falsos_rojos.oracle")
                              .read_text(encoding="utf-8"), encoding="utf-8")
            proy = self._proy(raiz)
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = cli.cmd_formatear(proy, "catalogos/medida.oracle")
            self.assertEqual(codigo, 0)

    # Mutante 20: tools/cli.py:885:24:booleano (and ↔ or)
    def test_cmd_formatear_directorio_ignora_carpeta_diferencial(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            directorio = raiz / "subcarpeta"
            (directorio / "diferencial").mkdir(parents=True)
            archivo_dif = directorio / "diferencial/test.oracle"
            archivo_dif.write_text((RAIZ / "catalogos/proceso/proceso.verificador_sin_falsos_rojos.oracle")
                                   .read_text(encoding="utf-8"), encoding="utf-8")
            proy = self._proy(raiz)
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = cli.cmd_formatear(proy, str(directorio))
            self.assertEqual(codigo, 1)
            self.assertIn("no hay archivos .oracle, .caso, .relacion ni .requisito", salida.getvalue())

    # Mutante 21: tools/cli.py:888:12:retorno (return <algo> → return None)
    def test_cmd_formatear_directorio_sin_archivos_retorna_uno_no_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            proy = self._proy(raiz)
            with redirect_stdout(io.StringIO()):
                codigo = cli.cmd_formatear(proy, str(raiz))
            self.assertIs(codigo, 1)

    # Mutante 22: tools/cli.py:888:19:constante (1 → 2)
    def test_cmd_formatear_directorio_sin_archivos_retorna_uno_no_dos(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            proy = self._proy(raiz)
            with redirect_stdout(io.StringIO()):
                codigo = cli.cmd_formatear(proy, str(raiz))
            self.assertEqual(codigo, 1)

    # Mutante 23: tools/cli.py:895:7:booleano (and ↔ or)
    def test_cmd_formatear_archivo_extension_no_soportada_rechaza(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            archivo = raiz / "documento.txt"
            archivo.write_text("texto plano", encoding="utf-8")
            proy = self._proy(raiz)
            salida = io.StringIO()
            with redirect_stdout(salida):
                try:
                    codigo = cli.cmd_formatear(proy, str(archivo))
                except ValueError:
                    codigo = -1
            self.assertEqual(codigo, 1)
            self.assertIn("se espera un archivo .oracle, .caso, .relacion o .requisito, o un directorio", salida.getvalue())

    # Mutante 24: tools/cli.py:897:8:retorno (return <algo> → return None)
    def test_cmd_formatear_archivo_extension_invalida_retorna_uno_no_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            archivo = raiz / "documento.txt"
            archivo.write_text("texto plano", encoding="utf-8")
            proy = self._proy(raiz)
            with redirect_stdout(io.StringIO()):
                codigo = cli.cmd_formatear(proy, str(archivo))
            self.assertIs(codigo, 1)

    # Mutante 25: tools/cli.py:897:15:constante (1 → 2)
    def test_cmd_formatear_archivo_extension_invalida_retorna_uno_no_dos(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            archivo = raiz / "documento.txt"
            archivo.write_text("texto plano", encoding="utf-8")
            proy = self._proy(raiz)
            with redirect_stdout(io.StringIO()):
                codigo = cli.cmd_formatear(proy, str(archivo))
            self.assertEqual(codigo, 1)
