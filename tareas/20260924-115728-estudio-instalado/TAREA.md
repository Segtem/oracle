# Hacer funcionar oracle-estudio desde el wheel instalado

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

## Evidencia

Al instalar un wheel local en un venv aislado y ejecutar `oracle-estudio --proyecto <checkout>
--destino <temporal>` fuera del árbol, el proceso sale con código 1: `tools/estudio.py`
busca `README.md` bajo `site-packages/oracle_metalenguaje/`, donde el wheel no lo incluye.
Desde el árbol, `python3 tools/estudio.py --destino <temporal>` sí generó los 10 documentos.
La mudanza de `repo-limpio` no resuelve esta frontera de empaquetado.

## Próximo paso

Definir qué partes del paquete de estudio deben viajar en el wheel y adaptar la generación
instalada; verificarla desde un venv aislado y desde el árbol.
