"""El censo cuenta y no juzga, y las dos vistas dicen lo mismo.

Un informe que agrega está a un paso de un tablero, y un tablero a un paso de una métrica que se
vuelve objetivo. Este proyecto ya lo vivió con la proporción de falsación, que era el número que
publicaba como criterio y el que nadie estaba midiendo. Los tests de acá fijan las tres reglas que
lo evitan: **ni cocientes ni conformidad**, **todo denominador presente**, y **la página no dice
nada que la terminal no diga**.
"""

import io
import json
import re
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from nucleo.proyecto import EscalaresNoConfiables
from tools import censar

RAIZ = Path(__file__).resolve().parents[1]


class ElCensoCuentaYNoJuzga(unittest.TestCase):
    def hechos(self):
        return censar.censar([RAIZ], confiar=True)

    def test_ningun_hecho_es_un_cociente_ni_un_juicio_de_conformidad(self):
        """La regla, y la que más fácil se rompe: alcanza con que a alguien le parezca útil un %.

        Un `estado: "ok"` o una `tasa: 0.05` convierten al emisor en juez, que es el pecado que
        `nucleo/marco.py` nombra: «el veredicto sobre el marco estaba en código imperativo mientras
        el resto del proyecto exige que los veredictos sean datos».
        """
        fila = self.hechos()[censar.RELACION][0]
        for campo, valor in fila.items():
            with self.subTest(campo=campo):
                self.assertNotIsInstance(valor, float,
                                         f"«{campo}» es flotante: un cociente disfrazado")
                if isinstance(valor, bool):
                    # El único booleano admitido describe el ESTADO del árbol, no si está bien.
                    self.assertEqual(campo, "arbol_sucio")
        prohibidos = ("tasa", "porcentaje", "ratio", "salud", "puntaje", "score",
                      "estado", "ok", "aprobado", "conforme", "nivel")
        for prohibido in prohibidos:
            with self.subTest(prohibido=prohibido):
                self.assertNotIn(prohibido, [c.lower() for c in fila],
                                 f"«{prohibido}» convierte el censo en un tablero")

    def test_cada_numerador_viaja_con_su_denominador(self):
        """`915 muertos` no dice nada sin `de 915, con 29 mutadores`. Se midió por qué importa: el
        2026-09-07 el paquete publicado medía con 5 de 29 y devolvía «0 sobrevivientes»."""
        fila = self.hechos()[censar.RELACION][0]
        # Los observados y construidos se leen contra el total de casos, que está.
        self.assertIn("casos", fila)
        self.assertEqual(fila["casos"],
                         fila["casos_observados"] + fila["casos_construidos"]
                         + fila["casos_generados"] + fila["casos_sin_procedencia"])
        # Los ilegibles, contra el total de archivos verificados.
        self.assertIn("archivos_verificados", fila)
        self.assertLessEqual(fila["archivos_ilegibles"], fila["archivos_verificados"])
        # El reparto de medidas suma el total: ninguna se pierde ni se cuenta dos veces.
        self.assertEqual(fila["medidas"],
                         fila["medidas_del_proyecto"] + fila["medidas_del_catalogo_base"]
                         + fila["medidas_de_perfiles"] + fila["medidas_de_bibliotecas"])
        # Y la cobertura de mutadores viaja con el censo, no se supone.
        self.assertGreater(fila["mutadores_disponibles"], 0)

    def test_no_agrega_ni_compensa_entre_proyectos(self):
        """La deuda de un proyecto no se tapa con el volumen de otro: no hay totales de columna."""
        hechos = censar.censar([RAIZ, RAIZ], confiar=True)
        self.assertEqual(list(hechos), [censar.RELACION])
        self.assertEqual(len(hechos[censar.RELACION]), 2)

    def test_cada_fila_dice_de_que_proyecto_y_de_que_commit_habla(self):
        # El nombre sale del directorio, no de un literal: el arnés de mutación copia el proyecto a
        # uno llamado `proyecto`, y clavar «oracle» acá afirmaba un accidente del checkout.
        fila = self.hechos()[censar.RELACION][0]
        self.assertEqual(fila["proyecto"], RAIZ.name)
        self.assertRegex(fila["commit"], r"^([0-9a-f]{7,}|sin_git)$")
        self.assertEqual(fila["oracle_distribucion"], censar.VERSION_DISTRIBUCION)

    def test_no_salen_rutas_de_esta_maquina(self):
        """Un censo con rutas absolutas no se puede comparar con el de otra máquina ni compartir."""
        crudo = json.dumps(self.hechos(), ensure_ascii=False)
        self.assertNotIn(str(Path.home()), crudo)
        self.assertNotIn(str(RAIZ), crudo)

    def test_el_nombre_de_un_proyecto_es_el_del_repositorio_y_no_el_de_medidas(self):
        """Un consumidor pone su proyecto Oracle en `medidas/`, y llamarlo «medidas» en el censo
        haría que dos consumidores distintos se vieran iguales."""
        with TemporaryDirectory() as td:
            raiz = Path(td) / "un-consumidor" / "medidas"
            (raiz / "catalogos").mkdir(parents=True)
            (raiz / "corpus").mkdir()
            (raiz / "oracle.json").write_text(
                json.dumps({"esquema": "oracle.proyecto/v1", "perfiles": []}), encoding="utf-8")
            self.assertEqual(censar.censar_uno(raiz, confiar=False)["proyecto"], "un-consumidor")

    def test_un_proyecto_sin_git_lo_dice_en_vez_de_inventar_un_commit(self):
        with TemporaryDirectory() as td:
            raiz = Path(td) / "vacio"
            (raiz / "catalogos").mkdir(parents=True)
            (raiz / "corpus").mkdir()
            (raiz / "oracle.json").write_text(
                json.dumps({"esquema": "oracle.proyecto/v1", "perfiles": []}), encoding="utf-8")
            fila = censar.censar_uno(raiz, confiar=False)
        self.assertEqual(fila["commit"], "sin_git")
        self.assertEqual(fila["medidas_del_proyecto"], 0)
        self.assertEqual(fila["casos"], 0)


