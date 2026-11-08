"""49 pruebas de regresión de los límites documentados del parser.

Incluye aceptaciones incorrectas de palabras reservadas en C++ (C10-C12).
"""
import csv
import unittest
from pathlib import Path

from main import PARSER_CPP, PARSER_ES
from lexer_cpp import obtener_tokens, ErrorLexico
from lexer_es_v3 import obtener_tokens_es_v3, ErrorLexicoEspanol
from parser_ll1 import ErrorSintactico

ARCHIVO = Path(__file__).resolve().parent.parent / 'evidencias_fallos' / 'Resultados_pruebas_limites_TLP.csv'
with ARCHIVO.open(encoding='utf-8-sig', newline='') as f:
    CASOS = list(csv.DictReader(f))

if len(CASOS) != 49:
    raise ValueError('La auditoría debe contener exactamente 49 casos.')

class PruebasLimitesParser(unittest.TestCase):
    """Ejecuta cada caso con el lexer correspondiente y el motor LL(1) compartido."""


def crear_prueba(caso):
    def prueba(self):
        if caso['lenguaje'] == 'Español':
            parser, lexer = PARSER_ES, obtener_tokens_es_v3
        else:
            parser, lexer = PARSER_CPP, obtener_tokens
        try:
            parser.analizar(lexer(caso['entrada']))
        except (ErrorLexico, ErrorLexicoEspanol, ErrorSintactico) as exc:
            resultado, error = 'RECHAZA', str(exc)
        else:
            resultado, error = 'ACEPTA', ''
        self.assertEqual(resultado, caso['resultado'],
                         f"{caso['id']}: {caso['entrada']}")
        self.assertEqual(error, caso['error'],
                         f"Cambió el mensaje de diagnóstico en {caso['id']}")
    prueba.__doc__ = f"{caso['id']} ({caso['lenguaje']}): {caso['fenomeno']}"
    return prueba

for c in CASOS:
    setattr(PruebasLimitesParser, 'test_'+c['id']+'_'+('es' if c['lenguaje']=='Español' else 'cpp'), crear_prueba(c))

if __name__ == '__main__':
    unittest.main(verbosity=2)
