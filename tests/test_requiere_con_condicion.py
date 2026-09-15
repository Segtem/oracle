"""Pruebas para `requiere` con condición y múltiples líneas (0.21.0).

Verifica:
- Carga y forma canónica de `requiere` con condición.
- Rechazo de formas inválidas (alias inválido, relación repetida, alias ajeno, condición no booleana, entrada incompleta, sintaxis).
- Evaluación semántica: SIN EVIDENCIA con relación ausente, relación vacía, filas de otro tipo o sin filas que cumplan.
- Medición correcta cuando hay filas que cumplen la condición.
- Fallo con ErrorDeAlgebra cuando se evalúa un campo ausente en la condición.
- Compatibilidad hacia atrás: medida sin condición idéntica en forma canónica y veredicto.
- Generación de hechos con columna `con_condicion` en `requiere` y `dependencia_de_medida`.
- Superficie `.oracle`: lectura e impresión con ninguna, una o varias líneas `requiere`, round-trip y preservación de ubicaciones de `ambito` y `alcance`.
"""

import unittest
from pathlib import Path

from nucleo.algebra import ErrorDeAlgebra
from nucleo.medida import Medida, MedidaMalDeclarada, como_hechos
from nucleo.sintaxis import ErrorSintaxis, imprimir, leer

RAIZ = Path(__file__).resolve().parents[1]

COND_CODIGO = ["==", ["campo", "m", "tipo"], "codigo"]
COND_MEDIDA = ["==", ["campo", "m", "tipo"], "medida"]

FILA_MEDIDA = {
    "id": "d.x·f",
    "apunta_a": "d.x",
    "cambio": "f",
    "tipo": "medida",
    "detecciones_conductuales": 0,
    "rechazos_del_algebra": 0,
}

FILA_CODIGO = {
    "id": "a.py:1:1:c",
    "apunta_a": "a.py",
    "cambio": "c",
    "tipo": "codigo",
    "estado": "pasaron",
    "murio": False,
    "tests_fallaron": False,
    "error_arnes": False,
    "timeout": False,
    "codigo_salida": 0,
    "equivalente_declarado": False,
    "razon_equivalente": "",
}


def _crear_medida(requiere, *, donde=COND_CODIGO):
    tuberia = ["desde", ["de", "mutante", "m"]]
    if donde is not None:
        tuberia.append(["donde", donde])
    return [
        "medida", "d.prueba_cond",
        tuberia,
        ["resumen", "contar", 1],
        ["umbral", "<=", 0, "razón de prueba"],
        requiere,
        ["ambito", "universal"],
        ["alcance", "NO ve nada fuera de prueba"],
    ]


class RequiereConCondicionCargaTests(unittest.TestCase):
    def test_forma_canonica_se_preserva(self):
        datos = _crear_medida(["requiere", ["filas", "mutante", "m", COND_CODIGO]])
        medida = Medida.de_datos(datos)
        self.assertEqual(medida.a_datos()[5], datos[5])
        self.assertEqual(medida.requiere, (["filas", "mutante", "m", COND_CODIGO],))

    def test_forma_canonica_mixta_nombres_y_condiciones(self):
        datos = _crear_medida(["requiere", "pieza", ["filas", "mutante", "m", COND_CODIGO]])
        medida = Medida.de_datos(datos)
        self.assertEqual(medida.a_datos()[5], ["requiere", "pieza", ["filas", "mutante", "m", COND_CODIGO]])

    def test_rechazo_alias_invalido(self):
        for alias in ("M", "1m", "alias-con-guion", ""):
            with self.subTest(alias=alias), self.assertRaises((MedidaMalDeclarada, ErrorDeAlgebra)):
                Medida.de_datos(_crear_medida(["requiere", ["filas", "mutante", alias, COND_CODIGO]]))

    def test_rechazo_relacion_invalida(self):
        for rel in ("Mutante", "1rel", "rel-guion", ""):
            with self.subTest(rel=rel), self.assertRaises((MedidaMalDeclarada, ErrorDeAlgebra)):
                Medida.de_datos(_crear_medida(["requiere", ["filas", rel, "m", COND_CODIGO]]))

    def test_rechazo_relacion_repetida(self):
        casos = (
            ["requiere", "mutante", "mutante"],
            ["requiere", "mutante", ["filas", "mutante", "m", COND_CODIGO]],
            ["requiere", ["filas", "mutante", "m", COND_CODIGO], "mutante"],
            ["requiere", ["filas", "mutante", "m", COND_CODIGO], ["filas", "mutante", "m2", COND_MEDIDA]],
        )
        for req in casos:
            with self.subTest(req=req), self.assertRaises(MedidaMalDeclarada):
                Medida.de_datos(_crear_medida(req))

    def test_rechazo_condicion_no_booleana(self):
        casos_no_bool = (
            ["campo", "m", "tipo"],
            ["campo", "m", "codigo_salida"],
            123,
            "texto_literal",
            ["+", ["campo", "m", "codigo_salida"], 1],
        )
        for cond in casos_no_bool:
            with self.subTest(cond=cond), self.assertRaises((MedidaMalDeclarada, ErrorDeAlgebra)):
                Medida.de_datos(_crear_medida(["requiere", ["filas", "mutante", "m", cond]]))

    def test_rechazo_alias_ajeno(self):
        cond_ajena = ["==", ["campo", "otro_alias", "tipo"], "codigo"]
        with self.assertRaises(MedidaMalDeclarada):
            Medida.de_datos(_crear_medida(["requiere", ["filas", "mutante", "m", cond_ajena]]))

    def test_rechazo_referencia_a_col(self):
        cond_col = ["==", ["col", "total"], 0]
        with self.assertRaises(MedidaMalDeclarada):
            Medida.de_datos(_crear_medida(["requiere", ["filas", "mutante", "m", cond_col]]))

    def test_rechazo_entrada_incompleta_o_mal_formada(self):
        casos_mal_formados = (
            ["requiere", ["filas", "mutante", "m"]],
            ["requiere", ["filas", "mutante"]],
            ["requiere", ["filas"]],
            ["requiere", ["otra_cabeza", "mutante", "m", COND_CODIGO]],
            ["requiere", 123],
        )
        for req in casos_mal_formados:
            with self.subTest(req=req), self.assertRaises(MedidaMalDeclarada):
                Medida.de_datos(_crear_medida(req))


