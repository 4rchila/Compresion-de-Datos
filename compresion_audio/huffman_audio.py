# compresion_audio/huffman_audio.py
import os
import re
import wave
import heapq
import pickle
import shutil
from collections import Counter
from typing import Optional, Tuple, Dict, List


# ======================== NODO HUFFMAN ========================
class NodoHuffman:
    def __init__(self, valor: Optional[int] = None, freq: int = 0,
                 izq: 'NodoHuffman' = None, der: 'NodoHuffman' = None):
        self.valor = valor      # byte (0..255) o None si nodo interno
        self.freq = freq
        self.izq = izq
        self.der = der

    def __lt__(self, otro: 'NodoHuffman'):
        return self.freq < otro.freq


# ===================== UTILIDADES DE BITS =====================
def _pack_bits(bits_str: str) -> Tuple[bytes, int]:
    """'0101...' -> (bytes, n_bits_validos)"""
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
    if not data or n_valid_bits == 0:
        return ""
    bits = ''.join(f'{b:08b}' for b in data)
    return bits[:n_valid_bits]


def _unique_path(path: str) -> str:
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    n = 2
    while True:
        cand = f"{base} ({n}){ext}"
        if not os.path.exists(cand):
            return cand
        n += 1


def _with_suffix(base_path: str, suffix: str, ext: str) -> str:
    return _unique_path(f"{base_path}{suffix}{ext}")


# ==================== CLASE PRINCIPAL ====================
class CompresionAudio:
    """
    Compresión/Descompresión con Huffman operando sobre los **bytes crudos** del WAV.
    Soporta WAV PCM de 8/16/24/32 bits, mono o estéreo (no importa el formato: se comprimen bytes).
    - Al comprimir: crea **copia WAV** y **archivo .flac** (contenedor propio con pickle).
    - Al descomprimir: desde .flac crea **WAV descomprimido** (tercera copia).
    """
    def __init__(self, ruta: str, muestras: Optional[List[int]] = None):
        self._ruta = ruta
        self.muestras = muestras  # bytes -> lista de ints 0..255

    # Validación de ruta
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

    # Lectura WAV -> lista de bytes (ints 0..255)
    def leerMuestras(self) -> List[int]:
        try:
            with wave.open(self.ruta, "rb") as wav:
                frames = wav.readframes(wav.getnframes())
                self.muestras = list(frames)  # bytes crudos del WAV
            return self.muestras
        except Exception as e:
            raise ValueError(f"Error leyendo archivo WAV: {e}")

    # Cabecera WAV necesaria para reescritura
    def obtener_parametros_wav(self) -> Dict[str, int]:
        with wave.open(self.ruta, "rb") as wav:
            return {
                "nchannels": wav.getnchannels(),
                "sampwidth": wav.getsampwidth(),
                "framerate": wav.getframerate(),
                "nframes": wav.getnframes(),
            }

    # Huffman
    def construir_arbol(self, freqs: Dict[int, int]) -> NodoHuffman:
        heap = [NodoHuffman(v, f) for v, f in freqs.items()]
        heapq.heapify(heap)
        if not heap:
            return NodoHuffman(None, 0, None, None)
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
            codigos[nodo.valor] = prefijo or "0"
        else:
            self.generarCodigos(nodo.izq, prefijo + "0", codigos)
            self.generarCodigos(nodo.der, prefijo + "1", codigos)
        return codigos

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
    def comprimir(self, archivo_salida_flac: Optional[str] = None,
                  crear_copia_wav: bool = True,
                  sufijo_copia: str = " (copia)") -> Dict[str, str]:
        """
        Devuelve: {"wav_copia": <ruta|None>, "flac": <ruta_flac>}
        """
        if not self.ruta.lower().endswith(".wav"):
            raise ValueError("Inicializa con un archivo .wav para comprimir.")

        if self.muestras is None:
            self.leerMuestras()

        base, _ = os.path.splitext(self.ruta)

        # 1) Copia del WAV
        ruta_wav_copia = None
        if crear_copia_wav:
            ruta_wav_copia = _with_suffix(base, sufijo_copia, ".wav")
            shutil.copyfile(self.ruta, ruta_wav_copia)

        # 2) Archivo .flac (contenedor propio)
        if not archivo_salida_flac:
            archivo_salida_flac = base + ".flac"
        if not archivo_salida_flac.lower().endswith(".flac"):
            archivo_salida_flac += ".flac"
        archivo_salida_flac = _unique_path(archivo_salida_flac)

        freqs = Counter(self.muestras)
        raiz = self.construir_arbol(freqs)
        codigos = self.generarCodigos(raiz)

        bits = self.codificar(self.muestras, codigos)
        packed, n_valid = _pack_bits(bits)

        params = self.obtener_parametros_wav()
        payload = {
            "packed": packed,
            "n_valid_bits": n_valid,
            "frecuencias": dict(freqs),
            "parametros_wav": params,
            "n_muestras": len(self.muestras),
            "formato_original": "WAV",
        }
        with open(archivo_salida_flac, "wb") as f:
            pickle.dump(payload, f)

        return {"wav_copia": ruta_wav_copia, "flac": archivo_salida_flac}

    # ======================= DESCOMPRESIÓN =======================
    def extraerArchivo(self, archivo_comprimido: Optional[str] = None,
                       archivo_salida: Optional[str] = None,
                       sufijo_descomp: str = " (descomprimido)") -> str:
        """
        Devuelve la ruta del WAV generado.
        """
        if archivo_comprimido is None:
            if not self.ruta or not self.ruta.lower().endswith(".wav"):
                raise ValueError("Especifica archivo_comprimido o inicializa la clase con un WAV válido.")
            archivo_comprimido = os.path.splitext(self.ruta)[0] + ".flac"

        if not archivo_comprimido.lower().endswith(".flac"):
            raise ValueError("El archivo comprimido debe tener extensión .flac")
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
            archivo_salida = _with_suffix(base, sufijo_descomp, ".wav")

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
        destino = _unique_path(destino)
        with wave.open(destino, "wb") as w:
            w.setnchannels(params["nchannels"])
            w.setsampwidth(params["sampwidth"])
            w.setframerate(params["framerate"])
            w.setnframes(params["nframes"])
            w.writeframes(data_bytes)
