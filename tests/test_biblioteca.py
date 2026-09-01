"""Contrato local de las bibliotecas de políticas, incluida su certificación."""

from __future__ import annotations

import io
import sys
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from importlib import metadata
from pathlib import Path
from types import SimpleNamespace

from nucleo.biblioteca import (BibliotecaInvalida, cargar_manifiesto,
                               descubrir_bibliotecas, ruta_instalada_del_manifiesto,
                               verificar_biblioteca)
from tools import cli


RAIZ = Path(__file__).resolve().parents[1]
PAQUETE_EJEMPLO = RAIZ / "ejemplo" / "biblioteca-segtem"
EJEMPLO = (PAQUETE_EJEMPLO / "oracle_bibliotecas" /
           "oracle_biblioteca_segtem_meta_calidad")
NOMBRE_DISTRIBUCION = "oracle-biblioteca-segtem-meta-calidad"


class BibliotecaTests(unittest.TestCase):
    def _copia(self, temporal: str) -> Path:
        destino = Path(temporal) / "biblioteca"
        shutil.copytree(EJEMPLO, destino)
        return destino

    @staticmethod
    def _reemplazar(ruta: Path, antes: str, despues: str) -> None:
        texto = ruta.read_text(encoding="utf-8")
        if antes not in texto:
            raise AssertionError(f"el test no encontró {antes!r} en {ruta}")
        ruta.write_text(texto.replace(antes, despues), encoding="utf-8")

    @staticmethod
    def _instalar_metadata(base: Path, nombre=NOMBRE_DISTRIBUCION, version="0.1.0"):
        relativa = ruta_instalada_del_manifiesto(nombre)
        destino = base.joinpath(*relativa.parts).parent
        shutil.copytree(EJEMPLO, destino)
        normalizado = nombre.replace("-", "_").replace(".", "_")
        dist_info = base / f"{normalizado}-{version}.dist-info"
        dist_info.mkdir()
        (dist_info / "METADATA").write_text(
            f"Metadata-Version: 2.1\nName: {nombre}\nVersion: {version}\n",
            encoding="utf-8",
        )
        instalados = [p.relative_to(base).as_posix() for p in destino.rglob("*") if p.is_file()]
        instalados.extend([
            f"{dist_info.name}/METADATA",
            f"{dist_info.name}/RECORD",
        ])
        (dist_info / "RECORD").write_text(
            "".join(f"{ruta},,\n" for ruta in instalados), encoding="utf-8")
        return next(d for d in metadata.distributions(path=[base])
                    if d.metadata.get("Name") == nombre)

    def test_descubre_la_distribucion_por_metadata_y_ruta_fija_sin_importarla(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            distribucion = self._instalar_metadata(base)
            peligro = base / "paquete_que_no_debe_importarse.py"
            peligro.write_text('raise AssertionError("el descubrimiento importó código")\n',
                                encoding="utf-8")

            descubiertas = descubrir_bibliotecas(distribuciones=[distribucion])

        self.assertEqual(list(descubiertas), ["segtem.meta.calidad"])
        self.assertEqual(descubiertas["segtem.meta.calidad"].version, "0.1.0")
        self.assertNotIn("paquete_que_no_debe_importarse", sys.modules)

    def test_una_distribucion_instalada_sin_la_ruta_fija_no_es_biblioteca(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            distribucion = self._instalar_metadata(base)
            record = next(base.glob("*.dist-info/RECORD"))
            record.write_text(
                "".join(line for line in record.read_text(encoding="utf-8").splitlines(True)
                        if not line.startswith("oracle_bibliotecas/")),
                encoding="utf-8",
            )
            distribucion = next(metadata.distributions(path=[base]))
            self.assertEqual(descubrir_bibliotecas(distribuciones=[distribucion]), {})

    def test_metadata_sin_nombre_no_puede_convertirse_en_una_ruta(self) -> None:
        sin_nombre = SimpleNamespace(metadata={"Name": ""}, files=())
        self.assertEqual(descubrir_bibliotecas(distribuciones=[sin_nombre]), {})

    def test_dos_distribuciones_con_el_mismo_id_fallan_cerrado(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            primera = self._instalar_metadata(base)
            segunda = self._instalar_metadata(base, nombre="otra-biblioteca-oracle")
            with self.assertRaisesRegex(BibliotecaInvalida, "id de biblioteca ambiguo"):
                descubrir_bibliotecas(distribuciones=[primera, segunda])

    def test_la_version_instalada_y_la_publicada_no_pueden_divergir(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            distribucion = self._instalar_metadata(Path(td), version="0.2.0")
            with self.assertRaisesRegex(BibliotecaInvalida, "instala versión.*manifiesto"):
                descubrir_bibliotecas(distribuciones=[distribucion])

    def test_una_distribucion_de_biblioteca_con_python_se_rechaza_sin_importarlo(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            self._instalar_metadata(base)
            modulo = base / "codigo_ajeno.py"
            modulo.write_text('raise AssertionError("no ejecutar")\n', encoding="utf-8")
            record = next(base.glob("*.dist-info/RECORD"))
            record.write_text(
                record.read_text(encoding="utf-8") + "codigo_ajeno.py,,\n", encoding="utf-8")
            distribucion = next(metadata.distributions(path=[base]))
            with self.assertRaisesRegex(BibliotecaInvalida, "no ejecuta código"):
                descubrir_bibliotecas(distribuciones=[distribucion])
            self.assertNotIn("codigo_ajeno", sys.modules)

    def test_el_ejemplo_publica_y_sostiene_su_numero_de_mutacion(self) -> None:
        informe = verificar_biblioteca(EJEMPLO)

        self.assertEqual(informe.manifiesto.id, "segtem.meta.calidad")
        self.assertEqual(informe.manifiesto.version, "0.1.0")
        self.assertEqual(informe.manifiesto.certificacion_mutantes, 12)
        self.assertEqual(informe.mutantes, 12)
        self.assertEqual(informe.medidas, 2)
        self.assertEqual(informe.casos, 3)
        self.assertEqual(informe.defectos_rojos, 2)
        self.assertEqual(informe.verdes_correctos, 1)
        self.assertEqual(informe.relaciones, 0)

    def test_sin_numero_positivo_y_coincidente_no_se_certifica(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            manifiesto = biblioteca / "oracle-biblioteca.toml"
            self._reemplazar(manifiesto, "\n[certificacion]\nmutantes = 12\n", "")
            with self.assertRaisesRegex(BibliotecaInvalida, "faltan.*certificacion"):
                cargar_manifiesto(biblioteca)

        for valor in ("0", "true", '"12"'):
            with self.subTest(valor=valor), tempfile.TemporaryDirectory() as td:
                biblioteca = self._copia(td)
                manifiesto = biblioteca / "oracle-biblioteca.toml"
                self._reemplazar(manifiesto, "mutantes = 12", f"mutantes = {valor}")
                with self.assertRaisesRegex(BibliotecaInvalida, "entero positivo"):
                    cargar_manifiesto(biblioteca)

        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            manifiesto = biblioteca / "oracle-biblioteca.toml"
            self._reemplazar(manifiesto, "mutantes = 12", "mutantes = 1")
            self.assertEqual(cargar_manifiesto(biblioteca).certificacion_mutantes, 1)

        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            manifiesto = biblioteca / "oracle-biblioteca.toml"
            self._reemplazar(manifiesto, "mutantes = 12", "mutantes = 11")
            with self.assertRaisesRegex(BibliotecaInvalida, "publica 11.*mide 12"):
                verificar_biblioteca(biblioteca)

    def test_el_manifiesto_rechaza_textos_y_listas_ambiguas(self) -> None:
        for declaracion in ('id = 1', 'id = ""', 'id = " segtem.meta.calidad "'):
            with self.subTest(declaracion=declaracion), tempfile.TemporaryDirectory() as td:
                biblioteca = self._copia(td)
                manifiesto = biblioteca / "oracle-biblioteca.toml"
                self._reemplazar(
                    manifiesto, 'id = "segtem.meta.calidad"', declaracion)
                with self.assertRaisesRegex(BibliotecaInvalida, "texto no vacío y sin bordes"):
                    cargar_manifiesto(biblioteca)

        for declaracion in (
            'catalogos = "catalogos"',
            "catalogos = [1]",
            'catalogos = ["catalogos", "catalogos"]',
        ):
            with self.subTest(declaracion=declaracion), tempfile.TemporaryDirectory() as td:
                biblioteca = self._copia(td)
                manifiesto = biblioteca / "oracle-biblioteca.toml"
                self._reemplazar(manifiesto, 'catalogos = ["catalogos"]', declaracion)
                with self.assertRaisesRegex(BibliotecaInvalida, "lista de rutas sin duplicados"):
                    cargar_manifiesto(biblioteca)

        for declaracion in (
            'relaciones = "medida"',
            "relaciones = [1]",
            'relaciones = [""]',
            'relaciones = [" medida"]',
            'relaciones = ["medida", "medida"]',
        ):
            with self.subTest(declaracion=declaracion), tempfile.TemporaryDirectory() as td:
                biblioteca = self._copia(td)
                manifiesto = biblioteca / "oracle-biblioteca.toml"
                self._reemplazar(manifiesto, 'relaciones = ["medida"]', declaracion)
                with self.assertRaisesRegex(BibliotecaInvalida, "lista de nombres sin duplicados"):
                    cargar_manifiesto(biblioteca)

    def test_las_rutas_del_manifiesto_quedan_confinadas_y_son_fisicas(self) -> None:
        for declaracion, mensaje in (
            ('catalogos = [""]', "ruta POSIX relativa no vacía"),
            ("catalogos = ['a\\b']", "ruta POSIX relativa no vacía"),
            ('catalogos = ["/"]', "debe quedar dentro"),
            ('catalogos = ["../catalogos"]', "debe quedar dentro"),
            ('catalogos = ["ausente"]', "directorio físico"),
        ):
            with self.subTest(declaracion=declaracion), tempfile.TemporaryDirectory() as td:
                biblioteca = self._copia(td)
                manifiesto = biblioteca / "oracle-biblioteca.toml"
                self._reemplazar(manifiesto, 'catalogos = ["catalogos"]', declaracion)
                with self.assertRaisesRegex(BibliotecaInvalida, mensaje):
                    cargar_manifiesto(biblioteca)

        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            (biblioteca / "catalogos-enlace").symlink_to(
                biblioteca / "catalogos", target_is_directory=True)
            manifiesto = biblioteca / "oracle-biblioteca.toml"
            self._reemplazar(
                manifiesto, 'catalogos = ["catalogos"]', 'catalogos = ["catalogos-enlace"]')
            with self.assertRaisesRegex(BibliotecaInvalida, "directorio físico"):
                cargar_manifiesto(biblioteca)

        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as afuera:
            biblioteca = self._copia(td)
            (biblioteca / "intermedio").symlink_to(Path(afuera), target_is_directory=True)
            (Path(afuera) / "catalogos").mkdir()
            manifiesto = biblioteca / "oracle-biblioteca.toml"
            self._reemplazar(
                manifiesto, 'catalogos = ["catalogos"]',
                'catalogos = ["intermedio/catalogos"]')
            with self.assertRaisesRegex(BibliotecaInvalida, "escapa de la biblioteca"):
                cargar_manifiesto(biblioteca)

    def test_la_raiz_y_el_manifiesto_tienen_que_ser_fisicos(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            enlace = Path(td) / "biblioteca-enlace"
            enlace.symlink_to(EJEMPLO, target_is_directory=True)
            with self.assertRaisesRegex(BibliotecaInvalida, "directorio físico"):
                cargar_manifiesto(enlace)

        with tempfile.TemporaryDirectory() as td:
            archivo = Path(td) / "biblioteca"
            archivo.write_text("no es un directorio\n", encoding="utf-8")
            with self.assertRaisesRegex(BibliotecaInvalida, "directorio físico"):
                cargar_manifiesto(archivo)

        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            manifiesto = biblioteca / "oracle-biblioteca.toml"
            real = biblioteca / "manifiesto-real.toml"
            manifiesto.rename(real)
            manifiesto.symlink_to(real)
            with self.assertRaisesRegex(BibliotecaInvalida, "falta oracle-biblioteca.toml"):
                cargar_manifiesto(biblioteca)

        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            (biblioteca / "oracle-biblioteca.toml").unlink()
            with self.assertRaisesRegex(BibliotecaInvalida, "falta oracle-biblioteca.toml"):
                cargar_manifiesto(biblioteca)

    def test_un_caso_no_puede_reclamar_una_medida_ausente(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            caso = biblioteca / "corpus" / "001-medida-sin-alcance.caso"
            self._reemplazar(
                caso,
                "medida: meta.segtem.ninguna_medida_sin_alcance",
                "medida: meta.segtem.ausente",
            )
            with self.assertRaisesRegex(BibliotecaInvalida, "reclama una medida ausente"):
                verificar_biblioteca(biblioteca)

    def test_un_mutante_vivo_invalida_la_certificacion_en_vez_de_taparse(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            caso = biblioteca / "corpus" / "002-seis-umbrales-sin-origen.caso"
            self._reemplazar(
                caso,
                '            "dominio.sin_origen_6", "sin_declarar"\n',
                '            "dominio.sin_origen_6", "sin_declarar"\n'
                '            "dominio.sin_origen_7", "sin_declarar"\n',
            )
            with self.assertRaisesRegex(BibliotecaInvalida, "no se certifica.*sobrevivieron"):
                verificar_biblioteca(biblioteca)

    def test_listar_muestra_el_aflojamiento_y_el_alcance_completo(self) -> None:
        salida = io.StringIO()
        with redirect_stdout(salida):
            rc = cli.main(["biblioteca", "listar", str(EJEMPLO)])

        texto = salida.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("MUTACIÓN PUBLICADA · 12/12", texto)
        self.assertIn("meta.segtem.ninguna_medida_sin_alcance\n    UMBRAL:  <= 0", texto)
        self.assertIn("meta.segtem.todo_umbral_declara_origen\n    UMBRAL:  <= 5", texto)
        self.assertEqual(texto.count("    SEGUN:   contrato"), 2)
        self.assertIn(
            "    ALCANCE: ve si una medida declara algún alcance.\n"
            "             NO juzga si ese alcance es suficiente ni verdadero",
            texto,
        )

    def test_rechaza_versiones_del_lenguaje_incompatibles(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            manifiesto = biblioteca / "oracle-biblioteca.toml"
            self._reemplazar(manifiesto, 'algebra = "0.5"', 'algebra = "9.0"')

            with self.assertRaisesRegex(BibliotecaInvalida, "pide álgebra 9.0"):
                cargar_manifiesto(biblioteca)

    def test_rechaza_ids_de_medida_duplicados_entre_catalogos(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            segundo = biblioteca / "catalogos-2"
            segundo.mkdir()
            original = next((biblioteca / "catalogos").glob("*.oracle"))
            shutil.copy2(original, segundo / "duplicada.oracle")
            manifiesto = biblioteca / "oracle-biblioteca.toml"
            self._reemplazar(
                manifiesto,
                'catalogos = ["catalogos"]',
                'catalogos = ["catalogos", "catalogos-2"]',
            )

            with self.assertRaisesRegex(BibliotecaInvalida, "dos veces"):
                verificar_biblioteca(biblioteca)

    def test_rechaza_relaciones_no_declaradas_y_casos_que_no_las_traen(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            manifiesto = biblioteca / "oracle-biblioteca.toml"
            self._reemplazar(manifiesto, 'relaciones = ["medida"]', "relaciones = []")
            with self.assertRaisesRegex(BibliotecaInvalida, "no declara.*medida"):
                verificar_biblioteca(biblioteca)

        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            caso = biblioteca / "corpus" / "001-medida-sin-alcance.caso"
            self._reemplazar(caso, "        medida: id, alcance", "        pieza: id, alcance")
            with self.assertRaisesRegex(BibliotecaInvalida, "no trae relaciones necesarias.*medida"):
                verificar_biblioteca(biblioteca)

    def test_rechaza_medidas_sin_caso_y_expectativas_incorrectas(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            (biblioteca / "corpus" / "002-seis-umbrales-sin-origen.caso").unlink()
            with self.assertRaisesRegex(BibliotecaInvalida, "medidas sin ningún caso"):
                verificar_biblioteca(biblioteca)

        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            caso = biblioteca / "corpus" / "001-medida-sin-alcance.caso"
            self._reemplazar(caso, "etiqueta: falso_verde", "etiqueta: verde_correcto")
            with self.assertRaisesRegex(BibliotecaInvalida, "esperaba VERDE"):
                verificar_biblioteca(biblioteca)

    def test_datos_solamente_rechaza_codigo_y_symlinks_sin_ejecutarlos(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            (biblioteca / "instalar.py").write_text(
                'raise AssertionError("este archivo no debe ejecutarse")\n', encoding="utf-8")
            with self.assertRaisesRegex(BibliotecaInvalida, "no ejecuta código"):
                cargar_manifiesto(biblioteca)

        with tempfile.TemporaryDirectory() as td:
            biblioteca = self._copia(td)
            (biblioteca / "enlace").symlink_to(biblioteca / "catalogos", target_is_directory=True)
            with self.assertRaisesRegex(BibliotecaInvalida, "no admite symlinks"):
                cargar_manifiesto(biblioteca)

    def test_cli_certifica_sin_proyecto_y_falla_cerrado(self) -> None:
        salida = io.StringIO()
        with redirect_stdout(salida):
            rc = cli.main(["biblioteca", "verificar", str(EJEMPLO)])
        self.assertEqual(rc, 0)
        self.assertIn("BIBLIOTECA CERTIFICADA · segtem.meta.calidad 0.1.0", salida.getvalue())
        self.assertIn("12/12 mutantes muertos", salida.getvalue())

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            rc = cli.main(["biblioteca", "verificar", str(EJEMPLO / "ausente")])
        self.assertEqual(rc, 1)
        self.assertIn("BIBLIOTECA INVÁLIDA", stderr.getvalue())

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            rc = cli.main(["biblioteca", "listar", str(EJEMPLO / "ausente")])
        self.assertEqual(rc, 1)
        self.assertIn("BIBLIOTECA INVÁLIDA", stderr.getvalue())

    def test_cli_ofrece_ayuda_y_rechaza_formas_ambiguas(self) -> None:
        salida = io.StringIO()
        with redirect_stdout(salida):
            self.assertEqual(cli.main(["biblioteca"]), 0)
        self.assertIn("biblioteca listar", salida.getvalue())

        for argv, mensaje in (
            (["biblioteca", "publicar"], "verbo desconocido"),
            (["biblioteca", "verificar"], "falta la ruta"),
            (["biblioteca", "listar", str(EJEMPLO), "extra"], "sobran argumentos"),
        ):
            with self.subTest(argv=argv):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    rc = cli.main(argv)
                self.assertEqual(rc, 1)
                self.assertIn(mensaje, salida.getvalue())


if __name__ == "__main__":
    unittest.main()


class AndamioDeBiblioteca(unittest.TestCase):
    """`oracle biblioteca nueva`: el esqueleto, con la ruta fija ya puesta.

    El descubrimiento busca el manifiesto en un lugar derivado del nombre de la distribución y en
    ningún otro. Armar esa ruta a mano es donde se equivoca todo el mundo la primera vez, y el
    error es SILENCIOSO: la biblioteca no aparece y nada dice por qué.
    """

    def _crear(self, bid="aula.calidad", destino=None):
        from nucleo.biblioteca import andamio
        return andamio(Path(destino), bid, algebra="0.5", sintaxis="0.1")

    def test_el_manifiesto_queda_donde_el_descubrimiento_lo_busca(self) -> None:
        from nucleo.biblioteca import ruta_instalada_del_manifiesto
        with tempfile.TemporaryDirectory() as td:
            raiz_datos = self._crear(destino=Path(td) / "x")
            esperada = ruta_instalada_del_manifiesto("oracle-biblioteca-aula-calidad")
            real = (raiz_datos / "oracle-biblioteca.toml").relative_to(Path(td) / "x")
        self.assertEqual(real.as_posix(), str(esperada))

    def test_el_manifiesto_generado_se_puede_cargar(self) -> None:
        """Un andamio que produce un manifiesto ilegible es peor que no tenerlo."""
        from nucleo.biblioteca import cargar_manifiesto
        with tempfile.TemporaryDirectory() as td:
            raiz_datos = self._crear(destino=Path(td) / "x")
            manifiesto = cargar_manifiesto(raiz_datos)
        self.assertEqual(manifiesto.id, "aula.calidad")
        self.assertEqual(manifiesto.algebra, "0.5")

    def test_los_mutantes_arrancan_en_uno_porque_cero_se_rechaza(self) -> None:
        """La plantilla no puede proponer un flujo imposible: con `mutantes = 0` el manifiesto se
        rechaza antes de llegar a `verificar`, que es quien dice el número real."""
        with tempfile.TemporaryDirectory() as td:
            raiz_datos = self._crear(destino=Path(td) / "x")
            texto = (raiz_datos / "oracle-biblioteca.toml").read_text(encoding="utf-8")
        self.assertIn("mutantes = 1", texto)
        self.assertNotIn("mutantes = 0", texto)

    def test_el_pyproject_empaqueta_los_datos_y_ninguna_dependencia(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            self._crear(destino=Path(td) / "x")
            texto = (Path(td) / "x" / "pyproject.toml").read_text(encoding="utf-8")
        for esperado in ("oracle-biblioteca.toml", "catalogos/*.oracle", "corpus/*.caso"):
            self.assertIn(esperado, texto)
        # Contra una LÍNEA de declaración, no contra la palabra: el comentario de la plantilla
        # explica justamente por qué no hay dependencias, y contendría la palabra igual.
        declara = [l for l in texto.splitlines()
                   if l.strip().startswith("dependencies")]
        self.assertEqual(declara, [], "una biblioteca de políticas es DATOS: sin dependencias")

    def test_un_id_invalido_falla_cerrado(self) -> None:
        from nucleo.biblioteca import BibliotecaInvalida
        for malo in ("SinPunto", "con.MAYUSCULAS", "con espacio", "", "punto.", ".punto"):
            with tempfile.TemporaryDirectory() as td, self.subTest(id=malo):
                with self.assertRaises(BibliotecaInvalida):
                    self._crear(malo, Path(td) / "x")

    def test_no_pisa_un_directorio_con_contenido(self) -> None:
        from nucleo.biblioteca import BibliotecaInvalida
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "x").mkdir()
            (Path(td) / "x" / "algo.txt").write_text("no me borres", encoding="utf-8")
            with self.assertRaises(BibliotecaInvalida):
                self._crear(destino=Path(td) / "x")
            self.assertTrue((Path(td) / "x" / "algo.txt").exists())

