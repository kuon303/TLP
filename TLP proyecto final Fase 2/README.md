# Parser LL(1) y comparacion con NLP moderno

Proyecto de **Teoria de Lenguajes de Programacion - Fase 2**.

Se compara un parser LL(1) propio con spaCy, NLTK y Gemini para comprobar si
60 oraciones pertenecen a un **subconjunto controlado del español**, definido
por la gramatica libre de contexto (CFG) del proyecto. El parser de la Fase 1
se conserva con sus lexers y gramaticas de C++ y español V3.

El experimento utiliza **cuatro enfoques** y presenta **cinco resultados**:
parser LL(1), spaCy, NLTK, Gemini zero-shot y Gemini few-shot.

## 1. Organizacion del proyecto

| Archivo o carpeta | Funcion |
| --- | --- |
| `main.py` | Menu interactivo del parser original para C++ y español. |
| `parser_ll1.py` | Parser predictivo LL(1): calcula FIRST, FOLLOW, tabla de analisis y construye el arbol. |
| `lexer_cpp.py`, `gramatica_cpp.py` | Analisis lexico y gramatica del subconjunto de C++. |
| `lexer_es_v3.py`, `gramatica_es_v3.py`, `vocabulario_es.py` | Tokens, producciones y vocabulario del subconjunto de español. |
| `fase2/corpus.csv` | Las 60 oraciones, nivel, etiqueta CFG esperada y justificaciones. |
| `fase2/benchmark_parser.py` | Ejecuta el corpus con el parser LL(1) y guarda sus decisiones. |
| `fase2/benchmark_spacy.py` | Obtiene las anotaciones POS, morfologicas y de dependencias de spaCy. |
| `fase2/benchmark_nltk.py` | Entrena un etiquetador con CESS-ESP y etiqueta el corpus. |
| `fase2/criterios_nlp.py`, `fase2/adaptar_nlp.py` | Transforman las anotaciones NLP en decisiones ACEPTADA/RECHAZADA mediante criterios definidos por el grupo. |
| `fase2/benchmark_llm_gemini.py` | Experimento de Gemini zero-shot y few-shot. |
| `fase2/benchmark_llm_openai.py` | Modulo auxiliar que reutiliza Gemini para construir las instrucciones, reglas y vocabulario; **no se uso OpenAI API** en la corrida final. |
| `fase2/evaluar_pos.py` | Compara las etiquetas de spaCy y NLTK con `referencia_pos.csv`. |
| `fase2/evaluar.py` | Calcula precision, recall, rechazo correcto, TP, TN, FP, FN y genera tablas y grafica. |
| `fase2/mostrar_corpus.py` | Analiza las 60 oraciones con el parser y genera el informe HTML/TXT, sin modificar logs. |
| `fase2/logs/` | Registros originales, decisiones derivadas y respuestas de Gemini. |
| `fase2/prompts/` | Instrucciones y plantillas exactas de Gemini. |
| `fase2/resultados/` | Tablas, errores, grafica, respuestas resumidas e informe por oracion. |

Los archivos `.env`, `.venv` y otras configuraciones privadas no forman parte
del repositorio. La plantilla `.env.example` no contiene credenciales.

## 2. Requisitos y preparacion

- **Python 3.13**. Los programas se ejecutan desde la **raiz del repositorio**,
  donde se encuentra `main.py`.
- Para **recalcular las metricas desde los logs incluidos**, basta Python: no
  hace falta acceder a internet ni tener una clave API.
- Para **volver a ejecutar spaCy y NLTK**, se necesitan las dependencias y
  recursos linguisticos correspondientes.

En PowerShell, la instalacion para realizar nuevas corridas es:

```powershell
python -m pip install -r requirements.txt
python -m spacy download es_core_news_sm
python -m nltk.downloader cess_esp
```

Si el comando `python` apunta a otra version, se puede utilizar `py -3.13`
en su lugar. Es recomendable utilizar un entorno virtual propio, no incluirlo
en GitHub.

Los logs originales indican las versiones utilizadas; entre ellas estan
**spaCy 3.8.18**, modelo **`es_core_news_sm`** y **NLTK 3.10.4** con el corpus
**CESS-ESP**. Los modelos estadisticos pueden producir resultados distintos
si se cambian sus versiones.

## 3. Comprobacion rapida sin ejecutar de nuevo los modelos

Esta es la opcion recomendada para **verificar las cifras de la entrega**,
porque utiliza la evidencia ya almacenada y no reemplaza los logs de las
corridas originales:

```powershell
python fase2/evaluar_pos.py
python fase2/evaluar.py
python fase2/mostrar_corpus.py
```

