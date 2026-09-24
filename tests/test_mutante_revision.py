"""Revisión independiente de 0.21.0: `requiere` con condición, relaciones con variantes y `mutante`.

Escrita por Claude contra `vault-kb/estudios/0.21.0-mutante/ENCARGO-AGY.md`, antes de leer la implementación.
Tarea `20260915-155111-mutante`.
"""

import unittest
from pathlib import Path

from nucleo.algebra import ErrorDeAlgebra
from nucleo.medida import Medida, MedidaMalDeclarada, como_hechos
from nucleo.relacion import Relacion, RelacionMalDeclarada, cargar, hechos_de_relaciones
from tools import sintaxis

RAIZ = Path(__file__).resolve().parents[1]

CONDICION = ["==", ["campo", "m", "tipo"], "codigo"]
FILA_MEDIDA = {"id": "d.x·f", "apunta_a": "d.x", "cambio": "f", "tipo": "medida",
               "detecciones_conductuales": 0, "rechazos_del_algebra": 0}
FILA_CODIGO = {"id": "a.py:1:1:c", "apunta_a": "a.py", "cambio": "c", "tipo": "codigo",
               "estado": "pasaron", "murio": False, "tests_fallaron": False, "error_arnes": False,
               "timeout": False, "codigo_salida": 0, "equivalente_declarado": False,
               "razon_equivalente": ""}


def _medida(requiere, *, donde=CONDICION):
    tuberia = ["desde", ["de", "mutante", "m"]]
    if donde is not None:
        tuberia.append(["donde", donde])
    return ["medida", "d.cond", tuberia, ["resumen", "contar", 1],
            ["umbral", "<=", 0, "razón"], requiere, ["alcance", "NO ve"]]


class RequiereConCondicionTests(unittest.TestCase):
    def test_carga_y_devuelve_la_forma_canonica(self):
        datos = _medida(["requiere", ["filas", "mutante", "m", CONDICION]])
        self.assertEqual(Medida.de_datos(datos).a_datos()[5], datos[5])

    def test_formas_invalidas_se_rechazan_al_cargar(self):
        casos = {
            "alias inválido": ["requiere", ["filas", "mutante", "M", CONDICION]],
            "relación inválida": ["requiere", ["filas", "Mutante", "m", CONDICION]],
            "relación repetida": ["requiere", "mutante", ["filas", "mutante", "m", CONDICION]],
            "condición no booleana": ["requiere", ["filas", "mutante", "m", ["campo", "m", "tipo"]]],
            "alias ajeno": ["requiere", ["filas", "mutante", "m", ["==", ["campo", "x", "tipo"], "c"]]],
            "entrada incompleta": ["requiere", ["filas", "mutante", "m"]],
        }
        for nombre, requiere in casos.items():
            with self.subTest(nombre), self.assertRaises((MedidaMalDeclarada, ErrorDeAlgebra)):
                Medida.de_datos(_medida(requiere))

    def test_sin_evidencia_si_no_hay_filas_de_la_condicion(self):
        medida = Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", CONDICION]]))
        for nombre, evidencia in (("vacía", {"mutante": []}), ("sin relación", {}),
                                  ("sólo del otro tipo", {"mutante": [FILA_MEDIDA]})):
            with self.subTest(nombre):
                v = medida.evaluar(evidencia)
                self.assertTrue(v.sin_evidencia, v)
                self.assertIn("mutante", v.sin_evidencia)
                self.assertFalse(v.ok)

    def test_mide_cuando_hay_filas_que_cumplen(self):
        medida = Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", CONDICION]]))
        v = medida.evaluar({"mutante": [FILA_MEDIDA, FILA_CODIGO]})
        self.assertFalse(v.sin_evidencia)
        self.assertEqual(v.valor, 1)

    def test_un_campo_ausente_en_la_condicion_levanta(self):
        condicion = ["==", ["campo", "m", "estado"], "pasaron"]
        medida = Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", condicion]], donde=None))
        with self.assertRaises(ErrorDeAlgebra):
            medida.evaluar({"mutante": [FILA_MEDIDA, FILA_CODIGO]})

    def test_una_medida_sin_condicion_no_cambia(self):
        datos = _medida(["requiere", "mutante"])
        medida = Medida.de_datos(datos)
        self.assertEqual(medida.a_datos()[5], ["requiere", "mutante"])
        self.assertEqual(medida.evaluar({"mutante": [FILA_MEDIDA]}).valor, 0)
        self.assertEqual(medida.evaluar({"mutante": []}).sin_evidencia, "mutante")

    def test_hechos_marcan_con_condicion(self):
        datos = _medida(["requiere", "pieza", ["filas", "mutante", "m", CONDICION]])
        filas = como_hechos([Medida.de_datos(datos)]).por_relacion["requiere"]
        self.assertEqual([(f["relacion"], f["con_condicion"]) for f in filas],
                         [("pieza", False), ("mutante", True)])


