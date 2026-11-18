"""Obtiene las anotaciones de spaCy para las 60 oraciones del corpus.

Requiere: py -3.13 -m pip install spacy
          py -3.13 -m spacy download es_core_news_sm
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from corpus_util import leer_corpus

BASE = Path(__file__).resolve().parent


def ejecutar(corpus, salida, modelo):
    try:
        import spacy
    except ImportError as e:
        raise RuntimeError('Falta spaCy. Instalar con: py -3.13 -m pip install spacy') from e
    try:
        nlp = spacy.load(modelo)
    except OSError as e:
        raise RuntimeError(f'Falta el modelo {modelo}. Descargar: py -3.13 -m spacy download {modelo}') from e
    casos = leer_corpus(corpus)
    salida.parent.mkdir(parents=True, exist_ok=True)
    res = []
    for c in casos:
        registro = []
        doc = nlp(c['oracion'])
        for t in doc:
            registro.append({'texto': t.text, 'pos': t.pos_, 'tag': t.tag_, 'lemma': t.lemma_,
                             'morph': str(t.morph), 'dep': t.dep_, 'head': t.head.text,
                             'head_index': t.head.i})
        res.append({'id': c['id'], 'oracion': c['oracion'], 'nivel': int(c['nivel']),
                    'esperado_cfg': c['esperado_cfg'], 'estado': 'ANOTADO',
                    'obtenido': None, 'tokens': registro})
    datos = {'herramienta': f'spaCy {modelo}', 'tipo_resultado': 'anotaciones_nlp',
             'metadatos': {'spacy_version': spacy.__version__,
                           'modelo': modelo, 'lang': nlp.lang,
                           'fecha_ejecucion_utc': datetime.now(timezone.utc).isoformat(),
                           'nota': 'Las anotaciones NLP no son veredictos CFG; el criterio se aplica por separado.'},
             'resultados': res}
    salida.write_text(json.dumps(datos, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'spaCy analizo {len(res)} oraciones. Log de anotaciones: {salida}')
    print('IMPORTANTE: este archivo NO afirma aceptacion/rechazo gramatical.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--corpus', type=Path, default=BASE/'corpus.csv')
    p.add_argument('--modelo', default='es_core_news_sm')
    p.add_argument('--salida', type=Path, default=BASE/'logs'/'spacy.json')
    a = p.parse_args()
    try:
        ejecutar(a.corpus, a.salida, a.modelo)
    except (RuntimeError, OSError) as exc:
        p.exit(2, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
