"""Pruebas de Gemini sin llamadas a la API."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import benchmark_llm_gemini as gemini
from benchmark_llm_openai import sha
from corpus_util import leer_corpus


class RespuestaSimulada:
    def __init__(self, texto):
        self.text = texto

    def model_dump(self, mode='json', exclude_none=True):
        return {'candidates': [{'content': {'parts': [{'text': self.text}]}}],
                'usage_metadata': {'prompt_token_count': 123}}


class ClienteSimulado:
    def __init__(self, fallar=False):
        self.llamadas = 0
        self.fallar = fallar
        self.models = self

    def generate_content(self, model, contents, config):
        self.llamadas += 1
        if self.fallar:
            raise RuntimeError('Fallo simulado')
        return RespuestaSimulada('{"resultado":{"oracion":' + json.dumps(contents.removeprefix("Oracion: "), ensure_ascii=False) + ' ,"resultado":"ACEPTADA","razon":"Cumple la CFG."}}')


class PruebasGemini(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.casos = leer_corpus(Path(gemini.BASE) / 'corpus.csv')
        self.corpus_hash = sha((Path(gemini.BASE) / 'corpus.csv').read_bytes())

    def correr(self, cliente, limite=1, modo='zero_shot'):
        with patch.object(gemini, 'BASE', self.base), patch.object(
            gemini, 'config_gemini', return_value=object()
        ), patch.object(gemini.time, 'sleep'):
            return gemini.ejecutar_modo(modo, 'modelo-prueba', self.casos,
                                       self.corpus_hash, limite, 0, 0, 1024,
                                       cliente, 'clave-ficticia')

    def test_formato_json(self):
        correcto = json.dumps({'resultado': {
            'oracion': 'El niño lee el libro.', 'resultado': 'RECHAZADA',
            'razon': 'La CFG no admite objetos directos.'}}, ensure_ascii=False)
        self.assertEqual(gemini.parsear_respuesta(correcto, 'El niño lee el libro.'),
                         ('RECHAZADA', 'La CFG no admite objetos directos.'))
        self.assertEqual(gemini.parsear_respuesta(correcto, 'Otra oracion.'), (None, None))
        self.assertEqual(gemini.parsear_respuesta('{"resultado":"ACEPTADA"}'), (None, None))

    def test_prompt_contiene_gramatica_y_ejemplos_aparte(self):
        zero = gemini.instrucciones_gemini('zero_shot')
        few = gemini.instrucciones_gemini('few_shot')
        self.assertIn('REGLAS DE PRODUCCION DE LA CFG', zero)
        self.assertIn('VOCABULARIO LEXICO', zero)
        self.assertNotIn('EJEMPLOS RESUELTOS', zero)
        self.assertIn('EJEMPLOS RESUELTOS', few)
        self.assertIn('\"razon\"', few)
        self.assertIn('\"oracion\"', zero)

    def test_guarda_log_y_reanuda(self):
        cliente = ClienteSimulado()
        self.assertTrue(self.correr(cliente))
        self.assertEqual(cliente.llamadas, 1)
        crudo = self.base/'logs'/'gemini_zero_shot.jsonl'
        resumen = self.base/'logs'/'llm_zero_shot.json'
        self.assertTrue(crudo.is_file())
        self.assertEqual(len(crudo.read_text(encoding='utf-8').splitlines()), 1)
        resultado = json.loads(resumen.read_text(encoding='utf-8'))
        self.assertEqual(resultado['tipo_resultado'], 'respuestas_llm_incompletas')
        self.assertEqual(resultado['resultados'][0]['obtenido'], 'ACEPTADA')
        self.assertTrue(self.correr(cliente))
        self.assertEqual(cliente.llamadas, 2)
        self.assertEqual(len(crudo.read_text(encoding='utf-8').splitlines()), 2)
        self.assertNotIn('clave-ficticia', crudo.read_text(encoding='utf-8'))
        compacto = json.loads((self.base/'resultados'/'gemini_zero_shot_respuestas.json').read_text(encoding='utf-8'))
        self.assertEqual(compacto['resultados'][0]['resultado']['resultado'], 'ACEPTADA')

    def test_respalda_formato_anterior(self):
        carpeta = self.base / 'logs'
        carpeta.mkdir()
        anterior = carpeta / 'llm_zero_shot.json'
        anterior.write_text(json.dumps({
            'herramienta': 'Gemini API - modelo-prueba - zero_shot',
            'metadatos': {'modelo': 'modelo-prueba', 'modo': 'zero_shot',
                          'corpus_sha256': self.corpus_hash,
                          'configuracion_sha256': 'formato-anterior'},
            'resultados': [],
        }), encoding='utf-8')
        bruto = carpeta / 'gemini_zero_shot.jsonl'
        bruto.write_text(json.dumps({
            'proveedor': 'Gemini', 'modelo': 'modelo-prueba',
            'corpus_sha256': self.corpus_hash,
            'instrucciones_sha256': 'prompt-viejo',
            'configuracion_sha256': 'formato-anterior',
        }) + '\n', encoding='utf-8')
        self.assertTrue(self.correr(ClienteSimulado()))
        respaldos = list((carpeta / 'historico').iterdir())
        self.assertEqual(len(respaldos), 2)
        self.assertTrue(anterior.exists())
        self.assertEqual(len(bruto.read_text(encoding='utf-8').splitlines()), 1)

    def test_registra_error_y_detiene(self):
        cliente = ClienteSimulado(fallar=True)
        self.assertFalse(self.correr(cliente))
        datos = json.loads((self.base/'logs'/'gemini_zero_shot.jsonl').read_text(encoding='utf-8'))
        self.assertIn('Fallo simulado', datos['error_api'])
        self.assertIsNone(datos['resultado_cfg'])

    def test_protege_log_de_otro_proveedor(self):
        carpeta = self.base/'logs'
        carpeta.mkdir()
        ruta = carpeta/'llm_zero_shot.json'
        ruta.write_text(json.dumps({'herramienta':'OpenAI API', 'metadatos':{}}),encoding='utf-8')
        with self.assertRaises(ValueError):
            self.correr(ClienteSimulado())


if __name__ == '__main__':
    unittest.main()
