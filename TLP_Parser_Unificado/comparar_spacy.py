
import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from main import PARSER_ES
from lexer_es_v3 import obtener_tokens_es_v3, ErrorLexicoEspanol
from parser_ll1 import ErrorSintactico, mostrar_arbol

BASE = Path(__file__).resolve().parent
COLUMNAS = [
    'id', 'fenomeno', 'oracion', 'gramaticalmente_correcta',
    'dentro_del_subconjunto', 'esperado_parser', 'parser_acepta',
    'parser_coincide_con_esperado', 'error_parser', 'spacy_estado',
    'spacy_etiquetas', 'spacy_dependencias',
]


def analizar_con_nuestro_parser(oracion):
    try:
        arbol = PARSER_ES.analizar(obtener_tokens_es_v3(oracion))
        return {'acepta': True, 'error': '', 'arbol': mostrar_arbol(arbol)}
    except (ErrorLexicoEspanol, ErrorSintactico) as exc:
        return {'acepta': False, 'error': str(exc), 'arbol': ''}


def cargar_modelo(nombre):
    try:
        import spacy
    except ImportError as exc:
        raise RuntimeError(
            'spaCy no está instalado. Ejecutá: py -3.13 -m pip install spacy'
        ) from exc
    try:
        nlp = spacy.load(nombre)
    except OSError as exc:
        raise RuntimeError(
            f'No está instalado el modelo {nombre!r}. Ejecutá: '
            f'py -3.13 -m spacy download {nombre}'
        ) from exc
    return spacy, nlp


def analizar_con_spacy(nlp, texto):
    doc = nlp(texto)
    anotaciones = []
    for tok in doc:
        anotaciones.append({
            'palabra': tok.text,
            'lema': tok.lemma_,
            'categoria': tok.pos_,
            'morfologia': str(tok.morph),
            'dependencia': tok.dep_,
            'depende_de': tok.head.text,
            'indice_cabeza': tok.head.i,
        })
    return anotaciones


def crear_resultados(casos, nlp=None):
    resultados = []
    for caso in casos:
        analisis = analizar_con_nuestro_parser(caso['oracion'])
        anotaciones = analizar_con_spacy(nlp, caso['oracion']) if nlp is not None else None
        resultados.append({
            **caso,
            'parser': analisis,
            'spacy': {
                'estado': 'ANALIZADO',
                'tokens': anotaciones,
                'nota': 'Anotaciones predichas; revisión lingüística manual pendiente.',
            } if anotaciones is not None else {
                'estado': 'NO_EJECUTADO',
                'tokens': [],
                'nota': 'No se ejecutó spaCy; no hay comparación NLP todavía.',
            }
        })
    return resultados


def escribir_csv(destino, resultados):
    with destino.open('w', encoding='utf-8-sig', newline='') as salida:
        writer = csv.DictWriter(salida, fieldnames=COLUMNAS)
        writer.writeheader()
        for caso in resultados:
            tokens = caso['spacy']['tokens']
            writer.writerow({
                'id': caso['id'],
                'fenomeno': caso['fenomeno'],
                'oracion': caso['oracion'],
                'gramaticalmente_correcta': 'SI' if caso['gramaticalmente_correcta'] else 'NO',
                'dentro_del_subconjunto': 'SI' if caso['dentro_del_subconjunto'] else 'NO',
                'esperado_parser': 'ACEPTA' if caso['esperado_parser'] else 'RECHAZA',
                'parser_acepta': 'ACEPTA' if caso['parser']['acepta'] else 'RECHAZA',
                'parser_coincide_con_esperado': 'SI' if caso['parser']['acepta'] == caso['esperado_parser'] else 'NO',
                'error_parser': caso['parser']['error'],
                'spacy_estado': caso['spacy']['estado'],
                'spacy_etiquetas': ' | '.join(f"{t['palabra']}:{t['categoria']}[{t['morfologia']}]" for t in tokens),
                'spacy_dependencias': ' | '.join(f"{t['palabra']}:{t['dependencia']}->{t['depende_de']}" for t in tokens),
            })