- `evaluar_pos.py` compara los resultados de etiquetado con las etiquetas de
  referencia y genera `tabla_pos.csv` y `errores_pos.csv`.
- `evaluar.py` compara cada decision con `esperado_cfg` y genera
  `tabla_metricas.csv`, `tabla_metricas.json`, `errores.csv` y
  `grafica_metricas.svg`.
- `mostrar_corpus.py` ejecuta nuestro parser sobre las 60 oraciones y muestra
  **un resumen breve en consola**. Genera `analisis_corpus.html` y su copia
  `.txt`, con explicaciones y arboles sintacticos, sin modificar ningun log.

Los documentos se guardan en **`fase2/resultados/`**. Para examinar el analisis
por oracion, abrir `fase2/resultados/analisis_corpus.html` en un navegador.

Para ejecutar las pruebas automatizadas del proyecto:

```powershell
python -m unittest discover -s fase2 -p "pruebas_*.py" -v
```

## 4. Repetir el experimento local completo, paso a paso

**Importante:** los benchmarks regeneran archivos en `fase2/logs/` y
`fase2/resultados/`. Por eso los logs originale estan en una carpeta llamada **Resultados obtenidos originales** dentro de la carpeta `fase2/logs/`.

Con las dependencias y recursos del apartado 2 instalados, ejecutar **en este
orden** desde la raiz:

```powershell
python fase2/benchmark_parser.py
python fase2/benchmark_spacy.py
python fase2/benchmark_nltk.py
python fase2/adaptar_nlp.py
python fase2/evaluar_pos.py
python fase2/evaluar.py
python fase2/mostrar_corpus.py
```

| Orden | Comando | Por que se ejecuta en ese momento |
| --- | --- | --- |
| 1 | `benchmark_parser.py` | Lee `corpus.csv`, aplica el lexer y parser V3, registra ACEPTADA/RECHAZADA y construye el arbol cuando acepta. Guarda `logs/parser.json` y un informe HTML/TXT. |
| 2 | `benchmark_spacy.py` | Procesa las mismas 60 oraciones con el modelo español de spaCy. Guarda **anotaciones**, no un veredicto CFG, en `logs/spacy.json`. |
| 3 | `benchmark_nltk.py` | Entrena el etiquetador con CESS-ESP y etiqueta las 60 oraciones. Guarda **anotaciones** en `logs/nltk.json`. |
| 4 | `adaptar_nlp.py` | Lee los dos logs anteriores y aplica los criterios de equivalencia. Genera `logs/spacy_cfg.json` y `logs/nltk_cfg.json` con decisiones binarias comparables. |
| 5 | `evaluar_pos.py` | Calcula los errores de categorias gramaticales de spaCy y NLTK contra `referencia_pos.csv`. |
| 6 | `evaluar.py` | Compara las decisiones del parser, spaCy, NLTK y las dos modalidades de Gemini con el corpus; calcula las metricas y los errores. |
| 7 | `mostrar_corpus.py` | Regenera el documento detallado usando el parser y las comparaciones de todos los logs disponibles. No altera los logs. |

**Por que existe `adaptar_nlp.py`:** spaCy y NLTK producen analisis y
etiquetas gramaticales; **no son validadores directos de nuestra CFG**. Los
criterios estan definidos en `fase2/criterios_nlp.py` y documentados en
`fase2/CRITERIOS_EVALUACION.md`. Se aplican de forma consistente al corpus,
sin utilizar la etiqueta esperada para tomar la decision.

Los scripts comparten el mismo `fase2/corpus.csv`. La columna `oracion` es la
entrada analizada; `esperado_cfg` sirve **despues** para comparar resultados,
no para que las herramientas conozcan de antemano la respuesta correcta.

## 5. Analisis detallado y arboles sintacticos

Para mostrar la demostracion del corpus sin volver a escribir `parser.json`:

```powershell
python fase2/mostrar_corpus.py
```

La terminal presenta un resumen de las 60 oraciones: aceptadas, rechazadas,
coincidencias, falsos positivos y falsos negativos, ademas de la ruta del
archivo generado. **No imprime los 40 arboles en consola**.

El documento `fase2/resultados/analisis_corpus.html` contiene, para cada caso:

- Oracion, ID, nivel y etiqueta esperada segun nuestra CFG.
- Resultado real del parser y explicacion de la aceptacion o del rechazo.
- Tokens reconocidos y error del lexer o parser, cuando corresponda.
- Arbol sintactico completo **si el parser acepta**.
- Comparacion con las decisiones guardadas de spaCy, NLTK y Gemini cuando
  estan disponibles, incluyendo motivos de clasificacion.
