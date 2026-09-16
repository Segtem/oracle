#!/bin/bash
# Arma un directorio aislado con la especificación vigente y le pide a Codex una implementación
# independiente del álgebra 0.8. Tarea 20260915-201030-codex.
#
#   estudios/0.26.0-codex/lanzar.sh <directorio-aislado> [modelo]
#
# El directorio tiene que quedar FUERA del repositorio: lo que Codex no puede ver no puede copiarlo.
# Lleva sólo lo que declara CONTRATO.md —la especificación, dos decisiones y el contrato—, y en
# particular NO lleva diferencial/referencia/, que es la implementación contra la que se va a comparar.
set -euo pipefail

REPO=$(cd "$(dirname "$0")/../.." && pwd)
DESTINO=${1:?falta el directorio aislado}
MODELO=${2:-gpt-5.6-luna}

case "$(realpath -m "$DESTINO")" in
  "$REPO"|"$REPO"/*) echo "el directorio aislado no puede estar dentro del repositorio" >&2; exit 2 ;;
esac

# Primero la cuota: un encargo que muere en el primer turno deja un directorio a medias que parece
# una entrega.
PRUEBA=$(cd "$(mktemp -d)" && timeout 120 codex exec --skip-git-repo-check --ephemeral \
  --ignore-user-config --ignore-rules -m "$MODELO" "Respondé sólo: ok" 2>&1 || true)
if grep -q "usage limit" <<<"$PRUEBA"; then
  echo "Codex sigue sin cuota con $MODELO; no se lanza nada." >&2
  exit 3
fi
if grep -q "not supported" <<<"$PRUEBA"; then
  echo "El modelo $MODELO no está disponible para esta cuenta." >&2
  exit 3
fi

mkdir -p "$DESTINO"
if [ -n "$(ls -A "$DESTINO")" ]; then
  echo "$DESTINO no está vacío; no se pisa una entrega" >&2
  exit 2
fi
cp "$REPO/ESPECIFICACION.md" \
   "$REPO/DECISION-001-RELACIONES-COMO-BOLSAS.md" \
   "$REPO/DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md" \
   "$REPO/estudios/0.26.0-codex/CONTRATO.md" "$DESTINO/"
# Las huellas de lo que se le dio van AL LADO, no adentro: el contrato dice qué archivos hay, y un
# archivo de más sería una mentira del propio encargo.
(cd "$DESTINO" && sha256sum *) > "$DESTINO.entrada.sha256"

codex exec -C "$DESTINO" -s workspace-write --skip-git-repo-check --ephemeral \
  --ignore-user-config --ignore-rules -m "$MODELO" \
  -o "$DESTINO.respuesta.md" \
  "Leé CONTRATO.md entero y después ESPECIFICACION.md, DECISION-001 y DECISION-002. Escribí en este directorio evaluador.py, test_evaluador.py y DECISIONES.md según el contrato. Podés correr tus tests con python3 -m unittest. No leas nada fuera de este directorio ni busques otra implementación del álgebra. Terminá con un resumen de las decisiones que tomaste donde la especificación te dejó margen." \
  > "$DESTINO.codex.log" 2>&1

echo "entrega en $DESTINO — ahora: python3 estudios/0.26.0-codex/contrastar.py $DESTINO/evaluador.py"
