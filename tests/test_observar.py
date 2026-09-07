"""El recorrido de observación tiene que negarse en los cinco lugares donde mentir es barato.

Cada test de acá pone una corrida que **discrimina**: no ejercita el camino feliz otra vez, sino
que rompe una sola cosa —la salida vacía, la lectura que cambia, el referente que se mueve, la
etiqueta que no corresponde, el valor que no es el declarado— y exige que el recorrido se plante.
Un recorrido que sólo sabe pasar convierte cualquier corrida en evidencia «observada», que es
exactamente la mentira que `PLAN-0.8.1-SENSOR.md` llama la más barata del proyecto.
"""

import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import FrozenInstanceError
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from nucleo.referente import Referente
from tools import observar
from tools.corpus import verificar

MEDIDA = [
    "ninguno", "dominio.pieza_faltante", "pieza", "p",
    ["==", ["campo", "p", "presente"], False],
    "cada pieza declarada tiene que estar en el disco; el umbral es cero porque una pieza ausente "
    "no se aproxima con otra",
    "ve la presencia del archivo declarado para cada pieza. NO lee su contenido ni juzga su calidad",
]

# El sensor de mentira escribe con una forma propia —cuatro espacios, acentos sin escapar y salto
# final— justamente para que «conservar la salida íntegra» se pueda comprobar byte a byte: si el
# recorrido reserializara la evidencia, este formato se perdería y el test lo vería.
SENSOR = '''
import json, sys
from pathlib import Path
raiz = Path(__file__).resolve().parents[1]
estado = json.loads((raiz / "mundo.json").read_text(encoding="utf-8"))
filas = [{"nombre": n, "ruta": f"piezas/{n}.dat",
          "presente": (raiz / "piezas" / f"{n}.dat").is_file()}
         for n in estado["piezas"]]
salida = sys.argv[sys.argv.index("--salida") + 1]
Path(salida).write_text(
    json.dumps({"pieza": [["clave", ["nombre"]], *filas]}, ensure_ascii=False, indent=4) + "\\n",
    encoding="utf-8")
print(f"SENSOR piezas={len(filas)} presentes={sum(f['presente'] for f in filas)}")
'''

SENSOR_INESTABLE = '''
import json, sys
from pathlib import Path
raiz = Path(__file__).resolve().parents[1]
corrida = len(list(raiz.glob("corrida-*")))
(raiz / f"corrida-{corrida}").write_text("1", encoding="utf-8")
salida = sys.argv[sys.argv.index("--salida") + 1]
Path(salida).write_text(json.dumps(
    {"pieza": [{"nombre": f"a{corrida}", "ruta": "piezas/a.dat", "presente": True}]}), encoding="utf-8")
print("SENSOR inestable")
'''

SENSOR_TIPO_CAMBIANTE = '''
import json, sys
from pathlib import Path
raiz = Path(__file__).resolve().parents[1]
corrida = len(list(raiz.glob("corrida-*")))
(raiz / f"corrida-{corrida}").write_text("1", encoding="utf-8")
# `true` en una corrida y `1` en la otra, en un campo que la medida NO mira: mismo valor para el
# `==` de Python, distinto tipo y distintos bytes.
revisado = True if corrida % 2 == 0 else 1
Path(sys.argv[sys.argv.index("--salida") + 1]).write_text(json.dumps(
    {"pieza": [{"nombre": "a", "ruta": "piezas/a.dat", "presente": False,
                "revisado": revisado}]}), encoding="utf-8")
print(f"SENSOR revisado={revisado!r}")
'''

SENSOR_CLAVES_DESORDENADAS = '''
import json, sys
from pathlib import Path
raiz = Path(__file__).resolve().parents[1]
corrida = len(list(raiz.glob("corrida-*")))
(raiz / f"corrida-{corrida}").write_text("1", encoding="utf-8")
fila = {"nombre": "a", "ruta": "piezas/a.dat", "presente": False}
if corrida % 2:
    fila = dict(reversed(list(fila.items())))
Path(sys.argv[sys.argv.index("--salida") + 1]).write_text(
    json.dumps({"pieza": [fila]}), encoding="utf-8")
print("SENSOR claves reordenadas")
'''

CASO = {
    "id": "001-una-pieza-declarada-no-esta",
    "titulo": "La corrida encuentra una pieza declarada y ausente",
    "etiqueta": "falso_verde",
    "como_se_detecto": "observacion",
    "sintoma": "El sensor leyó el mundo declarado y una de sus piezas no estaba en el disco.",
    "leccion": "Un catálogo coherente no hace completo al mundo que declara.",
}


