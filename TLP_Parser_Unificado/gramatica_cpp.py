"""Gramatica LL(1) de un subconjunto de C++.

Una tupla vacia () representa la producción vacía (ε).
"""
GRAMATICA_CPP = {
    'Programa': [('Instruccion', 'ListaInstrucciones', 'EOF')],
    'ListaInstrucciones': [('Instruccion', 'ListaInstrucciones'), ()],

    'Instruccion': [('Declaracion',), ('Asignacion',), ('Condicional',)],
    'Declaracion': [('Tipo', 'ID', 'Inicializacion', 'SEMI')],
    'Tipo': [('INT',), ('FLOAT',)],
    'Inicializacion': [('ASSIGN', 'Expresion'), ()],
    'Asignacion': [('ID', 'ASSIGN', 'Expresion', 'SEMI')],

    # Para evitar el problema del else ambiguo, exigimos bloques { }.
    'Condicional': [('IF', 'LPAREN', 'Condicion', 'RPAREN', 'Bloque', 'ElseOpcional')],
    'ElseOpcional': [('ELSE', 'Bloque'), ()],
    'Bloque': [('LBRACE', 'ListaInstrucciones', 'RBRACE')],
    'Condicion': [('Expresion', 'Comparador', 'Expresion')],
    'Comparador': [('GT',), ('LT',), ('GE',), ('LE',), ('EQ',), ('NE',)],

    # Precedencia: multiplicación/división antes que suma/resta.
    'Expresion': [('Termino', 'RestoExpresion')],
    'RestoExpresion': [('PLUS', 'Termino', 'RestoExpresion'),
                       ('MINUS', 'Termino', 'RestoExpresion'), ()],
    'Termino': [('Factor', 'RestoTermino')],
    'RestoTermino': [('TIMES', 'Factor', 'RestoTermino'),
                     ('DIVIDE', 'Factor', 'RestoTermino'), ()],
    'Factor': [('NUMBER',), ('ID',), ('LPAREN', 'Expresion', 'RPAREN'),
               ('MINUS', 'Factor')],
}
