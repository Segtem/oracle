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

    def test_la_igualdad_EXACTA_sobre_flotantes_esta_prohibida(self) -> None:
        """La última pregunta abierta de la especificación, resuelta negándose: 0.1+0.2 no es 0.3, y
        una medida que compare así diría verde sin que nadie se enterara."""
        for expr in ([" ==".strip(), 0.3, ["mas", 0.1, 0.2]], ["!=", 1.0, 1]):
            with self.subTest(expr=expr):
                with self.assertRaises(ErrorDeAlgebra) as e:
                    evaluar_expr(expr, {})
                self.assertIn("falsedad silenciosa", str(e.exception))

    def test_pero_los_enteros_y_booleanos_se_comparan_exacto(self) -> None:
        self.assertTrue(evaluar_expr(["==", 3, 3], {}))
        self.assertTrue(evaluar_expr(["==", True, True], {}))
        self.assertFalse(evaluar_expr(["!=", 0, 0], {}))

    def test_y_el_orden_sobre_flotantes_sigue_permitido(self) -> None:
        # una tolerancia es justamente una comparación de orden: eso está bien
        self.assertTrue(evaluar_expr(["<=", 0.5, 1.0], {}))
        self.assertTrue(evaluar_expr([">", 2.5, 1.0], {}))

    def test_cerca_reemplaza_la_igualdad_con_una_tolerancia_a_la_vista(self) -> None:
        self.assertTrue(evaluar_expr(["<=", ["cerca", ["mas", 0.1, 0.2], 0.3], 1e-9], {}))
        self.assertFalse(evaluar_expr(["<=", ["cerca", 1.0, 2.0], 0.1], {}))

    def test_un_alias_inexistente_no_pasa_en_silencio(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            evaluar_expr(["campo", "q", "x"], {"p": {"x": 1}})

    def test_una_cabeza_desconocida_es_error(self) -> None:
        # ojo: `penetracion` YA es una escalar declarada (dominio geometría). Hace falta un nombre
        # que de verdad no exista, o el test deja de comprobar lo que dice.
        with self.assertRaises(ErrorDeAlgebra) as e:
            evaluar_expr(["esta_escalar_no_existe", 1, 2], {})
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
        # `unir` salió al llegar el catálogo de geometría; `agrupar`, al llegar la AUSENCIA
        for op in ("con",):
            with self.assertRaises(OperadorNoImplementado) as e:
                desde(["desde", ["de", "pieza", "p"], [op, "x", 1]], EV)
            self.assertIn("se implementa cuando aparezca", str(e.exception).lower())

    def test_unir_hace_el_producto_y_conviven_los_alias(self) -> None:
        filas = desde(["desde", ["unir", ["de", "pieza", "a"], ["de", "pieza", "b"]]], EV)
        self.assertEqual(len(filas), 4)
        self.assertEqual(sorted(filas[0]), ["a", "b"])

    def test_unir_con_alias_repetido_no_pasa_en_silencio(self) -> None:
        with self.assertRaises(ErrorDeAlgebra) as e:
            desde(["desde", ["unir", ["de", "pieza", "a"], ["de", "pieza", "a"]]], EV)
        self.assertIn("alias repetido", str(e.exception))

    def test_unir_en_modo_izquierda_todavia_no_tiene_usuario(self) -> None:
        with self.assertRaises(OperadorNoImplementado) as e:
            desde(["desde", ["unir", ["de", "pieza", "a"], ["de", "pieza", "b"], "izquierda"]], EV)
        self.assertIn("ausencia", str(e.exception))

    def test_unir_solo_acepta_fuentes(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            desde(["desde", ["unir", ["donde", True], ["de", "pieza", "b"]]], EV)

    def test_agrupar_devuelve_UNA_fila_por_grupo_con_columnas_derivadas(self) -> None:
        ev = {"cosa": [{"g": "a", "n": 1}, {"g": "a", "n": 2}, {"g": "b", "n": 5}]}
        filas = desde(["desde", ["de", "cosa", "c"],
                       ["agrupar", [["grupo", ["campo", "c", "g"]]],
                                   [["cuantos", "contar", 1], ["total", "suma", ["campo", "c", "n"]]]]],
                      ev)
        # un grupo NO es un hecho: no lleva alias, lleva columnas derivadas
        self.assertEqual(
            sorted((f["_"]["grupo"], f["_"]["cuantos"], f["_"]["total"]) for f in filas),
            [("a", 2, 3), ("b", 1, 5)])
        self.assertNotIn("c", filas[0])

    def test_agrupar_expresa_la_AUSENCIA_sin_nulos(self) -> None:
        """Era una de las preguntas abiertas de la especificación. El truco no es un LEFT JOIN con
        nulos: es agrupar sobre el producto SIN filtrar y sumar un predicado — los booleanos suman
        0 y 1, así que un grupo donde nada casó da cero y sigue existiendo."""
        ev = {"modulo": [{"nombre": "usado"}, {"nombre": "solo_por_test"}, {"nombre": "huerfano"}],
              "importa": [{"a": "x", "b": "usado", "es_test": False},
                          {"a": "t", "b": "solo_por_test", "es_test": True}]}
        filas = desde(["desde",
                       ["unir", ["de", "modulo", "m"], ["de", "importa", "i"]],
                       ["agrupar", [["modulo", ["campo", "m", "nombre"]]],
                                   [["reales", "suma",
                                     ["y", ["==", ["campo", "i", "b"], ["campo", "m", "nombre"]],
                                           ["==", ["campo", "i", "es_test"], False]]]]],
                       ["donde", ["==", ["col", "reales"], 0]]], ev)
        self.assertEqual(sorted(f["_"]["modulo"] for f in filas), ["huerfano", "solo_por_test"])

    def test_agrupar_con_un_agregado_desconocido_es_error(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            desde(["desde", ["de", "pieza", "p"],
                   ["agrupar", [["k", ["campo", "p", "id"]]], [["x", "moda", 1]]]], EV)

    def test_contar_no_evalua_la_expresion(self) -> None:
        filas = desde(["desde", ["de", "pieza", "p"]], EV)
        self.assertEqual(resumir(["resumen", "contar", ["campo", "p", "no_existe"]], filas), 2)

    def test_los_agregados_sobre_cero_filas_dan_cero(self) -> None:
        for agg in ("max", "min", "suma", "promedio"):
            self.assertEqual(resumir(["resumen", agg, ["campo", "p", "x"]], []), 0)

    def test_max_sobre_filas_reales(self) -> None:
        filas = desde(["desde", ["de", "pieza", "p"]], EV)
        self.assertEqual(resumir(["resumen", "max", ["campo", "p", "x"]], filas), 7)

    def test_TODOS_los_comparadores_hacen_lo_que_dicen(self) -> None:
        """La mutación de código delató que sólo `<=` y `>` se ejercitaban: los otros cuatro estaban
        escritos y sin verificar. Cambiar `!=` por `==` en el álgebra no rompía ningún test."""
        casos = [("==", 2, 2, True), ("==", 2, 3, False),
                 ("!=", 2, 3, True), ("!=", 2, 2, False),
                 ("<", 1, 2, True), ("<", 2, 2, False),
                 ("<=", 2, 2, True), ("<=", 3, 2, False),
                 (">", 3, 2, True), (">", 2, 2, False),
                 (">=", 2, 2, True), (">=", 1, 2, False)]
        for op, a, b, esperado in casos:
            with self.subTest(op=op, a=a, b=b):
                self.assertEqual(evaluar_expr([op, a, b], {}), esperado)

    def test_y_o_no_hacen_lo_que_dicen(self) -> None:
        self.assertTrue(evaluar_expr(["y", True, True], {}))
        self.assertFalse(evaluar_expr(["y", True, False], {}))
        self.assertTrue(evaluar_expr(["o", False, True], {}))
        self.assertFalse(evaluar_expr(["o", False, False], {}))
        self.assertTrue(evaluar_expr(["no", False], {}))
        self.assertFalse(evaluar_expr(["no", True], {}))

    def test_el_decorador_escalar_devuelve_la_funcion_y_le_pone_la_unidad(self) -> None:
        @algebra.escalar("d_prueba_unidad", "cm")
        def _f(x):
            return x * 2

        try:
            self.assertEqual(_f(3), 6)                    # devuelve la función, no None
            self.assertEqual(_f.unidad, "cm")
            self.assertIs(algebra.ESCALARES["d_prueba_unidad"], _f)
        finally:
            del algebra.ESCALARES["d_prueba_unidad"]

    def test_promedio_sobre_filas_reales(self) -> None:
        filas = desde(["desde", ["de", "pieza", "p"]], EV)
        self.assertEqual(resumir(["resumen", "promedio", ["campo", "p", "x"]], filas), 3.5)
        self.assertEqual(resumir(["resumen", "suma", ["campo", "p", "x"]], filas), 7)
        self.assertEqual(resumir(["resumen", "min", ["campo", "p", "x"]], filas), 0)

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

    def test_la_linea_del_veredicto_dice_marca_valor_umbral_y_testigos(self) -> None:
        """El informe es contrato: los testigos son lo que una persona lee para actuar. La mutación
        de código delató que el formateo no lo verificaba nadie."""
        v = Medida.de_datos(_medida()).evaluar(EV)
        linea = v.linea()
        self.assertTrue(linea.startswith("✗"))
        self.assertIn("d.prueba", linea)
        self.assertIn("<= 0", linea)
        self.assertIn("p=b", linea)          # el testigo, identificado

    def test_un_veredicto_verde_no_lista_testigos(self) -> None:
        v = Medida.de_datos(_medida(pred=[">", ["campo", "p", "x"], 1000])).evaluar(EV)
        self.assertTrue(v.linea().startswith("✓"))
        self.assertNotIn("→", v.linea())

    def test_con_muchos_testigos_muestra_tres_y_cuenta_el_resto(self) -> None:
        muchos = {"pieza": [{"id": f"n{i}", "x": 9} for i in range(7)]}
        v = Medida.de_datos(_medida()).evaluar(muchos)
        linea = v.linea()
        self.assertEqual(linea.count("p=n"), 3)
        self.assertIn("+4", linea)

    def test_con_exactamente_tres_testigos_no_dice_mas(self) -> None:
        tres = {"pieza": [{"id": f"n{i}", "x": 9} for i in range(3)]}
        self.assertNotIn("+", Medida.de_datos(_medida()).evaluar(tres).linea().split("→")[1])

    def test_el_testigo_se_identifica_por_id_nombre_archivo_o_ruta(self) -> None:
        from nucleo.medida import _resumir_fila
        self.assertEqual(_resumir_fila({"a": {"id": "x"}}), "a=x")
        self.assertEqual(_resumir_fila({"a": {"nombre": "y"}}), "a=y")
        self.assertEqual(_resumir_fila({"a": {"ruta": "z.py"}}), "a=z.py")
        self.assertIn("otro", _resumir_fila({"a": {"otro": 1}}))

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
                         ["alcance", "dominio", "es_meta_por_el_nombre", "es_meta_por_lo_que_mide",
                          "id", "porque", "relacion", "umbral_op", "umbral_valor"])

    def test_los_dos_ejes_se_derivan_y_no_se_convienen(self) -> None:
        """El dominio sale del nombre; el NIVEL sale de sobre qué se mide. Que sean dos campos
        distintos es lo que permite comprobar que la convención se cumple."""
        hechos = {h["id"]: h for h in como_hechos(self.catalogo.values())}
        meta = hechos["meta.alcance_dice_que_no_ve"]
        self.assertTrue(meta["es_meta_por_el_nombre"])
        self.assertTrue(meta["es_meta_por_lo_que_mide"])
        self.assertEqual(meta["relacion"], "medida")

        delMundo = hechos["proceso.verificador_sin_falsos_rojos"]
        self.assertFalse(delMundo["es_meta_por_el_nombre"])
        self.assertFalse(delMundo["es_meta_por_lo_que_mide"])
        self.assertEqual(delMundo["dominio"], "proceso")

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
