"""Contratos aislados del álgebra, sin importarla durante el descubrimiento.

Importar el objetivo dentro de cada test hace que una rotura de inicialización sea un fallo del
código ejercitado y no un supuesto error del arnés de mutación.
"""

from __future__ import annotations

import importlib
import unittest
from dataclasses import FrozenInstanceError


def _algebra():
    return importlib.import_module("nucleo.algebra")


class ContratoAlgebraTests(unittest.TestCase):
    def test_00_los_limites_predeterminados_son_parte_del_contrato(self) -> None:
        algebra = _algebra()
        self.assertEqual(
            algebra.LIMITES_PREDETERMINADOS,
            algebra.LimitesAlgebra(
                filas_por_relacion=100_000,
                producto_cartesiano=1_000_000,
                profundidad_expresion=64,
            ),
        )
        with self.assertRaises(FrozenInstanceError):
            algebra.LIMITES_PREDETERMINADOS.filas_por_relacion = 1

    def test_cada_limite_exige_un_entero_positivo_y_acepta_uno(self) -> None:
        algebra = _algebra()
        for campo in (
            "filas_por_relacion",
            "producto_cartesiano",
            "profundidad_expresion",
        ):
            for invalido in (0, -1, True, 1.5):
                with self.subTest(campo=campo, invalido=invalido):
                    with self.assertRaisesRegex(algebra.ErrorDeAlgebra, campo):
                        algebra.LimitesAlgebra(**{campo: invalido})
            with self.subTest(campo=campo, valor=1):
                self.assertEqual(getattr(algebra.LimitesAlgebra(**{campo: 1}), campo), 1)

    def test_el_decorador_escalar_valida_nombre_unidad_firma_y_duplicados(self) -> None:
        algebra = _algebra()
        for nombre in (1, "Mayuscula", "con.punto", ""):
            with self.subTest(nombre=nombre):
                with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "nombre"):
                    algebra.escalar(nombre)
        for unidad in (1, "cm\ninyectado", "cm\rinjectado"):
            with self.subTest(unidad=unidad):
                with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "unidad"):
                    algebra.escalar("d_unidad_invalida", unidad)

        @algebra.escalar("d_contrato_aislado", "cm")
        def escalar_de_prueba(requerido, opcional=1, *extras, etiqueta="prueba"):
            self.assertEqual(etiqueta, "prueba")
            return requerido + opcional + sum(extras)

        self.addCleanup(algebra.ESCALARES.pop, "d_contrato_aislado", None)
        self.assertIs(algebra.ESCALARES["d_contrato_aislado"], escalar_de_prueba)
        self.assertEqual(escalar_de_prueba(1, 2, 3), 6)
        self.assertEqual(
            (
                escalar_de_prueba.nombre_escalar,
                escalar_de_prueba.unidad,
                escalar_de_prueba.aridad_min,
                escalar_de_prueba.aridad_max,
                escalar_de_prueba.procedencia_escalar,
            ),
            ("d_contrato_aislado", "cm", 1, None, "oracle"),
        )
        with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "ya está registrada"):
            algebra.escalar("d_contrato_aislado")(lambda: None)

        with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "sólo-keyword obligatorio"):
            @algebra.escalar("d_keyword_invalida")
            def _keyword_invalida(*, requerido):
                return requerido

    def test_los_mensajes_de_aridad_distinguen_exacta_rango_y_variadica(self) -> None:
        algebra = _algebra()

        @algebra.escalar("d_exacta_aislada")
        def exacta(a, b):
            return a + b

        @algebra.escalar("d_rango_aislado")
        def rango(a, b=0):
            return a + b

        @algebra.escalar("d_variadica_aislada")
        def variadica(a, *resto):
            return a + sum(resto)

        for nombre in ("d_exacta_aislada", "d_rango_aislado", "d_variadica_aislada"):
            self.addCleanup(algebra.ESCALARES.pop, nombre, None)

        casos = (
            (["d_exacta_aislada", 1], "acepta 2 argumento"),
            (["d_rango_aislado"], "acepta entre 1 y 2 argumento"),
            (["d_variadica_aislada"], "acepta 1 o más argumento"),
        )
        for expresion, mensaje in casos:
            with self.subTest(expresion=expresion):
                with self.assertRaisesRegex(algebra.ErrorDeAlgebra, mensaje):
                    algebra.validar_expr(expresion)

    def test_ausencia_y_objetos_no_escalares_conservan_su_diagnostico(self) -> None:
        algebra = _algebra()
        with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "sobre un valor ausente"):
            algebra.comparar(">", None, 0)
        with self.assertRaisesRegex(
            algebra.ErrorDeAlgebra, "sólo compara escalares, no object y numero"
        ):
            algebra.comparar("==", object(), 1)

        filas = [{"p": {"x": None}}]
        with self.assertRaisesRegex(algebra.ErrorDeAlgebra, r"no \['ausente'\]"):
            algebra.resumir(["resumen", "min", ["campo", "p", "x"]], filas)

    def test_comparar_un_campo_ausente_identifica_la_expresion(self) -> None:
        algebra = _algebra()
        for expresion in (
            [">", ["campo", "p", "ausente"], 0],
            [">", 0, ["campo", "p", "ausente"]],
        ):
            with self.subTest(expresion=expresion):
                with self.assertRaises(algebra.ErrorDeAlgebra) as error:
                    algebra.evaluar_expr(expresion, {"p": {}})
                self.assertIn(str(expresion), str(error.exception))

    def test_suma_y_promedio_aceptan_una_mezcla_de_numeros_e_indicadores(self) -> None:
        algebra = _algebra()
        filas = [{"p": {"x": True}}, {"p": {"x": 2}}]
        self.assertEqual(algebra.resumir(
            ["resumen", "suma", ["campo", "p", "x"]], filas), 3)
        self.assertEqual(algebra.resumir(
            ["resumen", "promedio", ["campo", "p", "x"]], filas), 1.5)

    def test_el_limite_de_filas_es_inclusivo(self) -> None:
        algebra = _algebra()
        tuberia = ["desde", ["de", "pieza", "p"]]
        limite = algebra.LimitesAlgebra(filas_por_relacion=2)
        self.assertEqual(len(algebra.desde(tuberia, {"pieza": [{}, {}]}, limite)), 2)
        with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "supera el límite de 2"):
            algebra.desde(tuberia, {"pieza": [{}, {}, {}]}, limite)

    def test_aplicar_unir_rechaza_el_operador_de_fuente_recibido(self) -> None:
        algebra = _algebra()
        with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "recibió «donde»"):
            algebra.aplicar(
                ["unir", ["donde", True], ["de", "pieza", "p"]],
                [],
                {"pieza": []},
                algebra.LIMITES_PREDETERMINADOS,
            )

    def test_un_resumen_desconocido_nombra_el_agregado_recibido(self) -> None:
        algebra = _algebra()
        with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "agregado desconocido: «moda»"):
            algebra.validar_resumen(["resumen", "moda", 1])