class LasDosVistasDicenLoMismo(unittest.TestCase):
    """Si la página mostrara un dato que la terminal no, habría dos verdades que sincronizar."""

    NUMERO = re.compile(r"(?<![\w.#-])\d+(?![\w.])")

    def setUp(self):
        self.hechos = censar.censar([RAIZ], confiar=True)
        self.cuando = "2026-09-08T00:00:00+00:00"

    def test_la_pagina_no_trae_ningun_numero_que_la_terminal_no_diga(self):
        # Se descuentan los pesos tipográficos del CSS, que no son datos.
        texto = set(self.NUMERO.findall(censar.imprimir(self.hechos, self.cuando)))
        pagina = set(self.NUMERO.findall(censar.a_html(self.hechos, self.cuando)))
        estilo = set(self.NUMERO.findall(censar._ESTILO))
        self.assertEqual(pagina - texto - estilo, set())

    def test_las_dos_vistas_arman_el_reparto_con_la_misma_funcion(self):
        fila = self.hechos[censar.RELACION][0]
        reparto = censar._reparto_medidas(fila)
        self.assertIn(reparto, censar.imprimir(self.hechos, self.cuando))
        self.assertIn(reparto, censar.a_html(self.hechos, self.cuando))

    def test_la_pagina_dice_que_no_es_un_puntaje(self):
        pagina = censar.a_html(self.hechos, self.cuando)
        self.assertIn("no un puntaje", pagina)
        self.assertIn("El juicio lo dan las medidas", pagina)

    def test_la_pagina_escapa_lo_que_viene_del_disco(self):
        """El nombre del proyecto sale de un directorio, y un directorio puede llamarse cualquier
        cosa. Sin escapar, un `<` en un nombre rompe la página o inyecta marcado."""
        hechos = {censar.RELACION: [dict(self.hechos[censar.RELACION][0],
                                         proyecto="<script>alerta</script>")]}
        pagina = censar.a_html(hechos, self.cuando)
        self.assertNotIn("<script>alerta", pagina)
        self.assertIn("&lt;script&gt;alerta", pagina)


