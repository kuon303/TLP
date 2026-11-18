"""Criterios deterministas aplicados a las anotaciones de spaCy y NLTK.

No ejecuta un parser CFG ni consulta etiquetas esperadas. Solo inspecciona
las etiquetas generadas por las herramientas y su posicion en la oracion.
Estos criterios son aproximaciones del subconjunto, NO validaciones nativas.
"""

VERSION = 'criterios_nlp_v1'


def rasgos_spacy(texto):
    rasgos = {}
    for elemento in (texto or '').split('|'):
        if '=' in elemento:
            clave, valor = elemento.split('=', 1)
            rasgos[clave] = valor
    return rasgos


def normalizar_spacy(tokens):
    salida = []
    for indice, tok in enumerate(tokens):
        palabra = tok['texto']
        pos = tok.get('pos', '')
        morph = rasgos_spacy(tok.get('morph', ''))
        mapa = {
            'DET': 'ART', 'NOUN': 'SUST', 'VERB': 'VERBO',
            'ADJ': 'ADJ', 'ADV': 'ADV', 'ADP': 'PREP',
        }
        categoria = mapa.get(pos, 'OTRO')
        if pos == 'PRON' and palabra.casefold() == 'que':
            categoria = 'QUE'
        if pos == 'PUNCT' and palabra == '.':
            categoria = 'PUNTO'
        salida.append({
            'indice': indice,
            'texto': palabra,
            'cat': categoria,
            'genero': {'Masc': 'm', 'Fem': 'f'}.get(morph.get('Gender')),
            'numero': {'Sing': 's', 'Plur': 'p'}.get(morph.get('Number')),
            'tiempo': morph.get('Tense'),
            'persona': morph.get('Person'),
            'dep': tok.get('dep'),
            'head_index': tok.get('head_index'),
        })
    return salida


def normalizar_nltk(tokens):
    salida = []
    for indice, tok in enumerate(tokens):
        palabra = tok['texto']
        etiqueta = tok.get('etiqueta_cess_esp', '')
        categoria, genero, numero, tiempo, persona = 'OTRO', None, None, None, None
        if etiqueta == 'SIN_ETIQUETA':
            categoria = 'SIN_ETIQUETA'
        elif etiqueta.startswith('d'):
            categoria = 'ART'
            if len(etiqueta) >= 5:
                genero = etiqueta[3] if etiqueta[3] in 'mf' else None
                numero = etiqueta[4] if etiqueta[4] in 'sp' else None
        elif etiqueta.startswith('n'):
            categoria = 'SUST'
            if len(etiqueta) >= 4:
                genero = etiqueta[2] if etiqueta[2] in 'mf' else None
                numero = etiqueta[3] if etiqueta[3] in 'sp' else None
        elif etiqueta.startswith('a'):
            categoria = 'ADJ'
            if len(etiqueta) >= 5:
                genero = etiqueta[3] if etiqueta[3] in 'mf' else None
                numero = etiqueta[4] if etiqueta[4] in 'sp' else None
        elif etiqueta.startswith('v'):
            categoria = 'VERBO'
            if len(etiqueta) >= 6:
                numero = etiqueta[5] if etiqueta[5] in 'sp' else None
                persona = etiqueta[4] if etiqueta[4].isdigit() else None
                tiempo = 'Pres' if etiqueta[3] == 'p' else etiqueta[3]
        elif etiqueta.startswith('r'):
            categoria = 'ADV'
        elif etiqueta.startswith('s'):
            categoria = 'PREP'
        elif etiqueta.startswith('p') and palabra.casefold() == 'que':
            categoria = 'QUE'
        elif etiqueta == 'Fp' and palabra == '.':
            categoria = 'PUNTO'
        salida.append({
            'indice': indice, 'texto': palabra, 'cat': categoria,
            'genero': genero, 'numero': numero, 'tiempo': tiempo,
            'persona': persona, 'dep': None, 'head_index': None,
        })
    return salida


class Rechazo(Exception):
    pass


