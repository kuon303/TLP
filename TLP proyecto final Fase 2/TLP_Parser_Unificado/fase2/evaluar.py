"""Calcula metricas reproducibles a partir de logs binarios ACEPTADA/RECHAZADA.

No hace llamadas a modelos, no modifica resultados ni infiere etiquetas.
Los logs NLP sin decision binaria explicita quedan fuera de las metricas binaras.
"""
import argparse
import csv
import json
from collections import Counter
from html import escape
from pathlib import Path

BASE = Path(__file__).resolve().parent
VALIDOS = {'ACEPTADA', 'RECHAZADA'}


def ratio(numerador, denominador):
    return round(numerador / denominador, 6) if denominador else None


def cargar_log(ruta):
    datos = json.loads(ruta.read_text(encoding='utf-8'))
    if datos.get('tipo_resultado') != 'clasificacion_cfg':
        raise ValueError(f'{ruta}: log sin clasificacion binaria segun la CFG; no se puede puntuar como aceptado/rechazado.')
    resultados = datos.get('resultados', [])
    if not resultados:
        raise ValueError(f'{ruta}: no tiene resultados.')
    ids = set()
    for r in resultados:
        if r.get('id') in ids:
            raise ValueError(f'{ruta}: id duplicado {r.get("id")!r}')
        ids.add(r.get('id'))
        if r.get('esperado_cfg') not in VALIDOS or r.get('obtenido') not in VALIDOS:
            raise ValueError(f'{ruta}: etiqueta faltante o invalida en id {r.get("id")}')
    return datos


def evaluar(datos):
    rs = datos['resultados']
    tp = sum(r['esperado_cfg'] == 'ACEPTADA' and r['obtenido'] == 'ACEPTADA' for r in rs)
    tn = sum(r['esperado_cfg'] == 'RECHAZADA' and r['obtenido'] == 'RECHAZADA' for r in rs)
    fp = sum(r['esperado_cfg'] == 'RECHAZADA' and r['obtenido'] == 'ACEPTADA' for r in rs)
    fn = sum(r['esperado_cfg'] == 'ACEPTADA' and r['obtenido'] == 'RECHAZADA' for r in rs)
    return {
        'herramienta': datos['herramienta'],
        'total': len(rs),
        'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
        'precision': ratio(tp, tp + fp),
        'recall': ratio(tp, tp + fn),
        'tasa_rechazo_correcto': ratio(tn, tn + fp),
        'exactitud': ratio(tp + tn, len(rs)),
        'exactitud_balanceada': ratio((ratio(tp,tp+fn) or 0) + (ratio(tn,tn+fp) or 0), 2),
        'errores_etiquetado': ('VER_tabla_pos.csv' if datos.get('metadatos', {}).get('decision_nativa') is False
                                else 'NO_APLICA'),
    }


def guardar_csv(ruta, filas):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open('w', encoding='utf-8-sig', newline='') as f:
        columnas = list(filas[0])
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(filas)


def dibujar_svg(ruta, metricas):
    """Genera un SVG con las metricas de los logs completos disponibles."""
    etiquetas = [('precision', 'Precision'), ('recall', 'Recall'),
                 ('tasa_rechazo_correcto', 'Rechazo correcto')]
    ancho = 970
    alto = 115 + len(metricas) * 145
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" '
              f'viewBox="0 0 {ancho} {alto}">',
              '<rect width="100%" height="100%" fill="#ffffff"/>',
              '<text x="34" y="44" font-family="Arial" font-size="23" fill="#1d2636" '
              'font-weight="bold">Resultados del benchmark — etiqueta CFG</text>',
              '<text x="34" y="68" font-family="Arial" font-size="12" fill="#526175">'
              'Solo incluye herramientas con clasificacion binaria registrada.</text>']
    colores = ['#326db2','#278779','#c7803a']
    for indice, m in enumerate(metricas):
        y0 = 96 + indice * 145
        partes.append(f'<text x="35" y="{y0}" font-family="Arial" font-size="15" '
                      f'font-weight="bold" fill="#1d2636">{escape(m["herramienta"])}</text>')
        for j, (clave, etiqueta) in enumerate(etiquetas):
            y = y0 + 23 + j * 33
            valor = m[clave]
            longitud = round(525 * valor) if valor is not None else 0
            partes += [f'<text x="35" y="{y+14}" font-family="Arial" font-size="13" '
                       f'fill="#3d4758">{etiqueta}</text>',
                       f'<rect x="233" y="{y}" width="525" height="18" rx="3" fill="#edf1f5"/>',
                       f'<rect x="233" y="{y}" width="{longitud}" height="18" rx="3" fill="{colores[j]}"/>',
                       f'<text x="772" y="{y+14}" font-family="Arial" font-size="13" '
                       f'fill="#1d2636">{f"{100*valor:.1f}%" if valor is not None else "N/D"}</text>']
    partes.append('</svg>')
    ruta.write_text('\n'.join(partes)+'\n',encoding='utf-8')


