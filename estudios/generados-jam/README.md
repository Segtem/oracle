# Estudio: evidencia generada sobre un consumidor real (2026-08-26)

Los 38 `.caso` de esta carpeta los fabricó `oracle caso generar` a partir de la **forma** de las
medidas de un proyecto consumidor —41 medidas, 24 casos escritos a mano—. No están en `corpus/`
a propósito: no son evidencia de Oracle, son el resultado de un experimento sobre otro repo.

## Lo que se midió, con `tools/mutar.py` y sobre una copia

|  | antes (24 casos) | después (62 casos) |
|---|---|---|
| mutantes de medida generados | 238 | **315** |
| murieron | 238 | 315 |
| **sobrevivieron** | **0** | **0** |
| `meta.toda_medida_esta_ejercitada` | **✗ 10** | **✓ 0** |

## Lo que ese cuadro dice, y lo que no

**No mató ni un mutante sobreviviente, porque no había ninguno.** El proyecto ya estaba en
`0 sobrevivientes` antes de generar nada. Un informe que dijera «100 % de mutantes muertos» sería
cierto y no significaría nada: es el mismo «489 tests OK» que el corpus de Oracle registra como
defecto —una cifra que sube y no distingue haber cubierto algo nuevo de haber medido otra vez lo ya
cubierto—.

**Lo que sí cerró es un agujero real, y es el que importa.** Diez medidas del consumidor no estaban
*ejercitadas*: ningún caso las tocaba, así que el mutador no les generaba mutantes y no podían tener
sobrevivientes. Cero sobrevivientes sobre 31 de 41 medidas se lee idéntico a cero sobrevivientes
sobre las 41. La medida `meta.toda_medida_esta_ejercitada` ya lo estaba diciendo —valor 10, en
rojo—; lo que faltaba era la evidencia para cerrarlo, y ésa es la que la herramienta fabrica.
Después: **41 de 41 ejercitadas, 77 mutantes más juzgados, ninguno vivo.**

**28 de los 38 casos no movieron el marcador.** Cubrían medidas que ya estaban ejercitadas. El
generador declara ruido sólo cuando una medida ya tiene 0 sobrevivientes, y ese criterio deja pasar
casos redundantes: es una debilidad conocida del filtro, no un descuido del estudio.

## El límite que ninguna cifra de acá levanta

Esta evidencia discrimina un mutante y **no dice nada sobre el mundo**. Un caso típico:

```
documento: area, carpeta
    "valor_a", "valor_b"
    "mismo_valor", "mismo_valor"
```

Matar un mutante no necesita evidencia verdadera: necesita evidencia que **difiera** entre la medida
y su mutante, y eso es una propiedad formal del par, que se fabrica. Lo que no se fabrica es la
sorpresa —un punto ciego que puedo imaginar ya dejó de ser mi punto ciego—. Por eso cada uno de
estos casos declara `procedencia: generada`, y por eso una medida sostenida sólo por ellos sigue
apareciendo en rojo bajo `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada`.

## Reproducirlo

La corrida necesita una copia del consumidor, porque uno de sus fixtures diferenciales está vencido
—deuda previa de ese proyecto— y `mutar.py` se niega a correr entero mientras lo esté. En la copia
se aparta ese fixture y se corre:

```bash
python tools/mutar.py --proyecto <copia>/medidas --confiar-escalares
```
