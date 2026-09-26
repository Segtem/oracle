"""`oracle relaciones --escribir`: borradores de las relaciones observadas que faltan declarar.

La primera versión de esta herramienta declaraba directo y escribía `sin_unidad` en todo: sobre
LyraGASP bajaba `meta.toda_cantidad_comparada_tiene_unidad_derivable` de 60 a 0 afirmando que
medidas en centímetros no tenían unidad. Estos tests fijan lo contrario: la herramienta escribe sólo
lo que se puede saber mirando la evidencia, y nunca cambia lo que el proyecto carga.
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from nucleo.proyecto import Proyecto, ProyectoInvalido, relaciones_del_proyecto
from tools import cli
from tools.medida import CARPETA_POR_REVISAR, _borrador, _tipo_declarable

CASO = """caso 001-un-tornillo:
    fecha: "2026-09-16"
    origen:
        tipo: "construido para probar los borradores"
    procedencia: construida
    titulo: "un tornillo"
    etiqueta: verde_correcto
    sintoma:
        Construido.
    como_se_detecto: persona
    medida: tornillos.ninguno_alto
    evidencia:
        tornillo: nombre, alto, visible
            "a", 3, true
            "b", 7, false
    leccion:
        Construido.
"""


class TipoYUnidadTests(unittest.TestCase):
    def test_el_tipo_sale_de_lo_que_la_evidencia_trajo(self) -> None:
        self.assertEqual(_tipo_declarable({"str"}), "texto")
        self.assertEqual(_tipo_declarable({"bool"}), "booleano")
        self.assertEqual(_tipo_declarable({"int"}), "entero")
        self.assertEqual(_tipo_declarable({"float"}), "flotante")

    def test_un_entero_y_un_flotante_juntos_son_flotante(self) -> None:
        self.assertEqual(_tipo_declarable({"int", "float"}), "flotante")

    def test_un_nulo_no_cambia_el_tipo_de_las_veces_que_vino(self) -> None:
        self.assertEqual(_tipo_declarable({"int", "NoneType"}), "entero")
        self.assertIsNone(_tipo_declarable({"NoneType"}))

    def test_una_mezcla_que_no_se_puede_decidir_no_se_adivina(self) -> None:
        self.assertIsNone(_tipo_declarable({"str", "int"}))
        self.assertIsNone(_tipo_declarable({"list"}))

    def test_solo_se_declara_la_unidad_que_se_puede_saber(self) -> None:
        """Un texto o un booleano no tienen magnitud: su `sin_unidad` es un hecho. Un número puede
        ser una cuenta, centímetros o segundos, y eso no está en la evidencia: queda vacío."""
        borrador, sin_decidir = _borrador(
            "tornillo", {"nombre": {"str"}, "alto": {"int"}, "visible": {"bool"}})
        self.assertEqual(sin_decidir, [])
        self.assertEqual(borrador[2], ["campos",
                                       ["campo", "alto", "entero", ""],
                                       ["campo", "nombre", "texto", "sin_unidad"],
                                       ["campo", "visible", "booleano", "sin_unidad"]])
        self.assertEqual(borrador[3], ["alcance", ""])

    def test_una_relacion_con_un_campo_ambiguo_no_tiene_borrador(self) -> None:
        borrador, sin_decidir = _borrador("tornillo", {"alto": {"int"}, "raro": {"str", "int"}})
        self.assertIsNone(borrador)
        self.assertEqual(sin_decidir, ["raro (int/str)"])


    def test_un_nombre_que_el_lector_no_acepta_no_tiene_borrador(self) -> None:
        """Un borrador con un nombre inválido no carga nunca, por más que se completen las
        unidades: mejor decirlo antes de que alguien lo revise."""
        borrador, sin_decidir = _borrador("tornillo", {"año": {"int"}, "alto": {"int"}})
        self.assertIsNone(borrador)
        self.assertEqual(sin_decidir, ["año (nombre inválido)"])
        borrador, sin_decidir = _borrador("Tornillo", {"alto": {"int"}})
        self.assertIsNone(borrador)
        self.assertEqual(sin_decidir, ["el nombre de la relación no es válido"])


class EscribirBorradoresTests(unittest.TestCase):
    def setUp(self) -> None:
        temporal = tempfile.TemporaryDirectory(prefix="oracle-borradores-")
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        with redirect_stdout(io.StringIO()):
            cli.main(["init", str(self.raiz)])
        caso = self.raiz / "corpus" / "tornillos" / "001-un-tornillo.caso"
        caso.parent.mkdir(parents=True, exist_ok=True)
        caso.write_text(CASO, encoding="utf-8")

    def _escribir(self) -> tuple[int, str]:
        salida = io.StringIO()
        with redirect_stdout(salida):
            rc = cli.main(["relaciones", "--escribir", "--proyecto", str(self.raiz)])
        return rc, salida.getvalue()

    def test_escribe_el_borrador_fuera_de_lo_que_el_proyecto_carga(self) -> None:
        rc, salida = self._escribir()
        self.assertEqual(rc, 0, salida)
        borrador = self.raiz / CARPETA_POR_REVISAR / "tornillo.relacion"
        self.assertTrue(borrador.is_file(), salida)
        self.assertIn("falta 1 unidad(es) y el alcance", salida)
        self.assertFalse((self.raiz / "relaciones" / "tornillo.relacion").exists())
        self.assertNotIn("tornillo", relaciones_del_proyecto(Proyecto(self.raiz)))

    def test_un_borrador_movido_sin_completar_no_carga_y_dice_que_falta(self) -> None:
        self._escribir()
        destino = self.raiz / "relaciones"
        destino.mkdir(exist_ok=True)
        (self.raiz / CARPETA_POR_REVISAR / "tornillo.relacion").rename(destino / "tornillo.relacion")
        with self.assertRaisesRegex(ProyectoInvalido, "tornillo.alto: falta unidad"):
            relaciones_del_proyecto(Proyecto(self.raiz))

    def test_completado_y_movido_carga_con_lo_que_decidio_el_autor(self) -> None:
        self._escribir()
        origen = self.raiz / CARPETA_POR_REVISAR / "tornillo.relacion"
        texto = origen.read_text(encoding="utf-8")
        texto = texto.replace("alto: entero", "alto: entero cm")
        texto = texto.replace('alcance ""', 'alcance "la altura y la visibilidad de cada tornillo; NO ve su posición"')
        destino = self.raiz / "relaciones"
        destino.mkdir(exist_ok=True)
        (destino / "tornillo.relacion").write_text(texto, encoding="utf-8")
        origen.unlink()
        tornillo = relaciones_del_proyecto(Proyecto(self.raiz))["tornillo"]
        self.assertEqual({c.nombre: c.unidad for c in tornillo.todos_los_campos},
                         {"alto": "cm", "nombre": "sin_unidad", "visible": "sin_unidad"})

    def test_no_pisa_un_borrador_que_ya_existe(self) -> None:
        """Puede tener trabajo de alguien a medio hacer."""
        self._escribir()
        borrador = self.raiz / CARPETA_POR_REVISAR / "tornillo.relacion"
        borrador.write_text("a medio completar", encoding="utf-8")
        rc, salida = self._escribir()
        self.assertEqual(rc, 0)
        self.assertIn("tornillo — ya tiene un borrador; no se pisa", salida)
        self.assertEqual(borrador.read_text(encoding="utf-8"), "a medio completar")

    def test_con_la_carpeta_ya_creada_escribe_el_borrador_nuevo(self) -> None:
        """Una segunda corrida, con otra relación nueva, encuentra la carpeta hecha."""
        self._escribir()
        otro = self.raiz / "corpus" / "tornillos" / "002-una-tuerca.caso"
        otro.write_text(CASO.replace("001-un-tornillo", "002-una-tuerca")
                        .replace("tornillo: nombre", "tuerca: nombre"), encoding="utf-8")
        rc, salida = self._escribir()
        self.assertEqual(rc, 0, salida)
        self.assertTrue((self.raiz / CARPETA_POR_REVISAR / "tuerca.relacion").is_file(), salida)

    def test_el_borrador_tiene_la_misma_forma_que_relaciones(self) -> None:
        """Lo va a editar una persona y lo va a mover a una carpeta donde todo está escrito así."""
        self._escribir()
        borrador = self.raiz / CARPETA_POR_REVISAR / "tornillo.relacion"
        texto = borrador.read_text(encoding="utf-8")
        self.assertIn("relacion tornillo:\n", texto)
        self.assertIn("alto: entero", texto)
        self.assertTrue(texto.endswith('    alcance ""\n'))

    def test_no_toca_una_relacion_ya_declarada(self) -> None:
        declarada = self.raiz / "relaciones" / "tornillo.json"
        declarada.parent.mkdir(exist_ok=True)
        declarada.write_text(json.dumps(
            ["relacion", "tornillo",
             ["campos", ["campo", "nombre", "texto", "sin_unidad"],
              ["campo", "alto", "entero", "mm"], ["campo", "visible", "booleano", "sin_unidad"]],
             ["alcance", "declarada a mano"]]), encoding="utf-8")
        rc, salida = self._escribir()
        self.assertEqual(rc, 0)
        self.assertIn("tornillo — ya declarada", salida)
        self.assertIn("No se escribió ningún borrador", salida)
        self.assertFalse((self.raiz / CARPETA_POR_REVISAR).exists())

    def test_una_evidencia_ilegible_sale_1_y_no_escribe_nada(self) -> None:
        roto = self.raiz / "corpus" / "tornillos" / "002-roto.caso"
        roto.write_text("caso 002-roto:\n    esto no es un caso\n", encoding="utf-8")
        rc, salida = self._escribir()
        self.assertEqual(rc, 1)
        self.assertIn("no se pudo inventariar la evidencia", salida)
        self.assertFalse((self.raiz / CARPETA_POR_REVISAR).exists())

    def test_el_mensaje_cuenta_las_unidades_que_faltan_en_cada_borrador(self) -> None:
        _rc, salida = self._escribir()
        self.assertIn("tornillo.relacion — falta 1 unidad(es) y el alcance", salida)

    def test_sin_la_bandera_el_verbo_sigue_siendo_de_lectura(self) -> None:
        salida = io.StringIO()
        with redirect_stdout(salida):
            rc = cli.main(["relaciones", "--proyecto", str(self.raiz)])
        self.assertEqual(rc, 0)
        self.assertIn("RELACIONES", salida.getvalue())
        self.assertFalse((self.raiz / CARPETA_POR_REVISAR).exists())


if __name__ == "__main__":
    unittest.main()