class RevisionDeLaEntregaTests(unittest.TestCase):
    """Defectos encontrados al revisar la entrega de agy (REVISION-CLAUDE.md)."""

    def test_la_condicion_recorre_filas_y_no_el_nodo_clave(self):
        medida = Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", CONDICION]]))
        con_clave = {"mutante": [["clave", ["id"]], FILA_MEDIDA, FILA_CODIGO]}
        self.assertEqual(medida.evaluar(con_clave).valor, 1)
        solo_clave = medida.evaluar({"mutante": [["clave", ["id"]]]})
        self.assertTrue(solo_clave.sin_evidencia)

    def test_una_condicion_que_no_da_booleano_levanta_al_evaluar(self):
        from nucleo import algebra
        registro = algebra.RegistroEscalares()

        @algebra.escalar("uno", registro=registro)
        def uno():
            return 1

        condicion = ["uno"]
        try:
            medida = Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", condicion]], donde=None),
                                     registro=registro)
        except (MedidaMalDeclarada, ErrorDeAlgebra):
            return   # rechazarla al cargar también cumple
        with self.assertRaises(ErrorDeAlgebra):
            medida.evaluar({"mutante": [FILA_MEDIDA]}, registro=registro)

    def test_un_nombre_simple_de_requiere_conserva_la_regla_de_06(self):
        datos = _medida(["requiere", "Pieza-Vieja"], donde=None)
        self.assertEqual(Medida.de_datos(datos).a_datos()[5], ["requiere", "Pieza-Vieja"])
        with self.assertRaises(MedidaMalDeclarada):
            Medida.de_datos(_medida(["requiere", "  "], donde=None))


class RondaDeMutacionDeMedidasTests(unittest.TestCase):
    """CI de 5040565: `tools/mutar.py` salía 1 porque la medida de código queda SIN EVIDENCIA."""

    def test_un_sin_evidencia_no_hace_fallar_la_ronda_y_un_rojo_si(self):
        from nucleo.medida import Informe, Veredicto
        from tools.mutar import _politicas_ok
        sin = Veredicto("proceso.codigo", 0, False, "<= 0", "r", "a", (),
                        sin_evidencia='mutante sin filas con m.tipo == "codigo"')
        verde = Veredicto("proceso.test", 0, True, "<= 0", "r", "a", ())
        rojo = Veredicto("meta.x", 1, False, "<= 0", "r", "a", ())
        self.assertTrue(_politicas_ok(Informe((sin, verde))))
        self.assertTrue(_politicas_ok(Informe(())))
        self.assertFalse(_politicas_ok(Informe((sin, rojo))))


