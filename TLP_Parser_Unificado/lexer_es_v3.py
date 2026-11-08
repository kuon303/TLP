"""Lexer del subconjunto de español.

Clasifica palabras según el vocabulario organizado en vocabulario_es.py.
"""
import re
from parser_ll1 import Token
from vocabulario_es import VOCABULARIO

PATRON = re.compile(r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+|\.')


def _tipo_contextual(palabra: str, tokens: list[Token]) -> str:
    opciones = VOCABULARIO.get(palabra.casefold(), ('DESCONOCIDA',))
    if len(opciones) == 1:
        return opciones[0]

    anterior = tokens[-1].tipo if tokens else None
    if anterior and anterior.startswith('ART_'):
        sustantivo = anterior.replace('ART_', 'SUST_')
        if sustantivo in opciones:
            return sustantivo
    if anterior and anterior.startswith('SUST_'):
        if anterior.endswith('MS'):
            preferidas = ('ADJ_MS', 'ADJ_COMUN_S')
        elif anterior.endswith('FS'):
            preferidas = ('ADJ_FS', 'ADJ_COMUN_S')
        elif anterior.endswith('MP'):
            preferidas = ('ADJ_MP', 'ADJ_COMUN_P')
        else:
            preferidas = ('ADJ_FP', 'ADJ_COMUN_P')
        for categoria in preferidas:
            if categoria in opciones:
                return categoria
    for categoria in ('VERBO_S', 'VERBO_P'):
        if categoria in opciones:
            return categoria
    return opciones[0]


class ErrorLexicoEspanol(Exception):
    """Caracter no reconocido por el lexer."""


def obtener_tokens_es_v3(oracion: str) -> list[Token]:
    tokens = []
    posicion, linea, columna = 0, 1, 1
    while posicion < len(oracion):
        caracter = oracion[posicion]
        if caracter.isspace():
            if caracter == '\n':
                linea, columna = linea + 1, 1
            else:
                columna += 1
            posicion += 1
            continue
        match = PATRON.match(oracion, posicion)
        if match is None:
            raise ErrorLexicoEspanol(
                f'Línea {linea}, columna {columna}: carácter no reconocido {caracter!r}.'
            )
        texto = match.group()
        tipo = 'PUNTO' if texto == '.' else _tipo_contextual(texto, tokens)
        tokens.append(Token(tipo, texto, linea, columna))
        posicion = match.end()
        columna += len(texto)
    tokens.append(Token('EOF', '$', linea, columna))
    return tokens
