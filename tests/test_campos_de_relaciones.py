"""Tests directos del lector de `CAMPOS_DE_RELACIONES`, de `campo_leido` y de `evaluar_conjunto` (0.22.0).

Reescritos por Claude en la revisión: los que acompañaban la entrega usaban una API que no existe
(ver `vault-kb/estudios/0.22.0-campos/REVISION-CLAUDE.md`). La conducta desde afuera la fija
`tests/test_campos_revision.py`; éstos fijan las ramas que la mutación necesita ver.
"""

import tempfile
import textwrap
import unittest
from pathlib import Path

from nucleo.campo_leido import _extraer_lecturas_de_arbol, hechos_de_campos_leidos
from nucleo.medida import Medida, evaluar_conjunto
from nucleo.relacion import Relacion, RelacionMalDeclarada, campos_de_relaciones_declarados


def _raiz_con(**archivos) -> tempfile.TemporaryDirectory:
    td = tempfile.TemporaryDirectory(prefix="oracle-campos-")
    nucleo = Path(td.name) / "nucleo"
    nucleo.mkdir()
    for nombre, fuente in archivos.items():
        (nucleo / f"{nombre}.py").write_text(textwrap.dedent(fuente), encoding="utf-8")
    return td


class LectorDeCamposTests(unittest.TestCase):
    VALIDO = """
        RELACIONES_DE_X = frozenset({"x"})
        CAMPOS_DE_RELACIONES = {"x": ("a", "b")}
    """

    def test_lee_los_campos_sin_importar_el_modulo(self):
        with _raiz_con(uno=textwrap.dedent(self.VALIDO) + "\nraise SystemExit('no se importa')\n") as td:
            self.assertEqual(campos_de_relaciones_declarados(Path(td)), {"x": ("a", "b")})

    def test_cada_forma_invalida_falla_cerrado(self):
        casos = {
            "no es un mapa": {"uno": 'RELACIONES_DE_X = frozenset({"x"})\nCAMPOS_DE_RELACIONES = [("x", ("a",))]\n'},
            "no es tupla": {"uno": 'RELACIONES_DE_X = frozenset({"x"})\nCAMPOS_DE_RELACIONES = {"x": ["a"]}\n'},
            "campo que no es texto": {"uno": 'RELACIONES_DE_X = frozenset({"x"})\nCAMPOS_DE_RELACIONES = {"x": ("a", 1)}\n'},
            "campo vacío": {"uno": 'RELACIONES_DE_X = frozenset({"x"})\nCAMPOS_DE_RELACIONES = {"x": ("a", " ")}\n'},
            "campo repetido": {"uno": 'RELACIONES_DE_X = frozenset({"x"})\nCAMPOS_DE_RELACIONES = {"x": ("a", "a")}\n'},
            "clave que no es texto": {"uno": 'RELACIONES_DE_X = frozenset({"x"})\nCAMPOS_DE_RELACIONES = {1: ("a",)}\n'},
            "relación en dos archivos": {"uno": self.VALIDO, "dos": self.VALIDO},
            "campos de una relación ajena": {"uno": 'RELACIONES_DE_X = frozenset({"x"})\nCAMPOS_DE_RELACIONES = {"x": ("a",), "y": ("b",)}\n'},
            "relación sin campos": {"uno": 'RELACIONES_DE_X = frozenset({"x", "z"})\nCAMPOS_DE_RELACIONES = {"x": ("a",)}\n'},
        }
        for nombre, archivos in casos.items():
            with self.subTest(nombre), _raiz_con(**archivos) as td, self.assertRaises(RelacionMalDeclarada):
                campos_de_relaciones_declarados(Path(td))

    def test_una_clave_que_no_es_texto_se_rechaza_por_su_forma(self):
        """Terminaría rechazada igual por «relación ajena»; el mensaje dice cuál fue el error."""
        for clave in ("1", '" "'):
            fuente = f'RELACIONES_DE_X = frozenset({{"x"}})\nCAMPOS_DE_RELACIONES = {{"x": ("a",), {clave}: ("b",)}}\n'
            with self.subTest(clave=clave), _raiz_con(uno=fuente) as td:
                with self.assertRaisesRegex(RelacionMalDeclarada, "mapa literal"):
                    campos_de_relaciones_declarados(Path(td))

    def test_un_directorio_o_un_enlace_con_nombre_de_modulo_no_se_leen(self):
        with _raiz_con(uno=self.VALIDO) as td:
            nucleo = Path(td) / "nucleo"
            (Path(td) / "ajeno.py").write_text("CAMPOS_DE_RELACIONES = {1: 2}\n", encoding="utf-8")
            (nucleo / "enlace.py").symlink_to(Path(td) / "ajeno.py")
            (nucleo / "carpeta.py").mkdir()
            self.assertEqual(campos_de_relaciones_declarados(Path(td)), {"x": ("a", "b")})