class ElVerboDelCli(unittest.TestCase):
    def test_censar_es_un_verbo_declarado_y_esta_en_la_ayuda(self):
        from tools import cli

        self.assertIn("censar", cli.verbos_documentados()["oracle"])
        salida = io.StringIO()
        with redirect_stdout(salida):
            cli.ayuda()
        self.assertIn("oracle censar", salida.getvalue())

    def test_el_cli_le_pasa_TODOS_los_proyectos_y_no_solo_el_ultimo(self):
        """El primer intento lo despachaba tarde y la resolución del proyecto se comía la bandera:
        `censar` llegaba con la lista vacía. Es el único verbo que toma varios `--proyecto`."""
        from tools import cli

        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = cli.main(["censar", "--proyecto", str(RAIZ), "--proyecto", str(RAIZ),
                               "--confiar-escalares"])
        self.assertEqual(codigo, 0)
        self.assertIn("2 proyecto(s)", salida.getvalue())

    def test_hechos_emite_la_relacion_y_nada_mas(self):
        from tools import cli

        salida = io.StringIO()
        with redirect_stdout(salida):
            cli.main(["censar", "--proyecto", str(RAIZ), "--hechos", "--confiar-escalares"])
        datos = json.loads(salida.getvalue())
        self.assertEqual(list(datos), [censar.RELACION])

    def test_con_html_escribe_el_archivo_y_lo_dice(self):
        from tools import cli

        with TemporaryDirectory() as td:
            destino = Path(td) / "censo.html"
            salida = io.StringIO()
            with redirect_stdout(salida):
                cli.main(["censar", "--proyecto", str(RAIZ), "--html", str(destino),
                          "--confiar-escalares"])
            self.assertTrue(destino.is_file())
            self.assertIn("<h1>Censo</h1>", destino.read_text(encoding="utf-8"))
        self.assertIn(str(destino), salida.getvalue())



class LoQueElCensoLeePreguntandoAGit(unittest.TestCase):
    """`_git` es la única parte del censo que habla con algo de afuera, y falla en tres formas."""

    def test_sin_git_en_el_camino_devuelve_vacio_en_vez_de_romperse(self):
        with patch("tools.censar.subprocess.run", side_effect=OSError("no hay git")):
            self.assertEqual(censar._git(RAIZ, "rev-parse", "HEAD"), "")

    def test_una_salida_que_falla_no_se_usa_aunque_traiga_texto(self):
        """`git rev-parse HEAD` en un repo sin commits escribe «HEAD» y sale 128. Sin mirar el
        código de salida, el censo anotaría el commit «HEAD»."""
        fallida = subprocess.CompletedProcess(["git"], returncode=128, stdout="HEAD", stderr="")
        with patch("tools.censar.subprocess.run", return_value=fallida):
            self.assertEqual(censar._git(RAIZ, "rev-parse", "HEAD"), "")

    def test_la_salida_se_pide_capturada_y_como_texto(self):
        """Sin `capture_output` el stdout es None y `.strip()` revienta; sin `text` son bytes y el
        commit terminaría en el JSON como `b'...'`."""
        vista = {}

        def espiar(argv, **kw):
            vista.update(kw)
            return subprocess.CompletedProcess(argv, returncode=0, stdout="abc123\n", stderr="")

        with patch("tools.censar.subprocess.run", side_effect=espiar):
            self.assertEqual(censar._git(RAIZ, "rev-parse", "--short", "HEAD"), "abc123")
        self.assertIs(vista.get("capture_output"), True)
        self.assertIs(vista.get("text"), True)

    def test_le_pregunta_al_repositorio_indicado_y_no_al_directorio_actual(self):
        vista = {}

        def espiar(argv, **kw):
            vista["argv"] = argv
            return subprocess.CompletedProcess(argv, returncode=0, stdout="", stderr="")

        with patch("tools.censar.subprocess.run", side_effect=espiar):
            censar._git(Path("/un/repo"), "status", "--short")
        self.assertEqual(vista["argv"][:3], ["git", "-C", "/un/repo"])


