"""El informe de `tools/diferencial.py`: qué marca, qué cuenta y con qué código sale.

`comparar_dominio` —lo que decide— tenía tests; lo que se IMPRIME y el código de salida, casi
ninguno. Medido al declarar el archivo como custodia (2026-09-16): 57 mutantes y 32 sobrevivientes,
todos acá. Un informe que dice ✓ cuando hubo un desacuerdo, o que sale 0 con fallas, es el falso
verde que el diferencial existe para evitar, contado por su propio verificador.
"""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from nucleo.fixtures import Fixture
from nucleo.medida import Medida
from tools import diferencial


def _medida(mid: str = "d.sin_malos") -> Medida:
    return Medida.de_datos(
        ["ninguno", mid, "hecho", "h", ["==", ["campo", "h", "malo"], True],
         "razón", "contrato", "universal", "NO ve"])


def _escenarios(*pares) -> list[dict]:
    """Un escenario por (malo, referencia_ok, guardado): lo que trae, lo que dice la referencia y
    lo que Oracle guardó al generar."""
    return [{"id": f"e{i}", "evidencia": {"hecho": [{"malo": malo}]}, "referencia_ok": ref,
             "oracle_al_generar": {"global_ok": guardado,
                                   "por_medida": {"d.sin_malos": guardado}}}
            for i, (malo, ref, guardado) in enumerate(pares)]


def _dominio(escenarios: list[dict]) -> dict:
    return {"esquema": "oracle.diferencial/v1", "origen": "prueba", "mundos": len(escenarios),
            "medidas": ["d.sin_malos"], "escenarios": escenarios}


def _grupos(casos: list[dict], mid: str = "d.sin_malos") -> dict:
    return {"esquema": "oracle.diferencial/v1", "origen": "prueba", "mundos": len(casos),
            "grupos": {mid: casos}}


