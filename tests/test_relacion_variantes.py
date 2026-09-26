"""Pruebas para relaciones con variantes y catálogo con mutante (0.21.0).

Verifica:
- Carga y round-trip de relaciones con y sin variantes (`a_datos`).
- Rechazo de cada regla estructural y semántica de variantes:
  * discriminante que no es campo común
  * discriminante que no es de tipo texto
  * nodo variantes vacío (sin variantes)
  * valor de variante duplicado o vacío
  * variante sin campos
  * variante que repite un campo común
  * campo repetido dentro de una misma variante
  * mismo nombre de campo en dos variantes con tipo o unidad discordante
- Generación de hechos `relacion_declarada` (columna `variantes`) y `campo_declarado` (columna `variante`).
- Mismo nombre de campo en dos variantes con idéntico tipo y unidad se acepta.
- Derivación de unidad de un campo de variante en `nucleo/unidad.py`.
- Puntos ciegos en `tools/medida.py` considerando `todos_los_campos`.
- Carga válida de `relaciones/mutante.relacion`.
- Evaluación de las medidas de `catalogos/proceso/` sobre evidencia de `mutante`:
  * Evidencia mezclada (medida y código) mide su fila sin levantar.
  * Evidencia sólo del otro tipo concluye SIN EVIDENCIA.
"""

import unittest
from pathlib import Path

from nucleo.medida import Medida
from nucleo.relacion import Campo, Relacion, RelacionMalDeclarada, cargar, hechos_de_relaciones
from nucleo.unidad import derivar_unidad_nodo

RAIZ = Path(__file__).resolve().parents[1]

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

VARIANTES_MUTANTE = [
    "variantes", "tipo",
    ["variante", "medida",
     ["campo", "detecciones_conductuales", "entero", "sin_unidad"],
     ["campo", "rechazos_del_algebra", "entero", "sin_unidad"]],
    ["variante", "codigo",
     ["campo", "estado", "texto", "sin_unidad"],
     ["campo", "murio", "booleano", "sin_unidad"]],
]


def _crear_relacion(variantes=None, comunes=None):
    comunes = comunes or [
        ["campo", "id", "texto", "sin_unidad"],
        ["campo", "tipo", "texto", "sin_unidad"],
    ]
    datos = ["relacion", "mutante", ["campos", *comunes]]
    if variantes is not None:
        datos.append(variantes)
    datos.append(["alcance", "no ve nada más"])
    return datos