class SobrevivientesDeMutacionTests(unittest.TestCase):
    """Sobrevivientes de las rondas de 0.21.0 sobre nucleo/medida.py y nucleo/relacion.py."""

    def test_una_condicion_literal_carga_y_se_comporta_como_el_nombre(self):
        medida = Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", True]], donde=None))
        self.assertEqual(medida.a_datos()[5], ["requiere", ["filas", "mutante", "m", True]])
        self.assertFalse(medida.evaluar({"mutante": [FILA_MEDIDA]}).sin_evidencia)
        self.assertTrue(medida.evaluar({"mutante": []}).sin_evidencia)
        with self.assertRaises(MedidaMalDeclarada):
            Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", 1]], donde=None))

    def test_una_condicion_con_y_u_o_carga_si_sus_operandos_son_booleanos(self):
        tipo = ["==", ["campo", "m", "tipo"], "codigo"]
        ident = ["==", ["campo", "m", "id"], "a.py:1:1:c"]
        for logico in ("y", "o"):
            with self.subTest(logico):
                medida = Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", [logico, tipo, ident]]],
                                                 donde=None))
                self.assertFalse(medida.evaluar({"mutante": [FILA_CODIGO]}).sin_evidencia)
                with self.assertRaises(MedidaMalDeclarada):
                    Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m",
                                                          [logico, tipo, ["campo", "m", "id"]]]], donde=None))

    def test_el_nodo_variantes_se_reconoce_por_su_cabeza_y_admite_una_sola(self):
        with self.assertRaises(RelacionMalDeclarada):
            Relacion.de_datos(_relacion(["otro", *VARIANTES[1:]]))
        una = Relacion.de_datos(_relacion(["variantes", "tipo", VARIANTES[2]]))
        self.assertEqual([v.valor for v in una.variantes], ["medida"])

    def test_formas_mal_armadas_dentro_de_las_variantes(self):
        campo = ["campo", "x", "texto", "sin_unidad"]
        def con(variante):
            return ["variantes", "tipo", variante]
        casos = {
            "variante que no es lista": con(("variante", "medida", campo)),
            "variante sin campos": con(["variante", "medida"]),
            "cabeza distinta": con(["otra", "medida", campo]),
            "valor que no es texto": con(["variante", 3, campo]),
            "campo que no es lista": con(["variante", "medida", ("campo", "x", "texto", "sin_unidad")]),
            "campo incompleto": con(["variante", "medida", ["campo", "x", "texto"]]),
            "campo con otra cabeza": con(["variante", "medida", ["dato", "x", "texto", "sin_unidad"]]),
            "nombre que no es texto": con(["variante", "medida", ["campo", 3, "texto", "sin_unidad"]]),
            "nombre inválido": con(["variante", "medida", ["campo", "X", "texto", "sin_unidad"]]),
            "tipo que no es texto": con(["variante", "medida", ["campo", "x", 3, "sin_unidad"]]),
            "tipo desconocido": con(["variante", "medida", ["campo", "x", "numero", "sin_unidad"]]),
            "unidad que no es texto": con(["variante", "medida", ["campo", "x", "texto", 3]]),
            "unidad en blanco": con(["variante", "medida", ["campo", "x", "texto", "  "]]),
        }
        for nombre, variantes in casos.items():
            with self.subTest(nombre), self.assertRaises(RelacionMalDeclarada):
                Relacion.de_datos(_relacion(variantes))

    def test_no_en_la_condicion_y_el_primer_operando_de_un_logico(self):
        tipo = ["==", ["campo", "m", "tipo"], "codigo"]
        campo = ["campo", "m", "id"]
        for condicion in (["no", tipo], ["y", tipo, ["no", tipo]]):
            with self.subTest(condicion=condicion):
                Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", condicion]], donde=None))
        for condicion in (["no", campo], ["y", campo, tipo], ["o", campo, tipo]):
            with self.subTest(condicion=condicion), self.assertRaises((MedidaMalDeclarada, ErrorDeAlgebra)):
                Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", condicion]], donde=None))
        medida = Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", ["no", tipo]]], donde=None))
        self.assertTrue(medida.evaluar({"mutante": [FILA_CODIGO]}).sin_evidencia)
        self.assertFalse(medida.evaluar({"mutante": [FILA_MEDIDA]}).sin_evidencia)

    def test_una_escalar_declarada_sirve_de_condicion(self):
        from nucleo import algebra
        registro = algebra.RegistroEscalares()

        @algebra.escalar("es_codigo", registro=registro)
        def es_codigo(tipo):
            return tipo == "codigo"

        condicion = ["es_codigo", ["campo", "m", "tipo"]]
        medida = Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", condicion]], donde=None),
                                 registro=registro)
        self.assertFalse(medida.evaluar({"mutante": [FILA_CODIGO]}, registro=registro).sin_evidencia)
        self.assertTrue(medida.evaluar({"mutante": [FILA_MEDIDA]}, registro=registro).sin_evidencia)

    def test_la_condicion_de_requiere_solo_usa_su_alias(self):
        for condicion in (["==", ["campo", "x", "tipo"], "codigo"], ["==", ["hecho", "x"], "codigo"]):
            with self.subTest(condicion=condicion), self.assertRaises((MedidaMalDeclarada, ErrorDeAlgebra)):
                Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", condicion]], donde=None))

    def test_un_alias_invalido_se_rechaza_aunque_la_condicion_lo_use(self):
        condicion = ["==", ["campo", "M", "tipo"], "codigo"]
        with self.assertRaises(MedidaMalDeclarada):
            Medida.de_datos(_medida(["requiere", ["filas", "mutante", "M", condicion]], donde=None))
        with self.assertRaises(MedidaMalDeclarada):
            Medida.de_datos(_medida(["requiere", ["filas", "mutante", 3, CONDICION]], donde=None))

    def test_una_dependencia_por_fuente_no_lleva_condicion(self):
        datos = _medida(["requiere", ["filas", "mutante", "m", CONDICION]], donde=None)
        filas = como_hechos([Medida.de_datos(datos)]).por_relacion["dependencia_de_medida"]
        self.assertEqual(sorted((f["clase"], f["con_condicion"]) for f in filas),
                         [("fuente", False), ("requiere", True)])

    def test_una_variante_es_inmutable(self):
        from dataclasses import FrozenInstanceError
        variante = Relacion.de_datos(_relacion(VARIANTES)).variantes[0]
        with self.assertRaises(FrozenInstanceError):
            variante.valor = "otra"


