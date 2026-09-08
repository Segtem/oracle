# Una sombra apagaba también el aviso de que la deuda crecía

**2026-09-08 · corte 0.12.0**

## Qué compraba una sombra, y qué compraba de más

La sombra existe por una razón buena: heredar un catálogo de políticas te pone en rojo, y con razón
—sus medidas ven cosas que las tuyas no veían—. Si la primera experiencia de heredarlo es que el
proyecto entero deja de pasar, no se hereda una segunda vez. La sombra apaga la **consecuencia** del
rojo, no la medición: la medida se sigue evaluando, se sigue imprimiendo con su cuenta, y tres
medidas la vigilan.

Lo que no estaba escrito en ningún lado es que también apagaba el **aviso de que el problema crece**.

`meta.todo_caso_observado_declara_de_donde_salio` estaba en 94. Un caso nuevo mal escrito la habría
puesto en 95 y la corrida habría pasado igual, porque 94 y 95 son los dos «rojo en sombra» y nadie
mira el número. La sombra deja de ser una etapa de transición y pasa a ser el lugar donde el
problema se agranda.

## Ya había un freno, y estaba en el peor lugar posible

El workflow tenía esto:

```yaml
# Baja de a un caso, a medida que cada `origen` dice de dónde salió. Si baja, se actualiza
# acá a mano: es el registro de que la deuda se está cerrando y no de que se apagó.
grep -q 'todo_caso_observado_declara_de_donde_salio       94 (<= 0)   \[EN SOMBRA\]' /tmp/acept.txt
```

Funcionaba, y el comentario explica exactamente por qué existía. Pero el número vivía en el archivo
de CI —no en el proyecto—, había que acordarse de editarlo, y **no viajaba a los consumidores**: Jam
y LyraGASP tienen tres sombras cada uno y ningún freno equivalente.

## La cota

Una entrada de `sombra` en `oracle.json` gana un campo opcional:

```json
"meta.todo_caso_observado_declara_de_donde_salio": {
  "desde": "2026-09-07", "porque": "…", "cota": 94
}
```

Y dos medidas la vigilan, una por dirección:

| | qué atrapa | por qué hace falta |
|---|---|---|
| `meta.ninguna_sombra_supera_su_cota` | la deuda **sube** | apagar la consecuencia no puede comprar que el problema crezca |
| `meta.ninguna_cota_mas_alta_que_su_deuda` | la cota queda **encima** | una cota con holgura vuelve a comprar lo mismo, y esconde el progreso |

La segunda es la que casi no escribo, y es la mitad del mecanismo. Sin ella la cota se escribe una
vez con lugar de sobra y no vuelve a tocarse nunca: si la deuda baja de 94 a 90 y la cota sigue en
94, las cuatro cerradas quedan disponibles para volver a abrirse gratis, y el proyecto no registra
su propio progreso. **Una cota es la deuda de hoy, no un presupuesto.**

Ninguna de las dos se puede tapar: las medidas que vigilan la sombra no se pueden poner en sombra,
que es la regla que impide que apagar salga gratis.

Las dos direcciones están **comprobadas contra el árbol**, no razonadas. Sobre una copia:

```
deuda 95 contra cota 94  →  ✗ meta.ninguna_sombra_supera_su_cota          1 (<= 0)
cota 100 sobre deuda 94  →  ✗ meta.ninguna_cota_mas_alta_que_su_deuda     1 (<= 0)
```

## El defecto que apareció escribiéndolo

La medida nueva daba verde. Y daba verde porque **no corría**.

La aceptación elegía las medidas que juzgan la sombra así:

```python
vigilan = [m for mid, m in sorted(catalogo.items()) if "sombra" in mid]
```

Por **subcadena en el id**. Un contrato de nombres que nadie había escrito en ninguna parte, y que
se paga en silencio: `meta.ninguna_cota_mas_alta_que_su_deuda` no tiene la palabra, así que nunca
entró a la segunda vuelta, y su `✓` era el de una medida que no se evaluó.

Es el mismo defecto que este repositorio cataloga noventa veces —un verde que no significa nada—,
cometido en el selector de su propia aceptación. Ahora se eligen por la relación que **leen**:

```python
vigilan = [m for _mid, m in sorted(catalogo.items()) if "sombra" in relaciones_de_medida(m)]
```

Lo que la medida lee está en su AST y no se puede olvidar de escribir.

## Los bordes los encontró la mutación, no la lectura

Tres tandas, tres cosas distintas:

- **`meta.ninguna_cota_mas_alta_que_su_deuda` tenía dos mutantes vivos.** El umbral aflojado a
  `<= 1` sobrevivía porque mi único rojo valía exactamente 1; y `valor >= 0` vuelto estricto
  sobrevivía porque ningún caso traía una deuda de **cero** — que es justo donde la holgura más
  engaña, porque ahí la cota no sólo esconde el progreso: esconde que la sombra entera sobra.
- **`cota >= 0` vuelto `> 0` sobrevivía en cuatro sitios.** Una cota de **cero** se habría leído
  como «no declarada»: la cota más exigente que se puede escribir, apagada en silencio.
- **El centinela `-1` estaba escrito dos veces** —el default de la clase y el del lector— y ningún
  test lo ataba. No es un detalle interno: ese número sale en la relación `sombra` que leen las
  medidas, y los casos `491` y `493` lo tienen escrito. Pasó a ser `SIN_COTA`, en un solo sitio.

## Lo que no hace

La cota **no baja sola**. Cuando una deuda se cierra hay que bajarla a mano, y eso es la mitad del
punto: el número lo escribe una persona y queda en el commit, que es la diferencia entre un registro
y un contador.

Y no verifica que la cota sea correcta en un proyecto que no corrió esa medida: ahí el valor es -1 y
las dos medidas se abstienen, porque no se puede afirmar el tamaño de una deuda que nadie midió.
