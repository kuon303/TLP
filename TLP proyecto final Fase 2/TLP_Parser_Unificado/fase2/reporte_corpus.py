"""Genera un informe por oracion con las decisiones del parser y los otros enfoques.

No ejecuta servicios externos ni modifica los logs. Los resultados de spaCy,
NLTK y Gemini se consultan en los archivos guardados cuando estan disponibles.
"""

import hashlib
import json
import re
from collections import Counter
from html import escape
from pathlib import Path

BASE = Path(__file__).resolve().parent

FUENTES = (
    ('spacy_cfg.json', 'spaCy + criterio'),
    ('nltk_cfg.json', 'NLTK + criterio'),
    ('llm_zero_shot.json', 'Gemini zero-shot'),
    ('llm_few_shot.json', 'Gemini few-shot'),
)
ETIQUETAS = {'ACEPTADA', 'RECHAZADA'}


def clase_resultado(esperado, obtenido):
    """Clasifica la decision respecto a la etiqueta esperada de la CFG."""
    if obtenido == 'ACEPTADA':
        return 'TP' if esperado == 'ACEPTADA' else 'FP'
    if obtenido == 'RECHAZADA':
        return 'TN' if esperado == 'RECHAZADA' else 'FN'
    return 'ND'


def nombre_clase(clase):
    return {
        'TP': 'Verdadero positivo',
        'TN': 'Verdadero negativo',
        'FP': 'Falso positivo: aceptada erroneamente',
        'FN': 'Falso negativo: rechazada erroneamente',
        'ND': 'Sin decision',
    }[clase]


def explicacion_parser(resultado):
    """Resume la salida real sin utilizar la etiqueta esperada."""
    if resultado['obtenido'] == 'ACEPTADA':
        tipos = [t['tipo'] for t in (resultado.get('tokens') or [])]
        opciones = {
            'ART_MS': ('SujetoMS', 'PredicadoS'),
            'ART_FS': ('SujetoFS', 'PredicadoS'),
            'ART_MP': ('SujetoMP', 'PredicadoP'),
            'ART_FP': ('SujetoFP', 'PredicadoP'),
        }
        sujeto, predicado = opciones.get(tipos[0] if tipos else '', ('Sujeto', 'Predicado'))
        extras = []
        if 'QUE' in tipos:
            extras.append('una relativa')
        if any(t.startswith('ADJ_') for t in tipos):
            extras.append('modificadores adjetivales')
        if 'ADV' in tipos:
            extras.append('adverbios')
        if 'PREP' in tipos:
            extras.append('complementos preposicionales')
        texto = (f'Derivacion valida: Oracion -> {sujeto} {predicado} PuntoOpcional EOF. '
                 'Los tokens se consumieron en el orden permitido por la CFG.')
        if extras:
            texto += ' Incluye ' + ', '.join(extras) + '.'
        return texto

    error = resultado.get('error') or ''
    if 'ErrorLexicoEspanol' in error:
        return 'El analisis lexico encontro un caracter no reconocido.'
    match = re.search(r'no hay produccion para (\w+) con (\w+) \((.+?)\)', error)
    if match:
        no_terminal, tipo, palabra = match.groups()
        if tipo == 'DESCONOCIDA':
            return f'El token {palabra} no pertenece al vocabulario valido en {no_terminal}.'
        return (f'No existe una produccion de {no_terminal} para el token '
                f'{tipo} ({palabra}).')
    match = re.search(r'se esperaba (\w+), pero aparecio (\w+) \((.+?)\)', error)
    if match:
        previsto, recibido, palabra = match.groups()
        return f'Se esperaba {previsto}, pero aparecio {recibido} ({palabra}).'
    return 'No se pudo construir una derivacion completa. Consultar el error exacto del parser.'


