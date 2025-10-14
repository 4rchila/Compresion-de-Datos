import re
import wave
import heapq #libreria usada par crear el heap
import pickle #libreria usada para crear el archvio .huff que comprime el audio
from collections import Counter

#Clase donde se declara el nodo dle arbol
class NodoHuffman:
    def __init__(self, valor=None, freq=0, izq=None, der=None):
        self.valor = valor
        self.freq = freq
        self.izq = izq
        self.der = der

    def __lt__(self, otro):
        return self.freq < otro.freq

#Clase principal
class CompresionAudio:
    def __init__(self, ruta, muestras=None):
        self._ruta = ruta
        self.muestras = muestras

    @property
    def ruta(self):
        return self._ruta 
    
    #Setter donde se asegura de que se ingrese una ruta de acceso
    @ruta.setter
    def ruta(self, rutaArchivo):
        protocolo = re.compile(r'^(?:[A-Za-z]:\\|\\\\|\/|~)?(?:[^\\\/\r\n]+[\\\/])*[^\\\/\r\n]+$')
        if re.match(protocolo, rutaArchivo):
            self._ruta = rutaArchivo
        else: 
            raise ValueError("Ruta inválida: intente otra vez con el formato específico")
    
    #Metodo para leer el archivo de audio
    def leerMuestras(self):
        try:
            with wave.open(self.ruta, "rb") as wav:
                frames = wav.readframes(wav.getnframes())
                muestras = list(frames)
                self.muestras = muestras 
            return self.muestras
        except Exception as e:
            raise ValueError(f"Error leyendo archivo WAV: {e}")

    #Construccion del arbol 
    def construir_arbol(self, freqs):
        heap = [NodoHuffman(v, f) for v, f in freqs.items()]
        heapq.heapify(heap)
        while len(heap) > 1:
            n1 = heapq.heappop(heap)
            n2 = heapq.heappop(heap)
            nuevo = NodoHuffman(None, n1.freq + n2.freq, n1, n2)
            heapq.heappush(heap, nuevo)
        return heap[0]

    def generarCodigos(self, nodo, prefijo="", codigos=None):
        if codigos is None:
            codigos = {}
        if nodo.valor is not None:
            codigos[nodo.valor] = prefijo
        else:
            self.generarCodigos(nodo.izq, prefijo + "0", codigos)
            self.generarCodigos(nodo.der, prefijo + "1", codigos)
        return codigos

    #Metodo para realizar la codificacion del audio 
    def codificar(self, muestras, codigos):
        return ''.join(codigos[m] for m in muestras)

    #Metodo donde se comprime el auido en un archivo .huff
    def comprimir(self, archivo_salida=None):
        if self.muestras is None:
            self.leerMuestras()
        
        # Si no se especifica archivo de salida, generar uno automáticamente
        if archivo_salida is None:
            archivo_salida = self.ruta.replace(".wav", ".huff")
        # Asegurar extensión .huff
        elif not archivo_salida.endswith('.huff'):
            archivo_salida += '.huff'
        
        # Calcular frecuencias
        freqs = Counter(self.muestras)
        
        # Construir árbol y códigos
        raiz = self.construir_arbol(freqs)
        codigos = self.generarCodigos(raiz)
        
        # Codificar muestras
        bits_codificados = self.codificar(self.muestras, codigos)
        
        # Guardar datos comprimidos
        datos_comprimidos = {
            "codificado": bits_codificados,
            "frecuencias": freqs,
            "parametros_wav": self.obtener_parametros_wav()
        }
        
        with open(archivo_salida, "wb") as f:
            pickle.dump(datos_comprimidos, f)
        
        print(f"Archivo comprimido guardado en: {archivo_salida}")
        return archivo_salida

    def obtener_parametros_wav(self):
        with wave.open(self.ruta, "rb") as wav:
            return {
                "nchannels": wav.getnchannels(),
                "sampwidth": wav.getsampwidth(),
                "framerate": wav.getframerate(),
                "nframes": wav.getnframes()
            }

    #Metodo para la extraccion del archivo
    def extraerArchivo(self, archivo_comprimido, archivo_salida=None):
        # Verificar que el archivo comprimido tenga extensión .huff
        if not archivo_comprimido.endswith('.huff'):
            raise ValueError("El archivo comprimido debe tener extensión .huff")
        
        # Generar nombre de salida automáticamente si no se especifica
        if archivo_salida is None:
            archivo_salida = archivo_comprimido.replace('.huff', '_descomprimido.wav')
        
        with open(archivo_comprimido, "rb") as f:
            datos = pickle.load(f)
    
    #Metodo que decodifica el audio
    def decodificar(self, bits, raiz):
        nodo = raiz
        decodificado = []

        for bit in bits:
            if bit == "0":
                nodo = nodo.izq
            else:
                nodo = nodo.der

            if nodo.valor is not None:
                decodificado.append(nodo.valor)
                nodo = raiz
        return decodificado