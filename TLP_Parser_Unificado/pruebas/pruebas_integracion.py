"""Pruebas de la aplicación unificada y su salida de consola."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

import main
from parser_ll1 import ParserLL1


class PruebasIntegracion(TestCase):
    def salida(self, funcion, *args):
        buffer = StringIO()
        with redirect_stdout(buffer):
            resultado = funcion(*args)
        return resultado, buffer.getvalue()

    def test_ambos_modos_comparten_tipo_de_motor_y_tablas_sin_conflictos(self):
        self.assertIs(type(main.PARSER_CPP), ParserLL1)
        self.assertIs(type(main.PARSER_ES), ParserLL1)
        self.assertTrue(main.PARSER_CPP.tabla)
        self.assertTrue(main.PARSER_ES.tabla)

    def test_cpp_valido_e_invalido(self):
        valido, salida = self.salida(main.analizar_codigo, 'int edad = 20;')
        self.assertTrue(valido)
        self.assertIn('ACEPTADO', salida)
        self.assertIn('Programa', salida)
        self.assertIn("NUMBER ('20')", salida)
        invalido, salida = self.salida(main.analizar_codigo, 'int edad = ;')
        self.assertFalse(invalido)
        self.assertIn('RECHAZADO', salida)
        self.assertIn('Línea 1, columna', salida)

    def test_espanol_concordancia_y_modificadores(self):
        valido, salida = self.salida(main.analizar_oracion, 'La niña pequeña canta.')
        self.assertTrue(valido)
        self.assertIn('ACEPTADO', salida)
        self.assertIn('Oracion', salida)
        self.assertIn("SUST_FS ('niña')", salida)
        invalido, salida = self.salida(main.analizar_oracion, 'La niña pequeño canta.')
        self.assertFalse(invalido)
        self.assertIn('RECHAZADO', salida)
        frase = 'Los niños pequeños que juegan en el parque corren rápidamente.'
        valido, salida = self.salida(main.analizar_oracion, frase)
        self.assertTrue(valido)
        self.assertIn('RelativaPOpc', salida)
        self.assertIn('FrasePrepOpc', salida)
        self.assertIn("ADV ('rápidamente')", salida)

    def test_archivos_cpp_y_espanol(self):
        with TemporaryDirectory() as carpeta:
            ruta_cpp = Path(carpeta) / 'programa.cpp'
            ruta_cpp.write_text('int edad = 20;', encoding='utf-8')
            valido, salida = self.salida(main.analizar_archivo_cpp, ruta_cpp)
            self.assertTrue(valido)
            self.assertIn('Programa', salida)
            ruta_cpp.write_text('int edad = ;', encoding='utf-8')
            valido, salida = self.salida(main.analizar_archivo_cpp, ruta_cpp)
            self.assertFalse(valido)
            self.assertIn('RECHAZADO', salida)

            ruta_es = Path(carpeta) / 'oraciones.txt'
            ruta_es.write_text('# comentario\nLa niña pequeña canta.\n', encoding='utf-8')
            valido, salida = self.salida(main.analizar_archivo_es, ruta_es)
            self.assertTrue(valido)
            self.assertIn('Oracion', salida)

    def test_menu_permite_volver_y_analizar_de_nuevo(self):
        entradas = iter(['1', '1', 'int edad = 20;', 'FIN', 'SALIR',
                         '2', '1', 'La niña pequeña canta.', 'SALIR', '3'])
        with mock.patch('builtins.input', side_effect=entradas):
            codigo, salida = self.salida(main.main)
        self.assertEqual(codigo, 0)
        self.assertEqual(salida.count('ACEPTADO'), 2)
        self.assertIn('Programa', salida)
        self.assertIn('Oracion', salida)
        self.assertIn('Saliendo.', salida)
