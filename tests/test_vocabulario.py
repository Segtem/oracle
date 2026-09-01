"""Los vocabularios cerrados declaran su significado, y el manual es una vista de eso."""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo.caso import DETECCIONES, ETIQUETAS, PROCEDENCIAS  # noqa: E402
from nucleo.marco import RELACIONES_DEL_LENGUAJE  # noqa: E402
from nucleo.vocabulario import (OPERADORES, ORIGENES_DE_UMBRAL,  # noqa: E402
                                RELACIONES_EXPLICADAS, opciones)


CERRADOS = {
    "operadores": OPERADORES,
    "segun": ORIGENES_DE_UMBRAL,
    "etiqueta": ETIQUETAS,
    "procedencia": PROCEDENCIAS,
    "como_se_detecto": DETECCIONES,
    "relaciones": RELACIONES_EXPLICADAS,
}


class OpcionesTests(unittest.TestCase):

    def test_una_linea_por_opcion_con_su_sentido(self) -> None:
        salida = opciones({"beta": "lo segundo", "alfa": "lo primero"})
        self.assertEqual(salida, "        alfa: lo primero\n        beta: lo segundo")

    def test_van_ordenadas_y_no_en_el_orden_de_declaracion(self) -> None:
        """Un vocabulario se lee para buscar un nombre. Si el orden es el de declaración, el
        orden lo decide quien editó último y el lector tiene que barrer la lista entera."""
        salida = opciones({"zeta": "z", "alfa": "a", "mu": "m"})
        self.assertEqual([l.split(":")[0].strip() for l in salida.splitlines()],
                         ["alfa", "mu", "zeta"])

    def test_no_pierde_ninguna_opcion(self) -> None:
        for nombre, vocabulario in CERRADOS.items():
            with self.subTest(vocabulario=nombre):
                salida = opciones(vocabulario)
                self.assertEqual(len(salida.splitlines()), len(vocabulario))
                for opcion in vocabulario:
                    self.assertIn(f"{opcion}: ", salida)

    def test_la_sangria_es_de_ocho_espacios(self) -> None:
        """Las opciones cuelgan de un mensaje de error que ya viene indentado; sin sangría se
        leen como si fueran errores nuevos, uno por línea."""
        for linea in opciones(ETIQUETAS).splitlines():
            self.assertTrue(linea.startswith(" " * 8), linea)
            self.assertFalse(linea.startswith(" " * 9), linea)


class TodaOpcionDeclaraSuSentidoTests(unittest.TestCase):
    """La afirmación que sostiene el manual: no hay nombre sin explicación."""

    def test_ninguna_opcion_queda_sin_prosa(self) -> None:
        for nombre, vocabulario in CERRADOS.items():
            for opcion, sentido in vocabulario.items():
                with self.subTest(vocabulario=nombre, opcion=opcion):
                    self.assertGreater(len(sentido.split()), 5,
                                       f"«{opcion}» se explica con menos de seis palabras")
                    # No «no contiene el nombre»: «de» es también una preposición, y la
                    # prosa de «de» habla de lo que «de» trajo. Lo que no puede es ABRIR con
                    # su propio nombre, que es la forma en que una definición no define.
                    self.assertFalse(sentido.split()[0].strip(",.:«»") == opcion,
                                     f"«{opcion}» se explica abriendo con su propio nombre")

    def test_los_nombres_son_ascii_porque_son_lo_que_se_tipea(self) -> None:
        for nombre, vocabulario in CERRADOS.items():
            for opcion in vocabulario:
                with self.subTest(vocabulario=nombre, opcion=opcion):
                    if nombre == "etiqueta" and opcion == "deuda_de_diseño":
                        continue  # anterior a la regla; renombrarlo rompería el corpus
                    self.assertTrue(opcion.isascii(), opcion)


class LasRelacionesExplicadasSonLasQueSeEmitenTests(unittest.TestCase):

    def test_ninguna_relacion_del_lenguaje_queda_sin_explicar(self) -> None:
        """El manual las muestra; si aparece una relación nueva y nadie la explica, el manual la
        omite en silencio. Acá se rompe, que es la única forma de que se note."""
        self.assertEqual(set(RELACIONES_EXPLICADAS), set(RELACIONES_DEL_LENGUAJE))


class LosOperadoresSonLosDelAlgebraTests(unittest.TestCase):

    @staticmethod
    def _literales_comparados_en(ruta: Path) -> set[str]:
        """Los textos contra los que el álgebra compara la cabeza de un paso.

        Se lee del AST y no de una lista escrita al lado: una lista al lado es una copia, y una
        copia se despega. Trae ruido —cualquier `x[0] == "…"`—, que para esta dirección no
        molesta: lo que se afirma es que los operadores del manual están adentro.
        """
        def es_cabeza(n: ast.AST) -> bool:
            return (isinstance(n, ast.Name) and n.id == "op") or (
                isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)
                and n.slice.value == 0)

        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        salida: set[str] = set()
        for n in ast.walk(arbol):
            if not (isinstance(n, ast.Compare) and len(n.ops) == 1
                    and isinstance(n.ops[0], (ast.Eq, ast.NotEq))):
                continue
            for a, b in ((n.left, n.comparators[0]), (n.comparators[0], n.left)):
                if es_cabeza(a) and isinstance(b, ast.Constant) and isinstance(b.value, str):
                    salida.add(b.value)
        return salida

    def test_todo_operador_nombrado_lo_reconoce_el_algebra(self) -> None:
        reconocidos = self._literales_comparados_en(RAIZ / "nucleo" / "algebra.py")
        self.assertLessEqual(set(OPERADORES), reconocidos,
                             "el manual nombra un operador que el álgebra no despacha")

    def test_el_lector_del_ast_encuentra_los_que_ya_se_sabe_que_estan(self) -> None:
        """Sin esto, un lector roto que devuelve todo haría pasar el test de arriba."""
        reconocidos = self._literales_comparados_en(RAIZ / "nucleo" / "algebra.py")
        self.assertIn("agrupar", reconocidos)
        self.assertNotIn("mengano", reconocidos)


class ElUmbralUsaEsteVocabularioTests(unittest.TestCase):

    def test_medida_valida_segun_contra_el_mismo_registro(self) -> None:
        from nucleo import medida
        self.assertIs(medida.ORIGENES_DE_UMBRAL, ORIGENES_DE_UMBRAL)


if __name__ == "__main__":
    unittest.main()
