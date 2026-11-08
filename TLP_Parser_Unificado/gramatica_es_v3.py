"""Gramatica LL(1) del subconjunto de español.

Incluye concordancia, relativas de sujeto y modificadores opcionales.
Una tupla vacia () representa una produccion vacia (ε).
"""
GRAMATICA_ES_V3 = {
    'Oracion': [
        ('SujetoMS', 'PredicadoS', 'PuntoOpcional', 'EOF'),
        ('SujetoFS', 'PredicadoS', 'PuntoOpcional', 'EOF'),
        ('SujetoMP', 'PredicadoP', 'PuntoOpcional', 'EOF'),
        ('SujetoFP', 'PredicadoP', 'PuntoOpcional', 'EOF'),
    ],
    # El articulo inicial determina que regla de genero y numero usar.
    'SujetoMS': [('ART_MS', 'SUST_MS', 'AdjetivoMSOpc', 'RelativaSOpc')],
    'SujetoFS': [('ART_FS', 'SUST_FS', 'AdjetivoFSOpc', 'RelativaSOpc')],
    'SujetoMP': [('ART_MP', 'SUST_MP', 'AdjetivoMPOpc', 'RelativaPOpc')],
    'SujetoFP': [('ART_FP', 'SUST_FP', 'AdjetivoFPOpc', 'RelativaPOpc')],
    # Adjetivos con concordancia de genero y numero, o comunes en genero.
    'AdjetivoMSOpc': [('ADJ_MS',), ('ADJ_COMUN_S',), ()],
    'AdjetivoFSOpc': [('ADJ_FS',), ('ADJ_COMUN_S',), ()],
    'AdjetivoMPOpc': [('ADJ_MP',), ('ADJ_COMUN_P',), ()],
    'AdjetivoFPOpc': [('ADJ_FP',), ('ADJ_COMUN_P',), ()],
    # La relativa de sujeto conserva el numero del antecedente.
    'RelativaSOpc': [('QUE', 'VERBO_S', 'AdverbioOpc', 'FrasePrepOpc'), ()],
    'RelativaPOpc': [('QUE', 'VERBO_P', 'AdverbioOpc', 'FrasePrepOpc'), ()],
    'PredicadoS': [('VERBO_S', 'AdverbioOpc', 'FrasePrepOpc')],
    'PredicadoP': [('VERBO_P', 'AdverbioOpc', 'FrasePrepOpc')],
    'AdverbioOpc': [('ADV',), ()],
    'FrasePrepOpc': [('PREP', 'SintagmaNominal'), ()],
    # El sintagma nominal preposicional mantiene concordancia, sin relativas.
    'SintagmaNominal': [('NominalMS',), ('NominalFS',), ('NominalMP',), ('NominalFP',)],
    'NominalMS': [('ART_MS', 'SUST_MS', 'AdjetivoMSOpc')],
    'NominalFS': [('ART_FS', 'SUST_FS', 'AdjetivoFSOpc')],
    'NominalMP': [('ART_MP', 'SUST_MP', 'AdjetivoMPOpc')],
    'NominalFP': [('ART_FP', 'SUST_FP', 'AdjetivoFPOpc')],
    'PuntoOpcional': [('PUNTO',), ()],
}
