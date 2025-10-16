# compresion_audio/huffman_audio.py
# Lógica de compresión/descompresión Huffman para WAV
# Python 3.8+

import os
import re
import wave
import heapq
import pickle
from collections import Counter
from typing import Optional, Tuple, Dict, List


# ======================== NODO HUFFMAN ========================
class NodoHuffman:
    def __init__(self, valor: Optional[int] = None, freq: int = 0,
                 izq: 'NodoHuffman' = None, der: 'NodoHuffman' = None):
        self.valor = valor      # byte 0..255 (símbolo) o None si nodo interno
        self.freq = freq
        self.izq = izq
        self.der = der

    def __lt__(self, otro: 'NodoHuffman'):
        return self.freq < otro.freq


# ===================== UTILIDADES DE BITS =====================
def _pack_bits(bits_str: str) -> Tuple[bytes, int]:
    """
    Empaqueta una cadena de bits '0101...' en bytes.
    Devuelve (bytes_empaquetados, n_bits_validos) para recuperar sin padding.
    """
    n = len(bits_str)
    if n == 0:
        return b"", 0
    pad = (-n) % 8  # cuantos ceros para completar múltiplo de 8
    if pad:
        bits_str += "0" * pad
    out = bytearray()
    for i in range(0, len(bits_str), 8):
        out.append(int(bits_str[i:i + 8], 2))
    return bytes(out), n


def _unpack_bits(data: bytes, n_valid_bits: int) -> str:
    """
    Convierte bytes a cadena de bits, recortando a n_bits_validos para
    eliminar padding.
    """
    if not data or n_valid_bits == 0:
        return ""
    bits = ''.join(f'{b:08b}' for b in data)
    return bits[:n_valid_bits]


