import tempfile
import unittest
from pathlib import Path

from nucleo.autoria import hechos_de_autoria
from nucleo.medida import cargar
from nucleo.proyecto import Proyecto


RAIZ = Path(__file__).resolve().parents[1]
MEDIDA = RAIZ / "catalogos/meta/meta.se_escribe_en_superficie.oracle"


class AutoriaTests(unittest.TestCase):
    def test_las_tres_clases_de_json_rompen_la_medida_y_la_superficie_la_deja_verde(self):
        medida = cargar(MEDIDA)
        with tempfile.TemporaryDirectory() as temporal:
            proy = Proyecto(Path(temporal))
            for directorio, nombre in (("catalogos", "regla.oracle"),
                                       ("corpus", "001-caso.caso"),
                                       ("relaciones", "pieza.relacion")):
                destino = proy.raiz / directorio
                destino.mkdir()
                (destino / nombre).write_text("", encoding="utf-8")
            self.assertTrue(medida.evaluar(hechos_de_autoria(proy)).ok)

            for directorio, viejo, nuevo in (("catalogos", "regla.oracle", "regla.json"),
                                             ("corpus", "001-caso.caso", "001-caso.json"),
                                             ("relaciones", "pieza.relacion", "pieza.json")):
                ruta = proy.raiz / directorio
                (ruta / viejo).rename(ruta / nuevo)
                hechos = hechos_de_autoria(proy)
                self.assertEqual(medida.evaluar(hechos).valor,
                                 len([fila for fila in hechos["archivo_de_autoria"]
                                      if fila["formato"] == "json"]))
                self.assertFalse(medida.evaluar(hechos).ok)
                (ruta / nuevo).rename(ruta / viejo)
            self.assertTrue(medida.evaluar(hechos_de_autoria(proy)).ok)

    def test_no_cuenta_json_fuera_de_los_tres_directorios(self):
        with tempfile.TemporaryDirectory() as temporal:
            proy = Proyecto(Path(temporal))
            (proy.raiz / "intercambio.json").write_text("{}", encoding="utf-8")
            self.assertEqual(hechos_de_autoria(proy)["archivo_de_autoria"], [])
