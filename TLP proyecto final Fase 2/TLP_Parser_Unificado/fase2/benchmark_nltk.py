"""Etiqueta las mismas oraciones con NLTK y el corpus español CESS-ESP.

Se crea un etiquetador estadistico (bigramas + unigramas) entrenado con CESS-ESP.
No es un validador de CFG: sus etiquetas no se convierten por si solas en ACEPTADA.

Requiere:
    py -3.13 -m pip install nltk
    py -3.13 -m nltk.downloader cess_esp
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from corpus_util import leer_corpus

BASE = Path(__file__).resolve().parent


def ejecutar(corpus, salida):
    try:
        import nltk
        from nltk.corpus import cess_esp
        from nltk.tag import DefaultTagger, UnigramTagger, BigramTagger
    except ImportError as exc:
        raise RuntimeError('Falta NLTK. Instalacion: py -3.13 -m pip install nltk') from exc

    try:
        # El entrenamiento utiliza CESS-ESP, no las etiquetas del corpus evaluado.
        entrenamiento = cess_esp.tagged_sents()
        if not entrenamiento:
            raise RuntimeError('El corpus CESS-ESP no devolvio oraciones.')
    except LookupError as exc:
        raise RuntimeError('Falta CESS-ESP. Descarga: py -3.13 -m nltk.downloader cess_esp') from exc

    # El etiquetador se entrena con datos externos al corpus evaluado.
    base = DefaultTagger('SIN_ETIQUETA')
    unigramas = UnigramTagger(entrenamiento, backoff=base)
    tagger = BigramTagger(entrenamiento, backoff=unigramas)
    casos = leer_corpus(corpus)
    resultados = []
    for caso in casos:
        palabras = nltk.wordpunct_tokenize(caso['oracion'])
        etiquetas = tagger.tag(palabras)
        resultados.append({
            'id': caso['id'], 'nivel': int(caso['nivel']),
            'oracion': caso['oracion'], 'esperado_cfg': caso['esperado_cfg'],
            'estado': 'ETIQUETADO', 'obtenido': None,
            'tokens': [{'texto': palabra, 'etiqueta_cess_esp': etiqueta} for palabra, etiqueta in etiquetas],
        })
    datos = {
        'herramienta': 'NLTK BigramTagger+UnigramTagger entrenado en CESS-ESP',
        'tipo_resultado': 'anotaciones_nlp',
        'metadatos': {
            'fecha_ejecucion_utc': datetime.now(timezone.utc).isoformat(),
            'nltk_version': nltk.__version__,
            'corpus_entrenamiento': 'CESS-ESP (NLTK)',
            'oraciones_entrenamiento': len(entrenamiento),
            'tagset': 'etiquetas originales CESS-ESP / EAGLES',
            'metodo': 'BigramTagger con retroceso a UnigramTagger y DefaultTagger',
            'nota': 'ETIQUETADO no equivale a ACEPTADA. Requiere anotacion de referencia/criterio de evaluacion.',
        },
        'resultados': resultados,
    }
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(datos, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'NLTK etiqueto {len(resultados)} oraciones. Log guardado en: {salida}')
    print('IMPORTANTE: este archivo NO contiene decisiones binarias segun la CFG.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--corpus', type=Path, default=BASE/'corpus.csv')
    p.add_argument('--salida', type=Path, default=BASE/'logs'/'nltk.json')
    a = p.parse_args()
    try:
        ejecutar(a.corpus, a.salida)
    except (OSError, RuntimeError) as exc:
        p.exit(2, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
