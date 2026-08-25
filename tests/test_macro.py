"""Tests de las macros. Una macro que expande mal es peor que no tenerla: mueve el error a un lugar
donde nadie lo mira."""

from __future__ import annotations

import json
import importlib
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo.algebra import LimitesAlgebra
from nucleo.macro import (DIRECTORIO_BASE, Macro, MacroMalDeclarada, MacroMalUsada,
                          exigir_biblioteca,
                          RegistroMacros, cargar_macros, es_macro, expandir, macros_base)
from nucleo.medida import Medida, cargar_catalogo, cargar_fuente_medida, rutas_de_catalogo

PRED = ["==", ["campo", "m", "murio"], False]


def setUpModule() -> None:
    """Registra las escalares del catálogo base DENTRO de la suite, no al importar el módulo.

    Como `import catalogos.escalares` al tope, el decorador `@escalar` corría durante el
    descubrimiento: un mutante en `escalar()`, `_registro()` o `_contrato_de_escalar()` rompía la
    importación del archivo de test y el arnés lo reportaba como «error» en vez de «muerte». Once
    mutantes de `nucleo/algebra.py` quedaban sin veredicto por esto. Acá el fallo es del test.
    """
    importlib.import_module("catalogos.escalares")


class ExpansionTests(unittest.TestCase):
    def test_ninguno_da_la_forma_de_contar_lo_que_ofende(self) -> None:
        d = expandir(["ninguno", "d.p", "mutante", "m", PRED, "razón", "NO ve nada"])
        self.assertEqual(d, ["medida", "d.p",
                             ["desde", ["de", "mutante", "m"], ["donde", PRED]],
                             ["resumen", "contar", 1],
                             ["umbral", "<=", 0, "razón"],
                             ["alcance", "NO ve nada"]])

    def test_ninguno_par_une_la_relacion_consigo_misma(self) -> None:
        d = expandir(["ninguno-par", "d.p", "doc", "a", "b", PRED, "razón", "NO ve nada"])
        self.assertEqual(d[2][1], ["unir", ["de", "doc", "a"], ["de", "doc", "b"]])
        self.assertEqual(d[3], ["resumen", "contar", 1])
        self.assertEqual(d[4], ["umbral", "<=", 0, "razón"])

    def test_ninguno_par_con_el_mismo_alias_dos_veces_no_pasa(self) -> None:
        with self.assertRaises(MacroMalUsada) as e:
            expandir(["ninguno-par", "d.p", "doc", "a", "a", PRED, "r", "NO ve"])
        self.assertIn("distintos", str(e.exception))

    def test_peor_escribe_la_tolerancia_UNA_vez_y_la_pone_en_los_dos_lados(self) -> None:
        """Es el caso 012 del corpus, cerrado por construcción: la tolerancia estaba duplicada en el
        filtro y en el umbral, y nada las mantenía juntas."""
        expr = ["desvio_de_grilla", ["hecho", "a"], 100.0]
        d = expandir(["peor", "snap.x", "pieza", "a", expr, 1.0, "razón", "NO ve nada"])

        self.assertEqual(d[2][2], ["donde", [">", expr, 1.0]])   # el filtro
        self.assertEqual(d[3], ["resumen", "max", expr])          # la medición
        self.assertEqual(d[4][2], 1.0)                            # el umbral
        # y la expresión es LA MISMA en el filtro y en el resumen: no hay dos copias que divergir
        self.assertIs(d[2][2][1][1], d[3][2])

    def test_cada_macro_exige_su_cantidad_de_argumentos(self) -> None:
        for nombre in macros_base():
            with self.subTest(macro=nombre):
                with self.assertRaises(MacroMalUsada):
                    expandir([nombre, "d.p", "faltan", "cosas"])

    def test_lo_canonico_pasa_de_largo(self) -> None:
        canonica = ["medida", "d.p", ["desde", ["de", "m", "m"]], ["resumen", "contar", 1],
                    ["umbral", "<=", 0, "r"], ["alcance", "NO ve"]]
        self.assertFalse(es_macro(canonica))
        self.assertIs(expandir(canonica), canonica)

    def test_expandir_es_idempotente(self) -> None:
        una = expandir(["ninguno", "d.p", "mutante", "m", PRED, "razón", "NO ve nada"])
        self.assertEqual(expandir(una), una)

    def test_una_macro_puede_construir_sobre_otra(self) -> None:
        """Negarle a un proyecto construir sobre `ninguno` lo obliga a copiar el cuerpo, que es
        justo lo que la macro vino a evitar. La torre se permite; lo que se acota es el largo."""
        torre = Macro.de_datos(
            ["defmacro", "sin-sobrevivientes", ["id"], [],
             ["ninguno", ["$", "id"], "mutante", "m", PRED, "razón", "NO ve los no generados"]])
        registro = macros_base()
        registro.declarar(torre)

        d = expandir(["sin-sobrevivientes", "d.p"], registro)
        self.assertEqual(d[0], "medida")
        self.assertEqual(d[1], "d.p")
        self.assertEqual(d[3], ["resumen", "contar", 1])

    def test_una_macro_que_se_expande_a_si_misma_se_corta_por_la_cota(self) -> None:
        bucle = Macro.de_datos(
            ["defmacro", "bucle", ["id"], [], ["bucle", ["$", "id"]]])
        registro = RegistroMacros()
        registro.declarar(bucle)

        with self.assertRaises(MacroMalUsada) as e:
            expandir(["bucle", "d.p"], registro)
        # el diagnóstico tiene que NOMBRAR la cadena: sin esto, saber que hubo bucle no dice cuál
        self.assertIn("superó las", str(e.exception))
        self.assertIn("bucle → bucle", str(e.exception))

    def test_la_cota_de_expansion_sale_de_los_limites_declarados(self) -> None:
        bucle = Macro.de_datos(["defmacro", "bucle", ["id"], [], ["bucle", ["$", "id"]]])
        registro = RegistroMacros()
        registro.declarar(bucle)

        with self.assertRaisesRegex(MacroMalUsada, "las 3 vueltas"):
            expandir(["bucle", "d.p"], registro, LimitesAlgebra(expansiones_maximas=3))