# ======================= CLASE PRINCIPAL =======================
class CompresionAudio:
    """
    Maneja compresión y descompresión Huffman sobre los BYTES crudos del WAV.
    No hay pérdida: se reescribe el mismo stream de bytes y se restauran
    los parámetros de cabecera (canales, sample width, framerate, nframes).
    """
    def __init__(self, ruta: str, muestras: Optional[List[int]] = None):
        self._ruta = ruta
        self.muestras = muestras

    # -------- validación de ruta --------
    @property
    def ruta(self) -> str:
        return self._ruta

    @ruta.setter
    def ruta(self, rutaArchivo: str):
        protocolo = re.compile(r'^(?:[A-Za-z]:\\|\\\\|\/|~)?(?:[^\\\/\r\n]+[\\\/])*[^\\\/\r\n]+$')
        if re.match(protocolo, rutaArchivo):
            self._ruta = rutaArchivo
        else:
            raise ValueError("Ruta inválida: intenta otra vez con un formato de ruta válido.")

    # -------- lectura WAV -> lista[int 0..255] --------
    def leerMuestras(self) -> List[int]:
        """
        Lee todos los frames del WAV (bytes crudos). Devuelve lista de enteros 0..255.
        """
        try:
            with wave.open(self.ruta, "rb") as wav:
                frames = wav.readframes(wav.getnframes())
                self.muestras = list(frames)
            return self.muestras
        except Exception as e:
            raise ValueError(f"Error leyendo archivo WAV: {e}")

    # -------- parámetros de cabecera --------
    def obtener_parametros_wav(self) -> Dict[str, int]:
        with wave.open(self.ruta, "rb") as wav:
            return {
                "nchannels": wav.getnchannels(),
                "sampwidth": wav.getsampwidth(),
                "framerate": wav.getframerate(),
                "nframes": wav.getnframes(),
            }

    # -------- árbol/códigos Huffman --------
    def construir_arbol(self, freqs: Dict[int, int]) -> NodoHuffman:
        heap = [NodoHuffman(v, f) for v, f in freqs.items()]
        heapq.heapify(heap)
        if not heap:
            return NodoHuffman(None, 0, None, None)  # WAV vacío
        while len(heap) > 1:
            n1 = heapq.heappop(heap)
            n2 = heapq.heappop(heap)
            heapq.heappush(heap, NodoHuffman(None, n1.freq + n2.freq, n1, n2))
        return heap[0]

    def generarCodigos(self, nodo: NodoHuffman, prefijo: str = "",
                       codigos: Optional[Dict[int, str]] = None) -> Dict[int, str]:
        if codigos is None:
            codigos = {}
        if nodo is None:
            return codigos
        if nodo.valor is not None:
            # caso símbolo único: evita código vacío
            codigos[nodo.valor] = prefijo or "0"
        else:
            self.generarCodigos(nodo.izq, prefijo + "0", codigos)
            self.generarCodigos(nodo.der, prefijo + "1", codigos)
        return codigos

    # -------- codificación/decodificación --------
    def codificar(self, muestras: List[int], codigos: Dict[int, str]) -> str:
        return ''.join(codigos[m] for m in muestras) if muestras else ""

    def decodificar(self, bits: str, raiz: NodoHuffman) -> List[int]:
        nodo = raiz
        out: List[int] = []
        for b in bits:
            nodo = nodo.izq if b == "0" else nodo.der
            if nodo.valor is not None:
                out.append(nodo.valor)
                nodo = raiz
        return out

    # ========================= COMPRESIÓN =========================
    def comprimir(self, archivo_salida_huff: Optional[str] = None, **kwargs) -> Tuple[str, str]:
        """
        Comprime el WAV actual.
        Devuelve (ruta_huff, ruta_wav_verificacion).

        - Si no se da archivo_salida_huff, crea '<original>.huff'.
        - Además crea '<original> (comprimido).wav' para escuchar/verificar.
        """
        # Compat: permitir archivo_salida=...
        if archivo_salida_huff is None and 'archivo_salida' in kwargs:
            archivo_salida_huff = kwargs.get('archivo_salida')

        if self.muestras is None:
            self.leerMuestras()

        # Rutas por defecto
        base, _ = os.path.splitext(self.ruta)
        if not archivo_salida_huff:
            archivo_salida_huff = base + ".huff"
        if not archivo_salida_huff.lower().endswith(".huff"):
            archivo_salida_huff += ".huff"
        wav_ver = f"{base} (comprimido).wav"

        # Construir modelo
        freqs = Counter(self.muestras)
        raiz = self.construir_arbol(freqs)
        codigos = self.generarCodigos(raiz)

        # Codificar y empaquetar
        bits = self.codificar(self.muestras, codigos)
        packed, n_valid = _pack_bits(bits)

        # Guardar .huff con metadatos
        params = self.obtener_parametros_wav()
        payload = {
            "packed": packed,
            "n_valid_bits": n_valid,
            "frecuencias": dict(freqs),
            "parametros_wav": params,
            "n_muestras": len(self.muestras),
        }
        with open(archivo_salida_huff, "wb") as f:
            pickle.dump(payload, f)

        # Reconstrucción inmediata (verificación audible)
        try:
            dec_bytes = bytes(self._decodificar_desde_paquete(packed, n_valid, freqs, len(self.muestras)))
            self._escribir_wav(dec_bytes, params, wav_ver)
        except Exception:
            # No bloquea la compresión si la verificación falla
            pass

        print(f"Archivo comprimido: {archivo_salida_huff}")
        print(f"WAV verificación:   {wav_ver}")
        return archivo_salida_huff, wav_ver

    # ======================= DESCOMPRESIÓN =======================
    def extraerArchivo(self, archivo_comprimido: Optional[str] = None,
                       archivo_salida: Optional[str] = None) -> str:
        """
        Descomprime un .huff a WAV.
        - Si archivo_comprimido es None, intenta usar '<self.ruta>.huff'.
        - Si archivo_salida es None, crea '<base>_descomprimido.wav'.
        Devuelve la ruta del WAV generado.
        """
        # Resolver .huff por defecto si no se pasa
        if archivo_comprimido is None:
            if not self.ruta or not self.ruta.lower().endswith(".wav"):
                raise ValueError("Especifica archivo_comprimido o inicializa la clase con un WAV válido.")
            archivo_comprimido = os.path.splitext(self.ruta)[0] + ".huff"

        if not archivo_comprimido.lower().endswith(".huff"):
            raise ValueError("El archivo comprimido debe tener extensión .huff")
        if not os.path.exists(archivo_comprimido):
            raise FileNotFoundError(f"No se encontró el archivo: {archivo_comprimido}")

        with open(archivo_comprimido, "rb") as f:
            datos = pickle.load(f)

        packed: bytes = datos.get("packed", b"")
        n_valid: int = datos.get("n_valid_bits", 0)
        freqs: Dict[int, int] = datos.get("frecuencias", {})
        params: Dict[str, int] = datos.get("parametros_wav", {})
        n_muestras: int = datos.get("n_muestras", 0)

        dec = self._decodificar_desde_paquete(packed, n_valid, freqs, n_muestras)
        raw = bytes(dec)

        # Ruta de salida
        if archivo_salida is None:
            base = os.path.splitext(archivo_comprimido)[0]
            archivo_salida = base + "_descomprimido.wav"

        self._escribir_wav(raw, params, archivo_salida)
        return archivo_salida

    
    def _decodificar_desde_paquete(self, data_packed: bytes, n_valid_bits: int,
                                   freqs: Dict[int, int], n_muestras: int) -> List[int]:
        raiz = self.construir_arbol(freqs)

       
        if raiz and raiz.valor is not None:
            total = int(n_muestras or sum(freqs.values()))
            return [raiz.valor] * total

        bits = _unpack_bits(data_packed, n_valid_bits)
        return self.decodificar(bits, raiz)

    def _escribir_wav(self, data_bytes: bytes, params: Dict[str, int], destino: str):
        """
        Escribe un WAV usando la misma cabecera que el original.
        """
        with wave.open(destino, "wb") as w:
            w.setnchannels(params["nchannels"])
            w.setsampwidth(params["sampwidth"])
            w.setframerate(params["framerate"])
            w.setnframes(params["nframes"])
            w.writeframes(data_bytes)
        print(f"WAV escrito: {destino}")