def cargar_comparaciones(casos, carpeta_logs, ruta_corpus=None):
    """Carga solo logs completos y compatibles con el corpus actual."""
    esperados = {c['id']: (c['oracion'], c['esperado_cfg']) for c in casos}
    sha_corpus = (hashlib.sha256(Path(ruta_corpus).read_bytes()).hexdigest()
                  if ruta_corpus is not None else None)
    fuentes = []
    advertencias = []
    for nombre, etiqueta in FUENTES:
        ruta = Path(carpeta_logs) / nombre
        if not ruta.is_file():
            advertencias.append(f'{nombre}: no disponible, se omite del informe.')
            continue
        try:
            datos = json.loads(ruta.read_text(encoding='utf-8'))
            if datos.get('tipo_resultado') != 'clasificacion_cfg':
                raise ValueError('sin clasificacion completa')
            registros = datos.get('resultados') or []
            if len(registros) != len(casos):
                raise ValueError(f'cantidad de registros distinta: {len(registros)}')
            indice = {}
            for r in registros:
                ident = r.get('id')
                if ident in indice or ident not in esperados:
                    raise ValueError('ID repetido o desconocido')
                if ((r.get('oracion'), r.get('esperado_cfg')) != esperados[ident]
                        or r.get('obtenido') not in ETIQUETAS):
                    raise ValueError(f'registro {ident} distinto al corpus actual')
                indice[ident] = r
            if sha_corpus:
                registrado = datos.get('metadatos', {}).get('corpus_sha256')
                if registrado and registrado != sha_corpus:
                    raise ValueError('la huella del corpus no coincide')
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            advertencias.append(f'{nombre}: no incluido ({exc}).')
            continue
        fuentes.append((etiqueta, indice))
    return fuentes, advertencias


def extraer_motivo(registro):
    """Mantiene los motivos originales de los logs, sin inventar explicaciones."""
    return (registro.get('criterio_motivo')
            or registro.get('justificacion')
            or registro.get('error')
            or 'No se registro una explicacion adicional.')


def resumen_matriz(casos, indices):
    salida = []
    for nombre, idx in indices:
        clases = Counter(clase_resultado(c['esperado_cfg'], idx[c['id']]['obtenido'])
                         for c in casos)
        salida.append({'nombre': nombre, 'TP': clases['TP'], 'TN': clases['TN'],
                       'FP': clases['FP'], 'FN': clases['FN']})
    return salida


def _tabla_resumen(filas):
    piezas = [
        '<table class="resumen"><thead><tr><th>Enfoque</th><th>ACEPTADA</th>'
        '<th>RECHAZADA</th><th>FP</th><th>FN</th><th>Coincidencias</th></tr></thead><tbody>'
    ]
    for f in filas:
        correctas = f['TP'] + f['TN']
        piezas.append(
            f'<tr><td>{escape(f["nombre"])}</td><td>{f["TP"]+f["FP"]}</td>'
            f'<td>{f["TN"]+f["FN"]}</td><td>{f["FP"]}</td>'
            f'<td>{f["FN"]}</td><td>{correctas}/{f["TP"]+f["TN"]+f["FP"]+f["FN"]}</td></tr>'
        )
    return '\n'.join(piezas + ['</tbody></table>'])


def _tabla_tokens(tokens):
    if tokens is None:
        return '<p>No se pudo completar la etapa lexica.</p>'
    filas = ['<table class="tokens"><thead><tr><th>Texto</th><th>Tipo</th></tr></thead><tbody>']
    for tok in tokens:
        filas.append('<tr><td>' + escape(str(tok['texto'])) + '</td><td>'
                     + escape(str(tok['tipo'])) + '</td></tr>')
    filas.append('</tbody></table>')
    return '\n'.join(filas)


def _detalle_original(caso):
    piezas = []
    if caso.get('fenomeno'):
        piezas.append('<p><b>Fenomeno:</b> ' + escape(caso['fenomeno']) + '</p>')
    if caso.get('estructura_esperada'):
        piezas.append('<p><b>Estructura esperada:</b> '
                      + escape(caso['estructura_esperada']) + '</p>')
    if caso.get('justificacion'):
        piezas.append('<p><b>Nota de referencia:</b> '
                      + escape(caso['justificacion']) + '</p>')
    return '\n'.join(piezas)


