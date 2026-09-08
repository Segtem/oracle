"""Contrato de `oracle reportar`: vista previa local, completa y sin publicación automática."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from nucleo.diagnostico import Diagnostico
from tools import cli, manual, reportar


DIAGNOSTICO = Diagnostico({
    "oracle": {"distribucion": "0.7.0", "algebra": "0.6", "sintaxis": "0.2"},
    "entorno": {"python": "3.13.0", "sistema": "Linux", "arquitectura": "x86_64"},
    "proyecto": None,
    "bibliotecas": [],
    "perfiles": [],
})

REPORTE_MINIMO = """# Reporte de límite de Oracle

## sintoma

### que_se_quiso_expresar_o_medir

```text
Medir piezas sin dueño
```

### que_ocurrio_en_cambio

```text
El lenguaje no pudo expresar la ausencia
```

## como_se_detecto

`persona`

## diagnostico

```json
{
  "oracle": {
    "distribucion": "0.7.0",
    "algebra": "0.6",
    "sintaxis": "0.2"
  },
  "entorno": {
    "python": "3.13.0",
    "sistema": "Linux",
    "arquitectura": "x86_64"
  },
  "proyecto": null,
  "bibliotecas": [],
  "perfiles": []
}
```
"""


class PreparacionTests(unittest.TestCase):

    def test_por_omision_sale_el_reporte_entero_y_nada_sensible(self) -> None:
        """La ausencia de banderas es una decisión de privacidad, no un reporte incompleto por
        casualidad: ni `medida` ni `evidencia` pueden aparecer por búsqueda automática."""
        hecho = reportar.preparar(
            esperado="Medir piezas sin dueño",
            ocurrido="El lenguaje no pudo expresar la ausencia",
            como_se_detecto="persona",
            diagnostico=DIAGNOSTICO,
        )
        self.assertEqual(hecho.texto, REPORTE_MINIMO)

    def test_medida_y_evidencia_aparecen_enteras_cuando_se_incluyen(self) -> None:
        """El consentimiento vale sobre el contenido visible. Recortar la evidencia en la vista
        previa haría que la persona autorizara algo distinto de lo que después copia."""
        hecho = reportar.preparar(
            esperado="Medir piezas sin dueño",
            ocurrido="El lenguaje no pudo expresar la ausencia",
            como_se_detecto="persona",
            diagnostico=DIAGNOSTICO,
            medida="dominio.pieza_sin_dueno",
            evidencia='pieza: id, nombre\n    "p-7", "cliente ACME"',
        )
        self.assertEqual(
            hecho.texto,
            REPORTE_MINIMO
            + "\n## medida\n\n```text\ndominio.pieza_sin_dueno\n```\n"
            + "\n## evidencia\n\n```text\npieza: id, nombre\n"
              '    "p-7", "cliente ACME"\n```\n')

    def test_redacta_rutas_conocidas_en_todas_las_partes_escritas(self) -> None:
        """Una ruta se puede colar en la explicación además de en las filas. Redactar sólo el
        archivo optativo dejaría el mismo dato personal visible por otro campo."""
        with tempfile.TemporaryDirectory(dir=Path.home()) as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            from nucleo.proyecto import Proyecto
            proy = Proyecto(raiz)
            absoluto = str(raiz.resolve())
            hecho = reportar.preparar(
                esperado=f"Abrir {absoluto}/catalogos",
                ocurrido=f"Falló bajo {Path.home()}/otro",
                como_se_detecto="observacion",
                diagnostico=DIAGNOSTICO,
                medida=f"definida en {absoluto}/catalogos/x.oracle",
                evidencia=f'ruta: "{absoluto}/datos.json"',
                proy=proy,
            )
        self.assertEqual(absoluto in hecho.texto, False)
        self.assertEqual(str(Path.home()) in hecho.texto, False)
        self.assertEqual(hecho.texto.count("<PROYECTO>"), 3)
        self.assertEqual(hecho.texto.count("<HOME>"), 1)

    def test_una_cerca_markdown_en_la_evidencia_no_oculta_el_resto(self) -> None:
        """La vista previa es el borde de consentimiento. Si una cerca aportada pudiera cerrarla,
        el render escondería o reinterpretaría una parte de lo que está por compartirse."""
        hecho = reportar.preparar(
            esperado="uno", ocurrido="dos", como_se_detecto="accidente",
            diagnostico=DIAGNOSTICO, evidencia="antes\n```\ndespués")
        bloque = hecho.texto.split("## evidencia\n\n", 1)[1]
        self.assertEqual(bloque, "````text\nantes\n```\ndespués\n````\n")

    def test_rechaza_campos_vacios_y_detecciones_inventadas(self) -> None:
        """Un artefacto vacío parece publicable pero no permite actuar; una detección libre deja
        de compartir el vocabulario de los casos al que el reporte aspira."""
        with self.assertRaisesRegex(reportar.ReporteInvalido, "`esperado` no puede estar vacío"):
            reportar.preparar(esperado="  ", ocurrido="pasó", como_se_detecto="persona",
                              diagnostico=DIAGNOSTICO)
        with self.assertRaisesRegex(reportar.ReporteInvalido, "debe ser una de"):
            reportar.preparar(esperado="quise", ocurrido="pasó", como_se_detecto="magia",
                              diagnostico=DIAGNOSTICO)


class ReportarCliTests(unittest.TestCase):

    @staticmethod
    def _correr(argv: list[str]):
        salida, error = io.StringIO(), io.StringIO()
        with redirect_stdout(salida), redirect_stderr(error), \
                mock.patch.object(cli, "_diagnostico_actual", return_value=DIAGNOSTICO):
            codigo = cli.main(argv)
        return codigo, salida.getvalue(), error.getvalue()

    @staticmethod
    def _proyecto(raiz: Path) -> list[str]:
        (raiz / "catalogos").mkdir()
        (raiz / "corpus").mkdir()
        return ["--proyecto", str(raiz)]

    def test_las_banderas_producen_exactamente_el_artefacto_copiable(self) -> None:
        """Los avisos van por stderr: stdout debe poder redirigirse o copiarse sin limpiar texto
        que no pertenece al cuerpo del issue."""
        with tempfile.TemporaryDirectory() as td:
            codigo, salida, error = self._correr([
                "reportar", "--esperado", "Medir piezas sin dueño",
                "--ocurrido", "El lenguaje no pudo expresar la ausencia",
                "--como-se-detecto", "persona", *self._proyecto(Path(td))])
        self.assertEqual(codigo, 0)
        self.assertEqual(salida, REPORTE_MINIMO)
        self.assertEqual(
            error,
            "Revisá el reporte entero antes de copiarlo. Oracle no lo manda a ningún lado.\n"
            "Si decidís publicarlo, copiá el artefacto a un issue público de Segtem/oracle.\n")

    def test_aun_si_se_guarda_se_muestra_entero_y_ambas_copias_son_iguales(self) -> None:
        """Guardar no reemplaza la revisión. Ese fue el borde ya establecido por diagnóstico y
        acá es más importante porque el reporte puede llevar contenido del dominio."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            proyecto = self._proyecto(raiz)
            destino = raiz / "reporte.md"
            codigo, salida, error = self._correr([
                "reportar", "--esperado", "Medir piezas sin dueño",
                "--ocurrido", "El lenguaje no pudo expresar la ausencia",
                "--como-se-detecto", "persona", "--salida", str(destino), *proyecto])
            guardado = destino.read_text(encoding="utf-8")
        self.assertEqual(codigo, 0)
        self.assertEqual(salida, REPORTE_MINIMO)
        self.assertEqual(guardado, REPORTE_MINIMO)
        self.assertEqual(
            error,
            f"escrito: {destino}\n"
            "Revisá el reporte entero antes de copiarlo. Oracle no lo manda a ningún lado.\n"
            "Si decidís publicarlo, copiá el artefacto a un issue público de Segtem/oracle.\n")

    def test_no_toca_el_corpus_ni_pregunta_por_contenido_sensible(self) -> None:
        """Preparar información no autoriza a registrarla como caso. Además, preguntar por medida
        o evidencia convertiría su omisión en una elección sugerida en vez del valor seguro."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            proyecto = self._proyecto(raiz)
            with mock.patch("builtins.input", side_effect=[
                    "Medir piezas sin dueño",
                    "El lenguaje no pudo expresar la ausencia",
                    "persona",
            ]) as entrada:
                codigo, salida, error = self._correr(["reportar", *proyecto])
            archivos = sorted(p.relative_to(raiz).as_posix()
                               for p in raiz.rglob("*") if p.is_file())
        self.assertEqual(codigo, 0)
        self.assertEqual(salida, REPORTE_MINIMO)
        self.assertEqual(
            error,
            "Revisá el reporte entero antes de copiarlo. Oracle no lo manda a ningún lado.\n"
            "Si decidís publicarlo, copiá el artefacto a un issue público de Segtem/oracle.\n")
        self.assertEqual([llamada.args[0] for llamada in entrada.call_args_list], [
            "¿Qué quisiste expresar o medir? ",
            "¿Qué ocurrió en cambio? ",
            "¿Cómo se detectó (persona, accidente, herramienta_ajena, observacion, mutacion)? ",
        ])
        self.assertEqual(archivos, [])

    def test_la_evidencia_entra_solo_desde_el_archivo_nombrado(self) -> None:
        """No recorrer el proyecto es una propiedad observable: un secreto presente pero no
        nombrado queda afuera; al usar la bandera aparece redactado en la vista completa."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            proyecto = self._proyecto(raiz)
            evidencia = raiz / "secreta.txt"
            evidencia.write_text(f'id, ruta\n7, "{raiz}/cliente.json"\n', encoding="utf-8")
            base = ["reportar", "--esperado", "quise", "--ocurrido", "pasó",
                    "--como-se-detecto", "persona", *proyecto]
            codigo_sin, salida_sin, _ = self._correr(base)
            codigo_con, salida_con, _ = self._correr(
                [*base, "--incluir-evidencia", str(evidencia)])
        self.assertEqual(codigo_sin, 0)
        self.assertEqual(codigo_con, 0)
        self.assertEqual("## evidencia" in salida_sin, False)
        self.assertEqual("secreta.txt" in salida_sin, False)
        self.assertEqual(salida_con.split("## evidencia\n\n", 1)[1],
                         '```text\nid, ruta\n7, "<PROYECTO>/cliente.json"\n\n```\n')

    def test_ni_una_salida_explicita_convierte_el_reporte_en_caso(self) -> None:
        """`--salida corpus/...` sigue sin ser una promoción: sin evidencia L0 comprobada el
        archivo aspira a caso, y aceptar esa ruta haría que pareciera uno por ubicación."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            proyecto = self._proyecto(raiz)
            destino = raiz / "corpus" / "reporte.md"
            codigo, salida, error = self._correr([
                "reportar", "--esperado", "quise", "--ocurrido", "pasó",
                "--como-se-detecto", "persona", "--salida", str(destino), *proyecto])
            existe = destino.exists()
        self.assertEqual(codigo, 1)
        self.assertEqual(salida, "")
        self.assertEqual(
            error,
            "REPORTE INVÁLIDO — la salida no puede ir dentro de `corpus/`: un reporte todavía "
            "no es un caso\n")
        self.assertEqual(existe, False)

    def test_no_reemplaza_el_archivo_que_se_esta_incluyendo(self) -> None:
        """Una salida explícita autoriza escribir un reporte, no destruir la única copia de la
        evidencia antes de que la persona haya podido compararla con la vista previa."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            proyecto = self._proyecto(raiz)
            evidencia = raiz / "evidencia.txt"
            evidencia.write_text("dato original", encoding="utf-8")
            codigo, salida, error = self._correr([
                "reportar", "--esperado", "quise", "--ocurrido", "pasó",
                "--como-se-detecto", "persona", "--incluir-evidencia", str(evidencia),
                "--salida", str(evidencia), *proyecto])
            conservado = evidencia.read_text(encoding="utf-8")
        self.assertEqual(codigo, 1)
        self.assertEqual(salida, "")
        self.assertEqual(error,
                         "REPORTE INVÁLIDO — la salida no puede reemplazar el archivo usado "
                         "como evidencia\n")
        self.assertEqual(conservado, "dato original")

    def test_el_verbo_esta_en_la_declaracion_la_ayuda_y_el_manual(self) -> None:
        """Aceptar el verbo sin esos dos lugares repite el defecto que vigila la medida meta: el
        trabajo existe, pero sólo lo descubre quien lee el despacho."""
        declarados = cli.verbos_documentados()
        manual_verbos = dict(manual.entradas("verbos"))
        codigo, ayuda, error = self._correr(["--help"])
        self.assertEqual(codigo, 0)
        self.assertEqual(error, "")
        self.assertEqual(declarados["oracle"], ("censar", "reportar"))
        self.assertEqual(manual_verbos["oracle"], "censar · reportar")
        self.assertEqual("oracle reportar" in ayuda, True)

    def test_la_ayuda_del_reporte_no_necesita_un_proyecto(self) -> None:
        """La explicación de las banderas es necesaria precisamente antes de poder nombrar un
        proyecto. Resolverlo primero haría fallar la ayuda de una instalación sin autocorpus."""
        salida, error = io.StringIO(), io.StringIO()
        with redirect_stdout(salida), redirect_stderr(error), \
                mock.patch.object(cli, "resolver", side_effect=AssertionError("no debe resolver")):
            codigo = cli.main(["reportar", "--help"])
        self.assertEqual(codigo, 0)
        self.assertEqual(error.getvalue(), "")
        self.assertEqual("--incluir-evidencia <ruta>" in salida.getvalue(), True)
        self.assertEqual("no abre un issue" in salida.getvalue(), True)


