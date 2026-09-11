"""Sombras contra el catálogo completo: integración conservada al final de los perfiles.

Estas ocho pruebas cuestan 14,2 segundos. Separarlas permite que las pruebas directas discriminen
antes, sin sustituir el catálogo, saltear verificaciones ni cambiar los escenarios de integración.
"""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tools import aceptacion


class ModoSombra(unittest.TestCase):
    """Una medida en sombra se mide, se reporta, y NO tumba la corrida.

    Existe porque heredar un catálogo de políticas te pone en rojo, y con razón. Pero si la
    primera experiencia de heredarlo es que el proyecto entero deja de pasar, no se hereda una
    segunda vez. La sombra compra tiempo sin comprar silencio.
    """

    MEDIDA_ROJA = """\
ninguno demo.siempre_roja:
    de item i
    donde i.mal == true
    umbral <= 0 segun contrato porque "ningun item malo pasa"
    ambito universal
    alcance "NO ve campos distintos de mal"
"""

    def _proyecto(self, raiz: Path, sombra: dict | None = None):
        from nucleo.proyecto import Proyecto
        (raiz / "catalogos" / "demo").mkdir(parents=True)
        (raiz / "corpus" / "demo").mkdir(parents=True)
        (raiz / "relaciones").mkdir()
        (raiz / "relaciones" / "item.json").write_text(json.dumps([
            "relacion", "item",
            ["campos", ["campo", "id", "texto", "sin_unidad"],
             ["campo", "mal", "booleano", "sin_unidad"]],
            ["alcance", "NO dice por qué un item está mal"],
        ]), encoding="utf-8")
        (raiz / "catalogos" / "demo" / "demo.siempre_roja.oracle").write_text(
            self.MEDIDA_ROJA, encoding="utf-8")
        # La aceptación no juzga sin corpus: un corpus vacío no puede poner a prueba nada.
        (raiz / "corpus" / "demo" / "001-item-malo.caso").write_text(
            "caso 001-item-malo:\n"
            "    fecha: \"2026-09-01\"\n"
            "    origen:\n"
            "        repo: \"prueba\"\n"
            "        commit: \"sin-commit\"\n"
            "    procedencia: construida\n"
            "    titulo: \"Un item malo la pone roja\"\n"
            "    etiqueta: falso_verde\n"
            "    sintoma:\n"
            "        Un item malo tiene que ponerla roja.\n"
            "    como_se_detecto: observacion\n"
            "    medida: demo.siempre_roja\n"
            "    evidencia:\n"
            "        item: id, mal\n"
            "            \"a\", true\n"
            "    leccion:\n"
            "        Sin este caso la medida nunca falla.\n", encoding="utf-8")
        # Sin el catálogo base no hay medidas `meta.*` que juzgar, y la sombra no tendría
        # sobre qué actuar: es justo el escenario que la sombra existe para hacer llevadero.
        config = {"esquema": "oracle.proyecto/v1", "catalogo_base": True}
        if sombra is not None:
            config["sombra"] = sombra
        (raiz / "oracle.json").write_text(json.dumps(config), encoding="utf-8")
        return Proyecto(raiz)

    def _correr(self, proy):
        salida = io.StringIO()
        with redirect_stdout(salida):
            rc = aceptacion._ejecutar(proy)
        return rc, salida.getvalue()

    def test_una_medida_en_sombra_no_hace_fallar_pero_se_reporta(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            proy_rojo = self._proyecto(raiz, sombra=None)
            rc_sin, _ = self._correr(proy_rojo)

            (raiz / "oracle.json").write_text(json.dumps({
                "esquema": "oracle.proyecto/v1", "catalogo_base": True,
                "sombra": {
                    "meta.toda_medida_esta_ejercitada": {
                        "desde": "2026-09-01", "porque": "en transición"},
                    # El caso del proyecto de prueba es `construida`, así que esta también
                    # está en rojo. Van las dos: la sombra sirve cuando cubre TODO lo que un
                    # catálogo heredado enciende, no una parte.
                    "meta.la_medida_no_se_fija_solo_con_evidencia_fabricada": {
                        "desde": "2026-09-01", "porque": "evidencia sintética por ahora"}},
            }), encoding="utf-8")
            rc_con, salida = self._correr(proy_rojo)

        self.assertEqual(rc_sin, 1, "sin sombra la medida tiene que tumbar la corrida")
        self.assertEqual(rc_con, 0, "en sombra NO tiene que tumbarla")
        self.assertIn("[EN SOMBRA]", salida)
        self.assertIn("EN SOMBRA — 2 medida(s)", salida)
        self.assertIn("en transición", salida, "el motivo se imprime, no se guarda callado")

    def test_la_antiguedad_se_imprime_en_cada_corrida(self) -> None:
        """«Lo tengo en sombra hace ocho meses» tiene que verse sin ir a buscarlo."""
        with tempfile.TemporaryDirectory() as td:
            proy = self._proyecto(Path(td), sombra={
                "meta.la_medida_no_se_fija_solo_con_evidencia_fabricada": {
                    "desde": "2020-01-01", "porque": "x"}})
            _rc, salida = self._correr(proy)
        self.assertRegex(salida, r"hace \d{4,} días")

    def test_la_marca_va_en_la_medida_ensombrecida_y_no_en_las_demas(self) -> None:
        """Marcar la línea equivocada es peor que no marcar ninguna: haría creer que un rojo
        que SÍ tumba la corrida está perdonado."""
        with tempfile.TemporaryDirectory() as td:
            proy = self._proyecto(Path(td), sombra={
                "meta.la_medida_no_se_fija_solo_con_evidencia_fabricada": {
                    "desde": "2026-09-01", "porque": "x"}})
            _rc, salida = self._correr(proy)
        marcadas = [l for l in salida.splitlines() if "[EN SOMBRA]" in l and l.startswith("  ")]
        self.assertTrue(
            any("meta.la_medida_no_se_fija_solo_con_evidencia_fabricada" in l for l in marcadas))
        self.assertFalse(any("meta.ninguna_medida_sin_alcance" in l for l in marcadas),
                         "una medida que NO está en sombra no puede aparecer marcada")

    def test_una_sombra_puesta_hoy_dice_hace_cero_dias_y_no_sin_fecha(self) -> None:
        """El borde: `dias == 0` es una fecha declarada, no una fecha ausente. Con `> 0` en vez
        de `>= 0`, una sombra puesta hoy se reporta como si nadie hubiera escrito cuándo."""
        from datetime import date
        with tempfile.TemporaryDirectory() as td:
            proy = self._proyecto(Path(td), sombra={
                "meta.la_medida_no_se_fija_solo_con_evidencia_fabricada": {
                    "desde": date.today().isoformat(), "porque": "x"}})
            _rc, salida = self._correr(proy)
        self.assertIn("hace 0 días", salida)
        self.assertNotIn("sin fecha", salida)

    def test_una_sombra_sin_fecha_lo_dice(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy = self._proyecto(Path(td), sombra={
                "meta.la_medida_no_se_fija_solo_con_evidencia_fabricada": {
                    "porque": "todavía no la fechamos"}})
            _rc, salida = self._correr(proy)
        self.assertIn("(sin fecha)", salida)

    def test_una_sombra_sin_motivo_hace_fallar_igual(self) -> None:
        """Las medidas que vigilan la sombra no se pueden poner en sombra: sería apagar el único
        mecanismo que impide que apagar salga gratis."""
        with tempfile.TemporaryDirectory() as td:
            proy = self._proyecto(Path(td), sombra={
                "meta.toda_medida_esta_ejercitada": {"desde": "2026-09-01"}})
            rc, salida = self._correr(proy)
        self.assertEqual(rc, 1)
        self.assertIn("meta.toda_sombra_declara_desde_y_porque", salida)

    def test_una_sombra_sobre_un_id_inexistente_hace_fallar(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy = self._proyecto(Path(td), sombra={
                "meta.no_existe_esta_medida": {"desde": "2026-09-01", "porque": "x"}})
            rc, salida = self._correr(proy)
        self.assertEqual(rc, 1)
        self.assertIn("meta.ninguna_sombra_sobre_una_medida_que_no_existe", salida)

    def test_una_sombra_sobre_una_medida_ya_verde_hace_fallar(self) -> None:
        """Sombra sobre algo que ya pasa: no hay nada que perdonar, y dejarla esconde que el
        proyecto podría estar exigiéndola."""
        with tempfile.TemporaryDirectory() as td:
            proy = self._proyecto(Path(td), sombra={
                "meta.ninguna_medida_sin_alcance": {"desde": "2026-09-01", "porque": "x"}})
            rc, salida = self._correr(proy)
        self.assertEqual(rc, 1)
        self.assertIn("meta.ninguna_sombra_ya_en_verde", salida)
