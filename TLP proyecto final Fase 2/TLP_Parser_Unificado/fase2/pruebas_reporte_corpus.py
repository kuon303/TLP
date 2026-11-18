"""Verifica el informe del corpus sin llamadas a servicios externos."""

import tempfile
import unittest
from pathlib import Path

from benchmark_parser import procesar_caso
from corpus_util import leer_corpus
from reporte_corpus import (cargar_comparaciones, clase_resultado,
                            generar_reporte, resumen_matriz)

BASE = Path(__file__).resolve().parent


class PruebasReporteCorpus(unittest.TestCase):
    def test_clasificacion_de_resultados(self):
        self.assertEqual(clase_resultado('ACEPTADA', 'ACEPTADA'), 'TP')
        self.assertEqual(clase_resultado('RECHAZADA', 'RECHAZADA'), 'TN')
        self.assertEqual(clase_resultado('RECHAZADA', 'ACEPTADA'), 'FP')
        self.assertEqual(clase_resultado('ACEPTADA', 'RECHAZADA'), 'FN')

    def test_lee_solo_logs_alineados(self):
        casos = leer_corpus(BASE / 'corpus.csv')
        fuentes, avisos = cargar_comparaciones(casos, BASE / 'logs', BASE / 'corpus.csv')
        self.assertFalse(avisos)
        self.assertEqual(len(fuentes), 4)
        self.assertTrue(all(len(fuente) == 60 for _, fuente in fuentes))

    def test_analisis_real_con_arbol_y_resumen(self):
        casos = leer_corpus(BASE / 'corpus.csv')
        resultados = [procesar_caso(c) for c in casos]
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / 'analisis.html'
            reporte = generar_reporte(casos, resultados, BASE / 'logs', destino,
                                      ruta_corpus=BASE / 'corpus.csv')
            html = destino.read_text(encoding='utf-8')
            self.assertIn('El niño corre.', html)
            self.assertIn('Arbol sintactico generado por el parser', html)
            self.assertIn('Verdadero negativo', html)
            self.assertEqual(len(reporte['filas']), 5)
            self.assertEqual([r['FP'] for r in reporte['filas']], [0, 0, 0, 6, 4])
            self.assertEqual([r['FN'] for r in reporte['filas']], [0, 8, 20, 1, 1])
            self.assertTrue(destino.with_suffix('.txt').exists())

    def test_aceptacion_erronea_conserva_arbol(self):
        caso = {'id': 'E1', 'nivel': '1', 'oracion': 'El niño corre.',
                'esperado_cfg': 'RECHAZADA', 'correcta_espanol': 'SI'}
        resultado = procesar_caso(caso)
        self.assertEqual(resultado['obtenido'], 'ACEPTADA')
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / 'fp.html'
            reporte = generar_reporte([caso], [resultado], Path(tmp), destino)
            html = destino.read_text(encoding='utf-8')
            self.assertIn('Falso positivo: aceptada erroneamente', html)
            self.assertIn('Arbol sintactico generado por el parser', html)
            self.assertIn('SujetoMS', html)
            self.assertEqual(reporte['filas'][0]['FP'], 1)

    def test_rechazo_erroneo_muestra_fallo(self):
        caso = {'id': 'E2', 'nivel': '1', 'oracion': 'Los niño corre.',
                'esperado_cfg': 'ACEPTADA', 'correcta_espanol': 'NO'}
        resultado = procesar_caso(caso)
        self.assertEqual(resultado['obtenido'], 'RECHAZADA')
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / 'fn.html'
            reporte = generar_reporte([caso], [resultado], Path(tmp), destino)
            html = destino.read_text(encoding='utf-8')
            self.assertIn('Falso negativo: rechazada erroneamente', html)
            self.assertIn('Error exacto:', html)
            self.assertEqual(reporte['filas'][0]['FN'], 1)


if __name__ == '__main__':
    unittest.main()