class RelacionVariantesReglasTests(unittest.TestCase):
    def test_roundtrip_con_y_sin_variantes(self):
        for datos in (_crear_relacion(VARIANTES_MUTANTE), _crear_relacion()):
            with self.subTest(tiene_variantes=len(datos) == 5):
                rel = Relacion.de_datos(datos)
                self.assertEqual(rel.a_datos(), datos)

    def test_rechazo_discriminante_no_comun(self):
        variantes = ["variantes", "no_existe",
                     ["variante", "v1", ["campo", "x", "texto", "sin_unidad"]]]
        with self.assertRaises(RelacionMalDeclarada):
            Relacion.de_datos(_crear_relacion(variantes))

    def test_rechazo_discriminante_no_texto(self):
        comunes = [["campo", "id", "texto", "sin_unidad"], ["campo", "tipo", "entero", "sin_unidad"]]
        variantes = ["variantes", "tipo",
                     ["variante", "v1", ["campo", "x", "texto", "sin_unidad"]]]
        with self.assertRaises(RelacionMalDeclarada):
            Relacion.de_datos(_crear_relacion(variantes, comunes))

    def test_rechazo_sin_variantes_declaradas(self):
        variantes = ["variantes", "tipo"]
        with self.assertRaises(RelacionMalDeclarada):
            Relacion.de_datos(_crear_relacion(variantes))

    def test_rechazo_valor_variante_repetido(self):
        v = ["variante", "medida", ["campo", "x", "texto", "sin_unidad"]]
        variantes = ["variantes", "tipo", v, v]
        with self.assertRaises(RelacionMalDeclarada):
            Relacion.de_datos(_crear_relacion(variantes))

    def test_rechazo_valor_variante_vacio(self):
        variantes = ["variantes", "tipo", ["variante", "   ", ["campo", "x", "texto", "sin_unidad"]]]
        with self.assertRaises(RelacionMalDeclarada):
            Relacion.de_datos(_crear_relacion(variantes))

    def test_rechazo_variante_sin_campos(self):
        variantes = ["variantes", "tipo", ["variante", "medida"]]
        with self.assertRaises(RelacionMalDeclarada):
            Relacion.de_datos(_crear_relacion(variantes))

    def test_rechazo_variante_repite_campo_comun(self):
        variantes = ["variantes", "tipo",
                     ["variante", "medida", ["campo", "id", "texto", "sin_unidad"]]]
        with self.assertRaises(RelacionMalDeclarada):
            Relacion.de_datos(_crear_relacion(variantes))

    def test_rechazo_campo_repetido_en_misma_variante(self):
        variantes = ["variantes", "tipo",
                     ["variante", "medida",
                      ["campo", "x", "texto", "sin_unidad"],
                      ["campo", "x", "texto", "sin_unidad"]]]
        with self.assertRaises(RelacionMalDeclarada):
            Relacion.de_datos(_crear_relacion(variantes))

    def test_rechazo_mismo_nombre_en_distintas_variantes_con_distinto_tipo(self):
        variantes = ["variantes", "tipo",
                     ["variante", "medida", ["campo", "comun_var", "entero", "sin_unidad"]],
                     ["variante", "codigo", ["campo", "comun_var", "texto", "sin_unidad"]]]
        with self.assertRaises(RelacionMalDeclarada):
            Relacion.de_datos(_crear_relacion(variantes))

    def test_rechazo_mismo_nombre_en_distintas_variantes_con_distinta_unidad(self):
        variantes = ["variantes", "tipo",
                     ["variante", "medida", ["campo", "peso", "flotante", "kg"]],
                     ["variante", "codigo", ["campo", "peso", "flotante", "g"]]]
        with self.assertRaises(RelacionMalDeclarada):
            Relacion.de_datos(_crear_relacion(variantes))

    def test_mismo_nombre_en_dos_variantes_con_igual_tipo_y_unidad_se_acepta(self):
        variantes = ["variantes", "tipo",
                     ["variante", "medida", ["campo", "peso", "flotante", "kg"]],
                     ["variante", "codigo", ["campo", "peso", "flotante", "kg"]]]
        rel = Relacion.de_datos(_crear_relacion(variantes))
        hechos = hechos_de_relaciones([rel])
        campos = [(f["campo"], f["variante"]) for f in hechos["campo_declarado"]]
        self.assertIn(("peso", "medida"), campos)
        self.assertIn(("peso", "codigo"), campos)


class RelacionVariantesHechosTests(unittest.TestCase):
    def test_hechos_relacion_y_campos(self):
        rel = Relacion.de_datos(_crear_relacion(VARIANTES_MUTANTE))
        hechos = hechos_de_relaciones([rel])

        self.assertEqual(hechos["relacion_declarada"][0]["variantes"], 2)
        campos_por_variante = {}
        for fila in hechos["campo_declarado"]:
            campos_por_variante.setdefault(fila["variante"], set()).add(fila["campo"])

        self.assertEqual(campos_por_variante[""], {"id", "tipo"})
        self.assertEqual(campos_por_variante["medida"], {"detecciones_conductuales", "rechazos_del_algebra"})
        self.assertEqual(campos_por_variante["codigo"], {"estado", "murio"})

    def test_relacion_sin_variantes_hechos(self):
        rel = Relacion.de_datos(_crear_relacion())
        hechos = hechos_de_relaciones([rel])
        self.assertEqual(hechos["relacion_declarada"][0]["variantes"], 0)
        for fila in hechos["campo_declarado"]:
            self.assertEqual(fila["variante"], "")


