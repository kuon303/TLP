"""Comprueba que el vocabulario ampliado funciona sin cambiar la gramática LL(1)."""
import unittest

from main import analizar_codigo, analizar_oracion
from lexer_es_v3 import obtener_tokens_es_v3
from vocabulario_es import VOCABULARIO


ACEPTADAS = (
    'El carro corre.', 'Los carros corren.',
    'Un carro rojo avanza.', 'Unos carros rojos avanzan.',
    'La niña come.', 'Las niñas comen.',
    'Una mujer trabaja.', 'Unas mujeres trabajan.',
    'El estudiante estudia.', 'La estudiante estudia.',
    'Los estudiantes estudian.', 'Las estudiantes estudian.',
    'El joven canta.', 'La joven canta.',
    'El niño joven canta.', 'La niña joven canta.',
    'La cocina funciona.', 'La niña cocina.',
    'La niña pregunta.', 'La pregunta aparece.',
    'El problema existe.', 'La mano funciona.',
    'El profesor enseña.', 'La profesora enseña.',
    'La universidad funciona.', 'El niño corre hoy.',
    'La niña camina velozmente.',
    'Los vehículos nuevos circulan rápidamente en las ciudades.',
    'Un doctor trabaja en el hospital.',
    'Las mariposas bonitas vuelan lentamente.',
    'Los perros felices juegan en el jardín.',
    'El carro corre en la ciudad.',
    'Las profesoras que enseñan trabajan tranquilamente.',
)

RECHAZADAS = (
    'La carro corre.', 'El carros corre.', 'Las carros corren.',
    'Los niñas corren.', 'Unas perro duerme.',
    'El carro corren.', 'Las niñas come.',
    'La niña pequeño canta.', 'Los vehículos nueva circulan.',
    'La niña canta y baila.', 'Corre el carro.',
    'El carro rápido rojo avanza.',
)


class PruebasVocabularioEspanol(unittest.TestCase):
    def test_tamano_y_categorias(self):
        self.assertGreaterEqual(len(VOCABULARIO), 1500)
        self.assertIn('SUST_MS', VOCABULARIO['carro'])
        self.assertIn('SUST_MP', VOCABULARIO['carros'])
        self.assertIn('VERBO_S', VOCABULARIO['avanza'])
        self.assertIn('ADV', VOCABULARIO['velozmente'])

    def test_acepta_nuevo_vocabulario(self):
        for oracion in ACEPTADAS:
            with self.subTest(oracion=oracion):
                self.assertTrue(analizar_oracion(oracion, mostrar=False))

    def test_mantiene_concordancia_y_limites_de_gramatica(self):
        for oracion in RECHAZADAS:
            with self.subTest(oracion=oracion):
                self.assertFalse(analizar_oracion(oracion, mostrar=False))

    def test_distingue_palabras_compartidas(self):
        ejemplos = {
            'El estudiante camina.': 'SUST_MS',
            'La estudiante camina.': 'SUST_FS',
            'Las estudiantes caminan.': 'SUST_FP',
            'Los estudiantes caminan.': 'SUST_MP',
            'La cocina funciona.': 'SUST_FS',
            'La niña cocina.': 'VERBO_S',
            'La niña joven canta.': 'ADJ_COMUN_S',
            'La joven canta.': 'SUST_FS',
        }
        for texto, categoria in ejemplos.items():
            with self.subTest(texto=texto):
                self.assertIn(categoria, [t.tipo for t in obtener_tokens_es_v3(texto)])

    def test_cpp_no_cambia(self):
        self.assertTrue(analizar_codigo('int edad = 20;', mostrar=False))
        self.assertFalse(analizar_codigo('int edad = ;', mostrar=False))


if __name__ == '__main__':
    unittest.main()