def ejecutar(rutas, carpeta):
    from corpus_util import leer_corpus
    casos = leer_corpus(BASE / 'corpus.csv')
    justificaciones_cfg = {c['id']: (c.get('justificacion') or '').strip() for c in casos}
    esperado = {(c['id'], c['oracion'], c['esperado_cfg']) for c in casos}
    fuentes = [cargar_log(r) for r in rutas]
    for fuente, ruta in zip(fuentes, rutas):
        observados = {(r['id'], r['oracion'], r['esperado_cfg']) for r in fuente['resultados']}
        if observados != esperado:
            raise ValueError(f'{ruta}: este log no corresponde al corpus actual de 60 oraciones')
    bases = [{(r['id'], r['oracion'], r['esperado_cfg']) for r in d['resultados']} for d in fuentes]
    for i, referencia in enumerate(bases[1:], 1):
        if referencia != bases[0]:
            raise ValueError(f'Los IDs, textos o etiquetas del corpus no coinciden en {rutas[0]} y {rutas[i]}.')
    resumen = [evaluar(log) for log in fuentes]
    carpeta.mkdir(parents=True, exist_ok=True)
    guardar_csv(carpeta / 'tabla_metricas.csv', resumen)
    (carpeta / 'tabla_metricas.json').write_text(json.dumps(resumen, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    fallos = []
    for log in fuentes:
        for r in log['resultados']:
            if r['obtenido'] != r['esperado_cfg']:
                detalle = r.get('error') or ''
                if log['herramienta'].startswith('Gemini API'):
                    razon_gemini = (r.get('justificacion') or '').strip()
                    razon_cfg = justificaciones_cfg.get(r['id'], '')
                    partes = []
                    if razon_gemini:
                        partes.append(f'Gemini: {razon_gemini}')
                    if razon_cfg:
                        partes.append(f'CFG: {razon_cfg}')
                    detalle = ' | '.join(partes) or 'Sin explicacion registrada'
                fallos.append({'herramienta': log['herramienta'], 'id': r['id'],
                               'oracion': r['oracion'], 'esperado_cfg': r['esperado_cfg'],
                               'obtenido': r['obtenido'],
                               'tipo_error': ('FALSO_POSITIVO' if r['obtenido'] == 'ACEPTADA'
                                              else 'FALSO_NEGATIVO'),
                               'detalle': detalle})
    # El archivo se genera incluso cuando no hay errores de clasificacion.
    cabecera = ['herramienta','id','oracion','esperado_cfg','obtenido','tipo_error','detalle']
    with (carpeta / 'errores.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cabecera); w.writeheader(); w.writerows(fallos)
    dibujar_svg(carpeta / 'grafica_metricas.svg', resumen)
    for m in resumen:
        print(f'{m["herramienta"]}: TP={m["tp"]}, TN={m["tn"]}, FP={m["fp"]}, FN={m["fn"]}, '
              f'precision={m["precision"]}, recall={m["recall"]}, rechazo_correcto={m["tasa_rechazo_correcto"]}')
    print('Resultados guardados en:', carpeta)
    if len(resumen) < 4:
        print('NOTA: resultados parciales. Todavia faltan logs con decisiones binarias de otros enfoques.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('logs', nargs='*', type=Path, help='Logs JSON completos; por defecto detecta los disponibles.')
    p.add_argument('--salida', type=Path, default=BASE/'resultados')
    args=p.parse_args()
    if args.logs:
        rutas = args.logs
    else:
        nombres = ['parser.json', 'spacy_cfg.json', 'nltk_cfg.json',
                   'llm_zero_shot.json', 'llm_few_shot.json']
        rutas = []
        for nombre in nombres:
            ruta = BASE / 'logs' / nombre
            if not ruta.exists():
                print(f'PENDIENTE: {nombre} no existe')
                continue
            datos = json.loads(ruta.read_text(encoding='utf-8'))
            if datos.get('tipo_resultado') != 'clasificacion_cfg':
                print(f'PENDIENTE: {nombre} tiene respuestas incompletas, no se incluye')
                continue
            rutas.append(ruta)
        if not rutas:
            raise SystemExit('ERROR: no hay logs validos para evaluar')
    try:
        ejecutar(rutas, args.salida)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        p.exit(2, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
