"""Evalua las etiquetas POS de los logs frente a una referencia por palabra.

Es una evaluacion diferente de la aceptacion/rechazo de oraciones.
La referencia POS se actualiza si cambia el corpus o su tokenizacion.
"""
import argparse
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def pos_nltk(etiqueta):
    if etiqueta == 'SIN_ETIQUETA':
        return 'SIN_ETIQUETA'
    if etiqueta.startswith('cc'):
        return 'CCONJ'
    if etiqueta.startswith('cs'):
        return 'SCONJ'
    mapa = {'d': 'DET', 'n': 'NOUN', 'v': 'VERB', 'a': 'ADJ',
            'r': 'ADV', 's': 'ADP', 'p': 'PRON', 'F': 'PUNCT'}
    return mapa.get(etiqueta[:1], 'OTRO')


def leer_referencia(ruta):
    with ruta.open('r', encoding='utf-8-sig', newline='') as f:
        filas = list(csv.DictReader(f))
    referencias = {}
    for row in filas:
        clave = (row['id'], int(row['indice_token']))
        if clave in referencias:
            raise ValueError(f'Referencia repetida: {clave}')
        referencias[clave] = row
    if not referencias:
        raise ValueError('Referencia POS vacia')
    return referencias


def evaluar_log(path, fuente, referencia):
    datos = json.loads(path.read_text(encoding='utf-8'))
    registros = datos.get('resultados', [])
    observados = {}
    for registro in registros:
        for indice, tok in enumerate(registro['tokens']):
            clave = (registro['id'], indice)
            if clave in observados:
                raise ValueError(f'Clave duplicada en {fuente}: {clave}')
            observados[clave] = tok
    if set(observados) != set(referencia):
        raise ValueError(f'{fuente}: distinta cantidad de tokens o IDs que la referencia POS')
    errores = []
    correctos = 0
    conocidos = 0
    for clave, gold in referencia.items():
        tok = observados[clave]
        if tok['texto'] != gold['texto']:
            raise ValueError(f'Token diferente en {fuente} {clave}: {tok["texto"]}')
        pred = tok['pos'] if fuente == 'spaCy' else pos_nltk(tok['etiqueta_cess_esp'])
        if pred != 'SIN_ETIQUETA':
            conocidos += 1
        if pred == gold['pos_esperado']:
            correctos += 1
        else:
            errores.append({
                'herramienta': fuente, 'id': clave[0], 'indice_token': clave[1],
                'texto': gold['texto'], 'pos_esperado': gold['pos_esperado'],
                'pos_obtenido': pred,
                'tipo_error': 'SIN_ETIQUETA' if pred == 'SIN_ETIQUETA' else 'POS_INCORRECTO',
            })
    total = len(referencia)
    return ({
        'herramienta': fuente, 'tokens_evaluados': total,
        'tokens_con_etiqueta': conocidos,
        'tokens_pos_correctos': correctos,
        'tokens_pos_incorrectos': total - correctos,
        'cobertura_etiquetado': round(conocidos/total, 6),
        'exactitud_pos': round(correctos/total, 6),
        'exactitud_pos_sobre_etiquetados': round(correctos/conocidos, 6) if conocidos else None,
    }, errores)


def guardar_csv(path, filas, columnas):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=columnas)
        w.writeheader()
        w.writerows(filas)


def ejecutar(referencia_path, spacy_path, nltk_path, salida):
    referencia = leer_referencia(referencia_path)
    resumen = []
    errores = []
    for fuente, path in [('spaCy', spacy_path), ('NLTK', nltk_path)]:
        actual, fallos = evaluar_log(path, fuente, referencia)
        resumen.append(actual)
        errores.extend(fallos)
        print(f'{fuente}: POS correctos {actual["tokens_pos_correctos"]}/{actual["tokens_evaluados"]}; '
              f'cobertura {actual["cobertura_etiquetado"]:.1%}; exactitud POS {actual["exactitud_pos"]:.1%}')
    guardar_csv(salida / 'tabla_pos.csv', resumen, list(resumen[0]))
    guardar_csv(salida / 'errores_pos.csv', errores,
                ['herramienta','id','indice_token','texto','pos_esperado','pos_obtenido','tipo_error'])
    (salida / 'tabla_pos.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Resultados POS guardados en:', salida)
    print('NOTA: las etiquetas de referencia deben ser revisadas por el grupo.')


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--referencia', type=Path, default=BASE / 'referencia_pos.csv')
    cli.add_argument('--spacy', type=Path, default=BASE / 'logs' / 'spacy.json')
    cli.add_argument('--nltk', type=Path, default=BASE / 'logs' / 'nltk.json')
    cli.add_argument('--salida', type=Path, default=BASE / 'resultados')
    a = cli.parse_args()
    try:
        ejecutar(a.referencia, a.spacy, a.nltk, a.salida)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        cli.exit(2, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