class Lector:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.sujeto = None
        self.verbo_principal = None
        self.relativa = None

    def actual(self):
        if self.i >= len(self.tokens):
            return None
        return self.tokens[self.i]

    def opcional(self, categoria):
        if self.actual() is not None and self.actual()['cat'] == categoria:
            tok = self.actual()
            self.i += 1
            return tok
        return None

    def obligatorio(self, categoria):
        tok = self.opcional(categoria)
        if tok is not None:
            return tok
        encontrado = self.actual()
        if encontrado is None:
            raise Rechazo(f'Se esperaba {categoria}, pero termino la oracion')
        raise Rechazo(f'Se esperaba {categoria}; aparece {encontrado["cat"]} ({encontrado["texto"]})')


def concordar(a, b, campos, descripcion):
    for campo in campos:
        valor_a, valor_b = a.get(campo), b.get(campo)
        if valor_a and valor_b and valor_a != valor_b:
            raise Rechazo(f'{descripcion}: {campo} diferente ({a["texto"]} / {b["texto"]})')


def nominal(lector, principal=False):
    articulo = lector.obligatorio('ART')
    sustantivo = lector.obligatorio('SUST')
    concordar(articulo, sustantivo, ('genero', 'numero'), 'Articulo y sustantivo')
    adj = lector.opcional('ADJ')
    if adj is not None:
        concordar(sustantivo, adj, ('genero', 'numero'), 'Sustantivo y adjetivo')
        concordar(articulo, adj, ('genero', 'numero'), 'Articulo y adjetivo')
    if principal:
        lector.sujeto = sustantivo
    return sustantivo


def frase_preposicional(lector):
    if lector.opcional('PREP') is not None:
        nominal(lector)


def validar_estructura(tokens, fuente):
    if not tokens:
        return 'RECHAZADA', 'Sin tokens'
    try:
        lector = Lector(tokens)
        nominal(lector, principal=True)
        if lector.opcional('QUE') is not None:
            lector.relativa = lector.obligatorio('VERBO')
            concordar(lector.sujeto, lector.relativa, ('numero',), 'Sujeto y verbo de la relativa')
            if lector.relativa['tiempo'] not in (None, 'Pres'):
                raise Rechazo('Tiempo de la relativa no es presente')
            lector.opcional('ADV')
            frase_preposicional(lector)
        lector.verbo_principal = lector.obligatorio('VERBO')
        concordar(lector.sujeto, lector.verbo_principal, ('numero',), 'Sujeto y verbo principal')
        if lector.verbo_principal['tiempo'] not in (None, 'Pres'):
            raise Rechazo('Tiempo verbal principal no es presente')
        lector.opcional('ADV')
        frase_preposicional(lector)
        lector.opcional('PUNTO')
        if lector.actual() is not None:
            tok = lector.actual()
            raise Rechazo(f'Sobran tokens: {tok["texto"]} ({tok["cat"]})')
        if fuente == 'spacy':
            verbo = lector.verbo_principal
            sujeto = lector.sujeto
            if verbo['dep'] != 'ROOT':
                raise Rechazo('El verbo principal no es ROOT en spaCy')
            if sujeto['dep'] != 'nsubj' or sujeto['head_index'] != verbo['indice']:
                raise Rechazo('spaCy no vincula el sujeto con el verbo principal')
            if lector.relativa is not None:
                relativa = lector.relativa
                if relativa['dep'] != 'acl' or relativa['head_index'] != sujeto['indice']:
                    raise Rechazo('spaCy no vincula la relativa con el sujeto')
        return 'ACEPTADA', 'Coincide con el patron de etiquetas y concordancia definido'
    except Rechazo as exc:
        return 'RECHAZADA', str(exc)


def clasificar(tokens_originales, fuente):
    if fuente == 'spacy':
        tokens = normalizar_spacy(tokens_originales)
    elif fuente == 'nltk':
        tokens = normalizar_nltk(tokens_originales)
    else:
        raise ValueError(f'Fuente no soportada: {fuente}')
    resultado, motivo = validar_estructura(tokens, fuente)
    return resultado, motivo, tokens
