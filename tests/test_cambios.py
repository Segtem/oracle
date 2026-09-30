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

    def test_un_proyecto_con_escalares_propias_pide_confianza(self) -> None:
        (self.raiz / "escalares.py").write_text(
            "from oracle_metalenguaje import escalar\n\n\n@escalar(\"es_grande\")\ndef es_grande(x):\n"
            "    return x > 10\n", encoding="utf-8")
        self._escribir(_medida().replace("donde c.codigo != 0", "donde es_grande(c.codigo)"), "falso_verde")
        self._commit("con escalares")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 1)
        self.assertIn("ESCALARES EXTERNAS NO EJECUTADAS", texto)
        from nucleo.proyecto import Proyecto
        from tools import cambios
        with redirect_stdout(io.StringIO()) as salida:
            self.assertEqual(cambios.main(Proyecto(self.raiz), "HEAD", confiar=True), 0)
        self.assertIn("nada se aflojó", salida.getvalue())
        from tools import cli
        with redirect_stdout(io.StringIO()) as salida:
            self.assertEqual(cli.main(["cambios", "--proyecto", str(self.raiz), "--confiar-escalares"]), 0)

    def test_un_proyecto_en_un_subdirectorio_del_repositorio(self) -> None:
        # Como el `medidas/` de un consumidor: el repositorio empieza un nivel más arriba.
        repo = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, repo)
        shutil.move(str(self.raiz), repo / "medidas")
        self.raiz.mkdir()  # el addCleanup de setUp borra esta ruta
        self.raiz = repo / "medidas"
        shutil.rmtree(self.raiz / ".git")
        for args in (["init", "-q"], ["add", "-A"],
                     ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base"]):
            subprocess.run(["git", "-C", str(repo), *args], check=True)
        self.assertEqual(self._correr()[0], 0)
        self._escribir(_medida(umbral="<= 3"), "falso_verde")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 1)
        self.assertIn("✗ umbral aflojado sin nueva defensa  dominio.x  <= 0 → <= 3", texto)

    def test_un_arbol_de_trabajo_que_no_carga_se_dice(self) -> None:
        self._escribir(_medida().replace("resumen contar(1)", "resumen contar(1"), "falso_verde")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 1)
        self.assertTrue(texto.startswith("✗ no se pudo leer el catálogo del árbol de trabajo: "), texto)

    def _sensores(self, *rutas: str) -> None:
        config = json.loads((self.raiz / "oracle.json").read_text(encoding="utf-8"))
        config["sensores"] = list(rutas)
        (self.raiz / "oracle.json").write_text(json.dumps(config), encoding="utf-8")

    def test_una_escalar_cambiada_nombra_las_medidas_que_la_usan(self) -> None:
        escalares = self.raiz / "escalares.py"
        base = ('"""Escalares."""\nfrom oracle_metalenguaje import escalar\n\n\n@escalar("es_grande")\n'
                'def es_grande(x):\n    return x > 10\n\n\n@escalar("es_chico")\ndef es_chico(x):\n'
                '    return x < 1\n')
        escalares.write_text(base, encoding="utf-8")
        self._escribir(_medida().replace("donde c.codigo != 0", "donde es_grande(c.codigo)"), "falso_verde")
        self._commit("con escalares")
        from nucleo.proyecto import Proyecto
        from tools import cambios

        def correr() -> tuple[int, str]:
            with redirect_stdout(io.StringIO()) as salida:
                codigo = cambios.main(Proyecto(self.raiz), "HEAD", confiar=True)
            return codigo, salida.getvalue()

        escalares.write_text(base.replace('"""Escalares."""', '"""Otra docstring."""')
                             .replace("x > 10", "x > 1000"), encoding="utf-8")
        codigo, texto = correr()
        self.assertEqual(codigo, 0)
        self.assertIn("· escalar cambiada  es_grande  (la usan: dominio.x)", texto)
        self.assertNotIn("es_chico", texto)
        # Un cambio en el código que comparten alcanza a todas.
        escalares.write_text(base.replace("from oracle_metalenguaje import escalar",
                                          "from oracle_metalenguaje import escalar\nLIMITE = 3"), encoding="utf-8")
        texto = correr()[1]
        self.assertIn("· escalar cambiada  es_chico  (ninguna medida la usa)", texto)
        self.assertIn("· escalar cambiada  es_grande  (la usan: dominio.x)", texto)

    def test_una_relacion_cambiada_nombra_las_medidas_que_la_leen(self) -> None:
        (self.raiz / "relaciones").mkdir()
        ruta = self.raiz / "relaciones" / "corrida.relacion"
        texto = 'relacion corrida:\n    codigo: entero sin_unidad\n    alcance "una corrida"\n'
        ruta.write_text(texto, encoding="utf-8")
        self._commit("con relación")
        self.assertIn("nada se aflojó", self._correr()[1])
        ruta.write_text(texto.replace("una corrida", "una corrida cualquiera"), encoding="utf-8")
        codigo, salida = self._correr()
        self.assertEqual(codigo, 0)
        self.assertIn("· relación cambiada  corrida  (la usan: dominio.x)", salida)

    def test_los_sensores_declarados_se_vigilan(self) -> None:
        (self.raiz / "sensores").mkdir()
        (self.raiz / "sensores" / "lee.py").write_text("HECHOS = 1\n", encoding="utf-8")
        self._sensores("sensores")
        self._commit("con sensores")
        self.assertIn("nada se aflojó", self._correr()[1])
        (self.raiz / "sensores" / "lee.py").write_text("HECHOS = 0\n", encoding="utf-8")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 0)
        self.assertIn("· sensor cambiado  sensores/lee.py", texto)
        # Dejar de vigilar es error, y lo tocado en el mismo cambio se sigue viendo.
        self._sensores()
        codigo, texto = self._correr()
        self.assertEqual(codigo, 1)
        self.assertIn("✗ sensor que se deja de vigilar  sensores", texto)
        self.assertIn("· sensor cambiado  sensores/lee.py", texto)

    def test_sensores_mal_declarados_o_fuera_del_repositorio(self) -> None:
        self._sensores("")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 1)
        self.assertIn("`sensores` de `oracle.json` debe ser una lista de rutas", texto)
        self._sensores("../../fuera")
        codigo, texto = self._correr()
        self.assertEqual(codigo, 1)
        self.assertIn("nombra una ruta que git no puede mirar", texto)

    def test_ref_inexistente(self) -> None:
        codigo, texto = self._correr("no-existe")
        self.assertEqual(codigo, 1)
        self.assertIn("«no-existe» no es un commit de git", texto)


if __name__ == "__main__":
    unittest.main()
