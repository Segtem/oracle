(
proyecto_prueba="$(mktemp -d)"
cd "$proyecto_prueba"
oracle tarea init --proyecto .

# 1. Crear una tarea y conservar su ID real
id_tarea="$(oracle tarea nueva "Desincronización de eventos en sensor" \
  --etiqueta bug --etiqueta sensor --sufijo sinc --json --proyecto . \
  | python3 -c 'import json, sys; print(json.load(sys.stdin)["id"])')"

# 2. Guardar una URL construida con una marca; no se descarga el video
oracle tarea anotar "$id_tarea" "Ejemplo de nota sobre monotonic clock" \
  --url "https://youtube.com/watch?v=ejemplo&t=150s" \
  --marca "02:30" --proyecto .

# 3. Crear un registro construido y adjuntarlo
printf 'Registro construido para practicar adjuntos.\n' > registro-ejemplo.txt
oracle tarea adjuntar "$id_tarea" registro-ejemplo.txt --proyecto .

# 4. Buscar términos en todas las tareas y notas del tracker
oracle tarea buscar "monotonic clock" --proyecto .

# 5. Crear una mención externa y reencontrarla por el ID
printf 'Investigación relacionada: %s\n' "$id_tarea" > referencias.md
oracle tarea referencias "$id_tarea" --proyecto .

# 6. Ver el resumen global de estados y etiquetas
oracle tarea resumen --proyecto .

# 7. Diagnosticar Git: este proyecto temporal todavía no tiene repositorio
oracle tarea seguimiento --proyecto .

# 8. Extraer hechos; el JSON declara sin_repositorio
oracle tarea hechos --git --proyecto . > hechos-tareas.json

# 9. Cerrar la tarea al finalizar
oracle tarea cerrar "$id_tarea" --proyecto .
oracle tarea listar --cerradas --proyecto .
printf 'Proyecto de práctica: %s\n' "$proyecto_prueba"
)