if __name__ == "__main__":
    unittest.main()


class LosCincoQueLaMutacionDejoVivosTests(unittest.TestCase):
    """Cada uno con la entrada que lo separa de su mutante.

    Cuatro de los cinco viven en la vista previa, que es la afirmación central de este módulo: lo
    que la persona ve es exactamente lo que va a compartir. Un defecto ahí no rompe una corrida —
    publica algo que su autor no revisó.
    """

    def _cercar(self):
        for nombre in ("_cercar", "_bloque", "_cerca"):
            fn = getattr(reportar, nombre, None)
            if fn is not None:
                return fn
        raise AssertionError("no se encontró la función que arma la cerca")

    def test_el_reporte_no_se_puede_reescribir_despues_de_mostrarlo(self) -> None:
        """`frozen`. El texto que se muestra ES el que se guarda: si alguien pudiera reasignarlo
        después de la vista previa, la persona habría revisado una cosa y copiado otra, que es
        justamente lo que este módulo existe para impedir.
        """
        import dataclasses

        reporte = reportar.Reporte(texto="lo que se revisó")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            reporte.texto = "otra cosa"

    def test_por_omision_el_texto_se_recorta(self) -> None:
        """El valor por omisión de `recortar`. Sin él, un salto de línea pegado al final de una
        respuesta interactiva viaja al issue y corre la estructura del Markdown."""
        self.assertEqual(reportar._texto_requerido("x", "  hola  "), "hola")

    def test_sin_recortar_conserva_los_bytes_tal_cual(self) -> None:
        """La otra dirección: donde el contenido es evidencia, un espacio puede ser significativo
        y recortarlo cambiaría lo que la persona creyó compartir."""
        self.assertEqual(reportar._texto_requerido("x", "  hola  ", recortar=False), "  hola  ")

    def test_un_contenido_sin_acentos_graves_usa_la_cerca_minima(self) -> None:
        """Los contadores arrancan en cero. Si arrancaran en uno, un contenido limpio saldría con
        una cerca de cuatro y el bloque dejaría de ser el Markdown que un issue espera."""
        salida = self._cercar()("sin acentos graves", "text")

        self.assertEqual(salida.splitlines()[0], "```text")
        self.assertEqual(salida.splitlines()[-1], "```")

    def test_una_corrida_al_principio_tambien_cuenta(self) -> None:
        """El contenido ARRANCA con la cerca. Un test cuyo contenido empieza con texto no
        distingue el valor inicial del acumulador: el primer carácter lo reinicia y la rama nunca
        se ejerce. Fue exactamente lo que dejó vivo a este mutante en la primera ronda."""
        salida = self._cercar()("````\ncuatro\n````", "text")

        self.assertEqual(salida.splitlines()[0], "`````text")

    def test_uno_o_dos_acentos_sueltos_no_alargan_la_cerca(self) -> None:
        """Sólo una corrida de tres o más puede cerrar una cerca de tres. Contar las de uno o dos
        alargaría el bloque sin motivo, y el `2` por omisión es justamente esa frontera."""
        self.assertEqual(self._cercar()("un `acento` suelto", "text").splitlines()[0], "```text")

    def test_un_contenido_con_su_propia_cerca_la_desborda(self) -> None:
        """Ésta es la afirmación: la vista previa muestra TODO. Con una cerca fija de tres, una
        evidencia que traiga la suya cerraría el bloque antes de tiempo y el resto se renderizaría
        como estructura del issue en vez de como los bytes que se están por compartir.
        """
        salida = self._cercar()("antes\n```\nadentro\n```\ndespués", "text")

        self.assertEqual(salida.splitlines()[0], "````text")
        self.assertEqual(salida.splitlines()[-1], "````")
        self.assertIn("```\nadentro\n```", salida)

    def test_el_diagnostico_viaja_legible_y_no_escapado(self) -> None:
        """`ensure_ascii`. Con el escape activado, «versión» sale como \\u00f3n y la persona revisa
        un texto que no puede leer: el consentimiento sobre lo que se comparte deja de ser
        informado si lo que se muestra está cifrado en puntos de código.
        """
        con_acentos = Diagnostico({
            "oracle": {"distribucion": "0.6.0", "algebra": "0.6", "sintaxis": "0.2"},
            "entorno": {"python": "3.13.0", "sistema": "Linux", "arquitectura": "x86_64"},
            "proyecto": {"nota": "medición de piezas del cañón"},
            "bibliotecas": [],
            "perfiles": [],
        })

        hecho = reportar.preparar(
            esperado="x", ocurrido="y", como_se_detecto="persona", diagnostico=con_acentos)

        self.assertIn("medición de piezas del cañón", hecho.texto)
        self.assertNotIn("\\u00f3", hecho.texto)
