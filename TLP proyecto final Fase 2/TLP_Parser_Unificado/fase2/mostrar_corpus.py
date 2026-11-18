"""Ejecuta el parser sobre el corpus y genera un informe detallado HTML/TXT.

Los arboles, tokens y errores se guardan en el documento. En consola solo se
imprime el resumen. Los logs originales no se modifican.
"""

import argparse
from pathlib import Path

from benchmark_parser import procesar_caso
from corpus_util import leer_corpus
from reporte_corpus import generar_reporte, mostrar_resumen

BASE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, default=BASE / 'corpus.csv')
    parser.add_argument('--salida', type=Path,
                        default=BASE / 'resultados' / 'analisis_corpus.html')
    parser.add_argument('--logs', type=Path, default=BASE / 'logs',
                        help='Carpeta con los resultados guardados de otros enfoques.')
    args = parser.parse_args()
    try:
        casos = leer_corpus(args.corpus)
        resultados = [procesar_caso(caso, incluir_arbol=True) for caso in casos]
        reporte = generar_reporte(casos, resultados, args.logs, args.salida,
                                  ruta_corpus=args.corpus)
        mostrar_resumen(reporte)
    except (OSError, ValueError) as error:
        parser.exit(2, f'ERROR: {error}\n')


if __name__ == '__main__':
    main()
