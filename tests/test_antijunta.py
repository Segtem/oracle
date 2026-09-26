"""Pruebas unitarias de la anti-junta (`sin`) en el álgebra, sintaxis y ecosistema.

Cubre:
- Semántica de `sin` en el álgebra: descarte de filas coincidentes, conservación de
  filas sin coincidencia, relación derecha vacía, relación derecha ausente (aún con
  izquierda vacía), preservación exclusiva de alias izquierdos, ausencia de cortocircuito,
  presupuesto cartesiano, detección de alias repetidos (en validación y ejecución),
  interacción con `agrupar`, y anotaciones de traza.
- Superficie (`nucleo/sintaxis.py`): lectura, impresión, ida y vuelta y errores sintácticos.
- Recorridos del árbol: `nucleo/version.py`, `nucleo/vocabulario.py`, `nucleo/unidad.py`,
  `nucleo/campo_leido.py` y `nucleo/medida.py`.
- Mutador: `nucleo/mutacion.quitar_antijunta`, entre los propios.
- Prueba de valor: medida del tracker de tareas reescrita y casos 023/024.
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from nucleo.algebra import (
    ALIAS_DERIVADO,
    ErrorDeAlgebra,
    LimitesAlgebra,
    aplicar,
    desde,
    trazar,
    validar_tuberia,
)
from nucleo.campo_leido import extraer_alias_de_medida
from nucleo.caso import cargar_fuente_caso
from nucleo.medida import (
    Medida,
    _fuentes_de_medida,
    cargar as cargar_medida,
    relaciones_de_medida,
)
from nucleo.relacion import cargar_fuente_relacion
from nucleo.sintaxis import ErrorSintaxis, imprimir, leer
from nucleo.unidad import (
    _extraer_comparaciones_de_paso,
    comparaciones_de_medida,
)
from nucleo.version import VERSION_ALGEBRA, VERSION_SINTAXIS, del_nucleo, del_nucleo_sintaxis
from nucleo.vocabulario import OPERADORES
from nucleo.mutacion import MUTADORES, quitar_antijunta
from tools.trazar import VIGILANTES

RAIZ = Path(__file__).resolve().parents[1]


class AntijuntaAlgebraTests(unittest.TestCase):
    """Semántica del paso «sin» en el álgebra de Oracle."""

    def test_sin_descarta_filas_que_casan_y_conserva_las_que_no(self) -> None:
        tuberia = [
            "desde",
            ["de", "persona", "p"],
            ["sin", ["de", "bloqueo", "b"], ["==", ["campo", "b", "dni"], ["campo", "p", "dni"]]],
        ]
        evidencia = {
            "persona": [
                {"dni": "111", "nombre": "Ana"},
                {"dni": "222", "nombre": "Beto"},
                {"dni": "333", "nombre": "Carla"},
            ],
            "bloqueo": [
                {"dni": "222", "motivo": "fraude"},
            ],
        }
        filas = desde(tuberia, evidencia)
        self.assertEqual(len(filas), 2)
        dnis_sobrevivientes = [f["p"]["dni"] for f in filas]
        self.assertEqual(dnis_sobrevivientes, ["111", "333"])

    def test_sin_salida_conserva_solo_alias_izquierdo(self) -> None:
        tuberia = [
            "desde",
            ["de", "persona", "p"],
            ["sin", ["de", "bloqueo", "b"], ["==", ["campo", "b", "dni"], ["campo", "p", "dni"]]],
        ]
        evidencia = {
            "persona": [{"dni": "111", "nombre": "Ana"}],
            "bloqueo": [{"dni": "999", "motivo": "otro"}],
        }
        filas = desde(tuberia, evidencia)
        self.assertEqual(len(filas), 1)
        # La fila resultante sólo debe tener la clave del alias 'p', nunca 'b'
        self.assertEqual(list(filas[0].keys()), ["p"])
        self.assertEqual(filas[0]["p"], {"dni": "111", "nombre": "Ana"})

    def test_sin_relacion_derecha_vacia_deja_pasar_todas_las_filas(self) -> None:
        tuberia = [
            "desde",
            ["de", "persona", "p"],
            ["sin", ["de", "bloqueo", "b"], ["==", ["campo", "b", "dni"], ["campo", "p", "dni"]]],
        ]
        evidencia = {
            "persona": [
                {"dni": "111", "nombre": "Ana"},
                {"dni": "222", "nombre": "Beto"},
            ],
            "bloqueo": [],
        }
        filas = desde(tuberia, evidencia)
        self.assertEqual(len(filas), 2)

    def test_sin_relacion_derecha_ausente_falla_como_de(self) -> None:
        tuberia = [
            "desde",
            ["de", "persona", "p"],
            ["sin", ["de", "inexistente", "x"], ["==", ["campo", "x", "id"], ["campo", "p", "id"]]],
        ]
        evidencia = {
            "persona": [{"id": 1}],
        }
        with self.assertRaises(ErrorDeAlgebra) as ctx:
            desde(tuberia, evidencia)
        self.assertIn("la relación «inexistente» no existe en la evidencia", str(ctx.exception))
        self.assertIn("una relación vacía se declara explícitamente como []", str(ctx.exception))

    def test_sin_relacion_derecha_ausente_falla_incluso_con_izquierda_vacia(self) -> None:
        """La relación derecha tiene que existir en la evidencia aunque no haya filas a la izquierda."""
        tuberia = [
            "desde",
            ["de", "persona", "p"],
            ["sin", ["de", "inexistente", "x"], ["==", ["campo", "x", "id"], ["campo", "p", "id"]]],
        ]
        evidencia = {
            "persona": [],
        }
        with self.assertRaises(ErrorDeAlgebra) as ctx:
            desde(tuberia, evidencia)
        self.assertIn("la relación «inexistente» no existe en la evidencia", str(ctx.exception))

    def test_sin_no_cortocircuita_evalua_todas_las_filas_derechas(self) -> None:
        """Si alguna fila derecha levanta un error al evaluar la condición, se propaga
        aunque una fila anterior ya haya cumplido la condición (semántica sin cortocircuito)."""
        tuberia = [
            "desde",
            ["de", "tarea", "t"],
            ["sin", ["de", "registro", "r"], ["==", ["campo", "r", "k"], ["campo", "t", "inexistente_en_t"]]],
        ]
        # La primera fila casa con True si k == null, pero acceder a un alias inexistente levanta
        tuberia_con_alias_roto = [
            "desde",
            ["de", "tarea", "t"],
            ["sin", ["de", "registro", "r"], [
                "y",
                ["==", ["campo", "r", "id"], ["campo", "t", "id"]],
                ["==", ["campo", "fantasma", "x"], 1],  # 'fantasma' no existe en la fila de trabajo
            ]],
        ]
        evidencia = {
            "tarea": [{"id": 1}],
            "registro": [
                {"id": 1},
                {"id": 2},
            ],
        }
        with self.assertRaises(ErrorDeAlgebra) as ctx:
            desde(tuberia_con_alias_roto, evidencia)
        self.assertIn("el alias «fantasma» no existe en la fila", str(ctx.exception))

    def test_sin_presupuesto_cartesiano_superado(self) -> None:
        tuberia = [
            "desde",
            ["de", "a", "x"],
            ["sin", ["de", "b", "y"], ["==", ["campo", "x", "k"], ["campo", "y", "k"]]],
        ]
        evidencia = {
            "a": [{"k": 1}, {"k": 2}, {"k": 3}],
            "b": [{"k": 1}, {"k": 2}],
        }
        # 3 * 2 = 6 pares. Con límite de 5 debe levantar error.
        limites = LimitesAlgebra(producto_cartesiano=5)
        with self.assertRaises(ErrorDeAlgebra) as ctx:
            desde(tuberia, evidencia, limites=limites)
        self.assertIn("producto cartesiano", str(ctx.exception))

    def test_sin_alias_repetido_en_validacion_estatica(self) -> None:
        tuberia = [
            "desde",
            ["de", "item", "i"],
            ["sin", ["de", "otro", "i"], ["==", ["campo", "i", "k"], 1]],
        ]
        with self.assertRaises(ErrorDeAlgebra) as ctx:
            validar_tuberia(tuberia)
        self.assertIn("alias repetido", str(ctx.exception))

    def test_sin_alias_repetido_en_ejecucion_directa(self) -> None:
        paso_sin = ["sin", ["de", "otro", "i"], ["==", ["campo", "i", "k"], 1]]
        filas = [{"i": {"k": 1}}]
        evidencia = {"otro": [{"k": 1}]}
        with self.assertRaises(ErrorDeAlgebra) as ctx:
            aplicar(paso_sin, filas, evidencia)
        self.assertIn("alias repetido", str(ctx.exception))

    def test_sin_despues_de_agrupar(self) -> None:
        """La condición de `sin` ve las columnas derivadas con `col` y los campos derechos con `campo`."""
        tuberia = [
            "desde",
            ["de", "venta", "v"],
            ["agrupar", [["cliente", ["campo", "v", "cliente"]]], [["total", "suma", ["campo", "v", "monto"]]]],
            ["sin", ["de", "vip", "vip"], ["==", ["campo", "vip", "cliente"], ["col", "cliente"]]],
        ]
        evidencia = {
            "venta": [
                {"cliente": "c1", "monto": 100},
                {"cliente": "c1", "monto": 50},
                {"cliente": "c2", "monto": 200},
            ],
            "vip": [
                {"cliente": "c1"},
            ],
        }
        filas = desde(tuberia, evidencia)
        self.assertEqual(len(filas), 1)
        # El cliente c1 fue descartado por VIP; sobrevive c2
        self.assertEqual(filas[0][ALIAS_DERIVADO]["cliente"], "c2")
        self.assertEqual(filas[0][ALIAS_DERIVADO]["total"], 200)

    def test_sin_anota_paso_en_la_traza(self) -> None:
        tuberia = [
            "desde",
            ["de", "tarea", "t"],
            ["sin", ["de", "cierre", "c"], ["==", ["campo", "c", "id"], ["campo", "t", "id"]]],
        ]
        evidencia = {
            "tarea": [{"id": 1}, {"id": 2}],
            "cierre": [{"id": 1}],
        }
        with trazar() as hechos_traza:
            desde(tuberia, evidencia)
        pasos = [campos for clase, campos in hechos_traza if clase == "paso"]
        pasos_sin = [p for p in pasos if p["operador"] == "sin"]
        self.assertEqual(len(pasos_sin), 1)
        self.assertEqual(pasos_sin[0]["filas_antes"], 2)
        self.assertEqual(pasos_sin[0]["filas_despues"], 1)


class AntijuntaSintaxisTests(unittest.TestCase):
    """Lectura, impresión e ida y vuelta del operador «sin» en la superficie infija."""

    def test_leer_paso_sin(self) -> None:
        texto = (
            "medida demo.sin_test:\n"
            "    de tarea t\n"
            "    sin commit_seguimiento c donde c.tarea_nombrada == t.id y c.es_cierre == true\n"
            "    resumen contar(0)\n"
            "    umbral <= 0 segun contrato porque \"debe tener cierre\"\n"
            "    alcance \"ejemplo de prueba\"\n"
        )
        datos = leer(texto)
        pasos = datos[2][2:]
        self.assertEqual(len(pasos), 1)
        paso_sin = pasos[0]
        self.assertEqual(paso_sin[0], "sin")
        self.assertEqual(paso_sin[1], ["de", "commit_seguimiento", "c"])
        self.assertEqual(paso_sin[2][0], "y")

    def test_imprimir_paso_sin_y_redondeo_ida_y_vuelta(self) -> None:
        texto = (
            "medida demo.sin_test:\n"
            "    de tarea t\n"
            "    donde t.estado == \"cerrada\"\n"
            "    sin commit_seguimiento c donde c.tarea_nombrada == t.id y c.es_cierre == true\n"
            "    resumen contar(0)\n"
            "    umbral <= 0 segun contrato porque \"debe tener cierre\"\n"
            "    alcance \"ejemplo de prueba\"\n"
        )
        datos = leer(texto)
        impreso = imprimir(datos)
        self.assertEqual(impreso, texto)

    def test_sintaxis_errores_en_paso_sin(self) -> None:
        # Falta relación
        with self.assertRaises(ErrorSintaxis):
            leer("medida demo.err:\n    de t x\n    sin\n    resumen contar(0)\n    umbral <= 0 segun contrato porque \"\"\n    alcance \"\"\n")
        # Falta alias
        with self.assertRaises(ErrorSintaxis):
            leer("medida demo.err:\n    de t x\n    sin rel_sola donde cond == 1\n    resumen contar(0)\n    umbral <= 0 segun contrato porque \"\"\n    alcance \"\"\n")
        # Falta palabra clave 'donde'
        with self.assertRaises(ErrorSintaxis):
            leer("medida demo.err:\n    de t x\n    sin rel alias c.k == x.k\n    resumen contar(0)\n    umbral <= 0 segun contrato porque \"\"\n    alcance \"\"\n")
        # Falta condición después de 'donde'
        with self.assertRaises(ErrorSintaxis):
            leer("medida demo.err:\n    de t x\n    sin rel alias donde\n    resumen contar(0)\n    umbral <= 0 segun contrato porque \"\"\n    alcance \"\"\n")


class AntijuntaEcosistemaTests(unittest.TestCase):
    """Integración con versiones, vocabulario, unidad, campo_leido, medida y mutadores."""

    def test_versiones_declaradas(self) -> None:
        self.assertEqual(VERSION_ALGEBRA, "1.0")
        self.assertEqual(VERSION_SINTAXIS, "1.0")
        self.assertEqual(str(del_nucleo()), "1.0")
        self.assertEqual(str(del_nucleo_sintaxis()), "1.0")

    def test_vocabulario_operadores_contiene_sin(self) -> None:
        self.assertIn("sin", OPERADORES)
        self.assertTrue(len(OPERADORES["sin"]) > 10)

    def test_unidad_extrae_comparaciones_de_paso_sin(self) -> None:
        paso_sin = ["sin", ["de", "rel", "r"], ["==", ["campo", "r", "x"], 42]]
        comparaciones = _extraer_comparaciones_de_paso(paso_sin)
        self.assertEqual(len(comparaciones), 1)
        self.assertEqual(comparaciones[0], (["campo", "r", "x"], 42))

    def test_unidad_comparaciones_de_medida_incluye_alias_sin(self) -> None:
        datos = [
            "medida", "demo.sin_unidad",
            ["desde", ["de", "tarea", "t"], ["sin", ["de", "commit", "c"], ["==", ["campo", "c", "n"], ["campo", "t", "n"]]]],
            ["resumen", "contar", 0],
            ["umbral", "<=", 0, "porque"],
            ["alcance", "alcance"],
        ]
        m = Medida.de_datos(datos)
        hechos = comparaciones_de_medida(m, {}, {}, frozenset())
        self.assertTrue(len(hechos) >= 2)

    def test_campo_leido_extrae_alias_de_paso_sin(self) -> None:
        datos = [
            "medida", "demo.campo_sin",
            ["desde", ["de", "tarea", "t"], ["sin", ["de", "commit_seguimiento", "c"], ["==", ["campo", "c", "sha"], "abc"]]],
            ["resumen", "contar", 0],
            ["umbral", "<=", 0, "porque"],
            ["alcance", "alcance"],
        ]
        m = Medida.de_datos(datos)
        alias_map = extraer_alias_de_medida(m)
        self.assertEqual(alias_map.get("t"), "tarea")
        self.assertEqual(alias_map.get("c"), "commit_seguimiento")

    def test_medida_relaciones_de_medida_incluye_relacion_en_sin(self) -> None:
        datos = [
            "medida", "demo.rel_sin",
            ["desde", ["de", "tarea", "t"], ["sin", ["de", "commit_seguimiento", "c"], ["==", ["campo", "c", "id"], 1]]],
            ["resumen", "contar", 0],
            ["umbral", "<=", 0, "porque"],
            ["alcance", "alcance"],
        ]
        m = Medida.de_datos(datos)
        rels = relaciones_de_medida(m)
        self.assertEqual(rels, ("tarea", "commit_seguimiento"))

    def test_medida_fuentes_de_medida_emite_fuente_en_sin(self) -> None:
        datos = [
            "medida", "demo.fuente_sin",
            ["desde", ["de", "tarea", "t"], ["sin", ["de", "commit_seguimiento", "c"], ["==", ["campo", "c", "id"], 1]]],
            ["resumen", "contar", 0],
            ["umbral", "<=", 0, "porque"],
            ["alcance", "alcance"],
        ]
        m = Medida.de_datos(datos)
        fuentes = _fuentes_de_medida(m)
        self.assertEqual(len(fuentes), 2)
        self.assertEqual(fuentes[0]["relacion"], "tarea")
        self.assertEqual(fuentes[1]["relacion"], "commit_seguimiento")

    def test_vigilantes_de_traza_contiene_meta_sin(self) -> None:
        self.assertIn("meta.sin_nunca_agrega_filas", VIGILANTES)

    def test_medida_meta_sin_nunca_agrega_filas_es_valida(self) -> None:
        ruta = RAIZ / "catalogos" / "meta" / "meta.sin_nunca_agrega_filas.oracle"
        self.assertTrue(ruta.exists(), f"El archivo {ruta} debe existir")
        m = cargar_medida(ruta)
        self.assertEqual(m.id, "meta.sin_nunca_agrega_filas")

    def test_mutador_quitar_antijunta(self) -> None:
        datos = [
            "medida", "demo.mut",
            ["desde", ["de", "tarea", "t"], ["donde", ["==", ["campo", "t", "x"], 1]], ["sin", ["de", "c", "c"], ["==", ["campo", "c", "id"], 1]]],
            ["resumen", "contar", 0],
            ["umbral", "<=", 0, "porque"],
            ["alcance", "alcance"],
        ]
        mutada = quitar_antijunta(datos)
        self.assertIsNotNone(mutada)
        pasos = mutada[2][2:]
        self.assertEqual(len(pasos), 1)
        self.assertEqual(pasos[0][0], "donde")
        # El original no fue modificado
        self.assertEqual(len(datos[2][2:]), 2)

    def test_mutador_quitar_antijunta_devuelve_none_sin_sin(self) -> None:
        datos = [
            "medida", "demo.sin_antijunta",
            ["desde", ["de", "tarea", "t"], ["donde", ["==", ["campo", "t", "x"], 1]]],
            ["resumen", "contar", 0],
            ["umbral", "<=", 0, "porque"],
            ["alcance", "alcance"],
        ]
        self.assertIsNone(quitar_antijunta(datos))

    def test_el_mutador_esta_registrado(self) -> None:
        """Un mutador que nadie carga no produce sobrevivientes: la mutación no lo ve."""
        self.assertIs(MUTADORES["quitar_antijunta"], quitar_antijunta)


class AntijuntaSeguimientoTareasTests(unittest.TestCase):
    """Prueba de valor: reescritura de la política en seguimiento-tareas."""

    def test_medida_del_tracker_reescrita_es_valida(self) -> None:
        ruta = RAIZ / "ejemplo" / "seguimiento-tareas" / "catalogos" / "seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre.oracle"
        m = cargar_medida(ruta)
        self.assertEqual(m.id, "seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre")
        pasos = m.tuberia[2:]
        self.assertEqual(len(pasos), 2)
        self.assertEqual(pasos[0][0], "donde")
        self.assertEqual(pasos[1][0], "sin")

    def test_relacion_tarea_seguimiento_no_declara_conteos_de_commits(self) -> None:
        ruta = RAIZ / "ejemplo" / "seguimiento-tareas" / "relaciones" / "tarea_seguimiento.relacion"
        datos = cargar_fuente_relacion(ruta)
        campos = [c[1] for c in datos[2] if isinstance(c, list) and len(c) >= 2 and c[0] == "campo"]
        self.assertNotIn("commits_que_la_nombran", campos)
        self.assertNotIn("commits_de_cierre", campos)

    def test_caso_023_tarea_cerrada_sin_su_commit_de_cierre_da_rojo(self) -> None:
        ruta_medida = RAIZ / "ejemplo" / "seguimiento-tareas" / "catalogos" / "seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre.oracle"
        medida = cargar_medida(ruta_medida)
        ruta_caso = RAIZ / "ejemplo" / "seguimiento-tareas" / "corpus" / "seguimiento" / "023-tarea-cerrada-sin-su-commit-de-cierre.caso"
        caso = cargar_fuente_caso(ruta_caso)
        self.assertEqual(caso["etiqueta"], "falso_verde")
        veredicto = medida.evaluar(caso["evidencia"])
        # Debe fallar (encontrar la ofensa de la tarea cerrada sin commit de cierre)
        self.assertFalse(veredicto.ok, "El caso 023 debe fallar porque una tarea cerrada no tiene commit de cierre")
        self.assertEqual(veredicto.valor, 1)

    def test_caso_024_cada_cerrada_con_su_cierre_da_verde(self) -> None:
        ruta_medida = RAIZ / "ejemplo" / "seguimiento-tareas" / "catalogos" / "seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre.oracle"
        medida = cargar_medida(ruta_medida)
        ruta_caso = RAIZ / "ejemplo" / "seguimiento-tareas" / "corpus" / "seguimiento" / "024-cada-cerrada-con-su-cierre.caso"
        caso = cargar_fuente_caso(ruta_caso)
        self.assertEqual(caso["etiqueta"], "verde_correcto")
        veredicto = medida.evaluar(caso["evidencia"])
        # Debe pasar en verde
        self.assertTrue(veredicto.ok, "El caso 024 debe dar verde porque toda tarea cerrada tiene su commit de cierre")
        self.assertEqual(veredicto.valor, 0)


if __name__ == "__main__":
    unittest.main()