def generar_reporte(casos, resultados_parser, carpeta_logs, destino_html,
                    destino_txt=None, ruta_corpus=None):
    """Genera HTML y TXT sin modificar los logs de los experimentos."""
    if len(casos) != len(resultados_parser):
        raise ValueError('Las decisiones del parser no coinciden en cantidad con el corpus.')
    indices_parser = {}
    for caso, resultado in zip(casos, resultados_parser):
        if ((caso['id'], caso['oracion'], caso['esperado_cfg'])
                != (resultado['id'], resultado['oracion'], resultado['esperado_cfg'])):
            raise ValueError(f'Resultado del parser incompatible con el caso {caso["id"]}.')
        indices_parser[caso['id']] = resultado

    fuentes, advertencias = cargar_comparaciones(casos, carpeta_logs, ruta_corpus)
    todos = [('Parser LL(1)', indices_parser)] + fuentes
    matrices = resumen_matriz(casos, todos)
    parser = matrices[0]
    destino_html = Path(destino_html)
    if destino_txt is None:
        destino_txt = destino_html.with_suffix('.txt')
    destino_txt = Path(destino_txt)
    destino_html.parent.mkdir(parents=True, exist_ok=True)
    destino_txt.parent.mkdir(parents=True, exist_ok=True)

    estilos = '''
    :root{font-family:Arial,Helvetica,sans-serif;color:#222b38;background:#f5f7fa}
    body{max-width:1050px;margin:28px auto;padding:0 19px;line-height:1.48}
    h1{font-size:27px;margin:0 0 10px}h2{font-size:19px;margin:0 0 8px}
    h3{font-size:15px;margin:16px 0 8px}
    .portada,.caso{background:#fff;border:1px solid #d7dfe9;border-radius:10px;
      padding:23px;margin-bottom:18px}
    .muted{color:#59677a;font-size:13px}.nota{border-left:3px solid #73869c;
      padding-left:11px;color:#415066}
    table{border-collapse:collapse;width:100%;margin:10px 0;table-layout:fixed}
    td,th{border-bottom:1px solid #e2e7ee;padding:8px 7px;text-align:left;
      font-size:13px;vertical-align:top;overflow-wrap:anywhere}
    th{background:#edf1f6}table.tokens{max-width:470px}td:first-child{width:22%}
    .titulo-caso{display:flex;align-items:baseline;justify-content:space-between;
      gap:10px;flex-wrap:wrap}
    .oracion{font-size:17px;margin:9px 0}.correcto{color:#075d45;font-weight:bold}
    .incorrecto{color:#a12e20;font-weight:bold}
    .alerta{border:1px solid #e6b1a2;background:#fff5f2;padding:10px 12px;
      border-radius:5px;margin:12px 0}
    .arbol{white-space:pre;overflow-x:auto;background:#f0f3f7;border:1px solid #e1e7ee;
      padding:11px;font:12px/1.45 Consolas,monospace}
    details{margin-top:12px}summary{cursor:pointer;font-weight:bold}
    .separador{height:1px;background:#d7dfe9;margin:17px 0}
    .indice{display:flex;gap:5px;flex-wrap:wrap;margin:12px 0 20px}
    .indice a{font-size:12px;padding:3px 8px;border:1px solid #dae0e8;
      border-radius:3px;text-decoration:none;color:#315776;background:white}
    .volver{font-size:12px}
    @media print{body{max-width:none;margin:0;background:white}.portada,.caso{
      border-radius:0;break-inside:auto}details{display:block}
      details>.arbol,details>table{display:block!important}
      .indice,.volver{display:none}.caso{break-before:page}}
    '''
    piezas = [
        '<!doctype html>', '<html lang="es"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>Analisis completo del corpus - Fase 2</title>',
        '<style>' + estilos + '</style></head><body>',
        '<section class="portada" id="inicio"><h1>Analisis del corpus de 60 oraciones</h1>',
        '<p class="muted">Demostracion detallada del parser LL(1) y comparacion '
        'con los resultados registrados de NLP y Gemini.</p>',
        f'<p><b>Casos:</b> {len(casos)} &nbsp; <b>Parser aceptadas:</b> '
        f'{parser["TP"] + parser["FP"]} &nbsp; <b>Parser rechazadas:</b> '
        f'{parser["TN"]+parser["FN"]} &nbsp; '
        f'<b>Falsos positivos:</b> {parser["FP"]} &nbsp; '
        f'<b>Falsos negativos:</b> {parser["FN"]}</p>',
        '<h2>Resumen de resultados</h2>', _tabla_resumen(matrices),
        '<p class="nota">La etiqueta esperada corresponde a la CFG controlada, '
        'no a la correccion general del español. FP significa que la herramienta '
        'acepto algo que la referencia marca como rechazado; FN significa lo inverso. '
        'Las decisiones de spaCy y NLTK son derivadas de criterios de equivalencia, '
        'no validaciones nativas de su API. Para Gemini se consultan respuestas '
        'ya guardadas, sin realizar nuevas llamadas.</p>',
    ]
    if advertencias:
        piezas.append('<h3>Archivos de comparacion omitidos</h3><ul>')
        piezas += ['<li>' + escape(x) + '</li>' for x in advertencias]
        piezas.append('</ul>')
    piezas.append('</section>')
    piezas.append('<nav class="indice" aria-label="Indice por ID">')
    piezas.extend(f'<a href="#caso-{escape(c["id"])}">{escape(c["id"])}</a>' for c in casos)
    piezas.append('</nav>')

    lineas = [
        'ANALISIS DEL CORPUS - FASE 2',
        f'Casos: {len(casos)} | Parser ACEPTADA: {parser["TP"]+parser["FP"]} '
        f'| RECHAZADA: {parser["TN"]+parser["FN"]} '
        f'| FP: {parser["FP"]} | FN: {parser["FN"]}',
        'La etiqueta esperada proviene del corpus y no se usa para decidir.', '',
    ]
    for f in matrices:
        lineas.append(f'{f["nombre"]}: TP={f["TP"]}, TN={f["TN"]}, '
                      f'FP={f["FP"]}, FN={f["FN"]}')
    lineas.append('')
    for caso in casos:
        rid = caso['id']
        resultado = indices_parser[rid]
        clasif = clase_resultado(caso['esperado_cfg'], resultado['obtenido'])
        estilo = 'incorrecto' if clasif in ('FP', 'FN') else 'correcto'
        piezas.extend([
            f'<section class="caso" id="caso-{escape(rid)}">',
            '<div class="titulo-caso">',
            f'<h2>Caso {escape(rid)} · Nivel {escape(caso["nivel"])}</h2>',
            f'<a class="volver" href="#inicio">Volver al resumen</a></div>',
            f'<p class="oracion"><b>Oracion:</b> {escape(caso["oracion"])}</p>',
            f'<p><b>Referencia CFG:</b> {escape(caso["esperado_cfg"])} &nbsp; '
            f'<b>Correcta en español general:</b> '
            f'{escape(caso.get("correcta_espanol", "Sin dato"))}</p>',
            f'<p><b>Parser LL(1):</b> <span class="{estilo}">'
            f'{escape(resultado["obtenido"])}</span> &mdash; '
            f'{escape(nombre_clase(clasif))}</p>',
            f'<p><b>Motivo obtenido del parser:</b> '
            f'{escape(explicacion_parser(resultado))}</p>',
        ])
        if clasif in ('FP', 'FN'):
            piezas.append(
                '<div class="alerta"><b>Discrepancia con la referencia: '
                + escape(nombre_clase(clasif)) + '.</b> '
                'El parser tomo una decision distinta a la etiqueta esperada. '
                'Debe revisarse la derivacion y el caso de prueba. '
                'Si el parser acepto, el arbol se conserva debajo.</div>'
            )
        if resultado.get('error'):
            piezas.append('<p><b>Error exacto:</b> '
                          + escape(resultado['error']) + '</p>')
        piezas.append(_detalle_original(caso))
        if resultado.get('arbol') and resultado['obtenido'] == 'ACEPTADA':
            piezas.append('<h3>Arbol sintactico generado por el parser</h3>')
            piezas.append('<pre class="arbol">' + escape(resultado['arbol']) + '</pre>')
        else:
            piezas.append('<p class="muted">No hay arbol sintactico completo porque '
                          'la oracion fue rechazada.</p>')
        piezas.append('<details><summary>Ver tokens del lexer</summary>')
        piezas.append(_tabla_tokens(resultado.get('tokens')))
        piezas.append('</details>')
        if fuentes:
            piezas.append('<h3>Otros enfoques (resultados guardados)</h3>')
            piezas.append('<table><thead><tr><th>Herramienta</th><th>Decision / error</th>'
                          '<th>Explicacion registrada</th></tr></thead><tbody>')
            for nombre, indice in fuentes:
                r = indice[rid]
                clase = clase_resultado(caso['esperado_cfg'], r['obtenido'])
                estilo_otro = 'incorrecto' if clase in ('FP', 'FN') else 'correcto'
                piezas.append(
                    '<tr><td>' + escape(nombre) + '</td><td><span class="'
                    + estilo_otro + '">' + escape(r['obtenido']) + '</span><div class="muted">'
                    + escape(nombre_clase(clase)) + '</div></td><td>'
                    + escape(str(extraer_motivo(r))) + '</td></tr>'
                )
            piezas.append('</tbody></table>')
        piezas.append('</section>')

        lineas.extend([
            '=' * 74,
            f'CASO {rid} | Nivel {caso["nivel"]}',
            f'Oracion: {caso["oracion"]}',
            f'Esperado CFG: {caso["esperado_cfg"]} | Español general: {caso.get("correcta_espanol", "")}',
            f'Parser: {resultado["obtenido"]} | {nombre_clase(clasif)}',
            f'Motivo del parser: {explicacion_parser(resultado)}',
        ])
        if resultado.get('error'):
            lineas.append(f'Error exacto: {resultado["error"]}')
        if caso.get('justificacion'):
            lineas.append(f'Nota del corpus: {caso["justificacion"]}')
        if resultado.get('arbol') and resultado['obtenido'] == 'ACEPTADA':
            lineas.extend(['ARBOL SINTACTICO:', resultado['arbol']])
        for nombre, indice in fuentes:
            r = indice[rid]
            clase = clase_resultado(caso['esperado_cfg'], r['obtenido'])
            lineas.append(f'{nombre}: {r["obtenido"]} | {nombre_clase(clase)} '
                          f'| Motivo: {extraer_motivo(r)}')
        lineas.append('')
    piezas.append('</body></html>')
    destino_html.write_text('\n'.join(piezas) + '\n', encoding='utf-8')
    destino_txt.write_text('\n'.join(lineas) + '\n', encoding='utf-8')
    return {'filas': matrices, 'advertencias': advertencias,
            'html': destino_html, 'txt': destino_txt}