class Consumidor:
    """Un consumidor de juguete: su mundo, su sensor, su medida y su plan."""

    def __init__(self, raiz: Path, *, piezas=("a", "b"), presentes=("a",)):
        self.raiz = raiz
        (raiz / "tools").mkdir(parents=True)
        (raiz / "piezas").mkdir()
        (raiz / "medidas").mkdir()
        (raiz / "observaciones").mkdir()
        (raiz / "tools" / "sensor.py").write_text(SENSOR, encoding="utf-8")
        (raiz / "mundo.json").write_text(json.dumps({"piezas": list(piezas)}), encoding="utf-8")
        for nombre in presentes:
            (raiz / "piezas" / f"{nombre}.dat").write_text("x", encoding="utf-8")
        (raiz / "medidas" / "dominio.pieza_faltante.json").write_text(
            json.dumps(MEDIDA, ensure_ascii=False), encoding="utf-8")

    def plan(self, **cambios) -> Path:
        datos = {
            "esquema": observar.ESQUEMA_PLAN,
            "raiz": "..",
            "sensor": ["{python}", "-B", "tools/sensor.py", "--salida", "{salida}"],
            "referentes": ["tools/sensor.py", "mundo.json"],
            "presencia": [{"relacion": "pieza", "campos": ["ruta"]}],
            "exige_filas": ["pieza"],
            "medida": "medidas/dominio.pieza_faltante.json",
            "caso": dict(CASO),
        }
        datos.update(cambios)
        ruta = self.raiz / "observaciones" / "plan.json"
        ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
        return ruta


