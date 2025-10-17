import os

def comprimir_a_rlebits(ruta):
    print("Leyendo archivo original")
    with open(ruta, "rb") as archivo:
        datos = archivo.read()

    print("Convirtiendo")
    bits = ""
    for byte in datos:
        bits_de_byte = format(byte, "08b") 
        bits += bits_de_byte

    print("Iniciando compresión")
    resultado = []
    contador = 1

    for i in range(1, len(bits)):
        if bits[i] == bits[i - 1] and contador < 255:
            contador += 1
        else:
            resultado.append(str(contador))
            resultado.append(bits[i - 1])
            contador = 1

    resultado.append(str(contador))
    resultado.append(bits[-1])

    nombre = os.path.splitext(os.path.basename(ruta))[0]
    carpeta = os.path.dirname(ruta)
    archivo_salida = os.path.join(carpeta, nombre + ".rlebits")

    print("Guardando archivo comprimido...")
    with open(archivo_salida, "w") as f:
        f.write(",".join(resultado))

    tamaño_original = os.path.getsize(ruta)
    tamaño_comprimido = os.path.getsize(archivo_salida)

    print("")
    print("Tamaño original:", tamaño_original, "bytes")
    print("Tamaño comprimido:", tamaño_comprimido, "bytes")

    return archivo_salida


def descomprimir_rlebits(ruta):
    print("Abriendo archivo ")
    with open(ruta, "r") as f:
        datos = f.read().split(",")

    print("Reconstruyendo")
    bits = ""
    for i in range(0, len(datos) - 1, 2):
        cantidad = int(datos[i])
        valor = datos[i + 1]
        bits += valor * cantidad

    print("Convirtiendo")
    bytes_resultado = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        if len(byte) < 8:
            byte = byte.ljust(8, "0") 
        bytes_resultado.append(int(byte, 2))

    nombre = os.path.splitext(os.path.basename(ruta))[0]
    carpeta = os.path.dirname(ruta)
    salida = os.path.join(carpeta, nombre + "_descomprimido.bin")

    print("Guardando archivo ")
    with open(salida, "wb") as f:
        f.write(bytes_resultado)

    return salida
