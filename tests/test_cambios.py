from __future__ import annotations

import io
import json
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tools.cambios import endurece_o_iguala

MEDIDA = """medida dominio.x:
    de corrida c
    donde c.codigo != 0
    resumen contar(1)
    umbral {umbral} segun contrato porque "{porque}"
    requiere corrida
    ambito universal
    alcance "{alcance}"
"""

CASO = """caso 001-rojo:
    fecha: "2026-09-28"
    origen:
        repo: "prueba"
        commit: "sin-commit"
    procedencia: construida
    titulo: "Una corrida que falla"
    etiqueta: {etiqueta}
    sintoma:
        Falla.
    como_se_detecto: persona
    medida: dominio.x
    evidencia:
        corrida: codigo
            1
    leccion:
        Tiene que dar rojo.
"""


def _medida(umbral="<= 0", porque="cero", alcance="mira el código", requiere=True) -> str:
    texto = MEDIDA.format(umbral=umbral, porque=porque, alcance=alcance)
    return texto if requiere else texto.replace("    requiere corrida\n", "")


class EndureceTests(unittest.TestCase):
    def test_umbral_superior(self) -> None:
        self.assertTrue(endurece_o_iguala("<=", 3, "<=", 3))
        self.assertTrue(endurece_o_iguala("<=", 3, "<=", 1))
        self.assertTrue(endurece_o_iguala("<=", 3, "<", 3))
        self.assertTrue(endurece_o_iguala("<", 3, "<", 3))
        self.assertFalse(endurece_o_iguala("<=", 0, "<=", 3))
        self.assertFalse(endurece_o_iguala("<", 3, "<=", 3))
        self.assertTrue(endurece_o_iguala("<", 3, "<=", 2))

    def test_umbral_inferior(self) -> None:
        self.assertTrue(endurece_o_iguala(">=", 5, ">=", 8))
        self.assertTrue(endurece_o_iguala(">=", 5, ">", 5))
        self.assertFalse(endurece_o_iguala(">=", 5, ">=", 2))
        self.assertFalse(endurece_o_iguala(">", 5, ">=", 5))
        self.assertTrue(endurece_o_iguala(">", 5, ">=", 6))

    def test_cambiar_de_sentido_o_la_igualdad_no_es_endurecer(self) -> None:
        self.assertFalse(endurece_o_iguala("<=", 0, ">=", 0))
        self.assertFalse(endurece_o_iguala("<=", 3, ">=", 1))
        self.assertFalse(endurece_o_iguala(">=", 1, "<=", 3))
        self.assertFalse(endurece_o_iguala("<", 3, ">", 3))
        self.assertFalse(endurece_o_iguala("==", 0, "==", 1))
        self.assertTrue(endurece_o_iguala("==", 0, "==", 0))


class CambiosTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raiz = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.raiz)
        (self.raiz / "catalogos").mkdir()
        (self.raiz / "corpus" / "g").mkdir(parents=True)
        (self.raiz / "diferencial").mkdir()
        self._escribir(_medida(), "falso_verde", cota=3, porque_sombra="deuda vieja")
        for args in (["init", "-q"], ["add", "-A"],
                     ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base"]):
            subprocess.run(["git", "-C", str(self.raiz), *args], check=True)

    def _escribir(self, medida: str | None, etiqueta: str | None, *, cota=3, porque_sombra="deuda vieja",
                  sombra=True) -> None:
        ruta_medida = self.raiz / "catalogos" / "dominio.x.oracle"
        ruta_caso = self.raiz / "corpus" / "g" / "001-rojo.caso"
        for ruta, texto in ((ruta_medida, medida), (ruta_caso, None if etiqueta is None else CASO.format(etiqueta=etiqueta))):
            if texto is None:
                ruta.unlink(missing_ok=True)
            else:
                ruta.write_text(texto, encoding="utf-8")
        config = {"esquema": "oracle.proyecto/v1", "catalogo_base": False, "perfiles": []}
        if sombra:
            config["sombra"] = {"dominio.x": {"desde": "2026-09-01", "porque": porque_sombra, "cota": cota}}
        (self.raiz / "oracle.json").write_text(json.dumps(config), encoding="utf-8")

    def _correr(self, ref="HEAD") -> tuple[int, str]:
        from nucleo.proyecto import Proyecto
        from tools import cambios
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = cambios.main(Proyecto(self.raiz), ref)
        return codigo, salida.getvalue()

    def test_sin_cambios(self) -> None:
        self.assertEqual(self._correr(), (0, "cambios desde HEAD:\n  nada se aflojó\n\n0 errores · 0 avisos\n"))

    def test_endurecer_no_se_senala(self) -> None:
        self._escribir(_medida(umbral="< 0"), "falso_verde", cota=1)
        self.assertEqual(self._correr()[0], 0)
        self.assertIn("nada se aflojó", self._correr()[1])

    def test_aflojar_sin_nueva_defensa_es_error(self) -> None:
        self._escribir(_medida(umbral="<= 3"), "falso_verde")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 1)
        self.assertIn("✗ umbral aflojado sin nueva defensa  dominio.x  <= 0 → <= 3  (el `porque` no cambió)", texto)

    def test_aflojar_con_nueva_defensa_es_aviso(self) -> None:
        self._escribir(_medida(umbral="<= 3", porque="tres, medido el 2026-09-28"), "falso_verde")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 0)
        self.assertIn("· umbral aflojado con nueva defensa  dominio.x  <= 0 → <= 3", texto)
        self.assertNotIn("nada se aflojó", texto)

    def test_quitar_requiere_es_error(self) -> None:
        self._escribir(_medida(requiere=False), "falso_verde")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 1)
        self.assertIn("✗ requiere quitado  dominio.x  corrida", texto)

    def test_alcance_caso_y_medida(self) -> None:
        self._escribir(_medida(alcance="mira otra cosa"), "verde_correcto")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 0)
        self.assertIn("· alcance cambiado  dominio.x", texto)
        self.assertIn("· caso con otra etiqueta  001-rojo  falso_verde → verde_correcto", texto)
        self._escribir(None, None)
        codigo, texto = self._correr()
        self.assertEqual(codigo, 0)
        self.assertIn("· medida borrada  dominio.x", texto)
        self.assertIn("· caso borrado  001-rojo", texto)
        self.assertIn("0 errores · 2 avisos", texto)

    def test_cota_de_sombra(self) -> None:
        self._escribir(_medida(), "falso_verde", cota=5)
        codigo, texto = self._correr()
        self.assertEqual(codigo, 1)
        self.assertIn("✗ cota de sombra subida  dominio.x  3 → 5  (el `porque` no cambió)", texto)
        self._escribir(_medida(), "falso_verde", cota=5, porque_sombra="subió porque entró la medida y")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 0)
        self.assertIn("· cota de sombra subida  dominio.x  3 → 5", texto)

    def test_sombra_nueva_es_aviso(self) -> None:
        self._escribir(_medida(), "falso_verde", sombra=False)
        subprocess.run(["git", "-C", str(self.raiz), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.raiz), "-c", "user.name=t", "-c", "user.email=t@t",
                        "commit", "-q", "-m", "sin sombra"], check=True)
        self._escribir(_medida(), "falso_verde")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 0)
        self.assertIn("· sombra nueva  dominio.x", texto)

    def test_por_la_cli(self) -> None:
        from tools import cli
        for argv, codigo, esperado in (
                (["cambios", "--proyecto", str(self.raiz)], 0, "cambios desde HEAD:"),
                (["proyecto", "cambios", "--desde", "HEAD", "--proyecto", str(self.raiz)], 0, "cambios desde HEAD:"),
                (["cambios", "HEAD", "--proyecto", str(self.raiz)], 1, "uso: oracle cambios [--desde <ref>]"),
                (["cambios", "--desde", "--proyecto", str(self.raiz)], 1, "uso: oracle cambios [--desde <ref>]")):
            salida = io.StringIO()
            with self.subTest(argv=argv), redirect_stdout(salida):
                self.assertEqual(cli.main(argv), codigo)
            self.assertIn(esperado, salida.getvalue())

    def _commit(self, mensaje: str) -> None:
        subprocess.run(["git", "-C", str(self.raiz), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.raiz), "-c", "user.name=t", "-c", "user.email=t@t",
                        "commit", "-q", "-m", mensaje], check=True)

    def test_un_ref_que_no_carga_se_dice(self) -> None:
        self._escribir(_medida().replace("resumen contar(1)", "resumen contar(1"), "falso_verde")
        self._commit("medida rota")
        self._escribir(_medida(), "falso_verde")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 1)
        self.assertTrue(texto.startswith("✗ no se pudo leer el catálogo de HEAD: "), texto)

    def test_un_ref_sin_corpus_ni_configuracion(self) -> None:
        shutil.rmtree(self.raiz / "corpus")
        (self.raiz / "oracle.json").unlink()
        self._commit("sin corpus ni oracle.json")
        (self.raiz / "corpus" / "g").mkdir(parents=True)
        self._escribir(_medida(), "falso_verde")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 0)
        self.assertIn("· sombra nueva  dominio.x", texto)
        self.assertIn("0 errores · 1 avisos", texto)

    def test_ref_inexistente(self) -> None:
        codigo, texto = self._correr("no-existe")
        self.assertEqual(codigo, 1)
        self.assertIn("«no-existe» no es un commit de git", texto)


if __name__ == "__main__":
    unittest.main()
