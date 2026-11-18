"""Convierte logs NLP brutos en decisiones binarias mediante criterios fijos.

Mantiene intactos spacy.json y nltk.json. No consulta el parser original ni
usa la etiqueta esperada para decidir: solo la emplea despues para comparar.
"""
import argparse
import hashlib
import json
from pathlib import Path

from criterios_nlp import VERSION, clasificar
from corpus_util import leer_corpus as leer_corpus_validado

BASE = Path(__file__).resolve().parent
VALIDAS = {'ACEPTADA', 'RECHAZADA'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def leer_corpus(path):
    return {r['id']: r for r in leer_corpus_validado(path)}


def ejecutar_fuente(fuente, path_raw, corpus, corpus_path, destino):
    datos = json.loads(path_raw.read_text(encoding='utf-8'))
    if datos.get('tipo_resultado') != 'anotaciones_nlp':
        raise ValueError(f'{path_raw} no es un log NLP original')
    nombre = datos.get('herramienta', '').lower()
    if fuente == 'spacy' and 'spacy' not in nombre:
        raise ValueError('El archivo indicado no es de spaCy')
    if fuente == 'nltk' and 'nltk' not in nombre:
        raise ValueError('El archivo indicado no es de NLTK')
    originales = datos.get('resultados', [])
    ids = [r['id'] for r in originales]
    if len(ids) != len(set(ids)) or set(ids) != set(corpus):
        raise ValueError('Los IDs de las anotaciones no coinciden con el corpus')
    calculados = []
    for registro in originales:
        caso = corpus[registro['id']]
        if (registro['oracion'] != caso['oracion'] or
                registro['esperado_cfg'] != caso['esperado_cfg'] or
                int(registro['nivel']) != int(caso['nivel'])):
            raise ValueError(f'Inconsistencia en oracion o etiqueta: {registro["id"]}')
        if registro.get('obtenido') is not None:
            raise ValueError('El log bruto no debe tener decision binaria')
        tokens_originales = registro.get('tokens')
        if not isinstance(tokens_originales, list) or not tokens_originales:
            raise ValueError(f'Anotaciones incompletas en id {registro["id"]}')
        if any(not isinstance(tok, dict) or not tok.get('texto') for tok in tokens_originales):
            raise ValueError(f'Token sin texto en id {registro["id"]}')
        obtenido, motivo, normalizados = clasificar(tokens_originales, fuente)
        calculados.append({
            'id': registro['id'],
            'nivel': int(registro['nivel']),
            'oracion': registro['oracion'],
            'esperado_cfg': caso['esperado_cfg'],
            'obtenido': obtenido,
            'coincide_con_esperado': obtenido == caso['esperado_cfg'],
            'criterio_motivo': motivo,
            'error': motivo if obtenido == 'RECHAZADA' else None,
            'tokens_normalizados': normalizados,
        })
    respuesta = {
        'herramienta': f'{datos["herramienta"]} + criterio equivalencia v1',
        'tipo_resultado': 'clasificacion_cfg',
        'metadatos': {
            'origen': 'criterio_derivado_de_anotaciones',
            'decision_nativa': False,
            'version_criterios': VERSION,
            'log_original': path_raw.name,
            'log_original_sha256': sha(path_raw),
            'corpus_sha256': sha(corpus_path),
            'nota': 'Decision derivada de POS/morfologia; spaCy y NLTK no validan CFG de forma nativa.',
        },
        'resultados': calculados,
    }
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(respuesta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    aceptadas = sum(r['obtenido'] == 'ACEPTADA' for r in calculados)
    aciertos = sum(r['coincide_con_esperado'] for r in calculados)
    print(f'{fuente}: {len(calculados)} entradas, {aceptadas} aceptadas por criterio, {aciertos} coincidencias')
    print(f'Decisiones derivadas guardadas en: {destino}')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--corpus', type=Path, default=BASE / 'corpus.csv')
    p.add_argument('--spacy', type=Path, default=BASE / 'logs' / 'spacy.json')
    p.add_argument('--nltk', type=Path, default=BASE / 'logs' / 'nltk.json')
    p.add_argument('--salida', type=Path, default=BASE / 'logs')
    a = p.parse_args()
    try:
        corpus = leer_corpus(a.corpus)
        for fuente, path in [('spacy', a.spacy), ('nltk', a.nltk)]:
            ejecutar_fuente(fuente, path, corpus, a.corpus, a.salida / f'{fuente}_cfg.json')
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        p.exit(2, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
