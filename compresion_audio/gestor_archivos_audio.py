
import pickle, heapq, wave
from collections import Counter



def construir_arbol(freqs: Counter):
    """Devuelve la raíz del árbol como dicts {'val','left','right'}."""
    if not freqs:
        raise ValueError("Frecuencias vacías")

    
    if len(freqs) == 1:
        único, rep = next(iter(freqs.items()))
        return {"val": None, "left": {"val": único, "left": None, "right": None}, "right": None, "_single": (único, rep)}

    heap, uid = [], 0
    for byte_val, f in freqs.items():
        node = {"val": byte_val, "left": None, "right": None}
        heap.append((f, uid, node)); uid += 1
    heapq.heapify(heap)

    while len(heap) > 1:
        f1, _, n1 = heapq.heappop(heap)
        f2, _, n2 = heapq.heappop(heap)
        parent = {"val": None, "left": n1, "right": n2}
        heapq.heappush(heap, (f1 + f2, uid, parent)); uid += 1

    return heap[0][2]

def decodificar_bits(bits: str, raiz) -> bytes:
    """Recorre el árbol por cada bit; emite byte al llegar a hoja."""
    
    if "_single" in raiz:
        byte_val, rep = raiz["_single"]
        return bytes([byte_val] * rep)

    out = bytearray()
    n = raiz
    for b in bits:
        n = n["left"] if b == "0" else n["right"]
        if n["val"] is not None:
            out.append(n["val"])
            n = raiz
    return bytes(out)

def escribir_wav(ruta_out: str, params: dict, pcm: bytes):
    """Escribe el WAV con los parámetros originales."""
    with wave.open(ruta_out, "wb") as w:
        w.setnchannels(params["nchannels"])
        w.setsampwidth(params["sampwidth"])
        w.setframerate(params["framerate"])
        w.writeframes(pcm)

def extraer_huff(archivo_huff: str, archivo_salida: str | None = None) -> str:
    """.huff -> .wav: cargar -> árbol -> decodificar -> escribir."""
    if not archivo_huff.endswith(".huff"):
        raise ValueError("Se requiere archivo .huff")

    if archivo_salida is None:
        archivo_salida = archivo_huff.replace(".huff", "_descomprimido.wav")

    
    with open(archivo_huff, "rb") as f:
        pkg = pickle.load(f)

    
    for k in ("codificado", "frecuencias", "parametros_wav"):
        if k not in pkg:
            raise ValueError(f"Paquete .huff incompleto, falta: {k}")

    bits: str = pkg["codificado"]
    freqs: Counter = pkg["frecuencias"]
    params: dict = pkg["parametros_wav"]

    # 3) Árbol
    raiz = construir_arbol(freqs)

    # 4) Decodificar
    pcm = decodificar_bits(bits, raiz)

    # 5) Escribir WAV
    escribir_wav(archivo_salida, params, pcm)
    return archivo_salida