class ReferenciaIndependienteTests(unittest.TestCase):
    """Desacuerdos con la referencia 0.7 (agy aislado), que el núcleo tenía mal."""

    CONDICION_ESTADO = ["==", ["campo", "m", "estado"], "pasaron"]

    def test_un_campo_ausente_levanta_aunque_otra_fila_ya_cumpla_en_cualquier_orden(self):
        medida = Medida.de_datos(_medida(["requiere", ["filas", "mutante", "m", self.CONDICION_ESTADO]],
                                         donde=None))
        for filas in ([FILA_CODIGO, FILA_MEDIDA], [FILA_MEDIDA, FILA_CODIGO]):
            with self.subTest(primero=filas[0]["tipo"]), self.assertRaises(ErrorDeAlgebra):
                medida.evaluar({"mutante": filas})

    def test_una_relacion_requerida_vacia_no_tapa_el_error_de_otra_condicion(self):
        requiere = ["requiere", "pieza", ["filas", "mutante", "m", self.CONDICION_ESTADO]]
        medida = Medida.de_datos(_medida(requiere, donde=None))
        with self.assertRaises(ErrorDeAlgebra):
            medida.evaluar({"pieza": [], "mutante": [FILA_MEDIDA]})
        self.assertEqual(medida.evaluar({"pieza": [], "mutante": [FILA_CODIGO]}).sin_evidencia, "pieza")


class SuperficieTests(unittest.TestCase):
    TEXTO = ("medida d.cond:\n"
             "    de mutante m\n"
             "    donde m.tipo == \"codigo\"\n"
             "    resumen contar(1)\n"
             "    umbral <= 0 segun contrato porque \"razón\"\n"
             "    requiere pieza\n"
             "    requiere mutante m donde m.tipo == \"codigo\"\n"
             "    ambito universal\n"
             "    alcance \"NO ve\"\n")

    def test_varias_lineas_requiere_se_juntan_en_orden_y_vuelven(self):
        datos = sintaxis.leer(self.TEXTO)
        self.assertEqual(datos[5], ["requiere", "pieza", ["filas", "mutante", "m", CONDICION]])
        self.assertEqual(datos[6], ["ambito", "universal"])
        self.assertEqual(datos[7], ["alcance", "NO ve"])
        self.assertEqual(sintaxis.leer(sintaxis.imprimir(datos)), datos)

    def test_una_sola_linea_con_condicion(self):
        texto = self.TEXTO.replace("    requiere pieza\n", "")
        datos = sintaxis.leer(texto)
        self.assertEqual(datos[5], ["requiere", ["filas", "mutante", "m", CONDICION]])
        self.assertEqual(sintaxis.leer(sintaxis.imprimir(datos)), datos)


def _relacion(variantes=None, comunes=None):
    comunes = comunes or [["campo", "id", "texto", "sin_unidad"], ["campo", "tipo", "texto", "sin_unidad"]]
    datos = ["relacion", "mutante", ["campos", *comunes]]
    if variantes is not None:
        datos.append(variantes)
    datos.append(["alcance", "no ve nada más"])
    return datos


VARIANTES = ["variantes", "tipo",
             ["variante", "medida", ["campo", "detecciones_conductuales", "entero", "sin_unidad"]],
             ["variante", "codigo", ["campo", "estado", "texto", "sin_unidad"]]]


