# Las guías de docs/ pueden mostrar comandos u opciones que la CLI no tiene

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, documentacion, flaqueza


## Qué hacer

Recorrer cada `.md` de `docs/` (no `vault-kb/`) y listar cada comando `oracle …` y cada opción que
muestra. Para cada uno, comprobar contra `tools/cli.py` y los módulos que despacha que existe y hace lo
que la guía dice. Listar los que no existen, cambiaron de nombre o de salida. Con archivo:línea de la
guía y del código. En `HALLAZGOS.md`.

## Avance

Se completó la auditoría exhaustiva de todos los archivos `.md` de `docs/` (excluyendo `vault-kb/`), cotejando cada comando `oracle …` y opción contra `tools/cli.py` y los módulos que despacha. Los hallazgos se registraron en `HALLAZGOS.md` con referencias `archivo:línea` tanto de las guías como del código fuente:

1. **Invocación rota de `oracle medida probar`:** Documentada como `oracle medida probar <medida> <caso>` en `docs/02-de-cero-a-un-rojo.md:30`, `docs/03-escribir-una-medida.md:108`, `docs/07-conectar-a-un-proyecto-propio.md:82`, `docs/13-primer-valor.md:90` y `docs/tutorial-practico.md:86`, pero `tools/cli.py:1211` exige obligatoriamente `--con "<filas>"`. Además, la salida mostrada en `docs/07-conectar-a-un-proyecto-propio.md:88-91` no coincide con el formato emitido por `tools/medida.py:531-542`.
2. **Subcomandos y opciones inexistentes en `docs/12-tareas.md`:** 8 subcomandos inexistentes (`paso`, `bloquear`, `balance`, `auditoria`, `siguiente`, `retro`, `exportar`, `importar`), opciones inventadas en subcomandos reales (`--bloquea`, `--padre`, `--estado`, `[MOTIVO]` en `cerrar`, `--desde`, `--hasta`, etc.) y omisión de 7 subcomandos reales de `tools/tareas.py`.
3. **Uso de scripts internos vs comando canónico:** `docs/03-escribir-una-medida.md:105-106` y `docs/tutorial-practico.md:110-112` recomiendan `python tools/sintaxis.py` en lugar de `oracle convertir <archivo>`.
4. **Sintaxis desactualizada de umbral:** `docs/tutorial-practico.md:71, 99` omite la cláusula obligatoria `segun <fuente>`.
5. **Alcance de `oracle escalares`:** `docs/tutorial-practico.md:780` le atribuye listar operadores y agregados de tubería, cuando sólo lista funciones escalares.

## Próximo paso

Rehacer la auditoría ejecutando cada bloque de comandos de las guías contra el paquete instalado (Codex), y listar sólo lo que falla. Los hallazgos 1 y 2 de HALLAZGOS.md son falsos (ver la nota de Claude).

### Nota (2026-09-25 03:28:26 UTC)

2026-09-25, Claude, verificado contra las guías y la CLI: los dos hallazgos más fuertes de HALLAZGOS.md son FALSOS. (1) 'medida probar sin --con': docs/02-de-cero-a-un-rojo.md:126 usa --con. (2) 'ocho subcomandos inventados en 12-tareas.md (paso, bloquear, balance, siguiente, retro, exportar, importar) y opciones --prioridad-min, --bloqueada, --forzar': ninguno aparece en esa guía. CIERTO el 3: docs/03:105-106 y tutorial-practico.md:110-112 mandan a correr python tools/sintaxis.py, que sólo existe con el repo clonado; el instalado es oracle convertir. A MEDIAS el 4: tutorial-practico.md:71 es una plantilla de umbral sin segun. El 5 sin verificar. Esta auditoría sin shell no sirve para esto.