def mostrar_resumen(reporte):
    """Imprime un resumen corto; el analisis detallado queda en el documento."""
    principal = reporte['filas'][0]
    total = sum(principal[k] for k in ('TP', 'TN', 'FP', 'FN'))
    print('\n' + '=' * 78)
    print('   REPORTE DEL CORPUS GENERADO CORRECTAMENTE')
    print('=' * 78)
    print(f'Oraciones: {total} | Aceptadas: {principal["TP"]+principal["FP"]} '
          f'| Rechazadas: {principal["TN"]+principal["FN"]}')
    print(f'Parser: {principal["TP"]+principal["TN"]}/{total} coincidencias '
          f'| Aceptadas erroneamente (FP): {principal["FP"]} '
          f'| Rechazadas erroneamente (FN): {principal["FN"]}')
    if len(reporte['filas']) > 1:
        print('Comparacion con logs guardados:')
        for r in reporte['filas'][1:]:
            print(f'  {r["nombre"]}: {r["TP"]+r["TN"]}/{total} '
                  f'| FP={r["FP"]} | FN={r["FN"]}')
    print('\nARCHIVO DE ANALISIS (HTML):', reporte['html'])
    print('COPIA EN TEXTO (TXT):      ', reporte['txt'])
    print('=' * 78)
    if reporte['advertencias']:
        print('AVISOS:')
        for aviso in reporte['advertencias']:
            print('  -', aviso)
    print('Los logs de los experimentos no fueron modificados.')