class RelacionConVariantesTests(unittest.TestCase):
    def test_ida_y_vuelta_con_y_sin_variantes(self):
        for datos in (_relacion(VARIANTES), _relacion()):
            with self.subTest(len(datos)):
                self.assertEqual(Relacion.de_datos(datos).a_datos(), datos)

    def test_reglas_de_variantes(self):
        entero_tipo = [["campo", "id", "texto", "sin_unidad"], ["campo", "tipo", "entero", "sin_unidad"]]
        casos = {
            "discriminante que no es común": (["variantes", "clase", *VARIANTES[2:]], None),
            "discriminante que no es texto": (VARIANTES, entero_tipo),
            "sin variantes": (["variantes", "tipo"], None),
            "valor repetido": (["variantes", "tipo", VARIANTES[2], VARIANTES[2]], None),
            "valor vacío": (["variantes", "tipo", ["variante", "", ["campo", "x", "texto", "sin_unidad"]],
                             VARIANTES[3]], None),
            "variante sin campos": (["variantes", "tipo", ["variante", "medida"], VARIANTES[3]], None),
            "repite un campo común": (["variantes", "tipo",
                                       ["variante", "medida", ["campo", "id", "texto", "sin_unidad"]],
                                       VARIANTES[3]], None),
            "mismo nombre con otro tipo": (["variantes", "tipo",
                                            ["variante", "medida", ["campo", "n", "entero", "sin_unidad"]],
                                            ["variante", "codigo", ["campo", "n", "texto", "sin_unidad"]]], None),
            "campo repetido en una variante": (["variantes", "tipo",
                                                ["variante", "medida", ["campo", "n", "entero", "sin_unidad"],
                                                 ["campo", "n", "entero", "sin_unidad"]], VARIANTES[3]], None),
        }
        for nombre, (variantes, comunes) in casos.items():
            with self.subTest(nombre), self.assertRaises(RelacionMalDeclarada):
                Relacion.de_datos(_relacion(variantes, comunes))

    def test_el_mismo_nombre_en_dos_variantes_con_igual_tipo_se_acepta(self):
        variantes = ["variantes", "tipo",
                     ["variante", "medida", ["campo", "n", "entero", "sin_unidad"]],
                     ["variante", "codigo", ["campo", "n", "entero", "sin_unidad"]]]
        hechos = hechos_de_relaciones([Relacion.de_datos(_relacion(variantes))])
        self.assertEqual(sorted((f["campo"], f["variante"]) for f in hechos["campo_declarado"]),
                         [("id", ""), ("n", "codigo"), ("n", "medida"), ("tipo", "")])

    def test_hechos_de_una_relacion_con_y_sin_variantes(self):
        hechos = hechos_de_relaciones([Relacion.de_datos(_relacion(VARIANTES))])
        self.assertEqual(hechos["relacion_declarada"][0]["variantes"], 2)
        self.assertEqual({(f["campo"], f["variante"]) for f in hechos["campo_declarado"]},
                         {("id", ""), ("tipo", ""), ("detecciones_conductuales", "medida"),
                          ("estado", "codigo")})
        sin = hechos_de_relaciones([Relacion.de_datos(_relacion())])
        self.assertEqual(sin["relacion_declarada"][0]["variantes"], 0)


class MutanteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from nucleo.proyecto import Proyecto, catalogo_efectivo
        from oracle_metalenguaje.motor import registro_base
        cls.registro = registro_base()
        catalogo = catalogo_efectivo(Proyecto(RAIZ), registro=cls.registro)
        cls.medidas = (catalogo["proceso.test_con_mutante_que_lo_mata"],
                       catalogo["proceso.codigo_con_mutante_que_lo_mata"])

    def test_la_relacion_declarada_trae_los_campos_de_los_dos_productores(self):
        relacion = cargar(RAIZ / "relaciones" / "mutante.json")
        hechos = hechos_de_relaciones([relacion])["campo_declarado"]
        por_variante = {}
        for fila in hechos:
            por_variante.setdefault(fila["variante"], set()).add(fila["campo"])
        self.assertEqual(por_variante[""], {"id", "apunta_a", "cambio", "tipo"})
        self.assertEqual(por_variante["medida"], {"detecciones_conductuales", "rechazos_del_algebra"})
        self.assertEqual(por_variante["codigo"], set(FILA_CODIGO) - {"id", "apunta_a", "cambio", "tipo"})

    def test_cada_medida_mide_su_fila_sobre_una_evidencia_mezclada(self):
        for medida in self.medidas:
            with self.subTest(medida.id):
                v = medida.evaluar({"mutante": [FILA_MEDIDA, FILA_CODIGO]}, registro=self.registro)
                self.assertFalse(v.sin_evidencia)
                self.assertEqual(v.valor, 1)

    def test_con_filas_solo_del_otro_tipo_sale_sin_evidencia(self):
        otra = {"proceso.test_con_mutante_que_lo_mata": FILA_CODIGO,
                "proceso.codigo_con_mutante_que_lo_mata": FILA_MEDIDA}
        for medida in self.medidas:
            with self.subTest(medida.id):
                v = medida.evaluar({"mutante": [otra[medida.id]]}, registro=self.registro)
                self.assertTrue(v.sin_evidencia)
                self.assertFalse(v.ok)


if __name__ == "__main__":
    unittest.main()
