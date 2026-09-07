"""La sonda de procedencia tiene que distinguir, no sólo pasar.

Su trabajo es sostener el `comando` que los casos 483 y 484 declaran en su `origen`. Si emitiera
cualquier cosa, esos dos casos declararían un puntero a la nada — que es exactamente el defecto que
`meta.todo_caso_observado_declara_de_donde_salio` existe para hacer visible.
"""

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from nucleo.medida import cargar
from tools import sondear_procedencia as sonda


class SondaDeProcedencia(unittest.TestCase):
    def ejecutar(self, args=()):
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = sonda.main(list(args))
        return codigo, salida.getvalue()

    def test_las_dos_sondas_declaran_su_expectativa_y_se_cumple(self):
        codigo, texto = self.ejecutar()
        self.assertEqual(codigo, 0, texto)
        self.assertIn("2 sondas sobre corpus reales", texto)
        self.assertNotIn("✗", texto)

    def test_las_dos_sondas_difieren_en_un_solo_campo_de_un_solo_caso(self):
        # Si difirieran en más, el verde no probaría que la medida mira ESE campo.
        rojo, verde = (sonda.SONDAS[n][0] for n in sonda.SONDAS)
        self.assertEqual(len(rojo), len(verde))
        distintos = [(a, b) for a, b in zip(rojo, verde) if a != b]
        self.assertEqual(len(distintos), 1)
        (_id_r, proc_r, origen_r), (_id_v, proc_v, origen_v) = distintos[0]
        self.assertEqual((proc_r, proc_v), ("observada", "observada"))
        self.assertEqual(set(origen_r), {"repo", "commit"})
        self.assertEqual(set(origen_v), {"repo", "commit", "comando"})

    def test_el_corpus_construido_se_lee_del_disco_con_el_cargador_real(self):
        raiz = sonda.escribir_corpus(sonda.SONDAS["un_caso_observado_no_dice_de_donde_salio"][0])
        archivos = sorted(p.name for p in (raiz / "dominio").iterdir())
        self.assertEqual(len(archivos), 3)
        self.assertTrue(all(n.endswith(".json") for n in archivos), archivos)
        # Cada sonda escribe en una carpeta nueva: no se pisan ni dependen del orden.
        otra = sonda.escribir_corpus(sonda.SONDAS["un_caso_observado_no_dice_de_donde_salio"][0])
        self.assertNotEqual(raiz, otra)

    def test_los_hechos_traen_el_campo_que_la_medida_mira(self):
        codigo, texto = self.ejecutar(("--hechos",))
        self.assertEqual(codigo, 0)
        datos = json.loads(texto)
        self.assertEqual(sorted(datos), sorted(sonda.SONDAS))
        rojo = datos["un_caso_observado_no_dice_de_donde_salio"]["caso"]
        verde = datos["todos_los_observados_dicen_de_donde_salieron"]["caso"]
        self.assertEqual([f["declara_de_donde_salio"] for f in rojo], [False, True, False])
        self.assertEqual([f["declara_de_donde_salio"] for f in verde], [True, True, False])
        # El `construida` sin origen está en las dos, y en las dos sale en `false`: es lo que hace
        # que quitarle el filtro de procedencia a la medida cambie el veredicto del verde.
        self.assertEqual([f["procedencia"] for f in verde][2], "construida")

    def test_la_medida_separa_las_dos_sondas(self):
        medida = cargar(Path("catalogos/meta") / f"{sonda.MID}.oracle")
        self.assertFalse(medida.evaluar(sonda.hechos("un_caso_observado_no_dice_de_donde_salio")).ok)
        self.assertTrue(medida.evaluar(sonda.hechos("todos_los_observados_dicen_de_donde_salieron")).ok)

    def test_una_sonda_que_no_cumple_su_expectativa_sale_uno_y_la_nombra(self):
        # La expectativa se declara en SONDAS y no se lee del veredicto: si se invierte, la sonda
        # tiene que quejarse aunque el marco y la medida no hayan cambiado.
        invertidas = {n: (entradas, not debe) for n, (entradas, debe) in sonda.SONDAS.items()}
        with patch.object(sonda, "SONDAS", invertidas):
            codigo, texto = self.ejecutar()
        self.assertEqual(codigo, 1)
        self.assertEqual(texto.count("✗"), 2)

    def test_con_hechos_el_codigo_de_salida_sigue_informando_la_discordancia(self):
        invertidas = {n: (entradas, not debe) for n, (entradas, debe) in sonda.SONDAS.items()}
        with patch.object(sonda, "SONDAS", invertidas):
            codigo, texto = self.ejecutar(("--hechos",))
        self.assertEqual(codigo, 1)
        self.assertEqual(sorted(json.loads(texto)), sorted(sonda.SONDAS))



class LineaDeComandos(unittest.TestCase):
    def test_sin_argv_explicito_lee_la_linea_de_comandos_del_proceso(self):
        salida = io.StringIO()
        with patch("sys.argv", ["sondear_procedencia.py", "--hechos"]), redirect_stdout(salida):
            codigo = sonda.main()
        self.assertEqual(codigo, 0)
        self.assertEqual(sorted(json.loads(salida.getvalue())), sorted(sonda.SONDAS))

    def test_lo_que_emite_se_puede_volver_a_leer_como_los_hechos_de_una_sonda(self):
        salida = io.StringIO()
        with patch("sys.argv", ["sondear_procedencia.py", "--hechos"]), redirect_stdout(salida):
            sonda.main()
        emitido = json.loads(salida.getvalue())
        for nombre in sonda.SONDAS:
            with self.subTest(sonda=nombre):
                self.assertEqual(emitido[nombre], sonda.hechos(nombre))

if __name__ == "__main__":
    unittest.main()
