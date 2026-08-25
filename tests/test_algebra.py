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
            algebra.limites_predeterminados(),
            algebra.LimitesAlgebra(
                filas_por_relacion=100_000,
                producto_cartesiano=1_000_000,
                profundidad_expresion=64,
                # Va explícito, como los otros tres. Si se dejara al valor por omisión, los dos lados
                # de la comparación lo tomarían del mismo lugar y cambiarlo no rompería nada — que es
                # justo lo que pasó: el mutante `16 → 17` sobrevivió a la ronda completa.
                expansiones_maximas=16,
            ),
        )
        with self.assertRaises(FrozenInstanceError):
            algebra.limites_predeterminados().filas_por_relacion = 1

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

    def test_los_logicos_no_cortocircuitan_sobre_un_campo_ausente(self) -> None:
        """Un `y`/`o` no puede tapar el error que §3 manda levantar.

        `all`/`any` sobre un generador dejaban de evaluar apenas el resultado estaba decidido, así
        que un campo mal escrito dentro de un `y` devolvía un `False` silencioso —un verde— en vez
        de romper. Dependía de los datos: la misma medida rota levantaba el error con una evidencia
        y lo escondía con otra, que es la peor forma del defecto.
        """
        algebra = _algebra()
        fila = {"a": {"n": 1}}
        casos = (
            # el primer operando ya decide, y aun así hay que mirar el segundo
            ["y", ["==", ["campo", "a", "n"], 999], ["==", ["campo", "a", "typo"], 1]],
            ["o", ["==", ["campo", "a", "n"], 1], ["==", ["campo", "a", "typo"], 1]],
            # y el error no depende de en qué posición cayó el campo inexistente
            ["y", ["==", ["campo", "a", "typo"], 1], ["==", ["campo", "a", "n"], 999]],
        )
        for expresion in casos:
            with self.subTest(expresion=expresion):
                with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "sobre un valor ausente"):
                    algebra._evaluar_expr(expresion, fila, {})

        # y sigue combinando bien cuando no hay nada roto
        self.assertIs(
            algebra._evaluar_expr(
                ["y", ["==", ["campo", "a", "n"], 1], ["==", ["campo", "a", "n"], 1]], fila, {}),
            True)
        self.assertIs(
            algebra._evaluar_expr(
                ["o", ["==", ["campo", "a", "n"], 9], ["==", ["campo", "a", "n"], 1]], fila, {}),
            True)
        self.assertIs(
            algebra._evaluar_expr(
                ["y", ["==", ["campo", "a", "n"], 1], ["==", ["campo", "a", "n"], 9]], fila, {}),
            False)

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

    def test_un_error_de_evaluacion_nombra_la_ruta_del_nodo(self) -> None:
        algebra = _algebra()
        tuberia = [
            "desde",
            ["de", "pieza", "p"],
            ["donde", ["y",
                       [">", ["campo", "p", "x"], 0],
                       ["==", ["campo", "p", "typo"], 2]]],
        ]

        with self.assertRaises(algebra.ErrorDeAlgebra) as error:
            algebra.desde(tuberia, {"pieza": [{"x": 1}]})

        mensaje = str(error.exception)
        self.assertEqual(error.exception.ruta, "2.2.1.2")
        self.assertIn("en `2.2.1.2`", mensaje)
        self.assertIn("«==» sobre un valor ausente", mensaje)
        self.assertIn("['==', ['campo', 'p', 'typo'], 2]", mensaje)

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
                algebra.limites_predeterminados(),
            )

    def test_un_resumen_desconocido_nombra_el_agregado_recibido(self) -> None:
        algebra = _algebra()
        with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "agregado desconocido: «moda»"):
            algebra.validar_resumen(["resumen", "moda", 1])