class LosConteosQueFaltanNoSeInventan(unittest.TestCase):
    """Un origen o una relación ausente vale CERO, y cero es un hecho: no se omite el campo."""

    VACIO = {"proyecto": "p", "commit": "sin_git", "arbol_sucio": False,
             "medidas": 0, "medidas_del_proyecto": 0, "medidas_del_catalogo_base": 0,
             "medidas_de_perfiles": 0, "medidas_de_bibliotecas": 0,
             "casos": 0, "casos_observados": 0, "casos_construidos": 0,
             "casos_generados": 0, "casos_sin_procedencia": 0,
             "sombras": 0, "sombra_mas_vieja_dias": 0,
             "archivos_verificados": 0, "archivos_ilegibles": 0,
             "mutadores_disponibles": 29, "mutadores_de_otro_autor": 24,
             "oracle_distribucion": "0.0.0", "oracle_algebra": "0.0",
             "oracle_sintaxis": "0.0"}

    def test_un_proyecto_sin_sombras_declara_cero_dias_y_no_falla(self):
        """`max()` sobre una lista vacía revienta sin su `default`, y un proyecto sin sombras es
        el caso normal, no el raro."""
        with TemporaryDirectory() as td:
            raiz = Path(td) / "sin-sombras"
            (raiz / "catalogos").mkdir(parents=True)
            (raiz / "corpus").mkdir()
            (raiz / "oracle.json").write_text(
                json.dumps({"esquema": "oracle.proyecto/v1", "perfiles": []}), encoding="utf-8")
            fila = censar.censar_uno(raiz, confiar=False)
        self.assertEqual(fila["sombras"], 0)
        self.assertEqual(fila["sombra_mas_vieja_dias"], 0)

    def test_un_proyecto_vacio_no_deja_un_separador_colgando(self):
        """Sin medidas no hay de dónde repartir, y un « · » suelto no separa nada."""
        texto = censar.imprimir({censar.RELACION: [self.VACIO]}, "x")
        self.assertIn("medidas    0\n", texto)
        self.assertNotIn("medidas    0 · \n", texto)

    def test_el_reparto_omite_los_origenes_en_cero_pero_el_hecho_los_lleva(self):
        """En la frase se omiten para que se lea; en la relación van en cero, porque un campo
        ausente y un cero son cosas distintas para una medida."""
        fila = dict(self.VACIO, medidas=3, medidas_del_proyecto=3)
        self.assertEqual(censar._reparto_medidas(fila), "3 del proyecto")
        self.assertIn("medidas_de_perfiles", fila)

    def test_sin_ningun_origen_el_reparto_queda_vacio_y_no_miente(self):
        self.assertEqual(censar._reparto_medidas(self.VACIO), "")

    def test_la_fecha_del_titulo_es_el_dia_y_el_cuerpo_lleva_el_instante_entero(self):
        cuando = "2026-09-08T17:05:19.925894+00:00"
        pagina = censar.a_html({censar.RELACION: [self.VACIO]}, cuando)
        self.assertIn("<title>Censo — 2026-09-08</title>", pagina)
        self.assertIn(cuando, pagina)

    def test_un_proyecto_sin_sombras_lo_dice_en_vez_de_callarlo(self):
        texto = censar.imprimir({censar.RELACION: [self.VACIO]}, "2026-09-08T00:00:00+00:00")
        self.assertIn("ninguna declarada", texto)
        pagina = censar.a_html({censar.RELACION: [self.VACIO]}, "2026-09-08T00:00:00+00:00")
        self.assertIn("ninguna declarada", pagina)

    def test_los_archivos_ilegibles_se_marcan_en_la_pagina_y_los_sanos_no(self):
        sano = censar.a_html({censar.RELACION: [dict(self.VACIO, archivos_verificados=5)]}, "x")
        roto = censar.a_html({censar.RELACION: [dict(self.VACIO, archivos_verificados=5,
                                                     archivos_ilegibles=2)]}, "x")
        self.assertNotIn("class=aviso", sano)
        self.assertIn("class=aviso", roto)
        self.assertIn(">3</span>/5 archivos se imprimen", roto)

    def test_el_arbol_sucio_se_dice_en_las_dos_vistas(self):
        sucio = {censar.RELACION: [dict(self.VACIO, arbol_sucio=True)]}
        self.assertIn("árbol sucio", censar.imprimir(sucio, "x"))
        self.assertIn("árbol sucio", censar.a_html(sucio, "x"))
        limpio = {censar.RELACION: [self.VACIO]}
        self.assertNotIn("árbol sucio", censar.imprimir(limpio, "x"))


