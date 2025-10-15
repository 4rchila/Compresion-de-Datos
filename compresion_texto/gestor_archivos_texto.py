import pickle
from compresion_texto import hyffman

class NodoHuffman:
    def __init__(self, caracter, frecuencia):
        self.caracter = caracter
        self.frecuencia = frecuencia
        self.izq = None
        self.der = None

    def __lt__(self, otro):
        return self.frecuencia < otro.frecuencia

def comprimir_archivo_txt(ruta_entrada, ruta_salida):
    with open(ruta_entrada, 'r', encoding='utf-8') as f:
        texto = f.read()

    texto_codificado, codigos = hyffman.comprimir_texto(texto)

    bits_extra = 8 - len(texto_codificado) % 8
    texto_codificado += "0" * bits_extra

    bytes_array = bytearray()
    for i in range(0, len(texto_codificado), 8):
        byte = texto_codificado[i:i+8]
        bytes_array.append(int(byte, 2))

   
    with open(ruta_salida, 'wb') as f:
        pickle.dump({"bits_extra": bits_extra, "data": bytes_array, "codigos": codigos}, f)

    print(f"Archivo comprimido guardado en: {ruta_salida}")
    print(f"Tamaño original: {len(texto)} caracteres")
    print(f"Tamaño comprimido: {len(bytes_array)} bytes")


##Ejemplo uso 
##if __name__ == "__main__":
##    entrada = "ejemplo.txt"
##    salida = "comprimido.bin"
##    comprimir_archivo_txt(entrada, salida)

# Descompresión de texto.

def descomprimir_archivo_txt(ruta_entrada, ruta_salida):
    with open(ruta_entrada, 'rb') as f:
        data = pickle.load(f)

    bits_extra = data["bits_extra"]
    bytes_array = data["data"]
    codigos = data["codigos"]

    texto_codificado = ''.join(f'{byte:08b}' for byte in bytes_array)
    texto_codificado = texto_codificado[:-bits_extra] if bits_extra > 0 else texto_codificado

    texto_descomprimido = descomprimir_con_arbol(texto_codificado, codigos)

    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write(texto_descomprimido)

    print(f"Archivo descomprimido guardado en: {ruta_salida}")

def descomprimir_con_arbol(texto_codificado, codigos):
    raiz = NodoHuffman(None, 0)
    for caracter, codigo in codigos.items():
        nodo_actual = raiz
        for bit in codigo:
            if bit == '0':
                if not nodo_actual.izq:
                    nodo_actual.izq = NodoHuffman(None, 0)
                nodo_actual = nodo_actual.izq
            else:
                if not nodo_actual.der:
                    nodo_actual.der = NodoHuffman(None, 0)
                nodo_actual = nodo_actual.der
        nodo_actual.caracter = caracter

    resultado = []
    nodo_actual = raiz
    for bit in texto_codificado:
        if bit == '0':
            nodo_actual = nodo_actual.izq
        else:
            nodo_actual = nodo_actual.der
        
        if nodo_actual.caracter is not None:
            resultado.append(nodo_actual.caracter)
            nodo_actual = raiz
    
    return ''.join(resultado)


if __name__ == "__main__":
    # Comprimir
    entrada = "ejemplo.txt"
    salida = "comprimido.bin"
    comprimir_archivo_txt(entrada, salida)
    
    # Descomprimir
    descomprimir_archivo_txt(salida, "descomprimido.txt")

# -----------------------

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