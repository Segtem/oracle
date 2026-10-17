# Completar el release de GitHub para v0.38.1

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: release

### Nota (2026-10-02 19:20:34 UTC)

Revisión solicitada de commit, push, tag y release: al inicio el árbol estaba limpio; HEAD y main remoto coinciden en ea5007d3389ef02447e3cdaa0215d475d0457935. git ls-remote confirma el tag anotado v0.38.1 publicado, resuelto a 790a95e7c32d41cd5ac12309005345b4c771b0df; main tiene dos commits posteriores de registro y cierre. gh release list confirma que el último release de GitHub es v0.38.0, sin release v0.38.1. Sólo se solicitó revisar: no se ejecutaron commit, push, tag ni publicación. Esta tarea registra el pendiente detectado.

## Próximo paso

Preparar el título y las notas del release `v0.38.1` a partir de `NOTAS-DE-RELEASE.md` y del tag existente; obtener autorización para publicarlo en GitHub, ya que el pedido actual sólo fue revisar el estado. Registrar esta tarea mediante commit y push cuando se retome el trabajo.

### Nota (2026-10-17 11:53:06 UTC)

Hecho el 2026-10-17: release de GitHub v0.38.1 (https://github.com/Segtem/oracle/releases/tag/v0.38.1) desde el tag existente 790a95e, con las notas de NOTAS-DE-RELEASE.md y el wheel y el sdist bajados de PyPI (mismas huellas); no marcado como latest.
