# Auditoría adversarial del parser unificado: Fase 1 TLP

**Código de referencia:** `TLP_Parser_Unificado.zip`. La auditoría se verificó de nuevo tras ampliar el vocabulario, sin alterar las reglas gramaticales.  
**Método:** ejecutar el motor `ParserLL1` con los lexers y gramáticas originales.  
**Cantidad:** 36 pruebas de español y 13 de C++ (9 iniciales + 4 adicionales).  
**Resultados:** español 8 aceptadas y 28 rechazadas; C++ 7 aceptadas y 6 rechazadas. Son resultados de reconocimiento, **NO medidas de precisión**.

## Hallazgos prioritarios

| ID | Entrada | Resultado real | Regla/punto preciso | Interpretación |
|---|---|---|---|---|
| S02 | El niño que juega con la niña que canta corre. | Rechaza | `PredicadoS` esperaba `VERBO_S` y apareció `QUE` | La relativa anidada no puede aparecer dentro de `SintagmaNominal` de la preposición. **Límite de nuestra gramática**; las CFG permiten recursividad. |
| S10 | La niña pequeña tranquila canta. | Rechaza | `RelativaSOpc` ante `ADJ_FS` | `AdjetivoFSOpc` permite un solo adjetivo. **Límite de implementación**. |
| S12 | El niño corre en el parque con la niña. | Rechaza | `AdjetivoMSOpc` ante `PREP` | `FrasePrepOpc` solo admite un complemento preposicional. **Límite de implementación**. |
| S08 | Corre el niño. | Rechaza | `Oracion` ante `VERBO_S` | Se implementó solamente orden sujeto-verbo. **Límite de gramática**. |
| S14 | La niña corre y canta. | Rechaza | `AdverbioOpc` ante `DESCONOCIDA ('y')` | No se implementó coordinación. **Límite de gramática y vocabulario**. |
| S34 | El niño que la niña conoce corre. | Rechaza | `RelativaSOpc` esperaba `VERBO_S`, llegó `ART_FS` | Solo se incluyen relativas de sujeto (`que` + verbo). Relativas de objeto quedan fuera, aunque `conoce` ya se reconoce como verbo. **Límite de gramática**. |
| S03 | Los niños que juegan con la niña corren. | **Acepta** | `SujetoMP` → `RelativaPOpc` → `PredicadoP` | **Contraejemplo** a la afirmación de que toda concordancia a distancia es imposible para una CFG. |
| S04 | Los niños que juegan con la niña corre. | Rechaza | `PredicadoP` ante `VERBO_S`, esperaba `VERBO_P` | Concordancia de sujeto plural con verbo principal. Regla sí la verifica. |
| S24 | El telescopio duerme. | **Acepta** | Gramática satisfecha | Sintaxis válida en el subconjunto; semántica literal extraña. El parser **no verifica significados**. |
| S23 | El niño vio a la niña con el telescopio. | Rechaza | `AdjetivoMSOpc` ante `DESCONOCIDA ('vio')` | **No demuestra resolución fallida de ambigüedad**: el rechazo ocurre antes, por vocabulario/estructura. |
| C02 | int main() { return 0; } | Rechaza | `Inicializacion` ante `LPAREN` | Código C++ válido fuera del subconjunto seleccionado (no funciones). No es defecto del parser. |
| C04 | int x = ; | Rechaza | `Expresion` ante `SEMI` | Error sintáctico correctamente detectado. |
| C10–C12 | `int while = 5;`, `int class = 2;`, `int return = 1;` | **Acepta** | `PALABRAS_RESERVADAS` del lexer solo contiene `int`, `float`, `if`, `else` | **Defecto real**: acepta como identificadores palabras reservadas del C++ estándar. |
| C06 | int x = y; | **Acepta** | Ninguna regla falló | `y` puede estar no declarada; comprobar declaraciones requiere análisis semántico, no sintáctico. |

## Conflicto LL(1) comprobado

Intento mínimo de añadir dos alternativas con igual comienzo:

```text
Oracion → ART_FS SUST_FS VERBO_S EOF
Oracion → ART_FS SUST_FS ADJ_FS VERBO_S EOF
```

El motor lanzó realmente:

```text
ValueError: La gramática NO es LL(1): conflicto en ('Oracion', 'ART_FS')
```

**Interpretación correcta:** esa **formulación** de la gramática no es LL(1); factorizar el prefijo común (y un adjetivo opcional) resuelve este caso. No prueba que el lenguaje analizado sea no libre de contexto.

## Contraste con los requisitos escritos del profesor (Fase 1)

1. **Parser C++ con árbol y errores básicos:** cubierto. El código demuestra aceptación/rechazo; recomendable corregir las palabras reservadas para que el lexer no acepte código C++ inválido.
2. **Concordancia género/número:** demostrado positivamente y negativamente (S03/S04/S05/S06/S07). No hay que presentar la concordancia básica como fuera del poder de las CFG: con un conjunto finito de características se representa mediante reglas duplicadas.
3. **Subordinadas:** hay una relativa simple que funciona (S01), pero una relativa anidada o de objeto falla (S02/S34). Se conocen el punto exacto y la causa en la implementación; **la recursión puede expresarse en CFG**.
4. **Modificadores:** se admite un adjetivo/adverbio/frase preposicional en determinadas posiciones; combinaciones de más de uno y otro orden fracasan (S10/S11/S12/S32).
5. **Análisis de ambigüedad y límites formales:** **aún necesita explicación teórica separada**. El caso del telescopio (S23) no constituye una prueba de incapacidad de CFG o LL(1) para representar ambigüedad porque el parser primero rechaza `vio` como palabra desconocida. Las CFG pueden ser ambiguas; un parser LL(1) determinista produce una sola derivación y no puede usar directamente una tabla con conflictos. No generalizar sobre todo el español a partir de esta muestra.
6. **Jerarquía de Chomsky:** conectar reglas sin contexto con Tipo 2 (CFG), y explicar que lenguajes abstractos como `{a^n b^n c^n | n≥1}` no son libres de contexto y sí requieren un mecanismo más potente. Este ejemplo abstracto **no es un experimento ejecutado con nuestro español**. También explicar distinción entre CFG, parser LL(1), léxico y análisis semántico.
7. **Comparación con spaCy:** ya existe el CSV/JSON de 33 casos anteriores; esas mismas entradas cumplen la exigencia de comparar salidas. **Estos 36 nuevos casos no fueron ejecutados con spaCy**; si se quieren usar en la sección comparativa, primero ejecutarlos con el mismo modelo y guardar sus salidas.
8. **Informe 5–7 páginas, código documentado, README y exposición de 15–20 minutos:** son entregables de presentación/documentación, no defectos de gramática; pendientes si aún no se han preparado.

## Recomendación de demostración (sin confundir conceptos)

Mostrar consecutivamente:
1. `El niño que juega corre.` (acepta: relativa básica).
2. `El niño que juega con la niña que canta corre.` (rechaza: anidación no implementada).
3. `Los niños que juegan con la niña corren.` (acepta: concordancia a distancia finita).
4. `Los niños que juegan con la niña corre.` (rechaza: discordancia sujeto-verbo).
5. `Corre el niño.` (rechaza una oración válida por orden no incluido).
6. `int while = 5;` (acepta por **error léxico real**: corregir antes de presentar o incluir como limitación honesta).

## Conclusión académica

El proyecto demuestra muy bien la **frontera entre una gramática LL(1) controlada y el español real**. Por sí solo no demuestra que la **clase completa de lenguajes libres de contexto** sea insuficiente para todos esos fenómenos. Para satisfacer con rigor la parte de teoría, explicar qué es límite **del subconjunto**, qué es límite **del método LL(1)**, qué sería límite **formal de CFG**, y qué corresponde a **semántica**.

**Archivos adjuntos**: `Resultados_pruebas_limites_TLP.csv` (todas las ejecuciones), `pruebas/pruebas_limites_tlp.py` (reproducir desde la carpeta raíz del proyecto). El código entregado originalmente no se modificó.