class InformeTests(unittest.TestCase):
    def _correr(self, fixtures, *, catalogo=None, frescura=(), fallas_de_carga=(),
                estructura=()) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as d:
            carpeta = Path(d) / "diferencial"
            carpeta.mkdir()
            objetos = []
            for i, datos in enumerate(fixtures):
                ruta = carpeta / f"f{i}.json"
                ruta.write_text("{}", encoding="utf-8")
                objetos.append(Fixture(ruta, datos))
            proy = SimpleNamespace(raiz=Path(d), diferencial=carpeta)
            catalogo = {"d.sin_malos": _medida()} if catalogo is None else catalogo
            with mock.patch.multiple(
                    diferencial,
                    problemas_estructura=lambda p, carpetas: list(estructura),
                    cargar_fixtures=lambda rutas: (objetos, list(fallas_de_carga)),
                    cargar_catalogo=lambda *a, **k: catalogo,
                    catalogos_a_cargar=lambda p: [],
                    macros_del_proyecto=lambda p: None,
                    revisar_frescura=lambda datos, raiz, cat: list(frescura)):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    rc = diferencial._ejecutar(proy)
        return rc, salida.getvalue()

    # ---- lo que corta antes de comparar ----

    def test_un_proyecto_sin_la_estructura_sale_1(self) -> None:
        rc, salida = self._correr([], estructura=["falta catalogos/"])
        self.assertIs(rc, 1)
        self.assertIn("PROYECTO INVÁLIDO — falta catalogos/", salida)

    def test_sin_fixtures_sale_1_y_lo_dice(self) -> None:
        rc, salida = self._correr([])
        self.assertIs(rc, 1)
        self.assertIn("no hay fixtures en diferencial/", salida)

    def test_un_fixture_ilegible_sale_1_y_lista_hasta_veinte_problemas(self) -> None:
        fallas = [f"problema {i}" for i in range(25)]
        rc, salida = self._correr([_dominio(_escenarios((False, True, True)))],
                                  fallas_de_carga=fallas)
        self.assertIs(rc, 1)
        self.assertIn("DIFERENCIAL ✗ — 25 problema(s) de fixture", salida)
        self.assertIn("  · problema 19", salida)
        self.assertNotIn("problema 20", salida)

    def test_un_fixture_vencido_no_se_compara_y_hace_fallar(self) -> None:
        rc, salida = self._correr([_dominio(_escenarios((False, True, True)))],
                                  frescura=["cambió catalogo"])
        self.assertIs(rc, 1)
        self.assertIn("✗ fixture vencido · 1 cambio(s) de procedencia", salida)
        self.assertIn("f0.json: cambió catalogo", salida)
        self.assertNotIn("acuerdo global", salida)

    # ---- escenarios ----

    def test_un_dominio_en_acuerdo_sale_0_con_sus_cuentas(self) -> None:
        rc, salida = self._correr([_dominio(_escenarios((False, True, True),
                                                        (True, False, False)))])
        self.assertIs(rc, 0)
        self.assertIn("✓ acuerdo global: 2 escenarios (1 verdes / 1 rojos) · 0 desacuerdos", salida)
        self.assertIn("✓ estabilidad individual: 1 medidas × 2 escenarios · 0 cambios", salida)
        self.assertIn("DIFERENCIAL ✓ — 2 acuerdos globales con referencias independientes · "
                      "2 veredictos individuales estables", salida)

    def test_un_desacuerdo_global_marca_x_y_sale_1(self) -> None:
        """La referencia dice verde y las medidas dicen rojo."""
        rc, salida = self._correr([_dominio(_escenarios((True, True, False),
                                                        (False, False, False)))])
        self.assertIs(rc, 1)
        self.assertIn("✗ acuerdo global: 2 escenarios (1 verdes / 1 rojos) · 2 desacuerdos", salida)
        self.assertIn("f0.json[e0]: las medidas y la referencia no coinciden", salida)

    def test_un_cambio_individual_marca_x_aunque_el_global_coincida(self) -> None:
        rc, salida = self._correr([_dominio(_escenarios((False, True, False)))])
        self.assertIs(rc, 1)
        self.assertIn("✓ acuerdo global", salida)
        self.assertIn("✗ estabilidad individual: 1 medidas × 1 escenarios · 1 cambios", salida)
        self.assertIn("f0.json[e0].d.sin_malos: veredicto individual cambió False →", salida)

    def test_una_falla_del_fixture_marca_x_en_las_dos_lineas(self) -> None:
        """Una medida que el fixture reclama y no existe no deja nada comparado: ninguna de las dos
        líneas puede decir ✓."""
        rc, salida = self._correr([_dominio(_escenarios((False, True, True)))], catalogo={})
        self.assertIs(rc, 1)
        self.assertIn("✗ acuerdo global", salida)
        self.assertIn("✗ estabilidad individual", salida)
        self.assertIn("reclama medidas que no están", salida)

    def test_lista_hasta_cinco_desacuerdos_y_cinco_cambios_por_fixture(self) -> None:
        pares = [(True, True, True)] * 7
        rc, salida = self._correr([_dominio(_escenarios(*pares))])
        self.assertIs(rc, 1)
        self.assertEqual(salida.count("las medidas y la referencia no coinciden"), 5)
        self.assertEqual(salida.count("veredicto individual cambió"), 5)
        self.assertIn("DIFERENCIAL ✗ — 10 desacuerdo(s)", salida)

    def test_el_resumen_final_lista_hasta_veinte_fallas(self) -> None:
        fixtures = [_dominio(_escenarios(*[(True, True, True)] * 7)) for _ in range(3)]
        rc, salida = self._correr(fixtures)
        self.assertIs(rc, 1)
        self.assertIn("DIFERENCIAL ✗ — 30 desacuerdo(s)", salida)
        resumen = salida.split("DIFERENCIAL ✗ — 30 desacuerdo(s)")[1]
        self.assertEqual(resumen.count("  · "), 20)

    # ---- grupos ----

    def test_un_grupo_en_acuerdo_cuenta_sus_casos(self) -> None:
        casos = [{"evidencia": {"hecho": [{"malo": False}]}, "esperado_ok": True},
                 {"evidencia": {"hecho": [{"malo": True}]}, "esperado_ok": False}]
        rc, salida = self._correr([_grupos(casos)])
        self.assertIs(rc, 0)
        self.assertIn("✓ d.sin_malos", salida)
        self.assertIn("2 casos (1 verdes / 1 rojos) · 0 desacuerdos", salida)
        self.assertIn("DIFERENCIAL ✓ — 2 veredictos individuales estables", salida)
        self.assertNotIn("acuerdos globales", salida)

    def test_un_grupo_en_desacuerdo_marca_x_y_lista_hasta_cinco(self) -> None:
        casos = [{"evidencia": {"hecho": [{"malo": True}]}, "esperado_ok": True}] * 7
        rc, salida = self._correr([_grupos(casos)])
        self.assertIs(rc, 1)
        self.assertIn("✗ d.sin_malos", salida)
        self.assertIn("7 casos (7 verdes / 0 rojos) · 7 desacuerdos", salida)
        self.assertEqual(salida.count("la referencia esperaba ok=True"), 5)

    def test_un_grupo_que_reclama_una_medida_que_no_esta_falla(self) -> None:
        casos = [{"evidencia": {"hecho": [{"malo": False}]}, "esperado_ok": True}]
        rc, salida = self._correr([_grupos(casos, mid="d.otra")])
        self.assertIs(rc, 1)
        self.assertIn("d.otra: el fixture la reclama y no está en el catálogo", salida)

    def test_una_evaluacion_que_levanta_en_un_grupo_marca_x(self) -> None:
        casos = [{"evidencia": {"hecho": [{"otro": 1}]}, "esperado_ok": True}]
        rc, salida = self._correr([_grupos(casos)])
        self.assertIs(rc, 1)
        self.assertIn("✗ d.sin_malos", salida)
        self.assertIn("error al evaluar", salida)


class MainTests(unittest.TestCase):
    def test_sin_proyecto_resuelto_sale_1(self) -> None:
        with mock.patch.object(diferencial, "resolver_cli", return_value=None):
            self.assertIs(diferencial.main([]), 1)

    def test_escalares_no_confiadas_sale_1_y_lo_dice(self) -> None:
        proy = SimpleNamespace()
        salida = io.StringIO()
        error = diferencial.EscalaresNoConfiables("hay un escalares.py")
        with mock.patch.object(diferencial, "resolver_cli", return_value=proy), \
                mock.patch.object(diferencial, "escalares_del_proyecto", side_effect=error), \
                redirect_stdout(salida):
            rc = diferencial.main([])
        self.assertIs(rc, 1)
        self.assertIn("ESCALARES EXTERNAS NO EJECUTADAS — hay un escalares.py", salida.getvalue())

    def test_la_ayuda_sale_0(self) -> None:
        salida = io.StringIO()
        with redirect_stdout(salida):
            rc = diferencial.main(["--help"])
        self.assertIs(rc, 0)
        self.assertIn("La prueba diferencial", salida.getvalue())

    def test_con_el_proyecto_de_oracle_sale_0(self) -> None:
        """Sobre el repositorio de verdad: el fixture versionado tiene que seguir de acuerdo."""
        salida = io.StringIO()
        with redirect_stdout(salida):
            rc = diferencial.main(["--proyecto", str(diferencial.RAIZ)])
        self.assertIs(rc, 0, salida.getvalue())


if __name__ == "__main__":
    unittest.main()
