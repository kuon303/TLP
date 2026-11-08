"""Motor predictivo LL(1) compartido por C++ y español.
"""
from dataclasses import dataclass, field

VACIO = 'vacia'  # Símbolo para una producción vacía (ε).


@dataclass
class Token:
    tipo: str
    texto: str
    linea: int
    columna: int


@dataclass
class Nodo:
    simbolo: str
    texto: str = ''
    hijos: list['Nodo'] = field(default_factory=list)


def mostrar_arbol(nodo: Nodo) -> str:
    """Convierte el árbol sintáctico en texto con ramas."""
    def etiqueta(actual: Nodo) -> str:
        if actual.texto:
            return f'{actual.simbolo} ({actual.texto!r})'
        return actual.simbolo

    lineas = [etiqueta(nodo)]

    def visitar(actual: Nodo, prefijo: str) -> None:
        for i, hijo in enumerate(actual.hijos):
            ultimo = (i == len(actual.hijos) - 1)
            lineas.append(prefijo + ('└── ' if ultimo else '├── ') + etiqueta(hijo))
            visitar(hijo, prefijo + ('    ' if ultimo else '│   '))

    visitar(nodo, '')
    return '\n'.join(lineas)


class ErrorSintactico(Exception):
    pass


class ParserLL1:
    def __init__(self, gramatica: dict[str, list[tuple[str, ...]]], inicial: str):
        # Cada no terminal tiene una lista de producciones alternativas.
        self.gramatica = gramatica
        self.inicial = inicial
        self.no_terminales = set(gramatica)
        if inicial not in self.no_terminales:
            raise ValueError('El símbolo inicial no pertenece a la gramática')

        self.primeros = self._calcular_primeros()
        self.siguientes = self._calcular_siguientes()
        self.tabla = self._construir_tabla()

    def _primeros_secuencia(self, secuencia: tuple[str, ...]) -> set[str]:
        """FIRST de una secuencia de símbolos."""
        if not secuencia:
            return {VACIO}
        resultado = set()
        for simbolo in secuencia:
            if simbolo in self.no_terminales:
                primeros_simbolo = self.primeros[simbolo]
            else:
                primeros_simbolo = {simbolo}
            resultado.update(primeros_simbolo - {VACIO})
            if VACIO not in primeros_simbolo:
                return resultado
        resultado.add(VACIO)
        return resultado

    def _calcular_primeros(self) -> dict[str, set[str]]:
        self.primeros = {nt: set() for nt in self.no_terminales}
        cambio = True
        while cambio:
            cambio = False
            for nt, alternativas in self.gramatica.items():
                for produccion in alternativas:
                    nuevos = self._primeros_secuencia(produccion) - self.primeros[nt]
                    if nuevos:
                        self.primeros[nt].update(nuevos)
                        cambio = True
        return self.primeros

    def _calcular_siguientes(self) -> dict[str, set[str]]:
        siguientes = {nt: set() for nt in self.no_terminales}
        siguientes[self.inicial].add('EOF')
        cambio = True
        while cambio:
            cambio = False
            for izquierda, alternativas in self.gramatica.items():
                for produccion in alternativas:
                    for i, simbolo in enumerate(produccion):
                        if simbolo not in self.no_terminales:
                            continue
                        resto = produccion[i + 1:]
                        primeros_resto = self._primeros_secuencia(resto)
                        agregar = primeros_resto - {VACIO}
                        if VACIO in primeros_resto:
                            agregar = agregar | siguientes[izquierda]
                        nuevos = agregar - siguientes[simbolo]
                        if nuevos:
                            siguientes[simbolo].update(nuevos)
                            cambio = True
        return siguientes

    def _construir_tabla(self) -> dict[tuple[str, str], tuple[str, ...]]:
        tabla = {}
        for nt, alternativas in self.gramatica.items():
            for produccion in alternativas:
                primeros = self._primeros_secuencia(produccion)
                terminales = primeros - {VACIO}
                if VACIO in primeros:
                    terminales = terminales | self.siguientes[nt]
                for terminal in terminales:
                    clave = (nt, terminal)
                    if clave in tabla and tabla[clave] != produccion:
                        raise ValueError(
                            f'La gramática NO es LL(1): conflicto en {clave}: '
                            f'{tabla[clave]} contra {produccion}'
                        )
                    tabla[clave] = produccion
        return tabla

    def analizar(self, tokens: list[Token]) -> Nodo:
        """Analiza tokens usando la pila + tabla LL(1) y construye árbol."""
        if not tokens or tokens[-1].tipo != 'EOF':
            raise ValueError('La secuencia de tokens debe terminar en EOF')
        raiz = Nodo(self.inicial)
        pila = [(self.inicial, raiz)]
        posicion = 0

        while pila:
            simbolo, nodo = pila.pop()
            actual = tokens[min(posicion, len(tokens) - 1)]

            if simbolo not in self.no_terminales:
                if simbolo != actual.tipo:
                    raise ErrorSintactico(
                        f'Línea {actual.linea}, columna {actual.columna}: '
                        f'se esperaba {simbolo}, pero apareció '
                        f'{actual.tipo} ({actual.texto!r}).'
                    )
                nodo.texto = actual.texto
                posicion += 1
                continue

            produccion = self.tabla.get((simbolo, actual.tipo))
            if produccion is None:
                esperados = sorted(t for (nt, t) in self.tabla if nt == simbolo)
                raise ErrorSintactico(
                    f'Línea {actual.linea}, columna {actual.columna}: '
                    f'no se puede analizar {simbolo} cuando aparece '
                    f'{actual.tipo} ({actual.texto!r}). '
                    f'Tokens esperados: {", ".join(esperados)}.'
                )

            if not produccion:
                nodo.hijos.append(Nodo(VACIO))
                continue

            nodo.hijos = [Nodo(s) for s in produccion]
            for hijo in reversed(nodo.hijos):
                pila.append((hijo.simbolo, hijo))

        if posicion != len(tokens):
            actual = tokens[min(posicion, len(tokens) - 1)]
            raise ErrorSintactico(
                f'Línea {actual.linea}, columna {actual.columna}: '
                'sobran tokens al terminar el análisis.'
            )
        return raiz
