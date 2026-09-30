"""La línea «respaldo real» de la mutación de medidas: cuánto de la fijación respalda un defecto real."""

from __future__ import annotations

import unittest

from nucleo.forma import datos_en_forma_unica
from nucleo.medida import Medida
from tools.mutar import respaldo_real

MEDIDA = """ninguno demo.alto:
    de pieza p
    donde p.alto > 400
    umbral <= 0 segun contrato porque "cuatro metros"
    ambito universal
    alcance "no mira la malla"
"""


def _caso(cid: str, procedencia: str, etiqueta: str, alto: int) -> dict:
    return {"id": cid, "medida": "demo.alto", "procedencia": procedencia, "etiqueta": etiqueta,
            "evidencia": {"pieza": [{"id": "a", "alto": alto}]}}


class RespaldoRealTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalogo = {"demo.alto": Medida.de_datos(datos_en_forma_unica(MEDIDA, "demo"))}
        self.mutantes = [{"apunta_a": "demo.alto", "cambio": f"m{i}", "detecciones_conductuales": 1,
                          "rechazos_del_algebra": 0} for i in range(3)]

    def test_sin_casos_observados_nada_tiene_respaldo(self) -> None:
        linea = respaldo_real(self.catalogo, [_caso("1-a", "construida", "falso_verde", 500)], self.mutantes)
        self.assertEqual(linea, "respaldo real: 0 de 3 muertos los mata al menos un caso observado; "
                                "3 sólo los sostiene evidencia construida, generada, sin procedencia o diferencial")

    def test_cuenta_solo_lo_que_mata_un_caso_observado_y_ya_estaba_muerto(self) -> None:
        from nucleo.mutacion import correr
        observado = _caso("2-b", "observada", "falso_verde", 500)
        muertos_por_observado = {m["cambio"] for m in correr(self.catalogo, [observado])["mutante"]
                                 if m["detecciones_conductuales"] or m["rechazos_del_algebra"]}
        self.assertTrue(muertos_por_observado)
        # Los muertos de la corrida entera son los que lo mata el observado más uno que no.
        fila = lambda cambio, c, r: {"apunta_a": "demo.alto", "cambio": cambio,  # noqa: E731
                                     "detecciones_conductuales": c, "rechazos_del_algebra": r}
        mutantes = [fila(cambio, 1, 0) for cambio in sorted(muertos_por_observado)]
        mutantes += [fila("ajeno", 0, 1), fila("vivo", 0, 0)]
        linea = respaldo_real(self.catalogo, [observado, _caso("3-c", "generada", "verde_correcto", 100)],
                              mutantes)
        n = len(muertos_por_observado)
        self.assertEqual(linea, f"respaldo real: {n} de {n + 1} muertos los mata al menos un caso "
                                "observado; 1 sólo los sostiene evidencia construida, generada, sin "
                                "procedencia o diferencial")


if __name__ == "__main__":
    unittest.main()
