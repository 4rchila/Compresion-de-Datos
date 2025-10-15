import heapq
from collections import Counter
import pickle

class NodoHuffman:
    def __init__(self, caracter, frecuencia):
        self.caracter = caracter
        self.frecuencia = frecuencia
        self.izq = None
        self.der = None

    def __lt__(self, otro):
        return self.frecuencia < otro.frecuencia


def construir_arbol(texto):
    frecuencias = Counter(texto)
    heap = [NodoHuffman(char, freq) for char, freq in frecuencias.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        nodo1 = heapq.heappop(heap)
        nodo2 = heapq.heappop(heap)
        nuevo = NodoHuffman(None, nodo1.frecuencia + nodo2.frecuencia)
        nuevo.izq = nodo1
        nuevo.der = nodo2
        heapq.heappush(heap, nuevo)

    return heap[0]


def generar_codigos(nodo, codigo_actual="", codigos=None):
    if codigos is None:
        codigos = {}

    if nodo is None:
        return codigos

    if nodo.caracter is not None:
        codigos[nodo.caracter] = codigo_actual
        return codigos

    generar_codigos(nodo.izq, codigo_actual + "0", codigos)
    generar_codigos(nodo.der, codigo_actual + "1", codigos)
    return codigos


def comprimir_texto(texto):
    arbol = construir_arbol(texto)
    codigos = generar_codigos(arbol)
    texto_codificado = ''.join(codigos[char] for char in texto)
    return texto_codificado, codigos
