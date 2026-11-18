"""Pruebas locales para corpus, adaptadores y calculo de metricas."""
import csv
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
sys.path.insert(0, str(ROOT))
from corpus_util import leer_corpus
from benchmark_parser import procesar_caso
from evaluar import evaluar
from evaluar_pos import leer_referencia
from criterios_nlp import clasificar
from benchmark_llm_openai import EJEMPLOS_AJENOS


class PruebasFase2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.casos = leer_corpus(BASE / 'corpus.csv')

    def test_corpus_60_40_20(self):
        self.assertEqual(len(self.casos), 60)
        self.assertEqual(Counter(x['esperado_cfg'] for x in self.casos),
                         {'ACEPTADA': 40, 'RECHAZADA': 20})

    def test_20_por_nivel(self):
        self.assertEqual(Counter(x['nivel'] for x in self.casos),
                         {'1': 20, '2': 20, '3': 20})
        for nivel in ('1', '2', '3'):
            datos = [x for x in self.casos if x['nivel'] == nivel]
            self.assertIn('ACEPTADA', {x['esperado_cfg'] for x in datos})
            self.assertIn('RECHAZADA', {x['esperado_cfg'] for x in datos})

    def test_identificadores_unicos(self):
        self.assertEqual(len({c['id'] for c in self.casos}), 60)
        self.assertEqual(set(c['id'] for c in self.casos),
                         {f'{i:02d}' for i in range(1, 61)})

    def test_los_60_resultados_con_parser_original(self):
        salidas = [procesar_caso(c, incluir_arbol=False) for c in self.casos]
        self.assertEqual(sum(r['coincide_con_esperado'] for r in salidas), 60)
        self.assertEqual(sum(r['obtenido'] == 'ACEPTADA' for r in salidas), 40)

    def test_referencia_pos_alineada(self):
        from lexer_es_v3 import obtener_tokens_es_v3
        referencia = leer_referencia(BASE / 'referencia_pos.csv')
        self.assertEqual(len(referencia), 396)
        for caso in self.casos:
            tokens = obtener_tokens_es_v3(caso['oracion'])[:-1]
            for i, t in enumerate(tokens):
                clave = caso['id'], i
                self.assertIn(clave, referencia)
                self.assertEqual(referencia[clave]['texto'], t.texto)

    def test_few_shot_fuera_del_corpus(self):
        corpus = {c['oracion'].casefold() for c in self.casos}
        for oracion, _ in EJEMPLOS_AJENOS:
            self.assertNotIn(oracion.casefold(), corpus)

    def test_spacy_a_partir_de_anotaciones(self):
        tokens = [
            {'texto':'El','pos':'DET','morph':'Gender=Masc|Number=Sing','dep':'det','head_index':1},
            {'texto':'niño','pos':'NOUN','morph':'Gender=Masc|Number=Sing','dep':'nsubj','head_index':2},
            {'texto':'corre','pos':'VERB','morph':'Number=Sing|Tense=Pres','dep':'ROOT','head_index':2},
            {'texto':'.','pos':'PUNCT','morph':'','dep':'punct','head_index':2},
        ]
        self.assertEqual(clasificar(tokens, 'spacy')[0], 'ACEPTADA')

    def test_nltk_a_partir_de_etiquetas(self):
        tokens = [
            {'texto':'El','etiqueta_cess_esp':'da0ms0'},
            {'texto':'niño','etiqueta_cess_esp':'ncms000'},
            {'texto':'corre','etiqueta_cess_esp':'vmip3s0'},
            {'texto':'.','etiqueta_cess_esp':'Fp'},
        ]
        self.assertEqual(clasificar(tokens, 'nltk')[0], 'ACEPTADA')
        tokens[2]['etiqueta_cess_esp'] = 'SIN_ETIQUETA'
        self.assertEqual(clasificar(tokens, 'nltk')[0], 'RECHAZADA')

    def test_evaluacion_binaria(self):
        casos = [
            {'esperado_cfg':'ACEPTADA','obtenido':'ACEPTADA'},
            {'esperado_cfg':'ACEPTADA','obtenido':'RECHAZADA'},
            {'esperado_cfg':'RECHAZADA','obtenido':'ACEPTADA'},
            {'esperado_cfg':'RECHAZADA','obtenido':'RECHAZADA'},
        ]
        m=evaluar({'herramienta':'PRUEBA_UNIDAD','resultados':casos})
        self.assertEqual((m['tp'],m['fn'],m['fp'],m['tn']),(1,1,1,1))
        self.assertEqual(m['precision'],0.5)
        self.assertEqual(m['exactitud_balanceada'],0.5)

    def test_rechaza_corpus_incompleto(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'corpus.csv'
            with (BASE/'corpus.csv').open(encoding='utf-8-sig',newline='') as f:
                rows=list(csv.DictReader(f))
            with p.open('w',encoding='utf-8',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]))
                writer.writeheader();writer.writerows(rows[:-1])
            with self.assertRaises(ValueError):leer_corpus(p)


if __name__ == '__main__':
    unittest.main()
