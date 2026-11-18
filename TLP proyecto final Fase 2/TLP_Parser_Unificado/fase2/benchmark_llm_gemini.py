"""Evalua el corpus con Gemini API en zero-shot y few-shot.

La vista previa no utiliza la API. La ejecucion real requiere --ejecutar.
Las respuestas originales se registran por solicitud y se pueden reanudar.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark_llm_openai import (
    EJEMPLOS_AJENOS, instrucciones, leer_corpus,
    sha,
)

ETIQUETAS = {'ACEPTADA', 'RECHAZADA'}
MODELO_PREDETERMINADO = 'gemini-3.5-flash-lite'


class DetalleCFG(BaseModel):
    oracion: str = Field(description='Oracion evaluada, exactamente como fue recibida')
    resultado: Literal['ACEPTADA', 'RECHAZADA']
    razon: str = Field(description='Motivo de no mas de 18 palabras segun la CFG')


class SalidaCFG(BaseModel):
    resultado: DetalleCFG


def instrucciones_gemini(modo):
    # La gramatica y los ejemplos se reutilizan sin modificar el parser.
    texto = instrucciones(modo)
    anterior = ('Responde exclusivamente un objeto JSON con: resultado (ACEPTADA o RECHAZADA)\n'
                'y justificacion (una frase breve explicando la regla decisiva).')
    nuevo = (
        'Devuelve SOLO un objeto JSON con esta estructura exacta: '
        '{"resultado":{"oracion":"texto original","resultado":"ACEPTADA o RECHAZADA",'
        '"razon":"explicacion breve"}}.\n'
        'Copia la oracion tal como fue recibida, incluyendo tildes y puntuacion.\n'
        'La razon debe tener como maximo 18 palabras y justificar la decision segun la CFG.'
    )
    if anterior not in texto:
        raise ValueError('No se encontro la instruccion de salida original.')
    texto = texto.replace(anterior, nuevo)
    if modo == 'few_shot':
        razones = (
            'Sujeto singular y verbo singular con vocabulario permitido.',
            'Sujeto plural y verbo plural con frase preposicional permitida.',
            'El articulo plural no concuerda con el sustantivo singular.',
            'El objeto directo no forma parte del predicado definido.',
        )
        for (oracion, etiqueta), razon in zip(EJEMPLOS_AJENOS, razones):
            anterior_ejemplo = json.dumps({'resultado': etiqueta}, ensure_ascii=False)
            nuevo_ejemplo = json.dumps({'resultado': {
                'oracion': oracion, 'resultado': etiqueta, 'razon': razon,
            }}, ensure_ascii=False)
            texto = texto.replace('Oracion: ' + oracion + '\n' + anterior_ejemplo,
                                  'Oracion: ' + oracion + '\n' + nuevo_ejemplo)
    return texto


def registrar_prompts_gemini():
    carpeta = BASE / 'prompts'
    carpeta.mkdir(parents=True, exist_ok=True)
    for modo in ('zero_shot', 'few_shot'):
        (carpeta / f'gemini_{modo}_instrucciones.txt').write_text(
            instrucciones_gemini(modo) + '\n', encoding='utf-8')
        (carpeta / f'gemini_{modo}_mensaje_plantilla.txt').write_text(
            'Oracion: {{ORACION}}\n', encoding='utf-8')
    return carpeta


def fecha_utc():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def guardar_json(ruta, datos):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def firma_configuracion(modelo, temperatura, max_salida):
    datos = {'modelo': modelo, 'temperatura': temperatura,
             'max_output_tokens': max_salida,
             'formato': SalidaCFG.model_json_schema()}
    return sha(json.dumps(datos, sort_keys=True).encode('utf-8'))


def respaldar_logs_anteriores(ruta_json, ruta_jsonl, modelo, corpus_hash,
                              prompt_hash, config_hash, modo):
    # Los ensayos anteriores se archivan en vez de mezclar prompts distintos.
    anteriores = []
    if ruta_json.exists():
        datos = json.loads(ruta_json.read_text(encoding='utf-8'))
        if not str(datos.get('herramienta', '')).startswith('Gemini API'):
            raise ValueError(f'{ruta_json} pertenece a otro proveedor.')
        m = datos.get('metadatos') or {}
        coincide = (m.get('modelo') == modelo and m.get('modo') == modo
                    and m.get('corpus_sha256') == corpus_hash
                    and m.get('configuracion_sha256') == config_hash)
        if not coincide:
            anteriores.append(ruta_json)
    if ruta_jsonl.exists():
        lineas = [x for x in ruta_jsonl.read_text(encoding='utf-8').splitlines() if x.strip()]
        if lineas:
            primero = json.loads(lineas[0])
            if primero.get('proveedor') != 'Gemini':
                raise ValueError(f'{ruta_jsonl} pertenece a otro proveedor.')
            coincide = (primero.get('modelo') == modelo
                        and primero.get('corpus_sha256') == corpus_hash
                        and primero.get('instrucciones_sha256') == prompt_hash
                        and primero.get('configuracion_sha256') == config_hash)
            if not coincide:
                anteriores.append(ruta_jsonl)
    if not anteriores:
        return
    carpeta = BASE / 'logs' / 'historico'
    carpeta.mkdir(parents=True, exist_ok=True)
    sello = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    for ruta in anteriores:
        destino = carpeta / f'{sello}_{ruta.name}'
        numero = 2
        while destino.exists():
            destino = carpeta / f'{sello}_{numero}_{ruta.name}'
            numero += 1
        ruta.rename(destino)
        print(f'Log anterior conservado: {destino}')


def leer_registros(ruta, modelo, corpus_hash, prompt_hash, config_hash):
    if not ruta.exists():
        return []
    registros = []
    for n, linea in enumerate(ruta.read_text(encoding='utf-8').splitlines(), 1):
        if not linea.strip():
            continue
        try:
            r = json.loads(linea)
        except json.JSONDecodeError as e:
            raise ValueError(f'Linea invalida {n} en {ruta}: {e}') from e
        valido = (r.get('proveedor') == 'Gemini' and r.get('modelo') == modelo
                  and r.get('corpus_sha256') == corpus_hash
                  and r.get('instrucciones_sha256') == prompt_hash
                  and r.get('configuracion_sha256') == config_hash)
        if not valido:
            raise ValueError(f'{ruta} corresponde a otro corpus, modelo o parametros. '
                             'Conservarlo y utilizar una copia de logs nueva.')
        registros.append(r)
    return registros


def verificar_salida(ruta, modelo, corpus_hash, modo, config_hash):
    if not ruta.exists():
        return
    datos = json.loads(ruta.read_text(encoding='utf-8'))
    metadatos = datos.get('metadatos') or {}
    if (not str(datos.get('herramienta', '')).startswith('Gemini API')
            or metadatos.get('modelo') != modelo
            or metadatos.get('modo') != modo
            or metadatos.get('corpus_sha256') != corpus_hash
            or metadatos.get('configuracion_sha256') != config_hash):
        raise ValueError(f'El archivo {ruta} ya existe y pertenece a otro experimento. '
                         'Guardarlo con otro nombre antes de continuar.')


def resumen(ruta, modo, modelo, corpus_hash, config_hash, registros, casos):
    ultimos = {}
    for registro in registros:
        clave = registro['id']
        if clave not in ultimos or registro.get('resultado_cfg') in ETIQUETAS:
            ultimos[clave] = registro
    filas = []
    for caso in casos:
        r = ultimos.get(caso['id'])
        if not r:
            continue
        filas.append({
            'id': caso['id'], 'oracion': caso['oracion'], 'nivel': int(caso['nivel']),
            'esperado_cfg': caso['esperado_cfg'], 'obtenido': r['resultado_cfg'],
            'justificacion': r.get('justificacion_generada'),
            'error': r.get('error_api'), 'timestamp_utc': r['timestamp_respuesta_utc'],
            'respuesta_bruta': r.get('respuesta_texto'),
        })
    completo = len(filas) == len(casos) and all(
        f['obtenido'] in ETIQUETAS for f in filas
    )
    datos = {
        'herramienta': f'Gemini API - {modelo} - {modo}',
        'tipo_resultado': 'clasificacion_cfg' if completo else 'respuestas_llm_incompletas',
        'metadatos': {
            'proveedor': 'Gemini', 'modelo': modelo, 'modo': modo,
            'corpus_sha256': corpus_hash, 'configuracion_sha256': config_hash,
            'registros_brutos_jsonl': f'gemini_{modo}.jsonl',
            'ejemplos_fuera_del_corpus': EJEMPLOS_AJENOS if modo == 'few_shot' else [],
            'estado': 'COMPLETO' if completo else 'INCOMPLETO',
        },
        'resultados': filas,
    }
    guardar_json(ruta, datos)
    # Archivo resumido para inspeccionar las respuestas sin abrir el log bruto.
    compactos = [
        {'resultado': {
            'oracion': f['oracion'], 'resultado': f['obtenido'],
            'razon': f['justificacion'] or ''
        }} for f in filas if f['obtenido'] in ETIQUETAS
    ]
    guardar_json(BASE / 'resultados' / f'gemini_{modo}_respuestas.json',
                 {'resultados': compactos})
    return len(filas), completo


def serializar_respuesta(respuesta):
    # Se conserva el objeto completo devuelto por el SDK.
    if hasattr(respuesta, 'model_dump'):
        return respuesta.model_dump(mode='json', exclude_none=True)
    if hasattr(respuesta, 'to_json_dict'):
        return respuesta.to_json_dict()
    return {'representacion': repr(respuesta)}


def parsear_respuesta(texto, oracion=None):
    try:
        objeto = json.loads(texto.strip())
        detalle = objeto.get('resultado') if isinstance(objeto, dict) else None
        if not isinstance(detalle, dict):
            return None, None
        etiqueta = detalle.get('resultado')
        razon = detalle.get('razon')
        repetida = detalle.get('oracion')
        if (etiqueta not in ETIQUETAS or not isinstance(razon, str)
                or not razon.strip() or not isinstance(repetida, str)
                or (oracion is not None and repetida != oracion)):
            return None, None
        return etiqueta, razon.strip()
    except (json.JSONDecodeError, AttributeError, TypeError):
        return None, None


def config_gemini(instruccion, temperatura, max_salida):
    from google.genai import types
    return types.GenerateContentConfig(
        system_instruction=instruccion,
        temperature=temperatura,
        max_output_tokens=max_salida,
        response_mime_type='application/json',
        response_schema=SalidaCFG,
    )


def guardar_registro(ruta, registro):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open('a', encoding='utf-8') as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + '\n')
        archivo.flush()


def limpiar_error(error, clave):
    texto = f'{type(error).__name__}: {error}'
    return texto.replace(clave, '[CLAVE_OCULTA]') if clave else texto


def ejecutar_modo(modo, modelo, casos, corpus_hash, limite, pausa, temperatura,
                 max_salida, cliente, clave):
    instruccion = instrucciones_gemini(modo)
    prompt_hash = sha(instruccion.encode('utf-8'))
    config_hash = firma_configuracion(modelo, temperatura, max_salida)
    ruta_json = BASE / 'logs' / f'llm_{modo}.json'
    ruta_jsonl = BASE / 'logs' / f'gemini_{modo}.jsonl'
    respaldar_logs_anteriores(ruta_json, ruta_jsonl, modelo, corpus_hash,
                              prompt_hash, config_hash, modo)
    verificar_salida(ruta_json, modelo, corpus_hash, modo, config_hash)
    registros = leer_registros(ruta_jsonl, modelo, corpus_hash, prompt_hash, config_hash)
    completados = {r['id'] for r in registros if r.get('resultado_cfg') in ETIQUETAS}
    pendientes = [c for c in casos if c['id'] not in completados]
    if limite is not None:
        pendientes = pendientes[:limite]
    print(f'{modo}: {len(completados)} anteriores, {len(pendientes)} solicitudes nuevas.')
    if not pendientes:
        n, completo = resumen(ruta_json, modo, modelo, corpus_hash, config_hash, registros, casos)
        print(f'Resumen: {n}/{len(casos)}. Completo: {completo}')
        return True

    config = config_gemini(instruccion, temperatura, max_salida)
    continuar = True
    for indice, caso in enumerate(pendientes, 1):
        if indice > 1 and pausa:
            time.sleep(pausa)
        entrada = 'Oracion: ' + caso['oracion']
        enviado = fecha_utc()
        texto = ''
        respuesta_completa = None
        error_api = None
        error_codigo = None
        try:
            respuesta = cliente.models.generate_content(
                model=modelo, contents=entrada, config=config,
            )
            respuesta_completa = serializar_respuesta(respuesta)
            texto = respuesta.text or ''
        except Exception as e:
            error_api = limpiar_error(e, clave)
            error_codigo = getattr(e, 'code', None) or getattr(e, 'status_code', None)
            # Se detiene una ejecucion con errores para no repetir llamadas inutiles.
            continuar = False
        etiqueta, justificacion = parsear_respuesta(texto, caso['oracion'])
        registro = {
            'proveedor': 'Gemini', 'id': caso['id'], 'nivel': int(caso['nivel']),
            'oracion': caso['oracion'], 'modelo': modelo, 'modo': modo,
            'corpus_sha256': corpus_hash, 'instrucciones_sha256': prompt_hash,
            'configuracion_sha256': config_hash,
            'timestamp_envio_utc': enviado, 'timestamp_respuesta_utc': fecha_utc(),
            'solicitud_exacta': {
                'model': modelo, 'contents': entrada,
                'config': {
                    'system_instruction': instruccion, 'temperature': temperatura,
                    'max_output_tokens': max_salida,
                    'response_mime_type': 'application/json',
                    'response_schema': SalidaCFG.model_json_schema(),
                },
            },
            'respuesta_texto': texto, 'respuesta_completa_api': respuesta_completa,
            'resultado_cfg': etiqueta, 'justificacion_generada': justificacion,
            'error_api': error_api, 'codigo_error': str(error_codigo) if error_codigo is not None else None,
        }
        guardar_registro(ruta_jsonl, registro)
        registros.append(registro)
        if etiqueta in ETIQUETAS:
            # La consola muestra solo la decision y su motivo.
            print(json.dumps({'resultado': {
                'oracion': caso['oracion'],
                'resultado': etiqueta,
                'razon': justificacion,
            }}, ensure_ascii=False, separators=(',', ':')))
        else:
            print(f'  {indice}/{len(pendientes)} - {caso["id"]}: SIN CLASIFICACION')
        if error_api:
            print(f'  Error API: {error_api}')
        if not continuar:
            break

    n, completo = resumen(ruta_json, modo, modelo, corpus_hash, config_hash, registros, casos)
    print(f'Log bruto: {ruta_jsonl.name} | Resumen: {ruta_json.name} ({n}/60, completo={completo})')
    return continuar


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--corpus', type=Path, default=BASE / 'corpus.csv')
    cli.add_argument('--modelo', default=MODELO_PREDETERMINADO)
    cli.add_argument('--modo', choices=('ambos', 'zero_shot', 'few_shot'), default='ambos')
    cli.add_argument('--limite', type=int, default=None,
                     help='Cantidad maxima de solicitudes nuevas POR MODO.')
    cli.add_argument('--pausa', type=float, default=8,
                     help='Segundos entre solicitudes del mismo modo.')
    cli.add_argument('--temperatura', type=float, default=0)
    cli.add_argument('--max-output-tokens', type=int, default=1024)
    cli.add_argument('--ejecutar', action='store_true',
                     help='Realizar solicitudes reales a Gemini API.')
    args = cli.parse_args()
    try:
        if args.limite is not None and args.limite < 1:
            raise ValueError('El limite debe ser positivo.')
        if args.pausa < 0 or not 0 <= args.temperatura <= 2 or args.max_output_tokens < 1:
            raise ValueError('Pausa, temperatura o tokens de salida invalidos.')
        casos = leer_corpus(args.corpus)
        corpus_hash = sha(args.corpus.read_bytes())
        modos = ('zero_shot', 'few_shot') if args.modo == 'ambos' else (args.modo,)
        registrar_prompts_gemini()
        corpus_textos = {c['oracion'].strip().casefold() for c in casos}
        if any(oracion.strip().casefold() in corpus_textos for oracion, _ in EJEMPLOS_AJENOS):
            raise ValueError('Un ejemplo few-shot se encuentra en el corpus de evaluacion.')
        if not args.ejecutar:
            print('VISTA PREVIA: sin llamadas API ni costos.')
            print(f'Modelo: {args.modelo} | Corpus: {len(casos)} | Modos: {", ".join(modos)}')
            print('Prompts: fase2/prompts/gemini_zero_shot_instrucciones.txt y gemini_few_shot_instrucciones.txt')
            print('Salida esperada: JSON con resultado: {oracion, resultado, razon}.')
            return
        try:
            from dotenv import load_dotenv
        except ImportError as e:
            raise RuntimeError('Falta python-dotenv; instalar en el entorno virtual.') from e
        load_dotenv(ROOT / '.env')
        clave = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not clave:
            raise ValueError('No se encontro GEMINI_API_KEY en .env ni en el entorno.')
        try:
            from google import genai
        except ImportError as e:
            raise RuntimeError('Falta google-genai; instalar en el entorno virtual.') from e
        cliente = genai.Client(api_key=clave)
        try:
            for modo in modos:
                if not ejecutar_modo(modo, args.modelo, casos, corpus_hash, args.limite,
                                     args.pausa, args.temperatura, args.max_output_tokens,
                                     cliente, clave):
                    print('Ejecucion detenida. Los datos registrados permiten reanudar.')
                    return
        finally:
            cliente.close()
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as e:
        cli.exit(2, f'ERROR: {e}\n')


if __name__ == '__main__':
    main()
