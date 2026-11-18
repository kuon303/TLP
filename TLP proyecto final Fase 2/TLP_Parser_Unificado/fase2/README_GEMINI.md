# Benchmark Gemini API

El experimento usa `benchmark_llm_gemini.py`, el corpus de 60 oraciones y
la CFG V3 del parser original. La corrida final se realizo con el modelo
`gemini-3.5-flash-lite` en los modos `zero_shot` y `few_shot`.

## Prompts y formato

El script genera instrucciones desde las producciones y el vocabulario del
proyecto. Los prompts exactos usados en el experimento estan guardados en:

- `prompts/gemini_zero_shot_instrucciones.txt`
- `prompts/gemini_few_shot_instrucciones.txt`
- `prompts/gemini_zero_shot_mensaje_plantilla.txt`
- `prompts/gemini_few_shot_mensaje_plantilla.txt`

El zero-shot no incluye ejemplos. El few-shot agrega cuatro ejemplos resueltos
que no pertenecen a las 60 oraciones evaluadas. Las etiquetas esperadas del
corpus no se envian al modelo para las oraciones de evaluacion.

Se pide una respuesta JSON minima con esta estructura:

```json
{
  "resultado": {
    "oracion": "El niño corre.",
    "resultado": "ACEPTADA",
    "razon": "Cumple la estructura de la CFG."
  }
}
```

Los logs originales guardan tambien los metadatos de cada solicitud. La salida
compacta se consulta en `resultados/gemini_*_respuestas.json`.

## Registros que ya estan incluidos

- `logs/gemini_zero_shot.jsonl`: 68 registros (60 respuestas validas y 8
  intentos sin clasificacion valida).
- `logs/gemini_few_shot.jsonl`: 64 registros (60 respuestas validas y 4
  intentos sin clasificacion valida).
- `logs/llm_zero_shot.json`, `logs/llm_few_shot.json`: los 60 resultados
  validos de cada modalidad para calcular las metricas.

La evidencia incluye las instrucciones exactas, modelo, parametros, marcas
UTC y respuestas completas disponibles del SDK. Los intentos fallidos no se
puntuan como respuestas correctas o incorrectas del modelo.

**No se necesita una API key para consultar estos registros ni para ejecutar
`evaluar.py`.**

## Configuracion para una corrida nueva

Python 3.13 y las dependencias de `requirements.txt` son suficientes para la
integracion. La clave se introduce mediante una variable de entorno o un
archivo `.env` privado, que no debe formar parte del repositorio. La
plantilla `.env.example` muestra el nombre de la variable.

En PowerShell, desde la raiz:

```powershell
python -m pip install -r requirements.txt
python fase2/benchmark_llm_gemini.py
```

La vista previa no hace llamadas. Para ejecutar una prueba limitada, en una
copia del proyecto con logs separados:

```powershell
python fase2/benchmark_llm_gemini.py --ejecutar --limite 1
```

Para procesar los 60 casos por modalidad:

```powershell
python fase2/benchmark_llm_gemini.py --ejecutar --pausa 30
```

Las solicitudes pueden consumir cuota o generar costos segun la configuracion
del proyecto de Google. Si la API falla, el script conserva el registro y
puede reanudar usando el mismo corpus, modelo, prompt y configuracion. Una
corrida nueva puede producir resultados distintos a los guardados. No se deben
mezclar logs de experimentos diferentes.

`benchmark_llm_openai.py` se conserva como modulo auxiliar de generacion de
prompts. El experimento final de este repositorio se realizo con Gemini.