class DeclaracionTests(unittest.TestCase):
    """Una macro mal declarada se rompe al LEERLA. Si esperara a la invocación, el error aparecería
    en el archivo de quien la usó y no en el de quien la escribió."""

    def _macro(self, nombre="propia", parametros=None, guardas=None, plantilla=None):
        return ["defmacro", nombre,
                parametros if parametros is not None else ["id"],
                guardas if guardas is not None else [],
                plantilla if plantilla is not None else ["medida", ["$", "id"]]]

    def test_las_tres_universales_salen_de_datos_y_no_de_python(self) -> None:
        archivos = {p.stem for p in DIRECTORIO_BASE.glob("*.json")}
        self.assertEqual(archivos, {"ninguno", "ninguno-par", "peor"})
        self.assertEqual(set(macros_base()), archivos)
        for macro in macros_base().values():
            self.assertIsInstance(macro, Macro)

    def test_un_nombre_reservado_del_lenguaje_no_puede_ser_macro(self) -> None:
        for reservada in ("medida", "donde", "de", "unir", "agrupar", "contar", "max", "y", "no"):
            with self.subTest(nombre=reservada):
                with self.assertRaisesRegex(MacroMalDeclarada, "palabra del lenguaje"):
                    Macro.de_datos(self._macro(nombre=reservada))

    def test_un_nombre_no_portable_no_pasa(self) -> None:
        for nombre in ("Mayuscula", "con espacio", "con.punto", "1empieza-con-digito", ""):
            with self.subTest(nombre=nombre):
                with self.assertRaises(MacroMalDeclarada):
                    Macro.de_datos(self._macro(nombre=nombre))

    def test_un_hueco_que_no_es_parametro_no_pasa(self) -> None:
        with self.assertRaisesRegex(MacroMalDeclarada, "no son parámetros"):
            Macro.de_datos(self._macro(
                parametros=["id"], plantilla=["medida", ["$", "id"], ["$", "inventado"]]))

    def test_un_parametro_que_la_plantilla_nunca_usa_no_pasa(self) -> None:
        """Es la misma regla que `meta.toda_medida_esta_ejercitada`: lo que nadie usa es
        decoración, y acá además infla la aridad que se le exige a quien invoca."""
        with self.assertRaisesRegex(MacroMalDeclarada, "nunca usa"):
            Macro.de_datos(self._macro(parametros=["id", "sobra"]))

    def test_un_parametro_usado_solo_en_una_guarda_cuenta_como_usado(self) -> None:
        macro = Macro.de_datos(self._macro(
            parametros=["id", "otro"],
            guardas=[["guarda", ["!=", ["$", "id"], ["$", "otro"]], "distintos"]]))
        self.assertEqual(macro.parametros, ("id", "otro"))

    def test_parametros_repetidos_no_pasan(self) -> None:
        with self.assertRaisesRegex(MacroMalDeclarada, "repetidos"):
            Macro.de_datos(self._macro(parametros=["id", "id"]))

    def test_sin_parametros_no_pasa(self) -> None:
        """La plantilla va SIN huecos a propósito: con huecos, una lista de parámetros vacía falla
        igual pero por otro motivo («usa huecos que no son parámetros»), y entonces el test pasa sin
        ejercitar esta comprobación. La mutación lo mostró — el mutante sobrevivía tapado."""
        for parametros in ([], "no-es-lista", {}):
            with self.subTest(parametros=parametros):
                with self.assertRaisesRegex(MacroMalDeclarada, "lista no vacía"):
                    Macro.de_datos(self._macro(parametros=parametros, plantilla=["medida"]))

    def test_una_guarda_mal_formada_no_pasa(self) -> None:
        for guarda in ([["guarda", ["!=", 1, 2]]], [["guarda", ["!=", 1, 2], ""]],
                       [["no-es-guarda", ["!=", 1, 2], "m"]], [["guarda"]]):
            with self.subTest(guarda=guarda):
                with self.assertRaises(MacroMalDeclarada):
                    Macro.de_datos(self._macro(guardas=guarda))

    def test_las_guardas_ausentes_se_declaran_como_lista_vacia(self) -> None:
        """El álgebra ya exige que una relación vacía se declare `[]` en vez de omitirse; una macro
        sin guardas sigue la misma regla en vez de aceptar un campo que falta."""
        with self.assertRaisesRegex(MacroMalDeclarada, "sin guardas se escribe"):
            Macro.de_datos(self._macro(guardas="ninguna"))

    def test_la_forma_de_defmacro_tiene_cinco_elementos(self) -> None:
        for datos in (["defmacro", "p", ["id"], []],
                      ["defmacro", "p", ["id"], [], ["medida", ["$", "id"]], "de+"],
                      ["no-defmacro", "p", ["id"], [], ["medida"]]):
            with self.subTest(datos=datos):
                with self.assertRaises(MacroMalDeclarada):
                    Macro.de_datos(datos)

    def test_un_hueco_mal_formado_se_denuncia_en_la_declaracion(self) -> None:
        with self.assertRaisesRegex(MacroMalDeclarada, "un hueco va"):
            Macro.de_datos(self._macro(plantilla=["medida", ["$"], ["$", "id"]]))

    def test_una_guarda_hereda_el_contrato_del_algebra(self) -> None:
        """No hay evaluador nuevo: la guarda se sustituye y la evalúa el álgebra, así que la
        prohibición de igualdad exacta entre flotantes vale también acá."""
        macro = Macro.de_datos(self._macro(
            parametros=["id"], guardas=[["guarda", ["==", ["$", "id"], 0.3], "igual"]]))
        with self.assertRaisesRegex(MacroMalUsada, "guarda no se pudo evaluar"):
            macro.expandir(["propia", 0.1 + 0.2])

    def test_un_nombre_declarado_dos_veces_no_se_sobrescribe(self) -> None:
        registro = macros_base()
        with self.assertRaisesRegex(MacroMalDeclarada, "ya está declarada"):
            registro.declarar(Macro.de_datos(self._macro(nombre="ninguno")))

    def test_cargar_una_macro_invalida_nombra_el_archivo(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            ruta = Path(td) / "rota.json"
            ruta.write_text(json.dumps(["defmacro", "medida", ["id"], [], ["x"]]),
                            encoding="utf-8")
            with self.assertRaisesRegex(MacroMalDeclarada, "rota.json"):
                cargar_macros(Path(td))

    def test_el_registro_base_no_se_contamina_desde_una_copia(self) -> None:
        copia = macros_base()
        copia.declarar(Macro.de_datos(self._macro(nombre="propia")))
        self.assertIn("propia", copia)
        self.assertNotIn("propia", macros_base())

    def test_una_macro_declarada_es_inmutable(self) -> None:
        """Si se pudiera reescribir la plantilla después de validarla, la validación no valdría
        nada: bastaría cargarla bien y ensuciarla antes de expandir."""
        macro = Macro.de_datos(self._macro())
        with self.assertRaises(Exception):
            macro.plantilla = ["otra", "cosa"]

    def test_una_plantilla_vacia_o_que_no_es_lista_no_pasa(self) -> None:
        for plantilla in ([], "una cadena", 0, {}):
            with self.subTest(plantilla=plantilla):
                with self.assertRaisesRegex(MacroMalDeclarada, "lista no vacía"):
                    Macro.de_datos(self._macro(plantilla=plantilla))

    def test_el_error_de_aridad_dice_cuantos_argumentos_llegaron(self) -> None:
        """Un diagnóstico que miente sobre la cuenta manda a buscar el error al lugar equivocado."""
        with self.assertRaises(MacroMalUsada) as e:
            expandir(["ninguno", "d.p", "mutante"])
        self.assertIn("recibió 2 argumento(s)", str(e.exception))
        self.assertIn("id, relacion, alias", str(e.exception))

    def test_una_guarda_incumplida_nombra_la_medida_y_no_la_macro(self) -> None:
        """El mensaje lo lee alguien que escribió UNA medida: tiene que decirle cuál de las suyas
        está mal, no cómo se llama la macro que eligió."""
        macro = Macro.de_datos(self._macro(
            parametros=["id"],
            guardas=[["guarda", ["!=", ["$", "id"], "prohibido"], "ese id no se puede usar"]]))
        with self.assertRaises(MacroMalUsada) as e:
            macro.expandir(["propia", "prohibido"])
        self.assertTrue(str(e.exception).startswith("prohibido:"), str(e.exception))

    def test_cargar_macros_acepta_una_lista_de_directorios(self) -> None:
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            (Path(a) / "una.json").write_text(
                json.dumps(self._macro(nombre="una")), encoding="utf-8")
            (Path(b) / "otra.json").write_text(
                json.dumps(self._macro(nombre="otra")), encoding="utf-8")
            registro = cargar_macros([Path(a), Path(b)])
        self.assertEqual(sorted(registro), ["otra", "una"])

    def test_una_cabeza_que_no_es_texto_no_es_macro_y_no_revienta(self) -> None:
        """`["x", …] in registro` explota si la cabeza no es hasheable. Preguntar por el tipo tiene
        que ir ANTES de preguntar por la pertenencia."""
        self.assertFalse(es_macro([["no", "es", "texto"], "d.p"]))
        self.assertFalse(es_macro([{"tampoco": 1}, "d.p"]))

    def test_una_instalacion_sin_biblioteca_estandar_se_denuncia(self) -> None:
        """Sin esta guarda, un wheel al que le falten los datos deja el lenguaje sin `ninguno` y el
        error aparece recién en el catálogo del proyecto, culpando al archivo equivocado."""
        with tempfile.TemporaryDirectory() as td:
            vacio = Path(td)
            self.assertEqual(cargar_macros(vacio), {})
            with self.assertRaisesRegex(MacroMalDeclarada, "instalación quedó incompleta"):
                exigir_biblioteca(cargar_macros(vacio), vacio)

    def test_un_registro_ajeno_al_tipo_no_pasa(self) -> None:
        with self.assertRaises(MacroMalDeclarada):
            expandir(["ninguno"], {"ninguno": None})


class ProyectoDeclaraLasSuyasTests(unittest.TestCase):
    """El criterio de éxito de todo esto: un proyecto define una forma propia y la usa **sin tocar
    una línea de Oracle**. Mientras `MACROS` fue un diccionario de Python, esto era imposible: los
    medios de abstracción tenían dueño, y el dueño era quien podía editar el núcleo."""

    MACRO_PROPIA = ["defmacro", "todos-cumplen",
                    ["id", "relacion", "alias", "predicado", "porque", "alcance"],
                    [],
                    ["medida", ["$", "id"],
                     ["desde", ["de", ["$", "relacion"], ["$", "alias"]],
                      ["donde", ["no", ["$", "predicado"]]]],
                     ["resumen", "contar", 1],
                     ["umbral", "<=", 0, ["$", "porque"]],
                     ["alcance", ["$", "alcance"]]]]

    def _proyecto(self, raiz: Path, macro=None) -> None:
        (raiz / "macros").mkdir()
        (raiz / "macros" / "todos-cumplen.json").write_text(
            json.dumps(macro if macro is not None else self.MACRO_PROPIA), encoding="utf-8")
        catalogo = raiz / "catalogos" / "demo"
        catalogo.mkdir(parents=True)
        (catalogo / "demo.todo_ok.json").write_text(json.dumps([
            "todos-cumplen", "demo.todo_ok", "item", "i",
            ["==", ["campo", "i", "ok"], True],
            "un item que no cumple invalida la entrega entera",
            "NO ve los items que nadie declaró",
        ]), encoding="utf-8")

    def test_una_macro_del_proyecto_se_carga_y_evalua_sin_tocar_oracle(self) -> None:
        from oracle_metalenguaje import Motor

        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._proyecto(raiz)

            motor = Motor.desde_proyecto(raiz)
            self.assertEqual([m.id for m in motor.medidas], ["demo.todo_ok"])

            verde = motor.evaluar({"item": [{"id": "a", "ok": True}]})
            rojo = motor.evaluar({"item": [{"id": "a", "ok": True}, {"id": "b", "ok": False}]})

        self.assertTrue(verde.ok)
        self.assertFalse(rojo.ok)
        # y los testigos son las filas que ofenden, igual que en cualquier medida canónica
        self.assertEqual(rojo.veredictos[0].testigos[0]["i"]["id"], "b")

    def test_la_medida_expandida_es_indistinguible_de_una_canonica(self) -> None:
        """Si el resto del sistema pudiera notar que hubo macro, la macro sería un mecanismo nuevo
        en vez de azúcar. La mutación y el nivel L2 tienen que seguir viendo formas canónicas."""
        from oracle_metalenguaje import Motor

        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._proyecto(raiz)
            medida = Motor.desde_proyecto(raiz).medidas[0]

        self.assertEqual(medida.a_datos()[0], "medida")
        self.assertEqual(medida.a_fuente()[0], "todos-cumplen")
        self.assertEqual(Medida.de_datos(medida.a_datos()).a_datos(), medida.a_datos())

    def test_un_proyecto_no_puede_redefinir_una_macro_universal(self) -> None:
        from oracle_metalenguaje import Motor

        propia = list(self.MACRO_PROPIA)
        propia[1] = "ninguno"
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._proyecto(raiz, macro=propia)
            with self.assertRaisesRegex(MacroMalDeclarada, "ya está declarada"):
                Motor.desde_proyecto(raiz)

    def test_una_macro_rota_del_proyecto_falla_al_cargar_el_catalogo(self) -> None:
        from oracle_metalenguaje import Motor

        propia = list(self.MACRO_PROPIA)
        propia[2] = ["id", "relacion", "alias", "predicado", "porque", "alcance", "sobra"]
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._proyecto(raiz, macro=propia)
            with self.assertRaisesRegex(MacroMalDeclarada, "nunca usa"):
                Motor.desde_proyecto(raiz)

    def test_sin_registro_del_proyecto_la_medida_no_se_lee_como_canonica(self) -> None:
        """Cargar el catálogo sin las macros del proyecto tiene que fallar, no interpretar la
        invocación como una medida canónica malformada y culpar al archivo equivocado."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._proyecto(raiz)
            with self.assertRaises(Exception) as e:
                cargar_catalogo(raiz / "catalogos")
        self.assertIn("una medida es", str(e.exception))


class ContratoConLaMedidaTests(unittest.TestCase):
    def test_una_macro_construye_una_medida_igual_que_la_canonica(self) -> None:
        macro = Medida.de_datos(["ninguno", "d.p", "mutante", "m", PRED, "razón", "NO ve nada"])
        canonica = Medida.de_datos(macro.a_datos())
        for campo in ("id", "tuberia", "resumen", "op", "limite", "porque", "alcance"):
            self.assertEqual(getattr(macro, campo), getattr(canonica, campo), campo)

    def test_a_datos_devuelve_SIEMPRE_la_canonica(self) -> None:
        m = Medida.de_datos(["ninguno", "d.p", "mutante", "m", PRED, "razón", "NO ve nada"])
        self.assertEqual(m.a_datos()[0], "medida")

    def test_a_fuente_devuelve_como_esta_escrita(self) -> None:
        m = Medida.de_datos(["ninguno", "d.p", "mutante", "m", PRED, "razón", "NO ve nada"])
        self.assertEqual(m.a_fuente()[0], "ninguno")
        c = Medida.de_datos(m.a_datos())
        self.assertEqual(c.a_fuente()[0], "medida")

    def test_una_macro_mal_usada_falla_al_LEERSE(self) -> None:
        with self.assertRaises(MacroMalUsada):
            Medida.de_datos(["peor", "d.p", "faltan"])


class CatalogoRealTests(unittest.TestCase):
    """El catálogo BASE del repo. Los dominios particulares se fueron a sus proyectos, así que acá
    quedan sólo las medidas universales: proceso, meta y simulación."""

    def setUp(self) -> None:
        self.catalogo = cargar_catalogo(RAIZ / "catalogos")
        self.crudos = {
            cargar_fuente_medida(p)[1]: cargar_fuente_medida(p)
            for p in rutas_de_catalogo(RAIZ / "catalogos")
        }

    def test_todas_cargan_y_la_mayoria_son_macro(self) -> None:
        macros = sum(1 for d in self.crudos.values() if es_macro(d))
        # se compara la PROPORCIÓN, no un número absoluto: contar medidas hacía que mover un dominio
        # a su proyecto rompiera un test que no tenía nada que ver
        self.assertGreater(macros / len(self.crudos), 0.8)
        self.assertEqual(len(self.catalogo), len(self.crudos))

    def test_la_expansion_de_cada_una_vuelve_a_construir_lo_mismo(self) -> None:
        """Idempotencia sobre el catálogo real: expandir y volver a leer no puede cambiar nada."""
        for mid, m in self.catalogo.items():
            with self.subTest(medida=mid):
                self.assertEqual(Medida.de_datos(m.a_datos()).a_datos(), m.a_datos())

    def test_ninguna_medida_escrita_como_macro_perdio_su_defensa_ni_su_alcance(self) -> None:
        for mid, m in self.catalogo.items():
            with self.subTest(medida=mid):
                self.assertTrue(m.porque.strip())
                self.assertIn("NO ", m.alcance)


if __name__ == "__main__":
    unittest.main()
