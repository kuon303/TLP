"""Pruebas de la gramática V3 usada por la aplicación principal."""
import unittest
from main import analizar_oracion, PARSER_ES
from lexer_es_v3 import obtener_tokens_es_v3

VALIDAS = (
    'El niño corre.', 'La niña canta.', 'Los niños corren.',
    'Las niñas cantan.', 'El niño pequeño corre.',
    'La niña pequeña canta.', 'Los niños pequeños corren.',
    'Las niñas pequeñas cantan.', 'El perro grande duerme.',
    'Las perras grandes duermen.',
    'El niño que juega corre.', 'Las niñas que cantan corren.',
    'Los niños pequeños que juegan corren.',
    'La niña pequeña que canta camina.',
    'La niña camina rápidamente.', 'Los niños corren lentamente.',
    'El niño corre en el parque.', 'La niña camina por la escuela.',
    'El niño juega con la niña pequeña.',
    'Los niños pequeños que juegan en el parque corren rápidamente.',
    'Las niñas grandes que caminan por el parque cantan tranquilamente.',
    'El niño que canta alegremente corre con el perro.',
    'El perro grande corre', 'LA NIÑA PEQUEÑA CANTA.',
    'La niña camina velozmente.',
)
INVALIDAS = (
    'La niño corre.', 'Los niño corre.', 'La niña cantan.',
    'Las niñas canta.', 'La niña pequeño canta.', 'El niño pequeña corre.',
    'Los niños pequeña corren.', 'Las niñas pequeños cantan.',
    'El perro grandes duerme.', 'Las perras grande duermen.',
    'El niño que juegan corre.', 'Los niños que juega corren.',
    'La niña que canta corren.', 'Las niñas que canta corren.',
    'El niño que corre cantan.',
    'El niño corre en la parque.', 'La niña canta con el perra.',
    'El niño corre en el parque con la niña.',  # solo una PP en V3
    'El niño corre rápidamente lentamente.',  # solo un ADV en V3
    'El niño corre?', 'Niño el corre.', 'El niño.',
)

class PruebasEspanolV3(unittest.TestCase):
    def test_acepta_oraciones_del_subconjunto(self):
        for texto in VALIDAS:
            with self.subTest(texto=texto):
                self.assertTrue(analizar_oracion(texto, mostrar=False))

    def test_rechaza_errores_y_fuera_de_alcance(self):
        for texto in INVALIDAS:
            with self.subTest(texto=texto):
                self.assertFalse(analizar_oracion(texto, mostrar=False))

    def test_reutiliza_motor_predictivo_ll1(self):
        self.assertGreater(len(PARSER_ES.tabla), 0)
        self.assertEqual(PARSER_ES.inicial, 'Oracion')

    def test_lexer_conserva_concordancia_y_modificadores(self):
        tokens = obtener_tokens_es_v3('Las niñas grandes que cantan corren rápidamente.')
        self.assertEqual([t.tipo for t in tokens], [
            'ART_FP', 'SUST_FP', 'ADJ_COMUN_P', 'QUE',
            'VERBO_P', 'VERBO_P', 'ADV', 'PUNTO', 'EOF'])

if __name__ == '__main__':
    unittest.main()
