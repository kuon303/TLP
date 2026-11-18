# Diseño del corpus de Fase 2

## Distribucion

| Nivel | ACEPTADA | RECHAZADA | Total |
| --- | ---: | ---: | ---: |
| 1 - simple | 16 | 4 | 20 |
| 2 - intermedio | 15 | 5 | 20 |
| 3 - complejo | 9 | 11 | 20 |
| Total | 40 | 20 | 60 |

## Seleccion

El nivel 1 contiene sujetos, articulos, sustantivos y verbos con variaciones
sencillas. El nivel 2 incorpora adjetivos, adverbios, frases preposicionales
y relativas simples. El nivel 3 combina estructuras largas que la CFG acepta
con otras que exceden sus reglas: subordinadas anidadas, coordinacion,
orden invertido, dos modificadores consecutivos, causales y objeto directo.

La columna `esperado_cfg` indica el resultado teorico definido por las
producciones de la gramatica española V3. Ese resultado se contrasto con el
parser. `correcta_espanol` distingue la correccion linguistica general de la
pertenencia al subconjunto de la CFG.

## Limitaciones

Este corpus fue diseñado para las capacidades y limites de la CFG. No
representa una muestra aleatoria del español ni permite extrapolar el
resultado al idioma completo. El conjunto contiene el doble de positivos
que de negativos, y los rechazos se concentran mas en el nivel 3.

Por esa distribucion, el informe utiliza tambien exactitud balanceada y
separa las metricas por clase cuando corresponde. El 100% del parser en su
propio corpus solo muestra consistencia con las etiquetas esperadas.

La referencia POS tiene 396 tokens y debe revisarse manualmente. Todos los
enfoques procesan las mismas 60 oraciones. Los logs antiguos de 40 entradas
no forman parte de este experimento.
