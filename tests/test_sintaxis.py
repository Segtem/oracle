"""Tests de la superficie infija de autoría."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools import sintaxis

RAIZ = Path(__file__).resolve().parents[1]


class SintaxisInfijaTests(unittest.TestCase):
    def test_todas_las_medidas_del_catalogo_vuelven_exactas(self) -> None:
        informe = sintaxis.verificar_catalogo(RAIZ)
        # Contado, no escrito: un 29 a mano vence con cada medida nueva y el test empieza a
        # medir cuántas hay en vez de que todas vuelvan exactas, que es lo que dice medir.
        del_catalogo = len(list((RAIZ / "catalogos").glob("*/*.json"))) + len(
            list((RAIZ / "perfiles").glob("*/catalogos/*/*.json")))
        self.assertEqual(informe["medidas"], del_catalogo)
        self.assertGreater(del_catalogo, 0)
        self.assertTrue(informe["json_igual"])
        self.assertTrue(informe["texto_igual"])
        self.assertLess(informe["puntuacion_superficie"], informe["puntuacion_json"])

    def test_una_macro_se_relee_como_macro_y_no_como_expansion(self) -> None:
        ruta = RAIZ / "catalogos/meta/meta.donde_compone.json"
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        superficie = sintaxis.imprimir(datos)

        self.assertTrue(superficie.startswith("ninguno meta.donde_compone:"))
        self.assertEqual(sintaxis.leer(superficie), datos)

    def test_una_medida_canonica_preserva_requiere_y_agrupar(self) -> None:
        ruta = RAIZ / "perfiles/python/catalogos/proceso/proceso.modulo_con_consumidor.json"
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        releida = sintaxis.leer(sintaxis.imprimir(datos))

        self.assertEqual(releida, datos)
        self.assertEqual(releida[5], ["requiere", "importa"])
        self.assertEqual(releida[2][2][0], "agrupar")

    def test_imprimir_leer_es_idempotente_sobre_la_superficie_generada(self) -> None:
        datos = ["ninguno", "d.prueba", "pieza", "p",
                 ["y", ["==", ["campo", "p", "mal"], True],
                  [">", ["campo", "p", "n"], 2]],
                 "una razón", "NO ve otros campos"]
        texto = sintaxis.imprimir(datos)

        self.assertEqual(sintaxis.imprimir(sintaxis.leer(texto)), texto)

    def test_un_error_de_expresion_trae_posicion_y_esperado(self) -> None:
        texto = "\n".join([
            "ninguno d.rota:",
            "    de pieza p",
            "    donde p.mal ==",
            "    umbral <= 0 porque \"razón\"",
            "    alcance \"NO ve\"",
        ])

        with self.assertRaises(sintaxis.ErrorSintaxis) as e:
            sintaxis.leer(texto)
        self.assertEqual(e.exception.linea, 3)
        self.assertIn("se esperaba expresión", str(e.exception))

    def test_la_metamorfica_de_sintaxis_juzga_todo_el_catalogo(self) -> None:
        from nucleo.medida import Medida
        from nucleo.proyecto import Proyecto
        from tools import metamorficas

        filas = metamorficas._sintaxis_ida_y_vuelta(Proyecto(RAIZ))
        del_catalogo = len(list((RAIZ / "catalogos").glob("*/*.json"))) + len(
            list((RAIZ / "perfiles").glob("*/catalogos/*/*.json")))
        self.assertEqual(len(filas), del_catalogo)
        self.assertTrue(all(f["mismo_veredicto"] and f["mismo_valor"] for f in filas))
        # La jueza se busca en el CATÁLOGO, no en el código de la herramienta: estuvo un rato
        # declarada adentro de `metamorficas.py` —consecuencia de una restricción de la tarea que
        # la escribió— y una medida que vive en Python no entra a la mutación ni al inventario de
        # puntos ciegos, que es justo lo que este proyecto le exige a todas las demás.
        import json
        jueza = json.loads(
            (RAIZ / "catalogos/meta/meta.sintaxis_ida_y_vuelta.json").read_text(encoding="utf-8"))
        from nucleo.proyecto import macros_del_proyecto
        m = Medida.de_datos(jueza, macros=macros_del_proyecto(Proyecto(RAIZ)))
        self.assertTrue(m.evaluar({"equivalencia": filas}).ok)


if __name__ == "__main__":
    unittest.main()
