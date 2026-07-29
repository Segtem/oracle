"""Tests del núcleo. `unittest` puro: el repo no tiene dependencias, ni de desarrollo.

(El oráculo viejo de Jam tenía 13 archivos de test escritos para pytest y sin pytest instalado: 0
tests corriendo durante 8 días. No se repite.)
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos.escalares  # noqa: F401  registra `contiene`
from nucleo import algebra
from nucleo.algebra import (ErrorDeAlgebra, OperadorNoImplementado, desde, evaluar_expr, resumir)
from nucleo.medida import (Informe, Medida, MedidaMalDeclarada, cargar_catalogo, como_hechos,
                           evaluar, inventario, puntos_ciegos)

EV = {"pieza": [{"id": "a", "x": 0}, {"id": "b", "x": 7}]}


def _medida(pred=None, porque="una razón", alcance="NO ve nada más", umbral=("<=", 0)):
    return ["medida", "d.prueba",
            ["desde", ["de", "pieza", "p"], ["donde", pred or [">", ["campo", "p", "x"], 3]]],
            ["resumen", "contar", 1],
            ["umbral", umbral[0], umbral[1], porque],
            ["alcance", alcance]]


class AlgebraTests(unittest.TestCase):
    def test_un_literal_se_evalua_a_si_mismo(self) -> None:
        for lit in (3, "hola", True, None, 2.5):
            self.assertEqual(evaluar_expr(lit, {}), lit)

    def test_los_accesores_son_explicitos(self) -> None:
        fila = {"p": {"id": "a", "x": 9}, "_": {"doble": 18}}
        self.assertEqual(evaluar_expr(["campo", "p", "x"], fila), 9)
        self.assertEqual(evaluar_expr(["hecho", "p"], fila), {"id": "a", "x": 9})
        self.assertEqual(evaluar_expr(["col", "doble"], fila), 18)

    def test_un_string_nunca_se_confunde_con_un_alias(self) -> None:
        # si un string suelto significara «alias», un dato de texto cambiaría de sentido
        self.assertEqual(evaluar_expr("p", {"p": {"x": 1}}), "p")

    def test_comparar_contra_un_campo_ausente_es_error_y_no_False(self) -> None:
        with self.assertRaises(ErrorDeAlgebra) as e:
            evaluar_expr([">", ["campo", "p", "no_existe"], 0], {"p": {"x": 1}})
        self.assertIn("ausente", str(e.exception))

    def test_un_alias_inexistente_no_pasa_en_silencio(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            evaluar_expr(["campo", "q", "x"], {"p": {"x": 1}})

    def test_una_cabeza_desconocida_es_error(self) -> None:
        with self.assertRaises(ErrorDeAlgebra) as e:
            evaluar_expr(["penetracion", 1, 2], {})
        self.assertIn("escalar declarada", str(e.exception))

    def test_la_escalar_declarada_se_llama(self) -> None:
        self.assertTrue(evaluar_expr(["contiene", "NO ve la malla", "NO "], {}))
        self.assertFalse(evaluar_expr(["contiene", "ve la malla", "NO "], {}))

    def test_declarar_dos_veces_la_misma_escalar_es_error(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            algebra.escalar("contiene")(lambda *a: None)

    def test_donde_filtra_y_lo_que_queda_son_los_testigos(self) -> None:
        filas = desde(["desde", ["de", "pieza", "p"], ["donde", [">", ["campo", "p", "x"], 3]]], EV)
        self.assertEqual([f["p"]["id"] for f in filas], ["b"])

    def test_una_relacion_ausente_da_cero_filas_y_no_explota(self) -> None:
        self.assertEqual(desde(["desde", ["de", "fantasma", "f"]], EV), [])

    def test_la_tuberia_tiene_que_empezar_con_una_fuente(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            desde(["desde", ["donde", True]], EV)

    def test_los_operadores_sin_usuario_dicen_su_disparador(self) -> None:
        for op in ("con", "unir", "agrupar"):
            with self.assertRaises(OperadorNoImplementado) as e:
                desde(["desde", ["de", "pieza", "p"], [op, "x", 1]], EV)
            self.assertIn("se implementa cuando aparezca", str(e.exception).lower())

    def test_contar_no_evalua_la_expresion(self) -> None:
        filas = desde(["desde", ["de", "pieza", "p"]], EV)
        self.assertEqual(resumir(["resumen", "contar", ["campo", "p", "no_existe"]], filas), 2)

    def test_los_agregados_sobre_cero_filas_dan_cero(self) -> None:
        for agg in ("max", "min", "suma", "promedio"):
            self.assertEqual(resumir(["resumen", agg, ["campo", "p", "x"]], []), 0)

    def test_max_sobre_filas_reales(self) -> None:
        filas = desde(["desde", ["de", "pieza", "p"]], EV)
        self.assertEqual(resumir(["resumen", "max", ["campo", "p", "x"]], filas), 7)

    def test_un_agregado_desconocido_es_error(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            resumir(["resumen", "moda", 1], [])


class MedidaTests(unittest.TestCase):
    def test_un_umbral_sin_defensa_no_se_carga(self) -> None:
        with self.assertRaises(MedidaMalDeclarada) as e:
            Medida.de_datos(_medida(porque="   "))
        self.assertIn("defensa", str(e.exception))

    def test_una_medida_sin_alcance_no_se_carga(self) -> None:
        with self.assertRaises(MedidaMalDeclarada) as e:
            Medida.de_datos(_medida(alcance="  "))
        self.assertIn("alcance", str(e.exception))

    def test_un_operador_de_umbral_inventado_no_se_carga(self) -> None:
        with self.assertRaises(MedidaMalDeclarada):
            Medida.de_datos(_medida(umbral=("≈", 0)))

    def test_falla_al_LEERSE_y_no_al_usarse(self) -> None:
        # la diferencia importa: una medida mal declarada no debe poder existir a medias
        with self.assertRaises(MedidaMalDeclarada):
            Medida.de_datos(["medida", "x", [], []])

    def test_los_testigos_son_las_filas_que_sobrevivieron(self) -> None:
        v = Medida.de_datos(_medida()).evaluar(EV)
        self.assertEqual(v.valor, 1)
        self.assertFalse(v.ok)
        self.assertEqual([t["p"]["id"] for t in v.testigos], ["b"])

    def test_el_veredicto_tiene_la_misma_forma_para_cualquier_dominio(self) -> None:
        v = Medida.de_datos(_medida()).evaluar(EV)
        self.assertEqual(sorted(v.a_dict()),
                         ["alcance", "id", "ok", "porque", "testigos", "umbral", "valor"])

    def test_ida_y_vuelta_a_datos(self) -> None:
        d = _medida()
        self.assertEqual(Medida.de_datos(d).a_datos(), d)

    def test_un_informe_verde_enumera_lo_que_no_miro_y_nunca_dice_todo_verde(self) -> None:
        m = Medida.de_datos(_medida(pred=[">", ["campo", "p", "x"], 1000]))
        texto = evaluar([m], EV).texto()
        self.assertIn("SIN MIRAR", texto)
        self.assertIn("NO ve nada más", texto)
        self.assertNotIn("TODO VERDE", texto)

    def test_un_informe_rojo_no_promete_alcance(self) -> None:
        texto = evaluar([Medida.de_datos(_medida())], EV).texto()
        self.assertIn("en rojo", texto)
        self.assertNotIn("SIN MIRAR", texto)

    def test_el_inventario_saca_los_umbrales_con_su_defensa(self) -> None:
        filas = inventario([Medida.de_datos(_medida())])
        self.assertEqual(filas[0]["umbral"], "<= 0")
        self.assertEqual(filas[0]["porque"], "una razón")

    def test_puntos_ciegos_lista_los_alcances(self) -> None:
        self.assertEqual(puntos_ciegos([Medida.de_datos(_medida())])[0]["alcance"],
                         "NO ve nada más")


class CatalogoRealTests(unittest.TestCase):
    """El catálogo del repo, cargado por el camino real."""

    def setUp(self) -> None:
        self.catalogo = cargar_catalogo(RAIZ / "catalogos")

    def test_todas_las_medidas_del_repo_cargan(self) -> None:
        self.assertGreaterEqual(len(self.catalogo), 8)

    def test_ninguna_medida_del_repo_tiene_umbral_sin_defensa(self) -> None:
        for f in inventario(self.catalogo.values()):
            self.assertTrue(f["porque"].strip(), f["id"])

    def test_como_hechos_sirve_el_catalogo_como_relacion_L2(self) -> None:
        hechos = como_hechos(self.catalogo.values())
        self.assertEqual(len(hechos), len(self.catalogo))
        self.assertEqual(sorted(hechos[0]),
                         ["alcance", "id", "porque", "relacion", "umbral_op", "umbral_valor"])

    def test_el_catalogo_cumple_su_propia_regla_meta(self) -> None:
        meta = self.catalogo["meta.alcance_dice_que_no_ve"]
        v = meta.evaluar({"medida": como_hechos(self.catalogo.values())})
        self.assertTrue(v.ok, f"alcances sin negación: {[t['m']['id'] for t in v.testigos]}")

    def test_un_id_repetido_en_el_catalogo_no_pasa(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for n in ("a.json", "b.json"):
                (Path(d) / n).write_text(json.dumps(_medida()), encoding="utf-8")
            with self.assertRaises(MedidaMalDeclarada):
                cargar_catalogo(Path(d))


if __name__ == "__main__":
    unittest.main()
