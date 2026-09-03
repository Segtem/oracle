"""Contrato del diagnóstico local: qué sale, qué NUNCA sale, y quién lo vigila."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from nucleo.diagnostico import (Diagnostico, MARCA_HOME, MARCA_PROYECTO, hechos_de_diagnostico,
                                redactar, reunir)
from nucleo.proyecto import Proyecto


def _proyecto(raiz: Path) -> Proyecto:
    (raiz / "catalogos" / "dominio").mkdir(parents=True)
    (raiz / "corpus").mkdir()
    (raiz / "catalogos" / "dominio" / "dominio.secreta.oracle").write_text("x", encoding="utf-8")
    return Proyecto(raiz)


class LoQueSale(unittest.TestCase):
    """El diagnóstico existe para pegarse en un issue público. Sale la FORMA, nunca el contenido."""

    def test_trae_las_tres_versiones_y_la_plataforma(self) -> None:
        datos = reunir().datos
        self.assertEqual(set(datos["oracle"]),
                         {"distribucion", "algebra", "sintaxis", "corriendo_desde"})
        self.assertEqual(set(datos["entorno"]), {"python", "sistema", "arquitectura"})

    def test_no_incluye_el_nombre_del_host(self) -> None:
        """`platform.node()` identifica una máquina y no ayuda a reproducir nada."""
        import platform
        host = platform.node()
        if not host or len(host) < 3:
            self.skipTest("esta máquina no tiene un nombre de host distinguible")
        self.assertNotIn(host, str(reunir().datos))

    def test_del_proyecto_sale_la_forma_y_no_los_nombres(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy = _proyecto(Path(td))
            datos = reunir(proy).datos
        self.assertEqual(datos["proyecto"]["medidas"], 1)
        self.assertTrue(datos["proyecto"]["carpetas"]["catalogos"])
        self.assertFalse(datos["proyecto"]["carpetas"]["diferencial"])
        self.assertNotIn("dominio.secreta", str(datos),
                         "el nombre de una medida del dominio NO puede salir")

    def test_sin_proyecto_igual_diagnostica(self) -> None:
        """La mitad de los reportes empiezan porque el proyecto NO se resuelve."""
        self.assertIsNone(reunir().datos["proyecto"])


class LaFormaCuentaBien(unittest.TestCase):
    """Los conteos son lo único cuantitativo que sale: si mienten, el diagnóstico desorienta."""

    def test_cuenta_medidas_en_las_dos_extensiones_y_nada_mas(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos" / "d").mkdir(parents=True)
            (raiz / "corpus").mkdir()
            for nombre in ("a.oracle", "b.json", "LEEME.md", "c.pyc"):
                (raiz / "catalogos" / "d" / nombre).write_text("x", encoding="utf-8")
            datos = reunir(Proyecto(raiz)).datos
        self.assertEqual(datos["proyecto"]["medidas"], 2, "sólo .oracle y .json son medidas")

    def test_cuenta_casos_en_las_dos_extensiones_y_nada_mas(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            (raiz / "corpus" / "g").mkdir(parents=True)
            for nombre in ("a.caso", "b.json", "notas.txt"):
                (raiz / "corpus" / "g" / nombre).write_text("x", encoding="utf-8")
            datos = reunir(Proyecto(raiz)).datos
        self.assertEqual(datos["proyecto"]["casos"], 2)

    def test_sin_las_carpetas_los_conteos_son_cero_y_no_revientan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            datos = reunir(Proyecto(raiz)).datos
        self.assertEqual((datos["proyecto"]["medidas"], datos["proyecto"]["casos"]), (0, 0))
        self.assertFalse(datos["proyecto"]["carpetas"]["corpus"])

    def test_una_carpeta_con_nombre_de_medida_no_cuenta_como_medida(self) -> None:
        """`rglob("*")` devuelve DIRECTORIOS. Sin `is_file()`, una carpeta `x.json` contaría."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos" / "trampa.json").mkdir(parents=True)
            (raiz / "corpus" / "trampa.caso").mkdir(parents=True)
            (raiz / "catalogos" / "real.oracle").write_text("x", encoding="utf-8")
            datos = reunir(Proyecto(raiz)).datos
        self.assertEqual(datos["proyecto"]["medidas"], 1)
        self.assertEqual(datos["proyecto"]["casos"], 0)

    def test_el_diagnostico_no_se_puede_modificar_despues(self) -> None:
        """Es lo que alguien revisó antes de compartir. Si se le pudiera agregar un campo
        después, la revisión dejaría de valer."""
        import dataclasses
        d = reunir()
        with self.assertRaises(dataclasses.FrozenInstanceError):
            d.datos = {}


