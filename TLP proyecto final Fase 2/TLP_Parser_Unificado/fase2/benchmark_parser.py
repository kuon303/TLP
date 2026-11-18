"""Procesa el corpus con el parser de español y registra cada resultado.

Ejecutar desde la carpeta del proyecto:
    py -3.13 fase2/benchmark_parser.py

Sin bibliotecas externas. No modifica gramatica, vocabulario, lexer ni parser.
"""
import argparse
import csv
import hashlib
import json
import platform
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

FASE2 = Path(__file__).resolve().parent
PROYECTO = FASE2.parent
if str(PROYECTO) not in sys.path:
    sys.path.insert(0, str(PROYECTO))

from gramatica_es_v3 import GRAMATICA_ES_V3
from parser_ll1 import ParserLL1
PARSER_ES = ParserLL1(GRAMATICA_ES_V3, 'Oracion')
from lexer_es_v3 import obtener_tokens_es_v3, ErrorLexicoEspanol
from parser_ll1 import ErrorSintactico, mostrar_arbol

CAMPOS = {'id', 'nivel', 'oracion', 'esperado_cfg', 'correcta_espanol', 'fenomeno'}
ETIQUETAS = {'ACEPTADA', 'RECHAZADA'}


def ahora_utc():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def huella(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def leer_corpus(ruta):
    with ruta.open('r', encoding='utf-8-sig', newline='') as archivo:
        lector = csv.DictReader(archivo)
        faltan = CAMPOS - set(lector.fieldnames or [])
        if faltan:
            raise ValueError(f'Faltan columnas en el CSV: {sorted(faltan)}')
        casos = list(lector)

    if len(casos) != 60:
        raise ValueError(f'El corpus debe tener 60 oraciones; hay {len(casos)}.')
    identificadores = set()
    for numero, caso in enumerate(casos, 2):
        identificador = (caso['id'] or '').strip()
        etiqueta = (caso['esperado_cfg'] or '').strip().upper()
        nivel = (caso['nivel'] or '').strip()
        if not identificador or identificador in identificadores:
            raise ValueError(f'ID vacio o duplicado en linea {numero}: {identificador!r}')
        if not (caso['oracion'] or '').strip():
            raise ValueError(f'Oracion vacia en linea {numero}')
        if etiqueta not in ETIQUETAS:
            raise ValueError(f'Etiqueta invalida en linea {numero}: {etiqueta!r}')
        if nivel not in {'1', '2', '3'}:
            raise ValueError(f'Nivel invalido en linea {numero}: {nivel!r}')
        identificadores.add(identificador)
        caso['id'] = identificador
        caso['esperado_cfg'] = etiqueta
        caso['oracion'] = caso['oracion'].strip()
    from collections import Counter
    if Counter(c['nivel'] for c in casos) != {'1': 20, '2': 20, '3': 20}:
        raise ValueError('Debe haber 20 oraciones por nivel.')
    if Counter(c['esperado_cfg'] for c in casos) != {'ACEPTADA': 40, 'RECHAZADA': 20}:
        raise ValueError('Debe haber 40 esperadas ACEPTADA y 20 RECHAZADA.')
    return casos


def procesar_caso(caso, incluir_arbol=True):
    oracion = caso['oracion']
    instante = ahora_utc()
    try:
        tokens = obtener_tokens_es_v3(oracion)
        arbol = PARSER_ES.analizar(tokens)
        obtenido = 'ACEPTADA'
        error = None
        arbol_texto = mostrar_arbol(arbol) if incluir_arbol else None
        tokens_registro = [
            {'tipo': tok.tipo, 'texto': tok.texto, 'linea': tok.linea, 'columna': tok.columna}
            for tok in tokens
        ]
    except (ErrorLexicoEspanol, ErrorSintactico) as exc:
        obtenido = 'RECHAZADA'
        error = f'{type(exc).__name__}: {exc}'
        arbol_texto = None
        # Los tokens se conservan si el lexer completo su analisis.
        tokens_registro = [
            {'tipo': tok.tipo, 'texto': tok.texto, 'linea': tok.linea, 'columna': tok.columna}
            for tok in tokens
        ] if 'tokens' in locals() else None

    return {
        'id': caso['id'],
        'nivel': int(caso['nivel']),
        'oracion': oracion,
        'esperado_cfg': caso['esperado_cfg'],
        'correcta_espanol': caso.get('correcta_espanol'),
        'fenomeno': caso.get('fenomeno'),
        'estructura_esperada': caso.get('estructura_esperada'),
        'obtenido': obtenido,
        'coincide_con_esperado': obtenido == caso['esperado_cfg'],
        'tokens': tokens_registro,
        'arbol': arbol_texto,
        'error': error,
        'timestamp_utc': instante,
    }


def ejecutar(corpus, destino, sin_arbol, crear_reporte=True, ruta_reporte=None):
    casos = leer_corpus(corpus)
    resultados = [procesar_caso(caso, incluir_arbol=True) for caso in casos]
    resultados_log = ([{**r, 'arbol': None} for r in resultados]
                      if sin_arbol else resultados)
    archivos = ['parser_ll1.py', 'lexer_es_v3.py', 'gramatica_es_v3.py', 'vocabulario_es.py']
    documento = {
        'herramienta': 'Parser LL(1) propio (español V3)',
        'tipo_resultado': 'clasificacion_cfg',
        'metadatos': {
            'fecha_ejecucion_utc': ahora_utc(),
            'python': platform.python_version(),
            'corpus': corpus.name,
            'corpus_sha256': huella(corpus),
            'archivos_fuente_sha256': {nombre: huella(PROYECTO / nombre) for nombre in archivos},
            'total_oraciones': len(casos),
            'nota': 'Resultados reales del parser V3; no se ajustan usando el esperado.',
        },
        'resultados': resultados_log,
    }
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(documento, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    contados = Counter(x['obtenido'] for x in resultados)
    iguales = sum(x['coincide_con_esperado'] for x in resultados)
    if crear_reporte:
        from reporte_corpus import generar_reporte, mostrar_resumen
        ruta_html = ruta_reporte or FASE2 / 'resultados' / 'analisis_corpus.html'
        # El informe usa estos resultados y los logs ya guardados.
        informe = generar_reporte(casos, resultados, FASE2 / 'logs', ruta_html,
                                  ruta_corpus=corpus)
        mostrar_resumen(informe)
    else:
        print(f'Procesadas: {len(resultados)} | Aceptadas: {contados["ACEPTADA"]} '
              f'| Rechazadas: {contados["RECHAZADA"]} | Coinciden: {iguales}/{len(resultados)}')
    print('Log del parser:', destino)
    if iguales < len(resultados):
        print('ADVERTENCIA: hay diferencias con las etiquetas esperadas. Revisar el log.')


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--corpus', type=Path, default=FASE2 / 'corpus.csv')
    cli.add_argument('--salida', type=Path, default=FASE2 / 'logs' / 'parser.json')
    cli.add_argument('--sin-arbol', action='store_true', help='No guardar arboles en el JSON.')
    cli.add_argument('--sin-reporte', action='store_true', help='Omite el informe HTML/TXT.')
    cli.add_argument('--reporte', type=Path, default=None,
                     help='Ruta del HTML; por defecto fase2/resultados/analisis_corpus.html.')
    args = cli.parse_args()
    try:
        ejecutar(args.corpus, args.salida, args.sin_arbol,
                 crear_reporte=not args.sin_reporte, ruta_reporte=args.reporte)
    except (OSError, ValueError) as exc:
        cli.exit(2, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
