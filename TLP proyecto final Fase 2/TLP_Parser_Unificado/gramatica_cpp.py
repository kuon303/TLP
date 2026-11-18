"""Gramatica LL(1) de un subconjunto de C++.

Las producciones vacias se representan con una tupla vacia ().
"""
GRAMATICA_CPP = {
    'Programa': [('Instruccion', 'ListaInstrucciones', 'EOF')],
    'ListaInstrucciones': [('Instruccion', 'ListaInstrucciones'), ()],

    'Instruccion': [('Declaracion',), ('Asignacion',), ('Condicional',)],
    'Declaracion': [('Tipo', 'ID', 'Inicializacion', 'SEMI')],
    'Tipo': [('INT',), ('FLOAT',)],
    'Inicializacion': [('ASSIGN', 'Expresion'), ()],
    'Asignacion': [('ID', 'ASSIGN', 'Expresion', 'SEMI')],

    # Los bloques obligatorios evitan el problema del else ambiguo.
    'Condicional': [('IF', 'LPAREN', 'Condicion', 'RPAREN', 'Bloque', 'ElseOpcional')],
    'ElseOpcional': [('ELSE', 'Bloque'), ()],
    'Bloque': [('LBRACE', 'ListaInstrucciones', 'RBRACE')],
    'Condicion': [('Expresion', 'Comparador', 'Expresion')],
    'Comparador': [('GT',), ('LT',), ('GE',), ('LE',), ('EQ',), ('NE',)],

    # La multiplicacion y division tienen prioridad sobre suma y resta.
    'Expresion': [('Termino', 'RestoExpresion')],
    'RestoExpresion': [('PLUS', 'Termino', 'RestoExpresion'),
                       ('MINUS', 'Termino', 'RestoExpresion'), ()],
    'Termino': [('Factor', 'RestoTermino')],
    'RestoTermino': [('TIMES', 'Factor', 'RestoTermino'),
                     ('DIVIDE', 'Factor', 'RestoTermino'), ()],
    'Factor': [('NUMBER',), ('ID',), ('LPAREN', 'Expresion', 'RPAREN'),
               ('MINUS', 'Factor')],
}
