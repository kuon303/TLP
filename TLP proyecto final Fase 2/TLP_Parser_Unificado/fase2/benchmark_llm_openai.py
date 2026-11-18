"""Ejecuta experimentos zero-shot y few-shot con un LLM mediante API.

Por defecto no se realizan llamadas a la API. Las solicitudes reales
requieren --ejecutar, OPENAI_API_KEY y acceso al modelo seleccionado.
Las solicitudes pueden generar costos. La clave no se guarda en el repositorio.

Desde la raiz del proyecto:
  py -3.13 -m pip install --upgrade openai
  py -3.13 fase2/benchmark_llm_openai.py
  py -3.13 fase2/benchmark_llm_openai.py --ejecutar --limite 1
  py -3.13 fase2/benchmark_llm_openai.py --ejecutar

El modelo recibe la oracion, las producciones y el vocabulario, pero no la etiqueta esperada.
En few-shot tambien recibe ejemplos externos al corpus de 60 pruebas.
"""
import argparse
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gramatica_es_v3 import GRAMATICA_ES_V3
from vocabulario_es import VOCABULARIO
from corpus_util import leer_corpus as leer_corpus_validado

ETIQUETAS = {'ACEPTADA', 'RECHAZADA'}
EJEMPLOS_AJENOS = [
    ('La mujer camina.', 'ACEPTADA'),
    ('Los perros juegan en el parque.', 'ACEPTADA'),
    ('Los niño caminan.', 'RECHAZADA'),
    ('El profesor lee un libro.', 'RECHAZADA'),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fecha():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def reglas_explicitas():
    lineas = ['REGLAS DE PRODUCCION DE LA CFG:']
    for nt, alternativas in GRAMATICA_ES_V3.items():
        producciones = [' '.join(alt) if alt else 'ε' for alt in alternativas]
        lineas.append(f'{nt} → ' + ' | '.join(producciones))
    lineas += ['', 'VOCABULARIO LEXICO POR CATEGORIA (los terminos se ignoran por mayusculas/minusculas):']
    grupos = defaultdict(set)
    for palabra, etiquetas in VOCABULARIO.items():
        for etiqueta in etiquetas:
            grupos[etiqueta].add(palabra)
    for etiqueta in sorted(grupos):
        lineas.append(f'{etiqueta}: ' + ', '.join(sorted(grupos[etiqueta])))
    return '\n'.join(lineas)


def instrucciones(modo):
    if modo not in ('zero_shot', 'few_shot'):
        raise ValueError('Modo invalido.')
    lineas = [
        'Actua como reconocedor FORMAL de este subconjunto del español, NO como corrector general.',
        'Evalua si la oracion pertenece EXACTAMENTE al lenguaje de la CFG especificada abajo.',
        'No aceptes frases simplemente porque sean gramaticales en español.',
        'Los simbolos ART_, SUST_, VERBO_, ADJ_, ADV, PREP, QUE, PUNTO y EOF son tokens.',
        'La entrada contiene un solo enunciado; EOF marca su final. ε significa secuencia vacia.',
        'Las palabras fuera del vocabulario se consideran DESCONOCIDA y se rechazan.',
        'Si una palabra tiene varias categorias, el lexer elige la categoria de sustantivo',
        'compatible con el articulo inmediatamente anterior; tras un sustantivo prefiere un',
        'adjetivo compatible; si no aplica, prefiere VERBO_S o VERBO_P; si no, la primera clase.',
        'No introduzcas reglas nuevas y no agregues estructuras opcionales no escritas.',
        'Responde exclusivamente un objeto JSON con: resultado (ACEPTADA o RECHAZADA)',
        'y justificacion (una frase breve explicando la regla decisiva).',
        '', reglas_explicitas(),
    ]
    if modo == 'few_shot':
        lineas += ['', 'EJEMPLOS RESUELTOS EXTERNOS AL CORPUS DE EVALUACION:']
        for ejemplo, etiqueta in EJEMPLOS_AJENOS:
            lineas.append('Oracion: ' + ejemplo)
            lineas.append(json.dumps({'resultado': etiqueta}, ensure_ascii=False))
        lineas.append('Los ejemplos son externos al corpus y solo ilustran el formato de clasificacion.')
    return '\n'.join(lineas)


def registrar_plantillas():
    carpeta = BASE / 'prompts'
    carpeta.mkdir(parents=True, exist_ok=True)
    for modo in ('zero_shot', 'few_shot'):
        (carpeta / f'{modo}_instrucciones.txt').write_text(instrucciones(modo)+'\n',encoding='utf-8')
        (carpeta / f'{modo}_mensaje_plantilla.txt').write_text('Oracion: {{ORACION}}\n',encoding='utf-8')
    return carpeta


def leer_corpus(corpus):
    return leer_corpus_validado(corpus)


def respuesta_binaria(texto):
    try:
        objeto = json.loads(texto.strip())
    except (json.JSONDecodeError, AttributeError):
        return None
    etiqueta = objeto.get('resultado') if isinstance(objeto, dict) else None
    return etiqueta if etiqueta in ETIQUETAS else None


def leer_previos(ruta, modelo, corpus_sha, prompt_sha):
    if not ruta.exists():
        return []
    previos = [json.loads(x) for x in ruta.read_text(encoding='utf-8').splitlines() if x.strip()]
    for registro in previos:
        if (registro.get('modelo') != modelo or registro.get('corpus_sha256') != corpus_sha
                or registro.get('instrucciones_sha256') != prompt_sha):
            raise ValueError(f'{ruta}: pertenece a otro modelo, corpus o prompt. Renombra los logs anteriores antes de continuar.')
    return previos


def volcar_resumen(ruta_json, modo, modelo, corpus_sha, previos, corpus):
    # Los registros individuales se conservan incluso si la ejecucion se interrumpe.
    # El resumen usa la ultima respuesta del ID sin alterar los registros brutos.
    ultimo = {}
    for r in previos:
        ultimo[r['id']] = r
    resultados = []
    for c in corpus:
        if c['id'] not in ultimo:
            continue
        r = ultimo[c['id']]
        resultados.append({
            'id': c['id'], 'oracion': c['oracion'], 'nivel': int(c['nivel']),
            'esperado_cfg': c['esperado_cfg'], 'obtenido': r['resultado_cfg'],
            'justificacion': r.get('justificacion_generada'),
            'error': r.get('error_api'),
            'timestamp_utc': r['timestamp_respuesta_utc'],
            'respuesta_bruta': r.get('respuesta_texto'),
        })
    completo = (len(resultados) == len(corpus) and
                all(r['obtenido'] in ETIQUETAS for r in resultados))
    datos = {
        'herramienta': f'OpenAI API — {modelo} — {modo}',
        'tipo_resultado': 'clasificacion_cfg' if completo else 'respuestas_llm_incompletas',
        'metadatos': {
            'modelo': modelo, 'modo': modo, 'corpus_sha256': corpus_sha,
            'ejemplos_fuera_del_corpus': EJEMPLOS_AJENOS if modo == 'few_shot' else [],
            'registros_brutos_jsonl': ruta_json.with_suffix('.jsonl').name,
            'estado': 'COMPLETO' if completo else 'INCOMPLETO: revisar errores antes de evaluar',
        },
        'resultados': resultados,
    }
    ruta_json.write_text(json.dumps(datos,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return len(resultados), completo


def ejecutar_modo(modo, modelo, corpus, corpus_sha, limite, cliente, max_output_tokens):
    instruccion = instrucciones(modo)
    hash_prompt = sha(instruccion.encode('utf-8'))
    path_json = BASE/'logs'/f'llm_{modo}.json'
    path_jsonl = path_json.with_suffix('.jsonl')
    path_json.parent.mkdir(parents=True, exist_ok=True)
    previos = leer_previos(path_jsonl, modelo, corpus_sha, hash_prompt)
    # Los reintentos conservan tambien las respuestas anteriores en el log bruto.
    completados = {r['id'] for r in previos if r.get('resultado_cfg') in ETIQUETAS}
    pendientes = [c for c in corpus if c['id'] not in completados]
    if limite:
        pendientes = pendientes[:limite]
    print(f'{modo}: {len(completados)} respuestas validas anteriores; {len(pendientes)} solicitudes nuevas.')
    for i, c in enumerate(pendientes, 1):
        entrada = 'Oracion: ' + c['oracion']
        enviado = fecha()
        error_api = None
        respuesta = None
        respuesta_texto = ''
        codigo_api = None
        dump_respuesta = None
        try:
            respuesta = cliente.responses.create(
                model=modelo,
                instructions=instruccion,
                input=entrada,
                max_output_tokens=max_output_tokens,
            )
            codigo_api = respuesta.id
            respuesta_texto = respuesta.output_text or ''
            dump_respuesta = respuesta.model_dump(mode='json', exclude_none=True)
        except Exception as exc:
            # Los errores y sus fechas se registran como evidencia de ejecucion.
            error_api = f'{type(exc).__name__}: {exc}'
        try:
            justificacion = json.loads(respuesta_texto.strip()).get('justificacion')
        except (json.JSONDecodeError, AttributeError, TypeError):
            justificacion = None
        registro = {
            'id': c['id'], 'nivel': int(c['nivel']), 'oracion': c['oracion'],
            'modelo': modelo, 'modo': modo, 'corpus_sha256': corpus_sha,
            'instrucciones_sha256': hash_prompt,
            'timestamp_envio_utc': enviado, 'timestamp_respuesta_utc': fecha(),
            'solicitud_exacta': {
                'model': modelo, 'instructions': instruccion, 'input': entrada,
                'max_output_tokens': max_output_tokens,
            },
            'respuesta_texto': respuesta_texto,
            'respuesta_completa_api': dump_respuesta,
            'response_id': codigo_api,
            'resultado_cfg': respuesta_binaria(respuesta_texto),
            'justificacion_generada': justificacion,
            'error_api': error_api,
        }
        with path_jsonl.open('a', encoding='utf-8') as f:
            f.write(json.dumps(registro,ensure_ascii=False)+'\n')
            f.flush()
        previos.append(registro)
        estado = registro['resultado_cfg'] or 'SIN CLASIFICACION VALIDA'
        print(f'  {i}/{len(pendientes)} · {c["id"]}: {estado}')
    total, completo = volcar_resumen(path_json,modo,modelo,corpus_sha,previos,corpus)
    print(f'Guardado: {path_jsonl} (salida original de cada llamada)')
    print(f'Guardado: {path_json} (resumen {total}/{len(corpus)}, completo={completo})')


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--corpus',type=Path,default=BASE/'corpus.csv')
    cli.add_argument('--modelo',default='gpt-4.1-mini',help='Identificador del modelo disponible en la cuenta API.')
    cli.add_argument('--modo',choices=('ambos','zero_shot','few_shot'),default='ambos')
    cli.add_argument('--limite',type=int,default=None,help='Numero maximo de llamadas NUEVAS por modo.')
    cli.add_argument('--max-output-tokens',type=int,default=700)
    cli.add_argument('--ejecutar',action='store_true',help='Autorizar las llamadas REALES que pueden tener costo.')
    a=cli.parse_args()
    try:
        if a.limite is not None and a.limite <= 0:
            raise ValueError('El limite debe ser positivo.')
        registrar_plantillas()
        casos=leer_corpus(a.corpus)
        corpus_sha=sha(a.corpus.read_bytes())
        modos=('zero_shot','few_shot') if a.modo=='ambos' else (a.modo,)
        if not a.ejecutar:
            print('VISTA PREVIA: NO se hicieron solicitudes API ni se generaron respuestas.')
            print('Modelos de prompts exactos guardados en:',BASE/'prompts')
            print(f'Corpus: {len(casos)} oraciones. Modos: {", ".join(modos)}.')
            print('Las llamadas reales requieren --ejecutar y pueden generar costos.')
            return
        if not os.environ.get('OPENAI_API_KEY'):
            raise ValueError('Falta OPENAI_API_KEY en el entorno local. La clave no debe incluirse en el repositorio.')
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError('Falta paquete openai: py -3.13 -m pip install --upgrade openai') from e
        cliente=OpenAI()
        for modo in modos:
            ejecutar_modo(modo,a.modelo,casos,corpus_sha,a.limite,cliente,a.max_output_tokens)
    except (ValueError,RuntimeError,OSError,json.JSONDecodeError) as exc:
        cli.exit(2,f'ERROR: {exc}\n')


if __name__=='__main__':
    main()
