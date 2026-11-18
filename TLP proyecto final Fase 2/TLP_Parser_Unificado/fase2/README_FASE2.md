# Fase 2 - Corpus y comparacion de enfoques

## Objetivo

Comparar el parser LL(1) propio, spaCy, NLTK y un LLM con el mismo conjunto de
60 oraciones. El LLM se ejecuta en zero-shot y few-shot, por lo que las tablas
contienen cinco filas para cuatro enfoques experimentales.

## Datos

- `corpus.csv`: 60 oraciones, 20 por nivel, con 40 ACEPTADA y 20 RECHAZADA
  de acuerdo con la CFG V3. Se conservan los campos de descripcion para
  justificar los casos.
- `referencia_pos.csv`: 396 etiquetas POS de referencia por token, incluida
  puntuacion. Es una anotacion de referencia preparada para este experimento;
  debe revisarse manualmente antes de la entrega academica definitiva.
- `DISENO_CORPUS.md`: criterios de seleccion y limites de interpretacion.

## Programas y registros

| Programa | Archivo de evidencia |
| --- | --- |
| `benchmark_parser.py` | `logs/parser.json` y `resultados/analisis_corpus.html` |
| `benchmark_spacy.py` | `logs/spacy.json` |
| `benchmark_nltk.py` | `logs/nltk.json` |
| `adaptar_nlp.py` | `logs/spacy_cfg.json`, `logs/nltk_cfg.json` |
| `benchmark_llm_gemini.py` | `logs/gemini_zero_shot.jsonl`, `logs/gemini_few_shot.jsonl` |
| Resumen de Gemini | `logs/llm_zero_shot.json`, `logs/llm_few_shot.json` |
| `evaluar_pos.py` | `resultados/tabla_pos.csv`, `resultados/errores_pos.csv` |
| `evaluar.py` | `resultados/tabla_metricas.csv`, `resultados/errores.csv`, `resultados/grafica_metricas.svg` |
| `mostrar_corpus.py` | `resultados/analisis_corpus.html` y `.txt`, sin modificar logs |

`benchmark_llm_openai.py` permanece en el proyecto porque contiene la funcion
que genera las producciones, el vocabulario y los ejemplos para los prompts
de Gemini. **La corrida final no utilizo OpenAI API.**

Los criterios de equivalencia para spaCy y NLTK estan definidos en
`criterios_nlp.py` y `CRITERIOS_EVALUACION.md`. Estas herramientas no validan
por si mismas la pertenencia a nuestra CFG: el criterio transforma sus
anotaciones en decisiones binarias. `adaptar_nlp.py` no usa `esperado_cfg`
para decidir la aceptacion.

## Reproducibilidad sin llamadas API

Todos los comandos se ejecutan desde la raiz del repositorio:

```powershell
python fase2/evaluar_pos.py
python fase2/evaluar.py
python -m unittest discover -s fase2 -p "pruebas_*.py" -v
```

El calculo de las metricas es determinista sobre los logs y el corpus
incluidos. Los scripts verifican que las decisiones correspondan a las 60
oraciones. Para comprobar anotaciones NLP originales, consultar los archivos
JSON de `logs/` y las versiones anotadas en sus metadatos.

## Volver a ejecutar los benchmarks

```powershell
python -m pip install -r requirements.txt
python -m spacy download es_core_news_sm
python -m nltk.downloader cess_esp
python fase2/benchmark_parser.py
python fase2/benchmark_spacy.py
python fase2/benchmark_nltk.py
python fase2/adaptar_nlp.py
python fase2/evaluar_pos.py
python fase2/evaluar.py
```

Estos comandos vuelven a generar archivos en `logs/` y `resultados/`. Para
conservar la evidencia de la corrida original se recomienda usar una copia
separada del repositorio.

## Demostracion detallada del corpus

Para analizar nuevamente las 60 oraciones con nuestro parser y mostrar solo un
resumen en la terminal:

```powershell
python fase2/mostrar_corpus.py
```

Se genera `fase2/resultados/analisis_corpus.html` y una version `.txt`. El
informe contiene los 60 casos, las decisiones, el motivo que se puede obtener
del parser, el error exacto cuando existe y el arbol completo para cada caso
aceptado. Si el parser acepta una oracion que la referencia marca como
rechazada, conserva el arbol y la identifica como falso positivo.

El informe incluye las decisiones de spaCy, NLTK y Gemini cuando los logs
completos ya estan disponibles. No realiza llamadas a Gemini y no altera los
registros originales. Las notas del corpus se muestran por separado y no se
utilizan para tomar decisiones.

`python fase2/benchmark_parser.py` tambien genera el mismo informe junto con
`logs/parser.json`. Puede utilizarse `--sin-reporte` para omitirlo. Aun con
`--sin-arbol`, el informe muestra los arboles; esa opcion solo omite los arboles
del log JSON. Para abrir el informe se utiliza cualquier navegador web.

## Gemini zero-shot y few-shot

El modelo utilizado fue `gemini-3.5-flash-lite`, con temperatura 0. Las
instrucciones exactas y las plantillas de mensaje estan en `prompts/` con
prefijo `gemini_`. El zero-shot recibe la CFG y el vocabulario; el few-shot
incluye ademas cuatro ejemplos externos al corpus de evaluacion.

La API devuelve un objeto JSON con `oracion`, `resultado` y `razon` dentro de
`resultado`. Los logs JSONL guardan la solicitud exacta, fechas UTC, respuesta
completa del SDK y los intentos fallidos (incluidos los errores 503). Solo
las 60 clasificaciones validas por modalidad se utilizan para las metricas.

Los archivos `resultados/gemini_*_respuestas.json` contienen versiones
compactas para lectura; no reemplazan los registros originales. Para ejecutar
una nueva corrida con una clave propia, consultar `README_GEMINI.md`.

## Metricas e interpretacion

Se calculan precision, recall, tasa de rechazo correcto, TP, TN, FP, FN,
exactitud y exactitud balanceada. En el analisis POS se separan errores de
etiquetado y tokens sin etiqueta. No se atribuye a spaCy ni a NLTK un
validador CFG nativo.

Las 60 etiquetas esperadas se construyeron para el subconjunto de la CFG, por
lo que el 100% del parser no mide dominio del español completo. El corpus no
es una muestra aleatoria. La referencia POS y las causas de los errores
requieren interpretacion academica en el informe.

El informe PDF final es un archivo separado y no esta incluido en este
repositorio de codigo y evidencia.
