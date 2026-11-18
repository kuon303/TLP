# Criterios de equivalencia: spaCy y NLTK

## Objetivo

spaCy y NLTK generan anotaciones linguisticas, no decisiones de pertenencia a
la CFG. En este proyecto se aplican criterios fijos para obtener un veredicto
binario a partir de sus salidas. Los criterios no consultan la respuesta
esperada; esa etiqueta solo se utiliza en la evaluacion posterior.

## Estructura evaluada

Patron utilizado por los adaptadores:

`ART SUST ADJ? (QUE VERBO ADV? (PREP NOMINAL)?)? VERBO ADV? (PREP NOMINAL)? PUNTO?`

`NOMINAL = ART SUST ADJ?`

- Se revisa la concordancia de genero y numero cuando hay rasgos morfologicos.
- Se comprueba la concordancia de numero entre sujeto y verbo.
- Se considera el tiempo presente cuando la herramienta lo proporciona.
- Se permite un adjetivo por nominal, un adverbio por predicado y una relativa simple.
- spaCy requiere verbo principal `ROOT` y sujeto `nsubj` relacionado. En las
  relativas se comprueba `acl` unido al sustantivo correspondiente.
- NLTK usa etiquetas CESS-ESP/EAGLES y orden de tokens, ya que el etiquetador
  utilizado no genera dependencias sintacticas.
- `SIN_ETIQUETA` impide validar la estructura en el adaptador de NLTK.

## Interpretacion de resultados

Los veredictos son decisiones de los adaptadores y no validaciones nativas de
spaCy o NLTK. Un rechazo puede producirse por errores POS, etiquetas ausentes,
dependencias incorrectas o diferencias entre estos criterios y la CFG formal.

El corpus contiene 40 positivos y 20 negativos, repartidos en tres niveles de
20 oraciones. Se informan precision, recall, rechazo correcto, falsos positivos,
falsos negativos y exactitud balanceada para no depender solo de la exactitud.

`referencia_pos.csv` contiene 396 categorias gramaticales esperadas por token.
Las categorias se contrastan con el texto y la funcion de cada palabra. La
referencia debe ser revisada manualmente antes de utilizarla como resultado
academico definitivo.

## Reproducibilidad

Los resultados originales se almacenan en `logs/spacy.json` y `logs/nltk.json`.
Las decisiones derivadas se guardan en `logs/spacy_cfg.json` y
`logs/nltk_cfg.json`. El adaptador registra las huellas SHA-256 de las entradas,
y `evaluar.py` comprueba la correspondencia con el corpus actual.

Los registros de 40 oraciones pertenecen al experimento anterior y no se
utilizan en el benchmark vigente. Los criterios se mantienen fijos durante
la comparacion.
