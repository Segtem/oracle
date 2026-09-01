# Biblioteca Segtem de ejemplo

Es una distribución instalable y contiene sólo datos. Desde la raíz de Oracle:

```bash
python -m pip install --no-deps ./ejemplo/biblioteca-segtem
```

La instalación no activa sus políticas. El proyecto consumidor las selecciona por el id del
manifiesto:

```json
{
  "esquema": "oracle.proyecto/v1",
  "bibliotecas": ["segtem.meta.calidad"]
}
```

El manifiesto instalado queda en la ruta fija
`oracle_bibliotecas/oracle_biblioteca_segtem_meta_calidad/oracle-biblioteca.toml`. El nombre del
segundo directorio se deriva del nombre de la distribución, no de código importable.
