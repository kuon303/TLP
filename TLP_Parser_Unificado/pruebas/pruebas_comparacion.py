"""Pruebas del conjunto y la exportación; no requiere spaCy instalado."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from comparar_spacy import BASE, analizar_con_nuestro_parser, ejecutar


class PruebasComparacion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.casos = json.loads((BASE / 'casos_comparacion_es.json').read_text(encoding='utf-8'))

    def test_33_casos_reproducen_resultados_esperados(self):
        self.assertEqual(len(self.casos), 33)
        for caso in self.casos:
            with self.subTest(caso=caso['id']):
                self.assertEqual(analizar_con_nuestro_parser(caso['oracion'])['acepta'], caso['esperado_parser'])

    def test_ejecutar_solo_parser_exporta_resultados_sin_fingir_spacy(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = SimpleNamespace(
                casos=BASE/'casos_comparacion_es.json',salida=Path(tmp),
                modelo='es_core_news_sm',solo_parser=True,arboles=True)
            self.assertEqual(ejecutar(args), 0)
            with (Path(tmp)/'preliminar_parser.csv').open(encoding='utf-8-sig',newline='') as f:
                filas=list(csv.DictReader(f))
            self.assertEqual(len(filas), 33)
            self.assertTrue(all(fila['spacy_estado']=='NO_EJECUTADO' for fila in filas))
            self.assertTrue((Path(tmp)/'preliminar_parser_arboles.txt').exists())


if __name__ == '__main__':
    unittest.main()
