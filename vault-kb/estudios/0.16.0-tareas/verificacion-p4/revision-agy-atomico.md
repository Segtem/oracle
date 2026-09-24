# Revisión de solo lectura — Escrituras atómicas y contrastes en `tools/tareas.py`

---

## 1. Centralización de escrituras atómicas y corrección de permisos

### Diagnóstico del defecto reproducido por Codex
En las tres implementaciones actuales:
1. [`tools/tareas.py#L355-L375`](file:///home/workstation/Dev/oracle/tools/tareas.py#L355-L375) (`actualizar_estado_tarea`)
2. [`tools/tareas_contexto.py#L352-L372`](file:///home/workstation/Dev/oracle/tools/tareas_contexto.py#L352-L372) (`cmd_anotar`)
3. [`tools/tareas_contexto.py#L562-L582`](file:///home/workstation/Dev/oracle/tools/tareas_contexto.py#L562-L582) (`cmd_adjuntar`)

El archivo temporal se crea con `tempfile.NamedTemporaryFile`, que fija por defecto el modo en `0600`. Si `os.fchmod` falla (o no está disponible) y posteriormente `os.chmod` también falla (por ejemplo, restricciones del sistema de archivos o interceptores de prueba), **ambas excepciones se silencian con `pass`**. Acto seguido se ejecuta `os.replace(temp_path, tarea_md)`. En consecuencia, la función devuelve éxito, el documento se modifica en disco, pero sus permisos originales (ej. `0640`) quedan degradados a `0600`.

### Propuesta de centralización pequeña
Unificar la lógica en una función auxiliar en [`tools/tareas.py`](file:///home/workstation/Dev/oracle/tools/tareas.py), por ejemplo `guardar_texto_atomico(ruta_destino: Path, contenido_bytes: bytes) -> None`:

```python
def guardar_texto_atomico(ruta_destino: Path, contenido_bytes: bytes) -> None:
    # 1. Leer permisos originales; si stat falla, propagar OSError
    modo_anterior = ruta_destino.stat().st_mode & 0o777

    # 2. Crear temporal en el mismo directorio (mismo filesystem para asegurar replace atómico)
    with tempfile.NamedTemporaryFile(dir=ruta_destino.parent, delete=False) as tf:
        temp_path = Path(tf.name)
        try:
            tf.write(contenido_bytes)
            tf.flush()
            os.fsync(tf.fileno())

            # 3. Aplicar modo y propagar error si falla antes de reemplazar
            chmod_ok = False
            if hasattr(os, "fchmod"):
                try:
                    os.fchmod(tf.fileno(), modo_anterior)
                    chmod_ok = True
                except OSError:
                    pass

            tf.close()

            if not chmod_ok:
                # Falla explícita si ni fchmod ni chmod logran preservar el modo
                os.chmod(temp_path, modo_anterior)

            # 4. Reemplazo atómico solo si la preparación y los permisos fueron exitosos
            os.replace(temp_path, ruta_destino)
        except Exception:
            tf.close()
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            raise
```

### Preservación del rollback de adjuntos
En [`tools/tareas_contexto.py#L583-L588`](file:///home/workstation/Dev/oracle/tools/tareas_contexto.py#L583-L588) (`cmd_adjuntar`), la copia del archivo físico en `destino` ocurre *antes* de editar `TAREA.md`. Al lanzar la excepción desde `guardar_texto_atomico` ante un fallo de escritura o permisos, el bloque `except Exception:` de `cmd_adjuntar` captura el error, ejecuta `destino.unlink(missing_ok=True)` y sale con código 1. La reversión se mantiene limpia y completa.

### Tests de conducta faltantes
1. **Fallo de permisos no corrompe modo ni muta documento**: un test que configure `TAREA.md` en `0o640`, simule fallo en `fchmod` y `chmod` (vía mock que lance `OSError`), y verifique que `actualizar_estado_tarea` lance `OSError`, el documento conserve su texto anterior y su modo siga siendo `0o640` sin temporales residuales.
2. **Rollback de adjunto ante fallo de permisos**: un test de `cmd_adjuntar` con fallo provocado en chmod al actualizar `TAREA.md`, constatando que el archivo adjunto copiado es retirado y el proceso sale con 1.
3. **Preservación explícita de modos no estándar**: pruebas en `anotar` y `adjuntar` confirmando que un `TAREA.md` con permisos `0o640` conserva exactamente `0o640` tras una edición exitosa.

### Premisas y límites de concurrencia
- **Garantía real**: `os.replace` garantiza atomicidad a nivel de inodo en sistemas POSIX. Un lector concurrente nunca leerá un archivo parcial o roto, y una caída del proceso no dejará el archivo corrupto.
- **Límite real**: **No existe serialización ni locking de procesos** (`fcntl.flock` o equivalente). Si dos procesos ejecutan simultáneamente `anotar`, `adjuntar` o `cerrar` sobre la misma tarea:
  - Ambos leen la versión $N$.
  - Ambos generan un archivo temporal.
  - El último en ejecutar `os.replace` sobrescribe silenciosamente las notas o cambios del primero (*last-write-wins*).
  - Si una concurrencia entre procesos sobre la misma tarea se tornara un requisito futuro, requeriría un mecanismo de exclusión mutua o detección de colisión optimista basada en hash/mtime.

---

## 2. Contraste de equivalentes en `tools/tareas.py` con los usos reales

| Elemento | Ubicación | Análisis de uso real | ¿Es eliminable? / Riesgo |
|---|---|---|---|
| **Retorno `Path` de `asegurar_confinamiento` y `asegurar_confinamiento_archivo`** | [`tools/tareas.py#L100-L119`](file:///home/workstation/Dev/oracle/tools/tareas.py#L100-L119) | Las 8 invocaciones en el código ([`tareas.py:447, 459, 812, 891, 937`](file:///home/workstation/Dev/oracle/tools/tareas.py#L447); [`tareas_contexto.py:296, 482, 483`](file:///home/workstation/Dev/oracle/tools/tareas_contexto.py#L296)) descartan el valor retornado. Los tests no la llaman directo. | **Sí, el retorno es prescindible** (puede retornar `None`). Riesgo nulo en los consumidores actuales. |
| **Segundo `is_dir()` de `tareas` en límite Git** | [`tools/tareas.py#L170-L174`](file:///home/workstation/Dev/oracle/tools/tareas.py#L170-L174) | En [`L168`](file:///home/workstation/Dev/oracle/tools/tareas.py#L168) ya se evaluó `if (recorrido / "tareas").is_dir(): return recorrido`. Si el flujo alcanza la [`L170`](file:///home/workstation/Dev/oracle/tools/tareas.py#L170), esa condición ya dio `False`. Las líneas 172-173 son código inalcanzable. | **Sí, es 100% código muerto**. Riesgo nulo; debe reducirse a `if (recorrido / ".git").exists(): break`. |
| **Filtrado de `combining` antes del regex en `_sanear_slug`** | [`tools/tareas.py#L82-L86`](file:///home/workstation/Dev/oracle/tools/tareas.py#L82-L86) | La normalización NFKD separa diacríticos (ej. `ó` en `o` + `\u0301`). Si se eliminara el filtrado de combining, `\u0301` entraría al regex `[^a-zA-Z0-9]+` y se convertiría en un guión extra (`"desincronizaci-o-n"`). | **NO es eliminable**. Rompería la transliteración limpia de títulos con acentos a slugs legibles. |
| **Helper `generar_id_tarea`** | [`tools/tareas.py#L414-L434`](file:///home/workstation/Dev/oracle/tools/tareas.py#L414-L434) | En runtime de producción no tiene ningún uso (el CLI usa `crear_carpeta_tarea_atomica` en [`L675`](file:///home/workstation/Dev/oracle/tools/tareas.py#L675)). Solo se consume en [`tests/test_tareas.py#L165, L416, L422, L428`](file:///home/workstation/Dev/oracle/tests/test_tareas.py#L165). | **No es eliminable aisladamente** en `tareas.py` porque rompería [`tests/test_tareas.py`](file:///home/workstation/Dev/oracle/tests/test_tareas.py). Para retirarlo del runtime, los tests deben migrarse previamente a usar `crear_carpeta_tarea_atomica` o mover el helper a `test_tareas.py`. |
