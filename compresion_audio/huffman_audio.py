# compresion_audio/huffman_audio.py
# Compresión/Descompresión de WAV usando Huffman → .huff (sin pérdida)
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
        self.valor = valor
        self.freq = freq
        self.izq = izq
        self.der = der

    def __lt__(self, otro: 'NodoHuffman'):
        return self.freq < otro.freq


# ===================== UTILIDADES DE BITS =====================
def _pack_bits(bits_str: str) -> Tuple[bytes, int]:
    """
    Empaqueta '010101...' en bytes. Retorna (bytes_empaquetados, n_bits_validos).
    """
    n = len(bits_str)
    if n == 0:
        return b"", 0
    pad = (-n) % 8
    if pad:
        bits_str += "0" * pad
    out = bytearray()
    for i in range(0, len(bits_str), 8):
        out.append(int(bits_str[i:i + 8], 2))
    return bytes(out), n


def _unpack_bits(data: bytes, n_valid_bits: int) -> str:
    """
    Convierte bytes a '0101...' y recorta a n_valid_bits para eliminar padding.
    """
    if not data or n_valid_bits == 0:
        return ""
    bits = ''.join(f'{b:08b}' for b in data)
    return bits[:n_valid_bits]


# ======================= CLASE PRINCIPAL ======================
class CompresionAudio:
    """
    Compresión Huffman sobre los BYTES crudos del WAV (lossless).
    Guarda .huff con:
      - packed (bytes) + n_valid_bits
      - frecuencias (símbolos 0..255)
      - parámetros WAV (nchannels, sampwidth, framerate, nframes)
      - n_muestras (largo del stream)
    También genera un WAV de verificación: '<base> (comprimido).wav'
    y al extraer crea '<base>_descomprimido.wav'
    """
    _re_ruta = re.compile(
        r'^(?:[A-Za-z]:\\|\\\\|\/|~)?(?:[^\\\/\r\n]+[\\\/])*[^\\\/\r\n]+$'
    )

    def __init__(self, ruta: str, muestras: Optional[List[int]] = None):
        if not isinstance(ruta, str) or not ruta:
            raise ValueError("Debes proporcionar una ruta de archivo.")
        if not self._re_ruta.match(ruta):
            raise ValueError("Ruta inválida: intenta otra vez con un formato de ruta válido.")
        self._ruta = ruta
        self.muestras = muestras

    # ------------ validación de ruta ------------
    @property
    def ruta(self) -> str:
        return self._ruta

    @ruta.setter
    def ruta(self, rutaArchivo: str):
        if not self._re_ruta.match(rutaArchivo):
            raise ValueError("Ruta inválida.")
        self._ruta = rutaArchivo

    # ------------ lectura WAV → lista [0..255] ------------
    def leerMuestras(self) -> List[int]:
        try:
            with wave.open(self.ruta, "rb") as wav:
                frames = wav.readframes(wav.getnframes())
                self.muestras = list(frames)  # bytes → ints 0..255
            return self.muestras
        except Exception as e:
            raise ValueError(f"Error leyendo WAV: {e}")

    # -------- parámetros de cabecera --------
    def obtener_parametros_wav(self) -> Dict[str, int]:
        with wave.open(self.ruta, "rb") as w:
            return {
                "nchannels": w.getnchannels(),
                "sampwidth": w.getsampwidth(),
                "framerate": w.getframerate(),
                "nframes": w.getnframes(),
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

    def decodificar(self, bits: str, raiz: NodoHuffman, total: int) -> List[int]:
        # caso símbolo único (árbol con un solo valor)
        if raiz and raiz.valor is not None:
            return [raiz.valor] * total
        out: List[int] = []
        nodo = raiz
        for b in bits:
            nodo = nodo.izq if b == "0" else nodo.der
            if nodo.valor is not None:
                out.append(nodo.valor)
                if len(out) == total:
                    break
                nodo = raiz
        return out

    # ========================= COMPRESIÓN =========================
    def comprimir(self, archivo_salida_huff: Optional[str] = None) -> Tuple[str, str]:
        """
        Comprime el WAV actual.
        Devuelve (ruta_huff, ruta_wav_verificacion).
        - Si no se pasa archivo_salida_huff, crea '<original>.huff'.
        - Genera '<original> (comprimido).wav' para escuchar/verificar.
        """
        if self.muestras is None:
            self.leerMuestras()

        base, ext = os.path.splitext(self.ruta)
        if ext.lower() != ".wav":
            raise ValueError("Para comprimir, el archivo de entrada debe ser .wav")

        if not archivo_salida_huff:
            archivo_salida_huff = base + ".huff"
        if not archivo_salida_huff.lower().endswith(".huff"):
            archivo_salida_huff += ".huff"

        wav_ver = f"{base} (comprimido).wav"

        # Modelo
        freqs = Counter(self.muestras)
        raiz = self.construir_arbol(freqs)
        codigos = self.generarCodigos(raiz)

        # Codificar + empaquetar
        bits = self.codificar(self.muestras, codigos)
        packed, n_valid = _pack_bits(bits)

        # Metadatos del WAV original
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
            dec = self._decodificar_desde_paquete(packed, n_valid, freqs, len(self.muestras))
            dec_bytes = bytes(dec)
            self._escribir_wav(dec_bytes, params, wav_ver)
        except Exception:
            # No bloquea la compresión si la verificación falla
            pass

        return archivo_salida_huff, wav_ver

    # ======================= DESCOMPRESIÓN =======================
    def extraerArchivo(self, archivo_comprimido: Optional[str] = None,
                       archivo_salida: Optional[str] = None) -> str:
        """
        Descomprime un .huff a WAV.
        - Si archivo_comprimido es None, usa '<self.ruta>.huff'.
        - Si archivo_salida es None, crea '<base>_descomprimido.wav'.
        Devuelve la ruta del WAV generado.
        """
        if archivo_comprimido is None:
            if not self.ruta or not self.ruta.lower().endswith(".wav"):
                raise ValueError("Especifica archivo_comprimido o inicializa con un WAV válido.")
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

        if archivo_salida is None:
            base = os.path.splitext(archivo_comprimido)[0]
            archivo_salida = base + "_descomprimido.wav"

        self._escribir_wav(raw, params, archivo_salida)
        return archivo_salida

    # ======================= HELPERS PRIVADOS ====================
    def _decodificar_desde_paquete(self, data_packed: bytes, n_valid_bits: int,
                                   freqs: Dict[int, int], n_muestras: int) -> List[int]:
        raiz = self.construir_arbol(freqs)

        # Caso símbolo único
        if raiz and raiz.valor is not None:
            total = int(n_muestras or sum(freqs.values()))
            return [raiz.valor] * total

        bits = _unpack_bits(data_packed, n_valid_bits)
        return self.decodificar(bits, raiz, n_muestras)

    def _escribir_wav(self, data_bytes: bytes, params: Dict[str, int], destino: str):
        with wave.open(destino, "wb") as w:
            w.setnchannels(params["nchannels"])
            w.setsampwidth(params["sampwidth"])
            w.setframerate(params["framerate"])
            w.setnframes(params["nframes"])
            w.writeframes(data_bytes)