class RelacionVariantesUnidadesYPuntosCiegosTests(unittest.TestCase):
    def test_derivar_unidad_nodo_encuentra_campo_de_variante(self):
        rel_vehiculo = Relacion(
            nombre="vehiculo",
            campos=(Campo("id", "texto", "sin_unidad"), Campo("tipo", "texto", "sin_unidad")),
            alcance="alcance vehiculo",
            variantes=(
                rel_variante := Relacion.de_datos([
                    "relacion", "vehiculo",
                    ["campos", ["campo", "id", "texto", "sin_unidad"], ["campo", "tipo", "texto", "sin_unidad"]],
                    ["variantes", "tipo",
                     ["variante", "auto", ["campo", "potencia", "flotante", "hp"]],
                     ["variante", "bici", ["campo", "cambios", "entero", "sin_unidad"]]],
                    ["alcance", "vehiculos"],
                ]).variantes
            ),
            discriminante="tipo",
        )
        relaciones = {"vehiculo": rel_vehiculo}
        unidad_potencia = derivar_unidad_nodo(
            ["campo", "v", "potencia"],
            alias_relaciones={"v": "vehiculo"},
            relaciones=relaciones,
            registro={},
            relaciones_lenguaje=frozenset(),
        )
        self.assertEqual(unidad_potencia, "hp")

    def test_todos_los_campos_contiene_comunes_y_variantes(self):
        rel = Relacion.de_datos(_crear_relacion(VARIANTES_MUTANTE))
        nombres = [c.nombre for c in rel.todos_los_campos]
        self.assertEqual(
            nombres,
            ["id", "tipo", "detecciones_conductuales", "rechazos_del_algebra", "estado", "murio"],
        )


class MutanteCatalogoProcesoTests(unittest.TestCase):
    def test_archivo_mutante_json_es_valido(self):
        ruta = RAIZ / "relaciones" / "mutante.relacion"
        self.assertTrue(ruta.exists(), f"no existe {ruta}")
        relacion = cargar(ruta)
        self.assertEqual(relacion.nombre, "mutante")
        self.assertEqual(relacion.discriminante, "tipo")
        self.assertEqual(len(relacion.variantes), 2)
        nombres_comunes = {c.nombre for c in relacion.campos}
        self.assertEqual(nombres_comunes, {"id", "apunta_a", "cambio", "tipo"})

    def test_medidas_proceso_sobre_evidencia_mutante(self):
        from nucleo.proyecto import Proyecto, catalogo_efectivo
        from oracle_metalenguaje.motor import registro_base

        registro = registro_base()
        catalogo = catalogo_efectivo(Proyecto(RAIZ), registro=registro)
        m_test = catalogo["proceso.test_con_mutante_que_lo_mata"]
        m_codigo = catalogo["proceso.codigo_con_mutante_que_lo_mata"]

        # Evidencia mezclada: ambas miden su fila sin levantar
        v_test = m_test.evaluar({"mutante": [FILA_MEDIDA, FILA_CODIGO]}, registro=registro)
        self.assertFalse(v_test.sin_evidencia)
        self.assertEqual(v_test.valor, 1)

        v_cod = m_codigo.evaluar({"mutante": [FILA_MEDIDA, FILA_CODIGO]}, registro=registro)
        self.assertFalse(v_cod.sin_evidencia)
        self.assertEqual(v_cod.valor, 1)

        # Evidencia con sólo filas del otro tipo: salen SIN EVIDENCIA
        v_test_sin = m_test.evaluar({"mutante": [FILA_CODIGO]}, registro=registro)
        self.assertTrue(v_test_sin.sin_evidencia)
        self.assertFalse(v_test_sin.ok)

        v_cod_sin = m_codigo.evaluar({"mutante": [FILA_MEDIDA]}, registro=registro)
        self.assertTrue(v_cod_sin.sin_evidencia)
        self.assertFalse(v_cod_sin.ok)


if __name__ == "__main__":
    unittest.main()