class LaLineaDeComandosDelCenso(unittest.TestCase):
    def test_sin_argv_explicito_lee_la_del_proceso(self):
        salida = io.StringIO()
        with patch("sys.argv", ["censar.py", "--proyecto", str(RAIZ), "--hechos",
                                "--confiar-escalares"]), redirect_stdout(salida):
            self.assertEqual(censar.main(), 0)
        self.assertEqual(list(json.loads(salida.getvalue())), [censar.RELACION])

    def test_sin_proyecto_no_corre(self):
        with self.assertRaises(SystemExit):
            censar.argumentos([])

    def test_con_hechos_no_imprime_el_informe_de_texto(self):
        salida = io.StringIO()
        with redirect_stdout(salida):
            censar.main(["--proyecto", str(RAIZ), "--hechos", "--confiar-escalares"])
        self.assertNotIn("CENSO —", salida.getvalue())

    def test_la_ayuda_describe_el_censo_y_no_una_seccion_del_medio(self):
        with self.assertRaises(SystemExit):
            with redirect_stdout(io.StringIO()) as s:
                censar.argumentos(["--help"])
        self.assertIn("Censa varios proyectos", s.getvalue())


class LosBordesQueLaMutacionEncontro(unittest.TestCase):
    """Los cinco sitios que sobrevivieron a la primera ronda, cada uno con lo que los distingue."""

    def _proyecto(self, td: str, *, con_escalares: bool = False) -> Path:
        raiz = Path(td) / "un-proyecto"
        (raiz / "catalogos").mkdir(parents=True)
        (raiz / "corpus").mkdir()
        (raiz / "oracle.json").write_text(
            json.dumps({"esquema": "oracle.proyecto/v1", "perfiles": []}), encoding="utf-8")
        if con_escalares:
            (raiz / "escalares.py").write_text("raise RuntimeError('no debería ejecutarse')\n",
                                               encoding="utf-8")
        return raiz

    def test_por_omision_NO_ejecuta_el_escalares_del_proyecto(self):
        """Correr el `escalares.py` de un proyecto ajeno es correr código de otro. El CLI lo exige
        con `--confiar-escalares`; la biblioteca no puede hacerlo sola por omisión."""
        with TemporaryDirectory() as td:
            raiz = self._proyecto(td, con_escalares=True)
            # El `escalares.py` del fixture estalla apenas se importa: si el censo lo ejecutara,
            # el error diría `EscalaresInvalidas` y no que hace falta autorizar.
            with self.assertRaises(EscalaresNoConfiables) as caido:
                censar.censar_uno(raiz)
            self.assertIn("--confiar-escalares", str(caido.exception))
            # `censar` no levanta: anota el motivo en la fila. Que el motivo sea ÉSE es lo que
            # distingue no haberlo ejecutado de haberlo ejecutado y que estallara.
            fila, = censar.censar([raiz])[censar.RELACION]
            self.assertIn("EscalaresNoConfiables", fila["no_se_pudo_censar"])
            self.assertNotIn("no debería ejecutarse", fila["no_se_pudo_censar"])

    def test_un_origen_ausente_cuenta_cero_y_no_uno(self):
        """`por_origen.get(x, 0)`: con un 1 por omisión, un proyecto sin perfiles declararía tener
        uno, y el reparto dejaría de cerrar contra el total."""
        with TemporaryDirectory() as td:
            fila = censar.censar_uno(self._proyecto(td))
        self.assertEqual(fila["medidas_de_perfiles"], 0)
        self.assertEqual(fila["medidas_del_catalogo_base"], 0)
        self.assertEqual(fila["medidas_de_bibliotecas"], 0)
        self.assertEqual(fila["medidas"], 0)

    def test_los_hechos_no_escapan_los_acentos(self):
        """El nombre sale de un directorio, y en español un directorio lleva acentos. Escaparlos
        volvería el JSON ilegible para quien lo abre a mano, que es la mitad de para qué está."""
        hechos = {censar.RELACION: [dict(LosConteosQueFaltanNoSeInventan.VACIO,
                                         proyecto="programación")]}
        salida = io.StringIO()
        with patch.object(censar, "censar", return_value=hechos), redirect_stdout(salida):
            censar.main(["--proyecto", ".", "--hechos"])
        self.assertIn("programación", salida.getvalue())
        self.assertNotIn("\\u00f3", salida.getvalue())

    def test_el_modulo_corre_solo_desde_la_linea_de_comandos(self):
        """El `sys.path` del arranque apunta a la raíz del repositorio. Si apuntara a otro lado, el
        módulo importado por la suite andaría igual —el path ya está puesto— y sólo se rompería
        corriéndolo suelto, que es como lo corre una persona."""
        salida = subprocess.run(
            [sys.executable, str(RAIZ / "tools" / "censar.py"), "--proyecto", str(RAIZ),
             "--hechos", "--confiar-escalares"],
            capture_output=True, text=True, cwd=str(Path(RAIZ).parent))
        self.assertEqual(salida.returncode, 0, salida.stderr[-600:])
        self.assertEqual(list(json.loads(salida.stdout)), [censar.RELACION])


