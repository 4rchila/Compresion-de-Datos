import re
import wave
import heapq
import struct
from collections import Counter

#Clase de compresion de audio
class CompresionAudio:
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
    



def decodificar(codigo_binario, arbol):
    resultado = []
    nodo = arbol
    for bit in codigo_binario:
        if bit == '0':
            nodo = nodo.izq
        else:
            nodo = nodo.der
        if nodo.valor is not None:
            resultado.append(nodo.valor)
            nodo = arbol
    return resultado


class HuffmanAudio:
    def __init__(self):
        pass

    def deserializar_arbol(self, data):
        it = iter(data)
        def _rec():
            try:
                t = next(it)
            except StopIteration:
                return None
            if t == 1:
                v = next(it)
                return NodoHuffman(valor=v, freq=0)
            else:
                izq = _rec()
                der = _rec()
                return NodoHuffman(None, 0, izq, der)
        return _rec()

    def bytes_a_bits(self, b):
        return ''.join(f'{byte:08b}' for byte in b)

    def decodificar_bits(self, bits, arbol, total_bytes=None):
        out = []
        nodo = arbol
        for bit in bits:
            nodo = nodo.izq if bit == '0' else nodo.der
            if nodo is not None and nodo.valor is not None:
                out.append(nodo.valor)
                if total_bytes is not None and len(out) >= total_bytes:
                    break
                nodo = arbol
            if nodo is None:
                nodo = arbol
        return out

    def descompresion_archivo(self, input_path, output_wav_path):
        with open(input_path, 'rb') as f:
            magic = f.read(4)
            if magic != b'HUFF':
                raise ValueError('Formato desconocido')
            tree_len = struct.unpack('<I', f.read(4))[0]
            arbol_ser = f.read(tree_len)
            params_packed = f.read(16)
            nchannels, sampwidth, framerate, nframes = struct.unpack('<IIII', params_packed)
            datos_bits = f.read()

        arbol = self.deserializar_arbol(arbol_ser)
        bits = self.bytes_a_bits(datos_bits)

        total_bytes = nframes * nchannels * sampwidth
        muestras = self.decodificar_bits(bits, arbol, total_bytes=total_bytes)

        frames = bytes(muestras)
        with wave.open(output_wav_path, 'wb') as wav:
            wav.setnchannels(nchannels)
            wav.setsampwidth(sampwidth)
            wav.setframerate(framerate)
            wav.writeframes(frames)