class LasRutasSeRedactan(unittest.TestCase):
    def test_el_home_se_reemplaza(self) -> None:
        self.assertEqual(redactar(str(Path.home()) + "/x"), f"{MARCA_HOME}/x")

    def test_el_proyecto_gana_sobre_el_home_cuando_esta_adentro(self) -> None:
        """Al revés, `<HOME>/Dev/proyecto` dejaría el nombre del proyecto a la vista."""
        # El home es un dato de entrada para la redacción, no un requisito de escritura: simularlo
        # permite comprobar la jerarquía aun cuando el home real esté montado como sólo lectura.
        with tempfile.TemporaryDirectory() as td, mock.patch.object(Path, "home", return_value=Path(td)):
            raiz = Path(td) / "proyecto"
            raiz.mkdir()
            proy = Proyecto(raiz)
            redactado = redactar(str(raiz.resolve() / "catalogos"), proy)
        self.assertEqual(redactado, f"{MARCA_PROYECTO}/catalogos")
        self.assertNotIn(raiz.name, redactado)

    def test_reemplaza_el_mas_largo_primero(self) -> None:
        """Si se ordenara por el reemplazo en vez de por la aguja, o al revés por longitud, el
        home taparía al proyecto y el nombre del directorio quedaría publicado."""
        with tempfile.TemporaryDirectory() as td, mock.patch.object(Path, "home", return_value=Path(td)):
            raiz = Path(td) / "proyecto"
            raiz.mkdir()
            proy = Proyecto(raiz)
            salida = redactar(f"{raiz.resolve()}/x y {Path.home()}/z", proy)
        self.assertEqual(salida.count(MARCA_PROYECTO), 1)
        self.assertEqual(salida.count(MARCA_HOME), 1)
        self.assertNotIn(raiz.name, salida)

    def test_un_texto_sin_rutas_no_se_toca(self) -> None:
        self.assertEqual(redactar("Linux x86_64"), "Linux x86_64")


class ElContratoSeMide(unittest.TestCase):
    """Que «nunca sale evidencia» sea prosa en un docstring no alcanza.

    Un campo agregado el martes puede filtrar sin que nadie lo note hasta que alguien pegue el
    JSON en un issue. Por eso hay hechos y una medida, no un comentario.
    """

    def test_marca_lo_que_se_colo_y_dice_que_fue(self) -> None:
        sucio = Diagnostico({"oracle": {"corriendo_desde": "/casa/alguien/proy"},
                             "medida_que_fallo": "dominio.secreta"})
        filas = hechos_de_diagnostico(sucio, ["/casa/alguien", "dominio.secreta"])
        self.assertEqual([f["es_del_dominio"] for f in filas["campo_diagnostico"]], [True, True])
        self.assertEqual(filas["campo_diagnostico"][1]["que_se_colo"], "dominio.secreta")

    def test_un_diagnostico_limpio_no_marca_nada(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy = _proyecto(Path(td))
            filas = hechos_de_diagnostico(
                reunir(proy), [str(Path(td).resolve()), str(Path.home()), "dominio.secreta"])
        self.assertEqual([f for f in filas["campo_diagnostico"] if f["es_del_dominio"]], [])

    def test_compara_por_contenido_y_no_por_igualdad(self) -> None:
        """Una ruta que EMPIEZA con el home ya publicó el usuario aunque siga con otra cosa."""
        sucio = Diagnostico({"ruta": "/casa/alguien/otra/cosa/mas"})
        filas = hechos_de_diagnostico(sucio, ["/casa/alguien"])["campo_diagnostico"]
        self.assertTrue(filas[0]["es_del_dominio"])

    def test_el_nombre_de_lo_que_se_colo_se_corta_en_cuarenta(self) -> None:
        """El testigo dice QUÉ se filtró, no el valor entero: un testigo que reimprime el secreto
        lo publica igual, y el diagnóstico está hecho para pegarse en un issue."""
        largo = "s" * 200
        filas = hechos_de_diagnostico(Diagnostico({"a": largo}), [largo])["campo_diagnostico"]
        self.assertEqual(len(filas[0]["que_se_colo"]), 40)

    def test_recorre_listas_y_diccionarios_anidados(self) -> None:
        sucio = Diagnostico({"bibliotecas": [{"id": "x"}, {"id": "dominio.secreta"}]})
        filas = hechos_de_diagnostico(sucio, ["dominio.secreta"])["campo_diagnostico"]
        self.assertEqual([f["campo"] for f in filas], ["bibliotecas[0].id", "bibliotecas[1].id"])
        self.assertEqual([f["es_del_dominio"] for f in filas], [False, True])

    def test_un_secreto_vacio_no_marca_todo(self) -> None:
        """`"" in texto` es siempre verdadero: sin este filtro, un secreto vacío pondría TODO
        en rojo y el diagnóstico dejaría de poder usarse."""
        sucio = Diagnostico({"a": "hola"})
        filas = hechos_de_diagnostico(sucio, ["", "   ", None])["campo_diagnostico"]
        self.assertFalse(filas[0]["es_del_dominio"])


if __name__ == "__main__":
    unittest.main()
