"""Construye dos historias indistinguibles para el recorrido local de observación.

Premisa: quien transcribe puede escribir el registro y leer los referentes. El experimento no
modela una custodia externa independiente y no cambia evidencia de ningún corpus real.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path = [str(RAIZ), *sys.path]

from tests.test_observar import Consumidor  # noqa: E402
from tools import observar  # noqa: E402


def contrastar() -> dict:
    """Captura de verdad, transcribe sin sensor y luego revalida ejecutando el sensor real."""
    with tempfile.TemporaryDirectory(prefix="oracle-autenticidad-") as directorio:
        raiz = Path(directorio)
        consumidor = Consumidor(raiz / "consumidor")
        plan = observar.leer_plan(consumidor.plan())
        trabajo = raiz / "trabajo"
        trabajo.mkdir()
        real, construida = raiz / "real", raiz / "construida"
        registro_real = observar.capturar(plan, real, trabajo)
        crudo = (real / "evidencia.json").read_bytes()
        # Sustituimos sólo la ejecución: los validadores y el cálculo de huellas siguen siendo reales.
        with mock.patch.object(observar, "correr_sensor", return_value=(
                observar.comando(plan, trabajo / "evidencia.json"),
                registro_real["salida_estandar"], crudo)) as transcripcion:
            registro_construido = observar.capturar(plan, construida, trabajo)
            llamadas_sustituidas = transcripcion.call_count
        relectura = observar.revalidar(plan, construida / "registro.json", trabajo)
        resultado = {
            "procedencia_del_experimento": "construida",
            "ejecuciones_sustituidas_por_transcripcion": llamadas_sustituidas,
            "captura_con_transcripcion_aceptada": registro_construido["resultado"] == registro_real["resultado"],
            "relectura_real_informa_sin_cambios": relectura["sin_cambios"],
            "autenticidad_comprobada": relectura["autenticidad"]["comprobada"],
            "alcance": "Atacante con escritura del registro y acceso a los mismos referentes; "
                       "no prueba nada contra un registro custodiado fuera de esa autoridad.",
        }
        assert llamadas_sustituidas == 2
        assert resultado["captura_con_transcripcion_aceptada"]
        assert resultado["relectura_real_informa_sin_cambios"]
        assert resultado["autenticidad_comprobada"] is False
        return resultado


if __name__ == "__main__":
    print(json.dumps(contrastar(), ensure_ascii=False, indent=2))