class LaPaginaSeAbreSolaEnUnNavegador(unittest.TestCase):
    """La página es la vista que viaja: se guarda en un archivo y alguien la abre después, sin el
    servidor ni la terminal que la produjo. Todo lo que necesita para leerse va adentro."""

    def _pagina(self) -> str:
        return censar.a_html({censar.RELACION: [LosConteosQueFaltanNoSeInventan.VACIO]},
                             "2026-09-08T17:52:16+00:00")

    def test_declara_la_codificacion_en_la_que_se_escribe(self):
        pagina = self._pagina()
        self.assertTrue(pagina.startswith("<!doctype html>"), pagina[:40])
        self.assertIn('<meta charset="utf-8">', pagina)
        self.assertIn('lang="es"', pagina)

    def test_el_archivo_escrito_se_relee_como_utf8_con_los_acentos_enteros(self):
        with TemporaryDirectory() as td:
            destino = Path(td) / "censo.html"
            hechos = {censar.RELACION: [dict(LosConteosQueFaltanNoSeInventan.VACIO,
                                             proyecto="programación")]}
            with patch.object(censar, "censar", return_value=hechos), redirect_stdout(io.StringIO()):
                censar.main(["--proyecto", ".", "--html", str(destino)])
            crudo = destino.read_bytes()
        self.assertIn("programación".encode("utf-8"), crudo)
        self.assertIn(b'<meta charset="utf-8">', crudo)

    def test_la_pagina_dice_que_no_es_un_puntaje(self):
        """Es la vista que se comparte, y la que más fácil se lee como un tablero de posiciones.
        La frase que lo desmiente no puede quedarse solamente en la terminal."""
        pagina = self._pagina()
        self.assertIn("no un puntaje", pagina)
        self.assertIn("oracle test", pagina)