class RequiereConCondicionEvaluacionTests(unittest.TestCase):
    def setUp(self):
        datos = _crear_medida(["requiere", ["filas", "mutante", "m", COND_CODIGO]])
        self.medida = Medida.de_datos(datos)

    def test_sin_evidencia_cuando_relacion_ausente(self):
        v = self.medida.evaluar({})
        self.assertTrue(v.sin_evidencia)
        self.assertIn("mutante", v.sin_evidencia)
        self.assertFalse(v.ok)
        self.assertEqual(v.valor, 0)

    def test_sin_evidencia_cuando_relacion_vacia(self):
        v = self.medida.evaluar({"mutante": []})
        self.assertTrue(v.sin_evidencia)
        self.assertIn("mutante", v.sin_evidencia)
        self.assertFalse(v.ok)

    def test_sin_evidencia_cuando_ninguna_fila_cumple(self):
        v = self.medida.evaluar({"mutante": [FILA_MEDIDA]})
        self.assertTrue(v.sin_evidencia)
        self.assertIn("mutante", v.sin_evidencia)
        self.assertIn("m.tipo == \"codigo\"", v.sin_evidencia)
        self.assertFalse(v.ok)

    def test_mide_cuando_hay_filas_que_cumplen(self):
        v = self.medida.evaluar({"mutante": [FILA_MEDIDA, FILA_CODIGO]})
        self.assertFalse(v.sin_evidencia)
        self.assertEqual(v.valor, 1)
        self.assertFalse(v.ok)  # umbral <= 0 con valor 1

    def test_mide_ok_cuando_cumple_umbral(self):
        datos = [
            "medida", "d.prueba_ok",
            ["desde", ["de", "mutante", "m"], ["donde", COND_CODIGO]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 1, "permite 1"],
            ["requiere", ["filas", "mutante", "m", COND_CODIGO]],
            ["alcance", "NO ve nada fuera de prueba"],
        ]
        medida_ok = Medida.de_datos(datos)
        v = medida_ok.evaluar({"mutante": [FILA_CODIGO]})
        self.assertFalse(v.sin_evidencia)
        self.assertTrue(v.ok)
        self.assertEqual(v.valor, 1)

    def test_campo_ausente_en_condicion_levanta_error_de_algebra(self):
        cond_campo_especifico = ["==", ["campo", "m", "estado"], "pasaron"]
        medida = Medida.de_datos(_crear_medida(
            ["requiere", ["filas", "mutante", "m", cond_campo_especifico]],
            donde=None,
        ))
        with self.assertRaises(ErrorDeAlgebra):
            medida.evaluar({"mutante": [FILA_MEDIDA, FILA_CODIGO]})

    def test_medida_sin_condicion_sigue_intacta(self):
        datos = [
            "medida", "d.sin_cond",
            ["desde", ["de", "mutante", "m"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "razón"],
            ["requiere", "mutante"],
            ["alcance", "NO ve nada"],
        ]
        medida = Medida.de_datos(datos)
        self.assertEqual(medida.a_datos()[4], ["umbral", "<=", 0, "razón", "sin_declarar"])
        self.assertEqual(medida.a_datos()[5], ["requiere", "mutante"])
        self.assertEqual(medida.evaluar({"mutante": [FILA_MEDIDA]}).valor, 1)
        self.assertEqual(medida.evaluar({"mutante": []}).sin_evidencia, "mutante")


class RequiereHechosTests(unittest.TestCase):
    def test_hechos_requiere_y_dependencia_de_medida(self):
        datos = _crear_medida(["requiere", "pieza", ["filas", "mutante", "m", COND_CODIGO]])
        medida = Medida.de_datos(datos)
        hechos = como_hechos([medida])

        filas_requiere = hechos.por_relacion["requiere"]
        self.assertEqual(
            [(f["relacion"], f["con_condicion"], f["indice"]) for f in filas_requiere],
            [("pieza", False, 0), ("mutante", True, 1)],
        )

        filas_dep = hechos.por_relacion["dependencia_de_medida"]
        deps_por_rel = {f["relacion"]: f for f in filas_dep}
        self.assertIn("pieza", deps_por_rel)
        self.assertIn("mutante", deps_por_rel)
        self.assertFalse(deps_por_rel["pieza"]["con_condicion"])
        self.assertEqual(deps_por_rel["pieza"]["clase"], "requiere")


class RequiereSuperficieTests(unittest.TestCase):
    def test_sin_requiere_lectura_e_impresion(self):
        texto = (
            "medida d.sin_req:\n"
            "    de mutante m\n"
            "    resumen contar(1)\n"
            "    umbral <= 0 porque \"razón\"\n"
            "    alcance \"NO ve\"\n"
        )
        datos = leer(texto)
        self.assertNotIn("requiere", [n[0] for n in datos if isinstance(n, list)])
        self.assertEqual(leer(imprimir(datos)), datos)

    def test_una_linea_simple_lectura_e_impresion(self):
        texto = (
            "medida d.un_req:\n"
            "    de mutante m\n"
            "    resumen contar(1)\n"
            "    umbral <= 0 porque \"razón\"\n"
            "    requiere pieza, corrida\n"
            "    alcance \"NO ve\"\n"
        )
        datos = leer(texto)
        self.assertEqual(datos[5], ["requiere", "pieza", "corrida"])
        self.assertEqual(leer(imprimir(datos)), datos)

    def test_una_linea_con_condicion_lectura_e_impresion(self):
        texto = (
            "medida d.cond:\n"
            "    de mutante m\n"
            "    donde m.tipo == \"codigo\"\n"
            "    resumen contar(1)\n"
            "    umbral <= 0 segun contrato porque \"razón\"\n"
            "    requiere mutante m donde m.tipo == \"codigo\"\n"
            "    ambito universal\n"
            "    alcance \"NO ve\"\n"
        )
        datos = leer(texto)
        self.assertEqual(datos[5], ["requiere", ["filas", "mutante", "m", COND_CODIGO]])
        self.assertEqual(datos[6], ["ambito", "universal"])
        self.assertEqual(datos[7], ["alcance", "NO ve"])
        self.assertEqual(leer(imprimir(datos)), datos)

    def test_varias_lineas_requiere_se_juntan_en_orden(self):
        texto = (
            "medida d.multi_req:\n"
            "    de mutante m\n"
            "    resumen contar(1)\n"
            "    umbral <= 0 porque \"razón\"\n"
            "    requiere pieza\n"
            "    requiere corrida\n"
            "    requiere mutante m donde m.tipo == \"codigo\"\n"
            "    ambito universal\n"
            "    alcance \"NO ve\"\n"
        )
        datos = leer(texto)
        self.assertEqual(
            datos[5],
            ["requiere", "pieza", "corrida", ["filas", "mutante", "m", COND_CODIGO]],
        )
        self.assertEqual(datos[6], ["ambito", "universal"])
        self.assertEqual(datos[7], ["alcance", "NO ve"])
        reimpreso = imprimir(datos)
        self.assertEqual(leer(reimpreso), datos)

    def test_diagnostico_ambito_y_alcance_tras_varias_lineas_requiere(self):
        texto = (
            "medida d.rutas:\n"
            "    de mutante m\n"
            "    resumen contar(1)\n"
            "    umbral <= 0 porque \"razón\"\n"
            "    requiere pieza\n"
            "    requiere mutante m donde m.tipo == \"codigo\"\n"
            "    ambito universal\n"
            "    alcance \"NO ve\"\n"
        )
        datos = leer(texto)
        self.assertEqual(datos[5][0], "requiere")
        self.assertEqual(datos[6], ["ambito", "universal"])
        self.assertEqual(datos[7], ["alcance", "NO ve"])


if __name__ == "__main__":
    unittest.main()
