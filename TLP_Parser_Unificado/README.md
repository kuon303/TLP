# Parser LL(1) — Fase 1

Requiere **Python 3.13**. El parser funciona sin instalar librerias externas.

## Ejecutar

Abrir esta carpeta en VS Code y escribir en la terminal:

```powershell
py -3.13 main.py
```

En el menu elegir **1. C++** o **2. Español** y despues:

- **Escribir entrada:** en C++ el codigo termina con `FIN`; en español presionando Enter despues de cada oracion. `SALIR` regresa al menu.
- **Leer archivo:** seleccionar un `.cpp` o un `.txt` (una oracion por linea), por ejemplo `ejemplos/valido.cpp` o `ejemplos/casos_fallas_es.txt`.

El programa muestra si acepta o rechaza la entrada, el error si corresponde y el arbol sintactico de las entradas aceptadas.

## Comparacion con spaCy (opcional)

Para ejecutar las 33 oraciones de comparacion, instalar spaCy y su modelo español:

```powershell
py -3.13 -m pip install spacy
py -3.13 -m spacy download es_core_news_sm
py -3.13 comparar_spacy.py --arboles
```

Los resultados se guardan en `resultados_comparacion/`. Sin spaCy se puede ejecutar `py -3.13 comparar_spacy.py --solo-parser`.

## Ejecutar las pruebas

```powershell
py -3.13 -m unittest discover -s pruebas -p "pruebas_*.py" -v
```
