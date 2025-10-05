import re
import wave
import heapq
from collections import Counter, defaultdict

#Clase de compresion de audio
class CompresionAuido:
    #Constructor de clases
    def __init__(self, ruta, muestras):
        self._ruta = ruta
        self.muestras = muestras
        self.Nodo = NodoHuffman

    @property
    def ruta(self):
        return self._ruta 
    
    #Metodo 
    @ruta.setter
    def ruta(self, rutaArchivo):
        protocolo = re.compile(r'^(?:[A-Za-z]:\\|\\\\|\/|~)?(?:[^\\\/\r\n]+[\\\/])*[^\\\/\r\n]+$')
        if re.match(protocolo, rutaArchivo):
            self._ruta = rutaArchivo
        else: 
            return("Intente otra vez con el formato especifico")
    
    def leerMuestras(self):
        with wave.open(self.ruta, "rb") as wav:
            frames = wav.readframes(wav.getnframes())
            muestras = list(frames)
            self.muestras = muestras 
        return self.muestras
    
    def construir_arbol(self, freqs):
        heap = [self.Nodo(v, f) for v, f in freqs.items()]
        heapq.heapify(heap)
        while len(heap) > 1:
            n1 = heapq.heappop(heap)
            n2 = heapq.heappop(heap)
            nuevo = self.Nodo(None, n1.freq + n2.freq, n1, n2)
            heapq.heappush(heap, nuevo)
        return heap[0]

    def generarCodigos(self, nodo, prefijo="", codigos=None):
        nodo = self.Nodo
        if codigos is None:
            codigos = {}
        if nodo.valor is not None:
            codigos[nodo.valor] = prefijo
        else:
            generarCodigos(self.Nodo.izq, prefijo + "0", codigos)
            generarCodigos(self.Nodo.der, prefijo + "1", codigos)
        return codigos

    def codificar(muestras, codigos):
        return ''.join(codigos[m] for m in muestras)

class NodoHuffman:
    def __init__(self, valor=None, freq=0, izq=None, der=None):
        self.valor = valor
        self.freq = freq
        self.izq = izq
        self.der = der

    def __lt__(self, otro):  # necesario para heapq
        return self.freq < otro.freq