- Indicacion visible de **falso positivo** si el parser aceptara una oracion
  marcada como RECHAZADA; en ese caso el arbol se conserva, pero el informe
  advierte la discrepancia.

La justificacion escrita en `corpus.csv` se presenta como **referencia
separada**. No forma parte de la decision del parser.

## 6. Gemini: zero-shot y few-shot

Se utilizo **`gemini-3.5-flash-lite`**, con temperatura **0**, en dos
modalidades sobre las mismas 60 oraciones:

- **Zero-shot:** se entrega la CFG completa y el vocabulario, sin ejemplos
  resueltos.
- **Few-shot:** se entrega lo mismo y cuatro ejemplos resueltos **externos al
  corpus de evaluacion**.

Las instrucciones y plantillas exactas estan en `fase2/prompts/` con prefijo
`gemini_`. Las 120 respuestas validas ya estan incluidas:

| Archivo | Contenido |
| --- | --- |
| `fase2/logs/gemini_zero_shot.jsonl` | Registro original por solicitud zero-shot, incluidos reintentos fallidos. |
| `fase2/logs/gemini_few_shot.jsonl` | Registro original por solicitud few-shot, incluidos reintentos fallidos. |
| `fase2/logs/llm_zero_shot.json` | 60 clasificaciones validas para `evaluar.py`. |
| `fase2/logs/llm_few_shot.json` | 60 clasificaciones validas para `evaluar.py`. |
| `fase2/resultados/gemini_*_respuestas.json` | Versiones compactas para consulta. |

Los JSONL conservan solicitudes, respuestas disponibles de la API,
configuracion y marcas UTC. Los intentos fallidos **no se cuentan como
clasificaciones validas**.

**No es necesario volver a ejecutar Gemini para comprobar las metricas.**
Para generar nuevas respuestas se requiere una clave API propia y pueden
aplicarse limites de cuota o costos. La guia especifica esta en
[`fase2/README_GEMINI.md`](fase2/README_GEMINI.md). Una nueva corrida debe
hacerse en otra copia para no mezclar resultados.

## 7. Resultados de referencia y como interpretarlos

En la corrida documentada, con 60 oraciones por evaluacion:

| Enfoque | TP | TN | FP | FN | Aciertos |
| --- | ---: | ---: | ---: | ---: | ---: |
| Parser LL(1) | 40 | 20 | 0 | 0 | 60/60 |
| spaCy + criterio | 32 | 20 | 0 | 8 | 52/60 |
| NLTK + criterio | 20 | 20 | 0 | 20 | 40/60 |
| Gemini zero-shot | 39 | 14 | 6 | 1 | 53/60 |
| Gemini few-shot | 39 | 16 | 4 | 1 | 55/60 |

- **TP:** esperaba ACEPTADA y se obtuvo ACEPTADA.
- **TN:** esperaba RECHAZADA y se obtuvo RECHAZADA.
- **FP:** se acepto una oracion que la CFG marcaba como RECHAZADA.
- **FN:** se rechazo una oracion que la CFG marcaba como ACEPTADA.
- **Precision:** `TP / (TP + FP)`.
- **Recall:** `TP / (TP + FN)`.
- **Rechazo correcto:** `TN / (TN + FP)`.

Los errores de etiquetado POS se evaluan por separado con
`fase2/referencia_pos.csv` y `evaluar_pos.py`, incluyendo tokens sin etiqueta.
Esa referencia requiere validacion academica por el grupo.

**Limite de interpretacion:** las etiquetas esperadas se establecieron
respecto al subconjunto definido por **nuestra CFG**, no respecto al español
general. Por ello, el 100% del parser demuestra coincidencia con las 60
pruebas seleccionadas, **no una capacidad general para comprender español**.
Algunas oraciones correctas en español se rechazan por no pertenecer al
subconjunto. El corpus no es una muestra aleatoria del idioma.

## 8. Documentacion y evidencia adicional

- [`fase2/README_FASE2.md`](fase2/README_FASE2.md): metodologia y descripcion
  tecnica de los programas.
- [`fase2/DISENO_CORPUS.md`](fase2/DISENO_CORPUS.md): distribucion de los 60
  casos, criterios de seleccion y limitaciones.
- [`fase2/CRITERIOS_EVALUACION.md`](fase2/CRITERIOS_EVALUACION.md): reglas de
  equivalencia para spaCy y NLTK.
- [`fase2/README_GEMINI.md`](fase2/README_GEMINI.md): prompts, modelo, logs y
  ejecucion opcional de una API nueva.
- `fase2/logs/README.md` y `fase2/resultados/README.md`: descripcion de los
  archivos de evidencia y resultados.