class Recorrido(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory(prefix="oracle-test-observar-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.consumidor = Consumidor(self.base / "consumidor")
        self.destino = self.base / "consumidor" / "observaciones" / "2026-09-07-piezas"

    def capturar(self, plan_ruta=None, destino=None):
        ruta = plan_ruta or self.consumidor.plan()
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = observar.main(["capturar", "--plan", str(ruta),
                                    "--destino", str(destino or self.destino)])
        return codigo, salida.getvalue()

    def registro(self):
        return json.loads((self.destino / "registro.json").read_text(encoding="utf-8"))

    # ---- lo que una captura conserva ----

    def test_la_captura_conserva_la_salida_del_sensor_byte_a_byte(self):
        codigo, texto = self.capturar()
        self.assertEqual(codigo, 0, texto)
        crudo = (self.destino / "evidencia.json").read_bytes()
        # El formato del sensor, no el de este recorrido: cuatro espacios de sangría y salto final.
        self.assertIn(b'\n    "pieza": [', crudo)
        self.assertTrue(crudo.endswith(b"\n"))
        self.assertEqual(self.registro()["evidencia"]["sha256"], observar.huella(crudo))

    def test_el_caso_emitido_trae_la_evidencia_tal_cual_y_la_procedencia_observada(self):
        self.capturar()
        caso = json.loads(
            (self.destino / f"{CASO['id']}.json").read_text(encoding="utf-8"))
        evidencia = json.loads((self.destino / "evidencia.json").read_text(encoding="utf-8"))
        self.assertEqual(caso["evidencia"], evidencia)
        self.assertEqual(caso["procedencia"], "observada")
        self.assertEqual(caso["etiqueta"], CASO["etiqueta"])
        self.assertEqual(caso["medida"], "dominio.pieza_faltante")
        self.assertEqual(caso["origen"]["evidencia_sha256"],
                         observar.huella((self.destino / "evidencia.json").read_bytes()))

    def test_el_caso_emitido_lo_acepta_el_verificador_del_corpus(self):
        # No alcanza con que sea un JSON parecido a un caso: lo tiene que leer el mismo verificador
        # que después va a leerlo en el repositorio del consumidor.
        self.capturar()
        corpus = self.base / "corpus" / "dominio"
        corpus.mkdir(parents=True)
        (corpus / f"{CASO['id']}.json").write_bytes(
            (self.destino / f"{CASO['id']}.json").read_bytes())
        fallas, cargados = verificar(self.base / "corpus")
        self.assertEqual(fallas, [])
        self.assertEqual([c["id"] for c in cargados], [CASO["id"]])

    def test_el_registro_no_afirma_autenticidad_en_ningun_lado(self):
        _, texto = self.capturar()
        registro = self.registro()
        self.assertIs(registro["autenticidad"]["comprobada"], False)
        self.assertIn("prueba que el sensor haya corrido", registro["autenticidad"]["porque"])
        self.assertIn("autenticidad: NO comprobada", texto)
        # Ni un campo que lo insinúe: nada del registro puede leerse como «esto está autenticado».
        self.assertNotIn("autentic", json.dumps(
            {k: v for k, v in registro.items() if k != "autenticidad"}, ensure_ascii=False))

    def test_el_registro_separa_lo_declarado_de_lo_ejecutado(self):
        self.capturar()
        registro = self.registro()
        # Lo reusable no lleva rutas de esta máquina; lo que sí las lleva está en `maquina`.
        self.assertEqual(registro["comando_declarado"],
                         ["{python}", "-B", "tools/sensor.py", "--salida", "{salida}"])
        self.assertEqual(registro["plan"]["archivo"], "observaciones/plan.json")
        self.assertEqual(registro["medida"]["archivo"], "medidas/dominio.pieza_faltante.json")
        for clave in ("plan", "comando_declarado", "medida", "expectativa", "resultado"):
            self.assertNotIn(str(self.base), json.dumps(registro[clave], ensure_ascii=False))
        self.assertEqual(registro["maquina"]["raiz"], str(self.consumidor.raiz))

    def test_los_referentes_incluyen_las_fuentes_y_la_presencia_derivada(self):
        self.capturar()
        registro = self.registro()
        nombres = [r[1] for r in registro["referentes_despues"]]
        self.assertEqual(nombres, ["tools/sensor.py", "mundo.json", "presencia:pieza:ruta"])
        self.assertEqual(len(registro["comparacion"]["referente_comparado"]), 3)

    # ---- lo que una captura RECHAZA ----

    def test_una_lectura_vacia_no_es_una_observacion(self):
        (self.consumidor.raiz / "mundo.json").write_text(json.dumps({"piezas": []}),
                                                         encoding="utf-8")
        codigo, texto = self.capturar()
        self.assertEqual(codigo, 1)
        self.assertIn("vino sin filas", texto)
        self.assertFalse(self.destino.exists())

    def test_una_relacion_exigida_que_no_esta_se_rechaza(self):
        plan = self.consumidor.plan(exige_filas=["pieza", "lote"])
        codigo, texto = self.capturar(plan)
        self.assertEqual(codigo, 1)
        self.assertIn("«lote»", texto)
        self.assertFalse(self.destino.exists())

    def test_una_lectura_que_cambia_entre_dos_corridas_no_se_captura(self):
        # El sensor cuenta cuántas veces lo llamaron y lo mete en la evidencia: la segunda lectura
        # no puede coincidir con la primera. No toca ninguna fuente declarada como referente, así
        # que lo único que puede rechazarlo es la comparación entre las dos lecturas.
        (self.consumidor.raiz / "tools" / "sensor.py").write_text(SENSOR_INESTABLE, encoding="utf-8")
        codigo, texto = self.capturar()
        self.assertEqual(codigo, 1)
        self.assertIn("evidencias distintas", texto)
        self.assertFalse(self.destino.exists())

    def test_un_tipo_que_cambia_entre_lecturas_es_una_lectura_inestable(self):
        # Lo encontró codex atacando la herramienta: en Python `True == 1`, así que comparar las
        # dos lecturas parseadas dejaba pasar un sensor que emite `true` y después `1`. Los bytes
        # eran distintos y el caso salía igual como `observada`.
        (self.consumidor.raiz / "tools" / "sensor.py").write_text(
            SENSOR_TIPO_CAMBIANTE, encoding="utf-8")
        codigo, texto = self.capturar()
        self.assertEqual(codigo, 1)
        self.assertIn("valor y tipo, no por bytes", texto)
        self.assertFalse(self.destino.exists())

    def test_reordenar_las_claves_no_es_una_lectura_inestable(self):
        # La otra cara: la comparación es por valor y tipo, no por bytes. Un objeto con las mismas
        # claves en otro orden no es un cambio del mundo, y las dos corridas escriben además en
        # rutas distintas, que un sensor podría incluir en su salida.
        (self.consumidor.raiz / "tools" / "sensor.py").write_text(
            SENSOR_CLAVES_DESORDENADAS, encoding="utf-8")
        codigo, texto = self.capturar()
        self.assertEqual(codigo, 0, texto)
        self.assertEqual(self.registro()["resultado"]["valor"], 1)

    def test_un_referente_que_cambia_durante_la_corrida_no_se_captura(self):
        # El sensor se reescribe a sí mismo: la fuente que se declaró leída ya no es la que hay.
        (self.consumidor.raiz / "tools" / "sensor.py").write_text(
            SENSOR + '\np = Path(__file__); p.write_text(p.read_text() + "# ")\n',
            encoding="utf-8")
        codigo, texto = self.capturar()
        self.assertEqual(codigo, 1)
        self.assertIn("cambió un referente", texto)
        self.assertIn("tools/sensor.py", texto)
        self.assertFalse(self.destino.exists())

    def test_el_sensor_que_falla_no_deja_observacion(self):
        (self.consumidor.raiz / "tools" / "sensor.py").write_text(
            'import sys\nsys.stderr.write("no pude leer el mundo\\n")\nsys.exit(3)\n',
            encoding="utf-8")
        codigo, texto = self.capturar()
        self.assertEqual(codigo, 1)
        self.assertIn("el sensor salió 3", texto)
        self.assertIn("no pude leer el mundo", texto)
        self.assertFalse(self.destino.exists())

    def test_el_sensor_que_sale_cero_sin_escribir_nada_no_deja_observacion(self):
        (self.consumidor.raiz / "tools" / "sensor.py").write_text(
            'print("todo bien")\n', encoding="utf-8")
        codigo, texto = self.capturar()
        self.assertEqual(codigo, 1)
        self.assertIn("no escribió evidencia", texto)

    def test_un_destino_ocupado_no_se_pisa(self):
        self.assertEqual(self.capturar()[0], 0)
        codigo, texto = self.capturar()
        self.assertEqual(codigo, 1)
        self.assertIn("ya conserva una observación", texto)
        # y la primera sigue entera
        self.assertEqual(self.registro()["esquema"], observar.ESQUEMA_REGISTRO)

    # ---- la expectativa se declara, no se deduce ----

    def test_la_etiqueta_declarada_no_se_reescribe_con_el_resultado(self):
        plan = self.consumidor.plan(caso={**CASO, "etiqueta": "verde_correcto"})
        codigo, texto = self.capturar(plan)
        self.assertEqual(codigo, 1)
        self.assertIn("«verde_correcto»", texto)
        self.assertIn(observar.MEDIDA_POLARIDAD, texto)
        self.assertFalse(self.destino.exists())

    def test_un_mundo_completo_con_etiqueta_verde_si_se_captura(self):
        # La otra polaridad del mismo recorrido: sin ella, el rechazo de arriba podría ser un «no
        # captura nunca» disfrazado de discriminación.
        consumidor = Consumidor(self.base / "completo", piezas=("a",), presentes=("a",))
        plan = consumidor.plan(caso={**CASO, "etiqueta": "verde_correcto"})
        destino = consumidor.raiz / "observaciones" / "corrida"
        codigo, texto = self.capturar(plan, destino)
        self.assertEqual(codigo, 0, texto)
        registro = json.loads((destino / "registro.json").read_text(encoding="utf-8"))
        self.assertIs(registro["resultado"]["ok"], True)
        self.assertEqual(registro["resultado"]["valor"], 0)

    def test_el_valor_esperado_es_opcional_y_no_es_parte_del_contrato(self):
        # Sin `espera`, el recorrido captura cualquier cantidad: el número de una corrida es de esa
        # corrida. Con `espera`, el consumidor lo fija para SU plan.
        self.assertEqual(self.capturar()[0], 0)
        self.assertEqual(self.registro()["resultado"]["valor"], 1)
        self.assertIsNone(self.registro()["expectativa"]["valor"])

    def test_un_valor_declarado_que_no_se_reproduce_detiene_la_captura(self):
        plan = self.consumidor.plan(espera={"valor": 2})
        codigo, texto = self.capturar(plan)
        self.assertEqual(codigo, 1)
        self.assertIn("espera valor 2", texto)
        self.assertIn("dio 1", texto)
        self.assertFalse(self.destino.exists())

    def test_un_valor_declarado_que_se_reproduce_captura(self):
        plan = self.consumidor.plan(espera={"valor": 1})
        codigo, texto = self.capturar(plan)
        self.assertEqual(codigo, 0, texto)
        self.assertEqual(self.registro()["expectativa"]["valor"], 1)

    # ---- el plan ----

    def test_el_plan_rechaza_rutas_absolutas_y_del_hogar(self):
        for campo, valor in (("referentes", [str(self.consumidor.raiz / "mundo.json")]),
                             ("medida", "/etc/passwd"),
                             ("raiz", "~/Dev")):
            with self.subTest(campo=campo):
                codigo, texto = self.capturar(self.consumidor.plan(**{campo: valor}))
                self.assertEqual(codigo, 1)
                self.assertIn("OBSERVACIÓN RECHAZADA", texto)
                self.assertIn(campo, texto)

    def test_el_plan_exige_una_sola_marca_de_salida(self):
        for sensor in (["{python}", "tools/sensor.py"],
                       ["{python}", "tools/sensor.py", "{salida}", "{salida}"]):
            with self.subTest(sensor=sensor):
                codigo, texto = self.capturar(self.consumidor.plan(sensor=sensor))
                self.assertEqual(codigo, 1)
                self.assertIn("exactamente una vez", texto)

    def test_el_plan_exige_una_etiqueta_y_una_deteccion_del_vocabulario(self):
        for campo in ("etiqueta", "como_se_detecto"):
            with self.subTest(campo=campo):
                codigo, texto = self.capturar(
                    self.consumidor.plan(caso={**CASO, campo: "lo_que_salga"}))
                self.assertEqual(codigo, 1)
                self.assertIn(f"`caso.{campo}`", texto)

    def test_el_plan_de_otro_esquema_no_se_lee(self):
        codigo, texto = self.capturar(self.consumidor.plan(esquema="oracle.observacion/v9"))
        self.assertEqual(codigo, 1)
        self.assertIn("oracle.observacion/v9", texto)

    def test_espera_no_admite_la_polaridad_disfrazada_de_valor(self):
        codigo, texto = self.capturar(self.consumidor.plan(espera={"ok": False}))
        self.assertEqual(codigo, 1)
        self.assertIn("la polaridad la declara `caso.etiqueta`", texto)

    def test_un_referente_declarado_que_no_existe_detiene_la_captura(self):
        codigo, texto = self.capturar(
            self.consumidor.plan(referentes=["tools/sensor.py", "no-esta.json"]))
        self.assertEqual(codigo, 1)
        self.assertIn("no se pudo leer el referente «no-esta.json»", texto)

    def test_una_presencia_sobre_un_campo_que_la_evidencia_no_trae_se_rechaza(self):
        codigo, texto = self.capturar(
            self.consumidor.plan(presencia=[{"relacion": "pieza", "campos": ["origen"]}]))
        self.assertEqual(codigo, 1)
        self.assertIn("no trae el campo «origen»", texto)

    def test_la_presencia_se_resuelve_contra_la_raiz_y_no_contra_el_cwd(self):
        # La evidencia trae rutas relativas: resueltas desde otro directorio darían «no está» sin
        # haber mirado, y las dos huellas de presencia coincidirían por la razón equivocada.
        anterior = Path.cwd()
        os.chdir(self.base)
        self.addCleanup(os.chdir, anterior)
        plan = observar.leer_plan(self.consumidor.plan())
        evidencia = {"pieza": [{"nombre": "a", "ruta": "piezas/a.dat", "presente": True},
                               {"nombre": "b", "ruta": "piezas/b.dat", "presente": False}]}
        derivado = observar.leer_referentes(plan, evidencia, "2026-09-07T00:00:00+00:00")[-1]
        vistos = [{"ruta": "piezas/a.dat", "es_archivo": True},
                  {"ruta": "piezas/b.dat", "es_archivo": False}]
        self.assertEqual(derivado.huella, observar.huella(observar._canonico(vistos)))

    # ---- lo que fija las piezas chicas ----

    def test_la_forma_canonica_de_la_presencia_no_depende_del_orden_ni_del_alfabeto(self):
        # Si la huella dependiera del orden de las claves o del escape del alfabeto, dos lecturas
        # idénticas podrían diferir —o dos distintas coincidir— por razones ajenas al mundo.
        self.assertEqual(observar._canonico([{"ruta": "piezas/ñ.dat", "es_archivo": True}]),
                         '[{"es_archivo": true, "ruta": "piezas/ñ.dat"}]'.encode("utf-8"))

    def test_la_fecha_del_caso_es_el_dia_de_la_corrida(self):
        self.capturar()
        caso = json.loads((self.destino / f"{CASO['id']}.json").read_text(encoding="utf-8"))
        self.assertRegex(caso["fecha"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertTrue(self.registro()["inicio_utc"].startswith(caso["fecha"] + "T"))

    def test_el_plan_leido_no_se_reescribe_a_mitad_de_camino(self):
        plan = observar.leer_plan(self.consumidor.plan())
        with self.assertRaises(FrozenInstanceError):
            plan.medida = "medidas/otra.json"

    def test_un_sensor_que_no_existe_se_nombra_en_el_rechazo(self):
        codigo, texto = self.capturar(
            self.consumidor.plan(sensor=["programa-que-no-existe-aca", "{salida}"]))
        self.assertEqual(codigo, 1)
        self.assertIn("no se pudo ejecutar el sensor 'programa-que-no-existe-aca'", texto)

    def test_el_rechazo_muestra_la_salida_estandar_cuando_el_sensor_no_escribio_en_error(self):
        (self.consumidor.raiz / "tools" / "sensor.py").write_text(
            'import sys\nprint("no encontré el manifiesto")\nsys.exit(2)\n', encoding="utf-8")
        codigo, texto = self.capturar()
        self.assertEqual(codigo, 1)
        self.assertIn("no encontré el manifiesto", texto)

    def test_el_rechazo_recorta_una_salida_de_error_enorme_en_el_limite_declarado(self):
        # 401 caracteres, con una marca en el primero: el recorte conserva los ÚLTIMOS 400, así que
        # la marca tiene que quedar afuera. Un test que sólo pidiera «se recorta» no distingue 400
        # de 401 y deja vivo al mutante que corre el límite un lugar.
        (self.consumidor.raiz / "tools" / "sensor.py").write_text(
            'import sys\nsys.stderr.write("M" + "x" * 399 + "Z")\nsys.exit(1)\n', encoding="utf-8")
        codigo, texto = self.capturar()
        self.assertEqual(codigo, 1)
        self.assertIn("x" * 399 + "Z", texto)
        self.assertNotIn("Mx", texto)

    def test_una_evidencia_que_no_es_l0_se_rechaza_mostrando_las_primeras_fallas(self):
        (self.consumidor.raiz / "tools" / "sensor.py").write_text(
            'import json, sys\nfrom pathlib import Path\n'
            'Path(sys.argv[sys.argv.index("--salida") + 1]).write_text(json.dumps('
            '{"pieza": [{"a": [1]}, {"b": [2]}, {"c": [3]}, {"d": [4]}]}))\n', encoding="utf-8")
        codigo, texto = self.capturar()
        self.assertEqual(codigo, 1)
        self.assertIn("no cumple L0", texto)
        self.assertEqual(texto.count("no es escalar"), 3)

    def test_el_estado_del_arbol_distingue_un_repositorio_de_lo_que_no_lo_es(self):
        sin_git = observar.estado_del_arbol(self.consumidor.raiz)
        self.assertIs(sin_git["versionado"], False)
        self.assertNotIn("commit", sin_git)

        repo = self.base / "repo"
        repo.mkdir()
        entorno = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                   "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
                   "GIT_CONFIG_GLOBAL": str(repo / "sin-config"),
                   "GIT_CONFIG_SYSTEM": str(repo / "sin-config")}
        for args in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "base"]):
            subprocess.run(["git", "-C", str(repo), *args], check=True, env=entorno,
                           capture_output=True)
        limpio = observar.estado_del_arbol(repo)
        self.assertIs(limpio["versionado"], True)
        self.assertRegex(limpio["commit"], r"^[0-9a-f]{40}$")
        self.assertIs(limpio["sucio"], False)

        (repo / "suelto.txt").write_text("x", encoding="utf-8")
        sucio = observar.estado_del_arbol(repo)
        self.assertIs(sucio["sucio"], True)
        self.assertIn("suelto.txt", sucio["estado"])
        self.assertEqual(sucio["commit"], limpio["commit"])

        # Sin `git` en la máquina tampoco se inventa un commit: es lo mismo que no estar versionado.
        with patch("tools.observar.subprocess.run", side_effect=OSError("no hay git")):
            self.assertIs(observar.estado_del_arbol(repo)["versionado"], False)

    def test_el_plan_falla_cerrado_ante_una_declaracion_mal_formada(self):
        malos = [
            ({"raiz": "no-existe"}, "`raiz` no es un directorio"),
            ({"referentes": "mundo.json"}, "lista de rutas relativas"),
            ({"referentes": []}, "al menos 1"),
            ({"referentes": [""]}, "`referentes[0]`"),
            ({"referentes": [7]}, "`referentes[0]`"),
            ({"referentes": ["mundo.json", "mundo.json"]}, "repite una ruta"),
            ({"medida": 7}, "`medida`"),
            ({"exige_filas": "pieza"}, "lista de nombres de relación"),
            ({"exige_filas": []}, "al menos 1"),
            ({"exige_filas": ["pieza", "  "]}, "`exige_filas[1]`"),
            ({"exige_filas": ["pieza", 3]}, "`exige_filas[1]`"),
            ({"exige_filas": ["pieza", "pieza"]}, "repite una relación"),
            ({"sensor": []}, "lista de argumentos"),
            ({"sensor": "tools/sensor.py {salida}"}, "lista de argumentos"),
            ({"sensor": ["{python}", "", "{salida}"]}, "`sensor[1]`"),
            ({"sensor": ["{python}", 3, "{salida}"]}, "`sensor[1]`"),
            ({"presencia": "pieza"}, "lista de {relacion, campos}"),
            ({"presencia": ["pieza"]}, "`presencia[0]`"),
            ({"presencia": [{"relacion": "  ", "campos": ["ruta"]}]}, "`presencia[0].relacion`"),
            ({"presencia": [{"relacion": 2, "campos": ["ruta"]}]}, "`presencia[0].relacion`"),
            ({"presencia": [{"relacion": "pieza", "campos": []}]}, "`campos` necesita"),
            ({"presencia": [{"relacion": "pieza", "campos": ["ruta"]},
                            {"relacion": "pieza", "campos": ["nombre"]}]},
             "dos veces la misma relación"),
            ({"espera": [1]}, "`espera` tiene que ser un objeto"),
            ({"espera": {"valor": True}}, "tiene que ser un número"),
            ({"espera": {"valor": "1"}}, "tiene que ser un número"),
            ({"caso": ["algo"]}, "`caso` tiene que ser el objeto"),
            ({"caso": {**CASO, "titulo": 5}}, "`caso.titulo`"),
            ({"caso": {**CASO, "leccion": "   "}}, "`caso.leccion`"),
            ({"caso": {**CASO, "origen": "repo"}}, "`caso.origen` tiene que ser un objeto"),
            ({"caso": {**CASO, "origen": {"repo": ["x"]}}}, "sólo admite campos escalares"),
        ]
        for cambio, esperado in malos:
            with self.subTest(cambio=sorted(cambio)[0], valor=repr(list(cambio.values())[0])[:40]):
                codigo, texto = self.capturar(self.consumidor.plan(**cambio))
                self.assertEqual(codigo, 1, texto)
                self.assertIn(esperado, texto)

    def test_los_artefactos_se_escriben_en_utf8_sin_escapar(self):
        # Un registro con `ó` en vez de «ó» sigue siendo válido, pero deja de ser legible por
        # la persona que va a revisar la observación, que es para quien se escribe.
        self.capturar()
        self.assertIn("declaración".encode("utf-8"),
                      (self.destino / "registro.json").read_bytes())
        self.assertIn("leyó".encode("utf-8"),
                      (self.destino / f"{CASO['id']}.json").read_bytes())

    def test_el_destino_se_crea_con_sus_padres_y_acepta_una_carpeta_ya_hecha(self):
        hondo = self.base / "consumidor" / "observaciones" / "2026" / "09" / "piezas"
        codigo, texto = self.capturar(destino=hondo)
        self.assertEqual(codigo, 0, texto)
        self.assertTrue((hondo / "registro.json").is_file())

        preparada = self.base / "consumidor" / "observaciones" / "hecha-a-mano"
        preparada.mkdir()
        codigo, texto = self.capturar(destino=preparada)
        self.assertEqual(codigo, 0, texto)
        self.assertTrue((preparada / "registro.json").is_file())

    def test_los_artefactos_se_guardan_con_la_sangria_del_corpus(self):
        self.capturar()
        for nombre in ("registro.json", f"{CASO['id']}.json"):
            with self.subTest(archivo=nombre):
                texto = (self.destino / nombre).read_text(encoding="utf-8")
                self.assertRegex(texto.splitlines()[1], r'^ {2}"')
                self.assertTrue(texto.endswith("\n"))

class Revalidacion(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory(prefix="oracle-test-revalidar-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.consumidor = Consumidor(self.base / "consumidor")
        self.plan = self.consumidor.plan()
        self.destino = self.consumidor.raiz / "observaciones" / "corrida"
        salida = io.StringIO()
        with redirect_stdout(salida):
            self.assertEqual(observar.main(
                ["capturar", "--plan", str(self.plan), "--destino", str(self.destino)]), 0,
                salida.getvalue())
        self.registro = self.destino / "registro.json"
        self.antes = {p.name: p.read_bytes() for p in sorted(self.destino.iterdir())}

    def revalidar(self, informe=None):
        args = ["revalidar", "--plan", str(self.plan), "--registro", str(self.registro)]
        if informe:
            args += ["--informe", str(informe)]
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = observar.main(args)
        return codigo, salida.getvalue()

    def test_revalidar_no_toca_la_observacion_guardada(self):
        self.revalidar()
        self.assertEqual({p.name: p.read_bytes() for p in sorted(self.destino.iterdir())},
                         self.antes)

    def test_sin_cambios_sale_cero_y_lo_dice(self):
        codigo, texto = self.revalidar()
        self.assertEqual(codigo, 0, texto)
        self.assertIn("REVALIDACIÓN — sin cambios", texto)

    def test_una_lectura_distinta_no_reescribe_la_historica(self):
        # El mundo se completa: hoy la medida da verde, y aquella corrida sigue diciendo 1.
        (self.consumidor.raiz / "piezas" / "b.dat").write_text("y", encoding="utf-8")
        informe_ruta = self.base / "informe.json"
        codigo, texto = self.revalidar(informe_ruta)
        self.assertEqual(codigo, 1)
        self.assertIn("REVALIDACIÓN — CAMBIÓ", texto)
        informe = json.loads(informe_ruta.read_text(encoding="utf-8"))
        self.assertEqual(informe["observacion_historica"]["resultado"]["valor"], 1)
        self.assertEqual(informe["lectura_actual"]["resultado"]["valor"], 0)
        self.assertIs(informe["sin_cambios"], False)
        self.assertEqual({p.name: p.read_bytes() for p in sorted(self.destino.iterdir())},
                         self.antes)

    def test_un_referente_cambiado_se_informa_como_frescura_y_no_como_resultado(self):
        # Cambia el mundo declarado sin cambiar el veredicto: sigue faltando una pieza, pero la
        # fuente que se leyó ya no es la misma.
        (self.consumidor.raiz / "piezas" / "b.dat").write_text("y", encoding="utf-8")
        (self.consumidor.raiz / "mundo.json").write_text(
            json.dumps({"piezas": ["a", "b", "c"]}), encoding="utf-8")
        informe_ruta = self.base / "informe.json"
        codigo, _ = self.revalidar(informe_ruta)
        informe = json.loads(informe_ruta.read_text(encoding="utf-8"))
        self.assertEqual(codigo, 1)
        self.assertEqual(informe["lectura_actual"]["resultado"]["valor"], 1)
        self.assertEqual(informe["observacion_historica"]["resultado"]["valor"], 1)
        self.assertIs(informe["frescura"]["estables"], False)
        self.assertIn("mundo.json", informe["frescura"]["cambiados"])

    def test_un_plan_con_otros_referentes_no_se_compara_a_ciegas(self):
        self.consumidor.plan(referentes=["tools/sensor.py"])
        informe_ruta = self.base / "informe.json"
        codigo, texto = self.revalidar(informe_ruta)
        informe = json.loads(informe_ruta.read_text(encoding="utf-8"))
        self.assertEqual(codigo, 1)
        self.assertIs(informe["frescura"]["comparable"], False)
        self.assertIn("mundo.json", informe["frescura"]["porque"])
        self.assertIs(informe["plan_sin_cambios"], False)
        self.assertIn("el plan cambió desde la captura", texto)

    def test_un_registro_de_otro_esquema_no_se_revalida(self):
        self.registro.write_text(json.dumps({"esquema": "otra/cosa"}), encoding="utf-8")
        codigo, texto = self.revalidar()
        self.assertEqual(codigo, 1)
        self.assertIn(observar.ESQUEMA_REGISTRO, texto)

    def test_el_informe_tampoco_afirma_autenticidad_ni_amplia_el_alcance(self):
        informe_ruta = self.base / "informe.json"
        self.revalidar(informe_ruta)
        informe = json.loads(informe_ruta.read_text(encoding="utf-8"))
        self.assertIs(informe["autenticidad"]["comprobada"], False)
        self.assertEqual(informe["alcance"], observar.LIMITE_OBSERVACION)
        self.assertIs(informe["plan_sin_cambios"], True)
        self.assertEqual(informe["observacion_historica"]["caso"]["id"], CASO["id"])
        self.assertEqual(informe["registro"], str(self.registro))

    def test_sin_informe_no_se_escribe_nada_fuera_de_la_pantalla(self):
        antes = sorted(p.name for p in self.base.rglob("*.json"))
        self.revalidar()
        self.assertEqual(sorted(p.name for p in self.base.rglob("*.json")), antes)

    def test_la_pantalla_distingue_referentes_estables_de_cambiados(self):
        _, estable = self.revalidar()
        self.assertIn("frescura:     estables", estable)
        (self.consumidor.raiz / "mundo.json").write_text(
            json.dumps({"piezas": ["a", "b", "c"]}), encoding="utf-8")
        _, cambiado = self.revalidar()
        self.assertIn("frescura:     cambiaron ", cambiado)
        self.assertIn("mundo.json", cambiado)

    def test_el_informe_se_guarda_legible_y_sin_escapar(self):
        informe_ruta = self.base / "informe.json"
        self.revalidar(informe_ruta)
        texto = informe_ruta.read_text(encoding="utf-8")
        self.assertRegex(texto.splitlines()[1], r'^ {2}"')
        self.assertTrue(texto.endswith("\n"))
        self.assertIn("declaración", texto)

class LimiteDeLasHuellas(unittest.TestCase):
    """El control que impide vender la frescura como autenticidad."""

    def test_dos_declaraciones_falsas_iguales_pasan_la_comparacion(self):
        falsa = "sha256:" + "0" * 64
        leidos = [Referente("lo-que-sea", falsa, "2026-09-07T00:00:00+00:00")]
        actuales = [Referente("lo-que-sea", falsa, "2026-09-07T00:00:01+00:00")]
        _hechos, v = observar.comparar_frescura(leidos, actuales)
        self.assertTrue(v.ok)
        self.assertEqual(v.valor, 0)

    def test_una_huella_distinta_da_rojo_uno(self):
        leidos = [Referente("lo-que-sea", "sha256:" + "0" * 64, "2026-09-07T00:00:00+00:00")]
        actuales = [Referente("lo-que-sea", "sha256:" + "1" * 64, "2026-09-07T00:00:01+00:00")]
        _hechos, v = observar.comparar_frescura(leidos, actuales)
        self.assertFalse(v.ok)
        self.assertEqual(v.valor, 1)



class LineaDeComandos(unittest.TestCase):
    """Lo que la línea de comandos exige, y lo que muestra cuando algo se rechaza."""

    def setUp(self):
        self.tmp = TemporaryDirectory(prefix="oracle-test-observar-cli-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.consumidor = Consumidor(self.base / "consumidor")

    def correr(self, args):
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = observar.main(args)
        return codigo, salida.getvalue()

    def test_la_ayuda_describe_el_recorrido_y_no_una_seccion_del_medio(self):
        salida = io.StringIO()
        with redirect_stdout(salida), self.assertRaises(SystemExit):
            observar.main(["--help"])
        texto = salida.getvalue()
        self.assertIn("Captura la corrida de un sensor del consumidor", texto)
        self.assertIn("capturar", texto)
        self.assertIn("revalidar", texto)

    def test_faltando_un_verbo_o_un_argumento_obligatorio_no_se_corre_nada(self):
        plan = str(self.consumidor.plan())
        for args in ([],
                     ["capturar", "--destino", str(self.base / "x")],
                     ["capturar", "--plan", plan],
                     ["revalidar", "--registro", str(self.base / "r.json")],
                     ["revalidar", "--plan", plan]):
            with self.subTest(args=args):
                with open(os.devnull, "w") as nulo, redirect_stderr(nulo):
                    with self.assertRaises(SystemExit) as e:
                        observar.main(args)
                self.assertEqual(e.exception.code, 2)

    def test_una_lectura_rechazada_despues_de_correr_queda_para_mirar(self):
        (self.consumidor.raiz / "mundo.json").write_text(json.dumps({"piezas": []}),
                                                         encoding="utf-8")
        codigo, texto = self.correr(["capturar", "--plan", str(self.consumidor.plan()),
                                     "--destino", str(self.base / "destino")])
        self.assertEqual(codigo, 1)
        quedo = [l for l in texto.splitlines() if "la lectura rechazada quedó en" in l]
        self.assertEqual(len(quedo), 1)
        carpeta = Path(quedo[0].split("quedó en ")[1])
        self.addCleanup(shutil.rmtree, carpeta, True)
        self.assertTrue((carpeta / "descubrimiento.json").is_file())

    def test_un_plan_rechazado_antes_de_correr_no_deja_carpeta_de_trabajo(self):
        antes = set(Path(tempfile.gettempdir()).glob("oracle-observar-*"))
        codigo, texto = self.correr(
            ["capturar", "--plan", str(self.consumidor.plan(medida="/etc/passwd")),
             "--destino", str(self.base / "destino")])
        self.assertEqual(codigo, 1)
        self.assertNotIn("la lectura rechazada quedó en", texto)
        self.assertEqual(set(Path(tempfile.gettempdir()).glob("oracle-observar-*")), antes)

    def test_una_captura_lograda_no_deja_carpeta_de_trabajo(self):
        antes = set(Path(tempfile.gettempdir()).glob("oracle-observar-*"))
        codigo, texto = self.correr(["capturar", "--plan", str(self.consumidor.plan()),
                                     "--destino", str(self.base / "destino")])
        self.assertEqual(codigo, 0, texto)
        self.assertEqual(set(Path(tempfile.gettempdir()).glob("oracle-observar-*")), antes)

    def test_sin_argv_explicito_lee_la_linea_de_comandos_del_proceso(self):
        destino = self.base / "por-sys-argv"
        argv = ["observar.py", "capturar", "--plan", str(self.consumidor.plan()),
                "--destino", str(destino)]
        salida = io.StringIO()
        with patch("sys.argv", argv), redirect_stdout(salida):
            codigo = observar.main()
        self.assertEqual(codigo, 0, salida.getvalue())
        self.assertTrue((destino / "registro.json").is_file())

if __name__ == "__main__":
    unittest.main()
