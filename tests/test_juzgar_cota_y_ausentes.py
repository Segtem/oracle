"""`oracle juzgar` y `Motor`: la sombra perdona hasta su cota, y lo que no se aplicó se nombra.

Tareas `20260916-160811-cota-juzgar` y `20260916-201124-juzgar-omite`.
"""

from __future__ import annotations

import json
import unittest

from nucleo.medida import Informe, Veredicto
from oracle_metalenguaje import Motor
from tests.test_juzgar import (POLITICA_LECTURA, POLITICA_REFERENCIAS, BaseJuzgarTest,
                               _fila_referencia)


class CotaDeLaSombraTests(BaseJuzgarTest):
    def _sombra(self, cota: int) -> None:
        ruta = self.proyecto / "oracle.json"
        config = json.loads(ruta.read_text(encoding="utf-8"))
        config["sombra"] = {POLITICA_REFERENCIAS: {"desde": "2026-09-16", "porque": "deuda",
                                                   "cota": cota}}
        ruta.write_text(json.dumps(config), encoding="utf-8")

    def _juzgar(self, *extra: str) -> tuple[int, str, str]:
        con = self.escribir_evidencia({"referencia_seguimiento": [
            _fila_referencia("ausente", "una.png"), _fila_referencia("ausente", "otra.png")]})
        return self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
                               "--medida", POLITICA_REFERENCIAS, *extra)

    def test_dentro_de_la_cota_la_sombra_perdona(self) -> None:
        self._sombra(2)
        rc, out, err = self._juzgar()
        self.assertEqual(rc, 0, out + err)
        self.assertNotIn("SUPERA SU COTA", out)

    def test_por_encima_de_la_cota_el_rojo_vuelve(self) -> None:
        self._sombra(1)
        rc, out, err = self._juzgar()
        self.assertEqual(rc, 1, out + err)
        self.assertIn("SUPERA SU COTA 1", out)
        self.assertIn("1 de 1 medidas en rojo", out)

    def test_el_json_dice_que_supera_la_cota(self) -> None:
        self._sombra(0)
        rc, out, _ = self._juzgar("--json")
        self.assertEqual(rc, 1)
        datos = json.loads(out)
        self.assertIs(datos["ok"], False)
        self.assertIs(datos["medidas"][0]["en_sombra"], True)
        self.assertIs(datos["medidas"][0]["supera_su_cota"], True)

    def test_el_motor_respeta_la_misma_cota(self) -> None:
        self._sombra(1)
        evidencia = {"referencia_seguimiento": [
            _fila_referencia("ausente", "una.png"), _fila_referencia("ausente", "otra.png")]}
        informe = Motor.desde_proyecto(self.proyecto).evaluar(evidencia)
        self.assertFalse(informe.ok)
        self.assertIn("SUPERA SU COTA 1", informe.texto())


class InformeTests(unittest.TestCase):
    def _v(self, valor) -> Veredicto:
        return Veredicto(id="d.x", valor=valor, ok=False, umbral="<= 0", porque="p",
                         alcance="a", testigos=[])

    def test_sin_un_numero_no_se_puede_afirmar_que_no_supera(self) -> None:
        informe = Informe((self._v("SIN EVIDENCIA"),), en_sombra=frozenset({"d.x"}),
                          cotas=(("d.x", 5),))
        self.assertFalse(informe.ok)

    def test_sin_cota_la_sombra_se_comporta_como_antes(self) -> None:
        informe = Informe((self._v(99),), en_sombra=frozenset({"d.x"}))
        self.assertTrue(informe.ok)

    def test_sin_cota_no_supera_nada_y_lo_dice_con_un_booleano(self) -> None:
        v = self._v(99)
        self.assertIs(Informe((v,), en_sombra=frozenset({"d.x"})).supera_su_cota(v), False)

    def test_cero_es_una_cota(self) -> None:
        self.assertTrue(Informe((self._v(0),), en_sombra=frozenset({"d.x"}),
                                cotas=(("d.x", 0),)).ok)
        self.assertFalse(Informe((self._v(1),), en_sombra=frozenset({"d.x"}),
                                 cotas=(("d.x", 0),)).ok)


class NoAplicadasTests(BaseJuzgarTest):
    def _evidencia(self):
        return {"referencia_seguimiento": [_fila_referencia("presente")]}

    def test_juzgar_nombra_la_medida_propia_cuya_relacion_no_vino(self) -> None:
        con = self.escribir_evidencia(self._evidencia())
        rc, out, err = self.correr_cli("juzgar", "--con", str(con),
                                       "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 0, out + err)
        self.assertIn("NO SE APLICARON", out)
        self.assertIn(f"{POLITICA_LECTURA}: falta lectura_seguimiento", out)
        # Las heredadas juzgan el catálogo, no esta evidencia: no se listan.
        self.assertNotIn("· meta.", out.split("NO SE APLICARON")[1].split("VEREDICTO")[0])

    def test_el_json_las_trae(self) -> None:
        con = self.escribir_evidencia(self._evidencia())
        rc, out, _ = self.correr_cli("juzgar", "--con", str(con),
                                     "--proyecto", str(self.proyecto), "--json")
        self.assertEqual(rc, 0)
        faltantes = {f["id"]: f["faltan"] for f in json.loads(out)["no_aplicadas"]}
        self.assertEqual(faltantes[POLITICA_LECTURA], ["lectura_seguimiento"])
        self.assertNotIn(POLITICA_REFERENCIAS, faltantes)

    def test_con_todas_las_relaciones_no_hay_bloque(self) -> None:
        con = self.escribir_evidencia(self._evidencia())
        rc, out, _ = self.correr_cli("juzgar", "--con", str(con), "--proyecto",
                                     str(self.proyecto), "--medida", POLITICA_REFERENCIAS)
        self.assertEqual(rc, 0)
        self.assertNotIn("NO SE APLICARON", out)

    def test_el_motor_tambien_las_nombra(self) -> None:
        informe = Motor.desde_proyecto(self.proyecto).evaluar(self._evidencia())
        self.assertIn(POLITICA_LECTURA, dict(informe.no_aplicadas))
        self.assertFalse(any(mid.startswith("meta.") for mid, _ in informe.no_aplicadas))
        self.assertIn("NO SE APLICARON", informe.texto())
        self.assertEqual(json.loads(informe.a_json())["no_aplicadas"][0]["id"],
                         informe.no_aplicadas[0][0])


if __name__ == "__main__":
    unittest.main()
