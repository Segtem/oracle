"""Tests de revisión de la anti-junta (0.26.0), escritos por Claude ANTES de leer la entrega.

Fijan el plan aprobado (`PLAN-0.26.0-ANTIJUNTA.md`) desde afuera, con la API pública: `desde`, la
superficie, `Medida` y las versiones. Si la entrega los pasa sin cambios, la semántica es la que se
pidió; si no, o la entrega o el plan están mal, y hay que decir cuál.
"""

from __future__ import annotations

import unittest

from nucleo.algebra import ErrorDeAlgebra, LimitesAlgebra, desde
from nucleo.medida import Medida
from nucleo import sintaxis
from nucleo.version import VERSION_ALGEBRA, VERSION_SINTAXIS

TAREAS = [{"id": "a", "estado": "CERRADA"}, {"id": "b", "estado": "CERRADA"},
          {"id": "c", "estado": "ABIERTA"}]
CIERRES = [{"tarea": "a", "done": True}, {"tarea": "b", "done": False}]


def _tuberia(*pasos):
    return ["desde", ["de", "tarea", "t"], *pasos]


def _sin(condicion, relacion="cierre", alias="c"):
    return ["sin", ["de", relacion, alias], condicion]


CORRESPONDE = ["y", ["==", ["campo", "c", "tarea"], ["campo", "t", "id"]],
               ["==", ["campo", "c", "done"], True]]