class ClaveDeUnicidadTests(unittest.TestCase):
    """La clave de unicidad declarable: un contrato opcional que se valida ANTES de medir.

    Una relación sigue siendo una bolsa; el nodo `clave` es la puerta por la que un dominio que
    conoce su identidad pide que un duplicado sea un defecto del sensor y no un hecho más.
    """

    def _de(self, relacion, evidencia):
        algebra = _algebra()
        return algebra.desde(["desde", ["de", relacion, "p"]], evidencia)

    def test_sin_clave_la_relacion_sigue_siendo_una_bolsa(self) -> None:
        hecho = {"id": "repetido", "x": 2}
        filas = self._de("pieza", {"pieza": [hecho, hecho]})
        self.assertEqual(len(filas), 2)

    def test_un_duplicado_bajo_una_clave_declarada_nombra_clave_y_fila(self) -> None:
        algebra = _algebra()
        evidencia = {"pieza": [["clave", ["id"]], {"id": "x", "v": 1}, {"id": "x", "v": 2}]}
        with self.assertRaises(algebra.ErrorDeAlgebra) as error:
            self._de("pieza", evidencia)
        mensaje = str(error.exception)
        self.assertIn("«pieza»", mensaje)     # la relación responsable
        self.assertIn("clave (id)", mensaje)  # la clave responsable
        self.assertIn("fila 1", mensaje)      # la fila que la viola
        self.assertIn("fila 0", mensaje)      # y contra quién

    def test_una_clave_declarada_sin_duplicado_mide_con_normalidad(self) -> None:
        evidencia = {"pieza": [["clave", ["id"]], {"id": "x"}, {"id": "y"}]}
        self.assertEqual(len(self._de("pieza", evidencia)), 2)

    def test_una_clave_compuesta_solo_repite_cuando_repiten_todos_sus_campos(self) -> None:
        algebra = _algebra()
        bien = {"cosa": [["clave", ["a", "b"]], {"a": 1, "b": 2}, {"a": 1, "b": 3}]}
        self.assertEqual(len(self._de("cosa", bien)), 2)
        mal = {"cosa": [["clave", ["a", "b"]], {"a": 1, "b": 2}, {"a": 1, "b": 2}]}
        with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "clave \\(a, b\\)"):
            self._de("cosa", mal)

    def test_una_clave_mal_declarada_falla_al_leerse(self) -> None:
        algebra = _algebra()
        for mala in (
            ["clave"],
            ["clave", []],
            ["clave", [""]],
            ["clave", [7]],
            ["clave", ["id", "id"]],
            ["clave", "id"],
        ):
            with self.subTest(clave=mala):
                with self.assertRaises(algebra.ErrorDeAlgebra):
                    algebra.separar_clave([mala, {"id": "x"}])

    def test_una_clave_con_un_campo_ausente_falla(self) -> None:
        algebra = _algebra()
        evidencia = {"pieza": [["clave", ["id"]], {"id": "x"}, {"otro": 1}]}
        with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "no trae el campo id"):
            self._de("pieza", evidencia)

    def test_una_clave_con_un_valor_no_escalar_falla(self) -> None:
        algebra = _algebra()
        evidencia = {"pieza": [["clave", ["id"]], {"id": ["x"]}]}
        with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "no la trae como escalar"):
            self._de("pieza", evidencia)

    def test_la_clave_no_cuenta_como_fila_para_el_limite(self) -> None:
        algebra = _algebra()
        limite = algebra.LimitesAlgebra(filas_por_relacion=2)
        evidencia = {"pieza": [["clave", ["id"]], {"id": "x"}, {"id": "y"}]}
        filas = algebra.desde(["desde", ["de", "pieza", "p"]], evidencia, limite)
        self.assertEqual(len(filas), 2)

    def test_una_clave_sobre_una_relacion_vacia_no_da_ningun_fallo(self) -> None:
        self.assertEqual(self._de("vacia", {"vacia": [["clave", ["id"]]]}), [])


class TrazaDelEvaluador(unittest.TestCase):
    """El evaluador como sensor de sí mismo.

    No se prueba que las medidas estén verdes —eso lo dice `tools/trazar.py` sobre el corpus— sino
    que la traza pueda ponerlas ROJAS. Una propiedad que no puede fallar no verifica nada, y acá el
    riesgo es concreto: el sensor vive dentro de lo que audita.
    """

    def _traza(self, medida, evidencia):
        from nucleo.medida import Medida

        algebra = _algebra()
        with algebra.trazar() as crudos:
            Medida.de_datos(medida).evaluar(evidencia)
        salida = {"paso": [], "nodo": [], "producto": []}
        for clase, campos in crudos:
            salida[clase].append(dict(campos))
        return salida

    def test_apagada_no_acumula_nada(self) -> None:
        """El costo cuando nadie mide tiene que ser una lectura de ContextVar, no una lista."""
        algebra = _algebra()
        self.assertIsNone(algebra._TRAZA_ACTIVA.get())
        algebra._anotar("paso", t=0)                    # sin contexto: se descarta
        self.assertIsNone(algebra._TRAZA_ACTIVA.get())

    def test_el_contexto_se_restaura_aunque_la_evaluacion_falle(self) -> None:
        algebra = _algebra()
        with self.assertRaises(ZeroDivisionError):
            with algebra.trazar():
                raise ZeroDivisionError
        self.assertIsNone(algebra._TRAZA_ACTIVA.get())

    def test_la_traza_registra_cada_paso_de_la_tuberia(self) -> None:
        medida = ["medida", "d.traza",
                  ["desde", ["de", "cosa", "c"], ["donde", [">", ["campo", "c", "n"], 1]]],
                  ["resumen", "contar", 1],
                  ["umbral", "<=", 0, "una razón"], ["alcance", "NO ve nada más"]]
        traza = self._traza(medida, {"cosa": [{"n": 1}, {"n": 2}, {"n": 3}]})
        self.assertEqual([p["operador"] for p in traza["paso"]], ["de", "donde"])
        donde = traza["paso"][1]
        self.assertEqual((donde["filas_antes"], donde["filas_despues"]), (3, 2))

    def test_el_producto_se_anota_con_lo_que_unir_devolvio(self) -> None:
        """La primera versión anotaba dentro de `_unir`, leyendo su propia variable: cualquier
        defecto entre esa línea y el punto de uso quedaba fuera de la medición."""
        medida = ["medida", "d.unir",
                  ["desde", ["unir", ["de", "a", "x"], ["de", "b", "y"]]],
                  ["resumen", "contar", 1],
                  ["umbral", "<=", 0, "una razón"], ["alcance", "NO ve nada más"]]
        traza = self._traza(medida, {"a": [{"n": 1}, {"n": 2}], "b": [{"m": 9}]})
        self.assertEqual(traza["producto"], [{"izquierda": 2, "derecha": 1, "salida": 2}])

    def test_los_logicos_declaran_cuantos_operandos_evaluaron(self) -> None:
        """El primer operando ya decide y aun así los dos tienen que quedar contados."""
        medida = ["medida", "d.logico",
                  ["desde", ["de", "cosa", "c"],
                   ["donde", ["y", [">", ["campo", "c", "n"], 100],
                              [">", ["campo", "c", "n"], 0]]]],
                  ["resumen", "contar", 1],
                  ["umbral", "<=", 0, "una razón"], ["alcance", "NO ve nada más"]]
        traza = self._traza(medida, {"cosa": [{"n": 1}]})
        self.assertEqual(traza["nodo"], [{"cabeza": "y", "declarados": 2, "evaluados": 2}])
