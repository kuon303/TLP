
from pathlib import Path

from gramatica_cpp import GRAMATICA_CPP
from gramatica_es_v3 import GRAMATICA_ES_V3
from lexer_cpp import ErrorLexico, obtener_tokens
from lexer_es_v3 import ErrorLexicoEspanol, obtener_tokens_es_v3
from parser_ll1 import ErrorSintactico, ParserLL1, mostrar_arbol


PARSER_CPP = ParserLL1(GRAMATICA_CPP, 'Programa')
PARSER_ES = ParserLL1(GRAMATICA_ES_V3, 'Oracion')


def analizar_codigo(codigo: str, mostrar: bool = True) -> bool:
    try:
        arbol = PARSER_CPP.analizar(obtener_tokens(codigo))
    except (ErrorLexico, ErrorSintactico) as error:
        if mostrar:
            print('RECHAZADO:', error)
        return False
    if mostrar:
        print('ACEPTADO: el codigo cumple la gramatica de C++.')
        print('\nARBOL SINTACTICO:')
        print(mostrar_arbol(arbol))
    return True


def analizar_oracion(oracion: str, mostrar: bool = True) -> bool:
    try:
        arbol = PARSER_ES.analizar(obtener_tokens_es_v3(oracion))
    except (ErrorLexicoEspanol, ErrorSintactico) as error:
        if mostrar:
            print('RECHAZADO:', error)
        return False
    if mostrar:
        print('ACEPTADO: la oracion cumple la gramatica de español.')
        print('\nARBOL SINTACTICO:')
        print(mostrar_arbol(arbol))
    return True


def analizar_archivo_cpp(ruta: Path) -> bool:
    try:
        codigo = ruta.read_text(encoding='utf-8')
    except OSError as error:
        print('RECHAZADO: no se pudo leer el archivo:', error)
        return False
    print(f'Analizando archivo: {ruta}')
    return analizar_codigo(codigo)


def analizar_archivo_es(ruta: Path) -> bool:
    try:
        lineas = ruta.read_text(encoding='utf-8').splitlines()
    except OSError as error:
        print('RECHAZADO: no se pudo leer el archivo:', error)
        return False
    oraciones = [linea.strip() for linea in lineas
                 if linea.strip() and not linea.lstrip().startswith('#')]
    if not oraciones:
        print('El archivo no contiene oraciones para analizar.')
        return False
    resultados = []
    for numero, oracion in enumerate(oraciones, 1):
        print(f'\n--- ORACION {numero}: {oracion} ---')
        resultados.append(analizar_oracion(oracion))
    return all(resultados)


def leer_codigo_cpp() -> None:
    print('Entrada de C++ por lineas. FIN termina el bloque; SALIR regresa al menu.')
    while True:
        lineas = []
        while True:
            linea = input('cpp> ' if not lineas else '...  ')
            if not lineas and linea.strip().upper() == 'SALIR':
                return
            if linea.strip() == 'FIN':
                break
            lineas.append(linea)
        if not any(linea.strip() for linea in lineas):
            print('Entrada vacia. No se analizo codigo.')
            continue
        analizar_codigo('\n'.join(lineas))


def leer_oraciones() -> None:
    print('Entrada de español: una oracion por linea. SALIR regresa al menu.')
    while True:
        oracion = input('es> ').strip()
        if oracion.upper() == 'SALIR':
            return
        if oracion:
            analizar_oracion(oracion)


def main() -> int:
    try:
        while True:
            print('\nPARSER LL(1) - C++ Y ESPANOL')
            print('1. Analizar C++')
            print('2. Analizar español')
            print('3. Salir')
            opcion = input('Opcion: ').strip()
            if opcion == '3':
                print('Saliendo.')
                return 0
            if opcion not in ('1', '2'):
                print('Opcion no valida.')
                continue
            print('1. Escribir entrada')
            print('2. Leer archivo ' + ('.cpp' if opcion == '1' else '.txt'))
            print('3. Volver al menú')
            accion = input('Opcion: ').strip()
            if accion == '1':
                (leer_codigo_cpp if opcion == '1' else leer_oraciones)()
            elif accion == '2':
                ruta = Path(input('Ruta del archivo: ').strip())
                (analizar_archivo_cpp if opcion == '1' else analizar_archivo_es)(ruta)
            elif accion != '3':
                print('Opcion no valida.')
    except (EOFError, KeyboardInterrupt):
        print('\nSaliendo.')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
