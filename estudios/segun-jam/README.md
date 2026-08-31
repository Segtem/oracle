# Migración de los 41 umbrales Jam a `segun`

Este directorio es un entregable para copiar a `~/Dev/jam/medidas/catalogos/` cuando el dueño del
consumidor decida adoptarlo. Jam se leyó, pero no se modificó.

La clasificación no la hizo una herramienta: `segun` es un juicio sobre de dónde salió el número.
El script sólo aplica esas decisiones a un espejo y verifica que el universo de entrada siga siendo
exactamente el clasificado.

## Resultado

| origen | medidas |
|---|---:|
| `contrato` | 38 |
| `convencion` | 3 |
| `medicion` | 0 |
| `tanteo` | 0 |

El dato incómodo es que Jam no tiene ningún umbral final que declare provenir de una medición. Tampoco
hay uno documentado como «se probó hasta que anduvo»: etiquetarlo `tanteo` inventaría procedencia.

Las decisiones con más riesgo se resolvieron así:

- `snap.al_ras`, `snap.grilla` y `snap.yaw` son las tres convenciones: su umbral final es la
  tolerancia discutible que decide cuándo una diferencia pasa a importar visualmente.
- `scatter.cobertura` es contrato, como dice su propia defensa: el dominio fijó 60% y el umbral final
  cero sólo prohíbe celdas que incumplan esa regla.
- Las 31 invocaciones `ninguno*` tienen umbral final `contar(1) <= 0`: ese cero es contractual aunque
  el predicado interno contenga una tolerancia discutible. `reemplazo.centrado`, por ejemplo, usa
  1 cm dentro del filtro, pero `segun` describe el cero final, no ese literal.
- `colocacion.bounds` conserva una deuda visible: nadie justifica el `0.001` interno con una medición
  o una norma. Aun así, la macro concluye contractualmente que debe haber cero filas ofensivas.
- Los invariantes topológicos de malla y las políticas declaradas de Vault son contratos de sus
  respectivos algoritmos y formatos.

## Reproducción

Desde la raíz de Oracle:

```bash
python estudios/segun-jam/migrar.py ~/Dev/jam
python estudios/segun-jam/migrar.py ~/Dev/jam --verificar
```

La primera orden sólo escribe bajo este estudio. La segunda no escribe y falla si cambió una fuente,
si apareció o desapareció una medida, si la forma dejó de ser compatible o si el espejo no coincide.

El espejo completo cargó como catálogo Oracle con los escalares y macros de Jam: 41 medidas,
38 `contrato` y 3 `convencion`, sin `sin_declarar`. La suite de Oracle quedó en 731 pruebas verdes.

La clasificación se cruzó además con una lectura independiente de agy, sin ediciones. Los puntos
representativos se comprobaron contra:

- `medidas/catalogos/geometria/snap.al_ras.json:4-6`, `geometry.py:18` y
  `oracle_snap.py:35-50` para la convención de contacto de 1 cm;
- `medidas/catalogos/geometria/snap.grilla.json:6-8`, `snap.py:25-36` y
  `oracle_shadow.py:108-119` para separar el paso de 100 cm de la tolerancia final de 1 cm;
- `medidas/catalogos/scatter/scatter.cobertura.json:4-6` y
  `oracle_scatter.py:30-32,53-68` para confirmar que 0,6 vive en el filtro y el cero final es
  contractual;
- `medidas/catalogos/reemplazo/reemplazo.centrado.json:2-7` y
  `oracle_reemplazo.py:17-27` para confirmar la misma separación entre tolerancia interna y umbral
  final.
