# Solicitud de juicio independiente a Claude

Leé únicamente CRITERIO.md, registros.json y plantilla.json, entregados con este
archivo en una sesión nueva sin acceso al repositorio ni a conversaciones previas.
No consultes resultados de modelos, informes anteriores, claves ni otras carpetas.

Aplicá las dos preguntas de CRITERIO.md a TODOS los registros, por su id opaco y
sin intentar identificar su procedencia. No hay respuestas precargadas: los null
de la plantilla son casilleros vacíos, salvo P2 cuando `aplica_vecino` es false.
Completá `porque_origen` con true/false y, cuando aplique, `porque_vecino` con
true/false. Cuando no aplique P2, dejá null y escribí «no aplica: umbral cero».
Incluí justificación breve y cita textual que sostengan cada respuesta aplicable.
No mejores la prosa ni presupongas lo que quiso decir su autor.

Devolvé la plantilla completa como juicio-ciego-claude.json, identificando fuera
del JSON la versión de Claude utilizada, la fecha y si hubo exposición previa
a otros juicios o resultados de esta prueba. Si la hubo, informala antes de juzgar.