class SemanticaTests(unittest.TestCase):
    def test_deja_las_filas_que_ninguna_de_la_otra_relacion_corresponde(self) -> None:
        filas = desde(_tuberia(_sin(CORRESPONDE)), {"tarea": TAREAS, "cierre": CIERRES})
        self.assertEqual([f["t"]["id"] for f in filas], ["b", "c"])

    def test_el_alias_nuevo_no_queda_en_la_salida(self) -> None:
        filas = desde(_tuberia(_sin(CORRESPONDE)), {"tarea": TAREAS, "cierre": CIERRES})
        self.assertEqual({tuple(sorted(f)) for f in filas}, {("t",)})

    def test_se_combina_con_donde(self) -> None:
        tuberia = _tuberia(["donde", ["==", ["campo", "t", "estado"], "CERRADA"]],
                           _sin(CORRESPONDE))
        filas = desde(tuberia, {"tarea": TAREAS, "cierre": CIERRES})
        self.assertEqual([f["t"]["id"] for f in filas], ["b"])

    def test_una_relacion_vacia_deja_pasar_todas(self) -> None:
        filas = desde(_tuberia(_sin(CORRESPONDE)), {"tarea": TAREAS, "cierre": []})
        self.assertEqual(len(filas), 3)

    def test_una_relacion_ausente_es_un_error_y_no_un_verde_por_omision(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            desde(_tuberia(_sin(CORRESPONDE)), {"tarea": TAREAS})

    def test_sin_filas_a_la_izquierda_no_queda_ninguna(self) -> None:
        self.assertEqual(desde(_tuberia(_sin(CORRESPONDE)), {"tarea": [], "cierre": CIERRES}), [])

    def test_no_cortocircuita_si_una_fila_posterior_levanta_levanta(self) -> None:
        """La primera fila de la derecha corresponde a «a»; la segunda no tiene `done`. Si se
        cortara en el primer acierto, el orden de la bolsa cambiaría el veredicto."""
        cierres = [{"tarea": "a", "done": True}, {"tarea": "a"}]
        with self.assertRaises(ErrorDeAlgebra):
            desde(_tuberia(_sin(CORRESPONDE)), {"tarea": TAREAS[:1], "cierre": cierres})

    def test_el_orden_de_la_derecha_no_cambia_el_resultado(self) -> None:
        normal = desde(_tuberia(_sin(CORRESPONDE)), {"tarea": TAREAS, "cierre": CIERRES})
        invertido = desde(_tuberia(_sin(CORRESPONDE)),
                          {"tarea": TAREAS, "cierre": list(reversed(CIERRES))})
        self.assertEqual(normal, invertido)

    def test_un_alias_que_ya_esta_en_la_fila_es_un_error(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            desde(_tuberia(_sin(CORRESPONDE, alias="t")), {"tarea": TAREAS, "cierre": CIERRES})

    def test_respeta_el_presupuesto_del_producto(self) -> None:
        limites = LimitesAlgebra(producto_cartesiano=5)
        with self.assertRaises(ErrorDeAlgebra):
            desde(_tuberia(_sin(CORRESPONDE)), {"tarea": TAREAS, "cierre": CIERRES}, limites)

    def test_despues_de_agrupar_la_condicion_ve_las_columnas(self) -> None:
        tuberia = ["desde", ["de", "tarea", "t"],
                   ["agrupar", [["estado", ["campo", "t", "estado"]]],
                    [["n", "contar", 1]]],
                   ["sin", ["de", "prohibido", "p"],
                    ["==", ["campo", "p", "estado"], ["col", "estado"]]]]
        filas = desde(tuberia, {"tarea": TAREAS, "prohibido": [{"estado": "ABIERTA"}]})
        self.assertEqual(len(filas), 1)

    def test_una_forma_mal_escrita_se_rechaza(self) -> None:
        for paso in (["sin", ["de", "cierre", "c"]],
                     ["sin", ["unir", ["de", "a", "x"], ["de", "b", "y"]], True],
                     ["sin", "cierre", CORRESPONDE]):
            with self.subTest(paso=paso), self.assertRaises(ErrorDeAlgebra):
                # `a` y `b` presentes: el `unir` se rechaza por su forma, no por una relación ausente.
                desde(_tuberia(paso), {"tarea": TAREAS, "cierre": CIERRES, "a": [], "b": []})

    def test_el_alias_repetido_se_rechaza_aunque_no_llegue_ninguna_fila(self) -> None:
        """Es un error de la medida, no de los datos: no puede depender de cuántas filas llegan."""
        with self.assertRaises(ErrorDeAlgebra):
            desde(_tuberia(["donde", False], _sin(True, alias="t")),
                  {"tarea": TAREAS, "cierre": CIERRES})

    def test_despues_de_agrupar_no_hay_alias_con_que_chocar(self) -> None:
        """Una columna se lee con `col` y un alias con `campo`: el mismo nombre no es ambiguo."""
        tuberia = ["desde", ["de", "tarea", "t"],
                   ["agrupar", [["c", ["campo", "t", "estado"]]], []],
                   _sin(["==", ["campo", "c", "tarea"], ["col", "c"]])]
        self.assertEqual(len(desde(tuberia, {"tarea": TAREAS, "cierre": CIERRES})), 2)


class SuperficieTests(unittest.TestCase):
    TEXTO = '''medida ejemplo.cerradas_sin_cierre:
    de tarea t
    donde t.estado == "CERRADA"
    sin cierre c donde c.tarea == t.id y c.done == true
    resumen contar(1)
    umbral <= 0 segun contrato porque "una cerrada necesita su cierre"
    ambito universal
    alcance "NO ve si el cierre fue correcto"
'''

    def test_la_superficie_lee_sin_en_su_forma_canonica(self) -> None:
        datos = sintaxis.leer(self.TEXTO)
        tuberia = datos[2]
        self.assertEqual(tuberia[-1],
                         ["sin", ["de", "cierre", "c"],
                          ["y", ["==", ["campo", "c", "tarea"], ["campo", "t", "id"]],
                           ["==", ["campo", "c", "done"], True]]])

    def test_ida_y_vuelta(self) -> None:
        datos = sintaxis.leer(self.TEXTO)
        self.assertEqual(sintaxis.leer(sintaxis.imprimir(datos)), datos)

    def test_la_medida_juzga_con_sin(self) -> None:
        medida = Medida.de_datos(sintaxis.leer(self.TEXTO))
        veredicto = medida.evaluar({"tarea": TAREAS, "cierre": CIERRES})
        self.assertEqual(veredicto.valor, 1)
        self.assertFalse(veredicto.ok)


class VersionTests(unittest.TestCase):
    def test_el_algebra_es_08_y_la_sintaxis_06(self) -> None:
        self.assertEqual(VERSION_ALGEBRA, "0.8")
        self.assertEqual(VERSION_SINTAXIS, "0.6")

    def test_el_vocabulario_explica_sin(self) -> None:
        from nucleo.vocabulario import OPERADORES
        self.assertIn("sin", OPERADORES)


if __name__ == "__main__":
    unittest.main()