class UnProyectoIlegibleNoSeLlevaPuestosALosDemas(unittest.TestCase):
    """Un censo de tres que muere en el primero no informa de los otros dos, que se podían leer.
    Es la lección de 0.9.1 —una herramienta que se cae no informa— aplicada al verbo nuevo."""

    def _roto(self, td: str) -> Path:
        raiz = Path(td) / "roto"
        raiz.mkdir(parents=True)
        (raiz / "oracle.json").write_text("{ esto no es JSON", encoding="utf-8")
        return raiz

    def test_los_demas_proyectos_se_censan_igual(self):
        with TemporaryDirectory() as td:
            sano = LosBordesQueLaMutacionEncontro()._proyecto(td)
            hechos = censar.censar([self._roto(td), sano])
        roto, ok = hechos[censar.RELACION]
        self.assertIn("no_se_pudo_censar", roto)
        self.assertNotIn("no_se_pudo_censar", ok)
        self.assertEqual(ok["casos"], 0)

    def test_la_fila_ilegible_no_inventa_un_cero(self):
        """«0 medidas» y «medidas que nadie contó» son cosas distintas, y la diferencia es todo el
        punto de esta herramienta."""
        with TemporaryDirectory() as td:
            fila, = censar.censar([self._roto(td)])[censar.RELACION]
        self.assertEqual(fila["proyecto"], "roto")
        for conteo in ("medidas", "casos", "sombras", "archivos_verificados"):
            self.assertNotIn(conteo, fila)

    def test_las_dos_vistas_dicen_que_no_se_pudo_y_por_que(self):
        with TemporaryDirectory() as td:
            hechos = censar.censar([self._roto(td)])
        motivo = hechos[censar.RELACION][0]["no_se_pudo_censar"]
        terminal = censar.imprimir(hechos, "2026-09-08T00:00:00+00:00")
        pagina = censar.a_html(hechos, "2026-09-08T00:00:00+00:00")
        self.assertIn("NO SE PUDO CENSAR", terminal)
        self.assertIn("No se pudo censar", pagina)
        for vista in (terminal, pagina):
            self.assertIn(motivo.split(":")[0], vista)


class LaFilaIlegibleTambienDiceDondeQuedoElArbol(unittest.TestCase):
    """La fila de un proyecto que no se pudo leer conserva las señas que sí se pudieron leer.

    Si dijera siempre lo mismo del árbol, un censo guardado no distinguiría un proyecto ilegible
    en un commit limpio de uno con cambios sin guardar — que es la primera pregunta al mirar
    después por qué falló."""

    def _roto(self, td: str, *, con_git: bool) -> Path:
        raiz = Path(td) / ("roto-git" if con_git else "roto-pelado")
        raiz.mkdir(parents=True)
        (raiz / "oracle.json").write_text("{ esto no es JSON", encoding="utf-8")
        if con_git:
            for orden in (["init", "-q"], ["add", "-A"],
                          ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "uno"]):
                subprocess.run(["git", "-C", str(raiz), *orden], capture_output=True, check=True)
            (raiz / "suelto.txt").write_text("sin guardar", encoding="utf-8")
        return raiz

    def test_el_arbol_sucio_se_lee_igual_que_en_una_fila_completa(self):
        with TemporaryDirectory() as td:
            sucia, = censar.censar([self._roto(td, con_git=True)])[censar.RELACION]
            pelada, = censar.censar([self._roto(td, con_git=False)])[censar.RELACION]
        self.assertIs(sucia["arbol_sucio"], True)
        self.assertNotEqual(sucia["commit"], "sin_git")
        self.assertIs(pelada["arbol_sucio"], False)
        self.assertEqual(pelada["commit"], "sin_git")

if __name__ == "__main__":
    unittest.main()
