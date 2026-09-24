# Encargo P3 — evidencia del tracker propio

2026-09-12. El dueño autorizó continuar y usar agy. Implementar un extractor explícito de hechos
del formato propio del tracker, no un sensor de dominios externos ni un cambio del lenguaje.
Leer roadmap, cierres anteriores, tools/tareas.py, tareas_contexto.py y tareas_git.py.

## Propiedad

Agy: nuevo `tools/tareas_hechos.py`, nuevo `tests/test_tareas_hechos.py`, integración de `hechos`
en `tools/tareas.py` y `tools/cli.py`, sección P3 en `docs/12-tareas.md`, avance/informe P3 propios.
Codex: políticas opcionales y relaciones en `ejemplo/seguimiento-tareas/`, sus pruebas/mutación,
tests independientes `tests/test_tareas_p3_revision.py` y `tools/verificar_instalacion.py`.
No editar archivos de Codex ni tests anteriores. No dependencias/versiones/commits/push/red/MCP.
Usar sólo herramientas de lectura y edición; NO shell, tests ni agentes: Codex ejecuta comandos.
Primero escribir `AVANCE-P3-AGY.md`; al finalizar `INFORME-P3-AGY.md` sin inventar verificaciones.

## CLI y forma de evidencia

`oracle tarea hechos [--git] [--json] [--proyecto RUTA]` siempre emite JSON a stdout (flag --json
aceptado por coherencia). No --salida: se redirige por shell fuera del tracker; no escribir nada.
Integrar verbos/ayuda/despacho sin cargar catálogo, igual que P1/P2. Códigos0/1/2 existentes.
En tareas.despachar llamar por import local a tareas_hechos.cmd_hechos(argv,args).

JSON es directamente un objeto relación → lista de filas (sin envoltorio), consumible por
la API `Medida.evaluar`. Corrección de Codex tras revisar el CLI: `medida probar --con` recibe
texto en superficie de evidencia, no una ruta JSON. Codex proveerá `ejemplo/seguimiento-tareas/evaluar.py`
como adaptador de archivo JSON a la API existente; no documentar el comando incorrecto.
Claves EXACTAS siempre presentes:

- `lectura_seguimiento`: una fila {esquema:"oracle.tareas.hechos/v1", completa:booleano,
  git:"no_solicitado"|"sin_repositorio"|"comprobado", head:texto}; head vacío si no hay commit.
- `tarea_seguimiento`: {id,titulo,estado_declarado,prioridad_declarada,ruta,sha256_documento}.
  Estado/prioridad provienen de metadatos DECLARADOS, no son verificaciones del trabajo realizado.
- `archivo_seguimiento`: {tarea_id,ruta,clase:"documento"|"adjunto"|"auxiliar",tipo:"regular"|
  "enlace"|"especial"|"ausente",tamano_bytes:entero,existe:booleano,git_comprobado:booleano,
  en_indice:booleano,en_head:booleano,ignorado:booleano,indice:texto,trabajo:texto}.
  Incluye TAREA.md, adjuntos recursivos y auxiliares documentados de tareas/. tarea_id vacío para
  auxiliares. Sin --git, git_comprobado=false, booleanos Git=false, indice/trabajo vacíos.
  Con --git, reutilizar tareas_git.seguimiento y reflejar también archivos borrados presentes
  en índice/HEAD; sin repositorio => git_comprobado=false. Git ausente/fallido cuando pedido =>1.
- `referencia_seguimiento`: {tarea_id,origen,linea:entero,destino_declarado,clase:"local"|
  "remota"|"ancla"|"no_admitida",estado:"presente"|"ausente"|"fuera_del_proyecto"|
  "no_comprobado"}. Una fila por aparición, orden origen/línea/destino estable.
- `omision_seguimiento`: {ruta,linea:entero,motivo}. linea0 cuando la omisión afecta al archivo.

Rutas relativas POSIX al proyecto; no timestamps de ejecución, rutas absolutas de instalación,
PID ni mtimes. Mismo árbol estable => mismo JSON byte por byte (sort_keys y orden estable).
No leer adjuntos binarios para extraer hechos: sólo stat/tamaño; hash sólo documentos TAREA.md.
Reutilizar parser y auditoría P1; registros centrales rotos o errores reales de E/S =>1, sin JSON
de éxito parcial. Capturar también errores de enumeración, no traceback. No tocar código P1/P2.

## Referencias y límites

Leer sólo Markdown .md regular dentro del tracker, máx2MiB por archivo con lectura acotada.
No atravesar enlaces, archivos especiales ni repositorios anidados. Registrar omisiones y
completa=false si se omite Markdown por tamaño/UTF8 o rutas inseguras; binarios no son omisiones
porque no pertenecen al alcance de lectura Markdown. Archivos especiales/enlaces se inventarían
sin abrirlos y causan omisión; no seguir symlinks aunque apunten dentro del proyecto.

Extraer enlaces Markdown inline `[texto](destino)` y `![alt](destino)`, incluyendo destinos
percent-encoded creados por adjuntar y paréntesis escapados/equilibrados. Soportar destinos entre
ángulos y título opcional si resulta simple; de lo contrario declarar esa sintaxis como omisión.
Registrar también URLs http/https de las líneas `- URL: ...` creadas por anotar y autolinks <http...>.
Evitar duplicados por la misma aparición; no leer enlaces de bloques cercados ni código inline.
Enlaces por referencia `[texto][clave]`/definiciones no resueltos => omisión explícita, no silencio.
No afirmar soporte CommonMark completo: documentar gramática y omisiones concretas.

Remotos http/https: clase remota, estado no_comprobado, sin red. Anclas #x: ancla/no_comprobado
(no comprobar encabezados). Otros esquemas: no_admitida/no_comprobado y omisión.
Locales: decodificar percent encoding, quitar query/fragment para resolver ruta relativa al
Markdown de origen, conservar destino_declarado exacto. Validar ruta antes de acceder al destino:
fuera del proyecto => fuera_del_proyecto, sin leerlo; dentro sin symlinks => presente/ausente.
Symlink en cualquier componente => no_comprobado + omisión. No convertir una URL //host en ruta
local ni permitir escapes mediante %2e%2e o separadores. Una referencia existente no demuestra
autenticidad del adjunto ni que una tarea se haya resuelto.

## Tests y documentación

Tests vía CLI público: determinismo entre dos corridas, datos declarados, inventario sin leer
binarios/FIFO, links presentes/rotos/remotos/anclas/escape, nombres Unicode y espacios de P2,
exclusión de código cercado e inline, omisiones de sintaxis no soportada y archivos grandes,
metadata corrupta =>1, ayuda sin escrituras, opcional --git sin catálogo/escalares.
Documentar uso real con redirección fuera de tareas/, relación por relación y límites.
Codex provee proyecto ejemplo con tres políticas opcionales y prueba su mutación:
referencias locales presentes, archivos confirmados sin cambios y lectura sin omisiones.