def resumen_md(resultados, modelo, version_spacy):
    cuenta = Counter('Dentro del subconjunto' if x['dentro_del_subconjunto'] else
                    'Error gramatical' if not x['gramaticalmente_correcta'] else
                    'Español correcto fuera del subconjunto' for x in resultados)
    aciertos = sum(x['parser']['acepta'] == x['esperado_parser'] for x in resultados)
    con_spacy = bool(resultados) and resultados[0]['spacy']['estado'] == 'ANALIZADO'
    lineas = [
        '# Comparación de nuestro parser LL(1) y spaCy', '',
        f'- Casos de prueba: **{len(resultados)}**',
        f'- Dentro del subconjunto: **{cuenta["Dentro del subconjunto"]}**',
        f'- Español incorrecto (concordancia): **{cuenta["Error gramatical"]}**',
        f'- Español correcto fuera del subconjunto: **{cuenta["Español correcto fuera del subconjunto"]}**',
        f'- Nuestro parser coincide con el resultado esperado según su alcance: **{aciertos}/{len(resultados)}**',
        f'- spaCy: **{modelo} ({version_spacy})**' if con_spacy else '- spaCy: **NO EJECUTADO** (falta instalar/ejecutar el modelo)',
        '',
        '> IMPORTANTE: el resultado esperado corresponde al alcance declarado de nuestra gramática, ',
        '> NO mide la calidad general del español ni es una medición de precisión de spaCy. ',
        '> spaCy produce anotaciones, no una decisión equivalente de aceptación/rechazo.', '',
        '| ID | Fenómeno | Oración | Español correcto | Parser | Esperado | spaCy |',
        '|---|---|---|:---:|:---:|:---:|---|',
    ]
    for x in resultados:
        forma = x['oracion'].replace('|','\\|')
        lineas.append(f"| {x['id']} | {x['fenomeno']} | {forma} | "
                      f"{'Sí' if x['gramaticalmente_correcta'] else 'No'} | "
                      f"{'Acepta' if x['parser']['acepta'] else 'Rechaza'} | "
                      f"{'Acepta' if x['esperado_parser'] else 'Rechaza'} | "
                      f"{x['spacy']['estado']} |")
    lineas += [
        '', '## Cómo interpretar las anotaciones de spaCy', '',
        '- `categoria`: determinante, sustantivo, adjetivo, verbo, etc. (`pos_`).',
        '- `morfologia`: información como género y número, si el modelo la predice.',
        '- `dependencia` y `depende_de`: relación sintáctica y palabra de la que depende.',
        '- Que spaCy entregue etiquetas **no significa** que la oración sea gramaticalmente correcta.',
        '- Las etiquetas automáticas pueden ser incorrectas: hay que revisar ejemplos representativos.',
        '', '## Observaciones que se deben comprobar al redactar el informe', '',
        '1. ¿El parser rechaza concordancias incorrectas que están contempladas por sus reglas?',
        '2. ¿Qué oraciones correctas rechaza por vocabulario o estructuras no implementadas?',
        '3. ¿spaCy identifica correctamente sujeto, verbo, adjetivos, adverbios y subordinadas?',
        '4. ¿Qué análisis distinto o discutible hace spaCy ante frases ambiguas o errores de concordancia?',
        '',
        'La revisión lingüística de las salidas de spaCy y las conclusiones finales deben hacerse '
        'después de ejecutar su modelo real. Este archivo no afirma que todas sus predicciones sean correctas.',
    ]
    return '\n'.join(lineas)+'\n'


def ejecutar(args):
    casos = json.loads(args.casos.read_text(encoding='utf-8'))
    ids = [c['id'] for c in casos]
    if len(ids) != len(set(ids)) or not all('oracion' in c and 'esperado_parser' in c for c in casos):
        raise ValueError('El conjunto de pruebas tiene IDs duplicados o campos faltantes.')
    version = None
    nlp = None
    if not args.solo_parser:
        spacy, nlp = cargar_modelo(args.modelo)
        version = spacy.__version__
    resultados = crear_resultados(casos, nlp)
    args.salida.mkdir(parents=True, exist_ok=True)
    prefijo = 'preliminar_parser' if args.solo_parser else 'comparacion_spacy'
    csv_path = args.salida / f'{prefijo}.csv'
    json_path = args.salida / f'{prefijo}.json'
    md_path = args.salida / f'{prefijo}.md'
    escribir_csv(csv_path, resultados)
    json_path.write_text(json.dumps({
        'metadatos': {'generado_en': datetime.now().astimezone().isoformat(),
                      'modo': 'SOLO_PARSER' if args.solo_parser else 'COMPARACION',
                      'modelo': args.modelo if nlp is not None else None,
                      'version_spacy': version},
        'casos': resultados,
    }, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    md_path.write_text(resumen_md(resultados, args.modelo, version), encoding='utf-8')
    if args.arboles:
        contenido = []
        for c in resultados:
            contenido.append(f"{c['id']} — {c['oracion']}\n" +
                             (c['parser']['arbol'] if c['parser']['acepta'] else 'RECHAZADO: '+c['parser']['error']))
        (args.salida/f'{prefijo}_arboles.txt').write_text('\n\n'.join(contenido)+'\n', encoding='utf-8')
    coincide = sum(x['parser']['acepta'] == x['esperado_parser'] for x in resultados)
    print(f'Parser LL(1): {coincide}/{len(resultados)} resultados según lo esperado para su subconjunto.')
    print('spaCy:', 'NO EJECUTADO (solo-parser)' if nlp is None else f'{args.modelo} {version} ejecutado')
    print('Archivos generados:', csv_path, json_path, md_path, sep='\n - ')
    if coincide != len(resultados):
        print('ATENCIÓN: hay discrepancias con los resultados esperados; revisá el CSV.')
    return 0


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--casos', type=Path, default=BASE/'casos_comparacion_es.json')
    p.add_argument('--salida', type=Path, default=BASE/'resultados_comparacion')
    p.add_argument('--modelo', default='es_core_news_sm')
    p.add_argument('--solo-parser', action='store_true', help='Comprueba el parser sin afirmar que spaCy fue ejecutado.')
    p.add_argument('--arboles', action='store_true', help='Guarda los árboles y los errores en un TXT.')
    args=p.parse_args()
    try:
        return ejecutar(args)
    except (RuntimeError, ValueError, OSError) as exc:
        p.exit(2, f'ERROR: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