def _medida(mid, fuente, donde, requiere=None):
    datos = ["medida", mid, ["desde", fuente, ["donde", donde]], ["resumen", "contar", 1],
             ["umbral", "<=", 0, "razón"]]
    if requiere:
        datos.append(requiere)
    datos.append(["alcance", "NO ve"])
    return Medida.de_datos(datos)


def _item() -> Relacion:
    # Dentro de una función: una mutación que rompe `Relacion.de_datos` tiene que matar tests, no
    # impedir que el módulo se importe (eso el arnés lo cuenta como error, no como muerte).
    return Relacion.de_datos(["relacion", "item",
    ["campos", ["campo", "id", "texto", "sin_unidad"], ["campo", "tipo", "texto", "sin_unidad"]],
    ["variantes", "tipo", ["variante", "medida", ["campo", "detecciones", "entero", "sin_unidad"]]],
    ["alcance", "NO ve nada más"]])


class CampoLeidoTests(unittest.TestCase):
    def filas(self, medida):
        return [(f["relacion"], f["campo"], f["origen"], f["existe"])
                for f in hechos_de_campos_leidos([medida], {"item": _item()})["campo_leido"]]

    def test_declarada_comun_de_variante_e_inexistente(self):
        donde = ["y", ["==", ["campo", "i", "id"], "a"],
                 ["y", ["==", ["campo", "i", "detecciones"], 0], ["==", ["campo", "i", "nada"], 1]]]
        self.assertEqual(self.filas(_medida("d.item", ["de", "item", "i"], donde)),
                         [("item", "id", "declarada", True), ("item", "detecciones", "declarada", True),
                          ("item", "nada", "declarada", False)])

    def test_relacion_del_lenguaje_y_sin_declarar(self):
        lenguaje = _medida("d.leng", ["de", "campo_declarado", "c"],
                           ["y", ["==", ["campo", "c", "tiene_unidad"], False], ["==", ["campo", "c", "inventado"], 1]])
        self.assertEqual(self.filas(lenguaje), [("campo_declarado", "tiene_unidad", "lenguaje", True),
                                                ("campo_declarado", "inventado", "lenguaje", False)])
        propia = _medida("d.propia", ["de", "pieza_propia", "p"], ["==", ["campo", "p", "alto"], 3])
        self.assertEqual(self.filas(propia), [("pieza_propia", "alto", "sin_declarar", False)])
        # El álgebra acepta un alias que ninguna fuente liga; la lectura queda sin relación.
        suelta = _medida("d.suelta", ["de", "item", "i"], ["==", ["campo", "z", "id"], 1])
        self.assertEqual(self.filas(suelta), [("", "id", "sin_declarar", False)])

    def test_una_lectura_en_la_condicion_de_requiere_resuelve_su_alias(self):
        medida = _medida("d.req", ["de", "item", "i"], ["==", ["campo", "i", "id"], "a"],
                         ["requiere", ["filas", "item", "j", ["==", ["campo", "j", "tipo"], "medida"]]])
        self.assertIn(("item", "tipo", "declarada", True), self.filas(medida))

    def test_hecho_y_col_no_son_lecturas_de_campo(self):
        arbol = ["y", ["==", ["hecho", "i"], 1], ["==", ["col", "total"], 2], ["==", ["campo", "i", "id"], 3]]
        self.assertEqual(list(_extraer_lecturas_de_arbol(arbol)), [("i", "id")])


class HechosDeCasosTests(unittest.TestCase):
    def test_un_caso_que_su_medida_no_puede_juzgar_nunca_se_pone_como_debe(self):
        from nucleo.marco import hechos_de_casos
        mala = _medida("d.mala", ["de", "item", "i"], ["==", ["campo", "i", "nada"], "x"])
        casos = [{"id": etiqueta, "medida": "d.mala", "etiqueta": etiqueta, "evidencia": {"item": [{"id": "a"}]}}
                 for etiqueta in ("falso_verde", "verde_correcto")]
        filas = {f["id"]: f for f in hechos_de_casos({"d.mala": mala}, casos)["caso"]}
        for etiqueta, fila in filas.items():
            with self.subTest(etiqueta):
                self.assertNotEqual(fila["dio_ok"], fila["esperado_ok"])


class EvaluarConjuntoTests(unittest.TestCase):
    def test_una_medida_que_no_puede_juzgar_no_corta_a_las_demas(self):
        buena = _medida("d.buena", ["de", "item", "i"], ["==", ["campo", "i", "id"], "x"])
        mala = _medida("d.mala", ["de", "item", "i"], ["==", ["campo", "i", "nada"], "x"])
        informe = evaluar_conjunto([mala, buena], {"item": [{"id": "a"}]})
        self.assertEqual([v.id for v in informe.veredictos], ["d.buena"])
        self.assertEqual([mid for mid, _ in informe.no_juzgaron], ["d.mala"])
        self.assertIn("ausente", informe.no_juzgaron[0][1])
        self.assertFalse(informe.ok)


if __name__ == "__main__":
    unittest.main()
