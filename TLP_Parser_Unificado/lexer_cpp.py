"""Analizador léxico del subconjunto de C++ mediante expresiones regulares."""
import re
from parser_ll1 import Token


class ErrorLexico(Exception):
    pass


# El orden importa: '==' debe revisarse antes de '='.
PATRONES = [
    ('COMENTARIO_BLOQUE', r'/\*[\s\S]*?\*/'),
    ('COMENTARIO_LINEA', r'//[^\n]*'),
    ('ESPACIOS', r'[ \t\r]+'),
    ('SALTO', r'\n'),
    ('NUMBER', r'\d+(?:\.\d+)?'),
    ('ID', r'[A-Za-z_][A-Za-z0-9_]*'),
    ('GE', r'>='), ('LE', r'<='), ('EQ', r'=='), ('NE', r'!='),
    ('ASSIGN', r'='), ('GT', r'>'), ('LT', r'<'),
    ('PLUS', r'\+'), ('MINUS', r'-'),
    ('TIMES', r'\*'), ('DIVIDE', r'/'),
    ('LPAREN', r'\('), ('RPAREN', r'\)'),
    ('LBRACE', r'\{'), ('RBRACE', r'\}'),
    ('SEMI', r';'),
]
REGEX = re.compile('|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in PATRONES))
PALABRAS_RESERVADAS = {'int': 'INT', 'float': 'FLOAT', 'if': 'IF', 'else': 'ELSE'}
IGNORADOS = {'ESPACIOS', 'SALTO', 'COMENTARIO_LINEA', 'COMENTARIO_BLOQUE'}


def obtener_tokens(codigo: str) -> list[Token]:
    tokens = []
    pos = 0
    linea = 1
    columna = 1

    while pos < len(codigo):
        match = REGEX.match(codigo, pos)
        if match is None:
            raise ErrorLexico(
                f'Línea {linea}, columna {columna}: carácter no válido {codigo[pos]!r}.'
            )

        tipo = match.lastgroup
        texto = match.group()
        if tipo not in IGNORADOS:
            if tipo == 'ID':
                tipo = PALABRAS_RESERVADAS.get(texto, 'ID')
            tokens.append(Token(tipo, texto, linea, columna))

        saltos = texto.count('\n')
        if saltos:
            linea += saltos
            columna = len(texto) - texto.rfind('\n')
        else:
            columna += len(texto)
        pos = match.end()

    tokens.append(Token('EOF', '$', linea, columna))
    return tokens
