import pickle
from compresion_texto import huffman

def comprimir_archivo_txt(ruta_entrada, ruta_salida):
    with open(ruta_entrada, 'r', encoding='utf-8') as f:
        texto = f.read()

    texto_codificado, codigos = huffman.comprimir_texto(texto)

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