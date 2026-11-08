"""Casos válidos e inválidos. Ejecutar: py -3.13 -m unittest -v"""
import unittest

from lexer_cpp import obtener_tokens, ErrorLexico
from parser_ll1 import ParserLL1, ErrorSintactico
from gramatica_cpp import GRAMATICA_CPP


class PruebasCPP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = ParserLL1(GRAMATICA_CPP, 'Programa')

    def validar(self, codigo):
        return self.parser.analizar(obtener_tokens(codigo))

    def test_declaracion_int(self):
        self.validar('int edad = 20;')

    def test_declaracion_float_decimal(self):
        self.validar('float promedio = 8.5;')

    def test_declaracion_sin_inicializar(self):
        self.validar('int contador;')

    def test_asignacion(self):
        self.validar('x = 3;')

    def test_precedencia_operaciones(self):
        self.validar('x = (a + b) * 2 - 7 / 3;')

    def test_numeros_negativos(self):
        self.validar('x = -12 + -b;')

    def test_varias_instrucciones_y_comentarios(self):
        self.validar('int a=1; // comentario\na=a+2; /* otro comentario */')

    def test_if_else(self):
        self.validar('if (a >= 18) { int x=2; } else { x=0; }')

    def test_if_anidado(self):
        self.validar('if (x != 0) { if (y < 3) { x = 4; } }')

    def test_seis_comparadores(self):
        for comparador in ('<', '>', '<=', '>=', '==', '!='):
            with self.subTest(comparador=comparador):
                self.validar(f'if (x {comparador} 10) {{ x=2; }}')

    def test_rechaza_declaracion_sin_valor(self):
        with self.assertRaises(ErrorSintactico):
            self.validar('int edad = ;')

    def test_rechaza_identificador_ausente(self):
        with self.assertRaises(ErrorSintactico):
            self.validar('int = 20;')

    def test_rechaza_sin_punto_coma(self):
        with self.assertRaises(ErrorSintactico):
            self.validar('int x = 4')

    def test_rechaza_expresion_incompleta(self):
        with self.assertRaises(ErrorSintactico):
            self.validar('x = a + ;')

    def test_rechaza_if_sin_condicion_completa(self):
        with self.assertRaises(ErrorSintactico):
            self.validar('if (x >) { x = 1; }')

    def test_rechaza_if_sin_llaves(self):
        with self.assertRaises(ErrorSintactico):
            self.validar('if (x > 5) x = 1;')

    def test_rechaza_entrada_vacia(self):
        with self.assertRaises(ErrorSintactico):
            self.validar('')

    def test_rechaza_caracter_no_valido(self):
        with self.assertRaises(ErrorLexico):
            self.validar('int x = @;')

    def test_rechaza_caracteres_ajenos(self):
        with self.assertRaises(ErrorSintactico):
            self.validar('cout << x;')


if __name__ == '__main__':
    unittest.main()
