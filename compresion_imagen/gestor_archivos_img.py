import os
from tkinter import Tk, filedialog
import rle_imagen 

print("Compresion y Descompresion")
print("")

ventana = Tk()
ventana.withdraw()

print("Por favor selecciona un archivo para trabajar.")
ruta_archivo = filedialog.askopenfilename(
    title="Selecciona un archivo cualquiera",
    filetypes=[("Todos los archivos", "*.*")]
)

if not ruta_archivo:
    print("No elegiste ningún archivo")
    input("Presiona Enter para salir...")
    exit()

nombre_archivo = os.path.splitext(os.path.basename(ruta_archivo))[0]
carpeta_archivo = os.path.dirname(ruta_archivo)
extension_archivo = os.path.splitext(ruta_archivo)[1].lower()

print("Has seleccionado:", ruta_archivo)
print("Nombre:", nombre_archivo)
print("Extensión:", extension_archivo)
print("Carpeta:", carpeta_archivo)
print("")

if extension_archivo == ".rlebits":
    print("Parece que este archivo ya está comprimido.")
    try:
        archivo_salida = rle_imagen.descomprimir_rlebits(ruta_archivo)
        print("")
        print("Archivo descomprimido correctamente.")
        print("Ruta del nuevo archivo:", archivo_salida)
    except Exception as e:
        print("Ocurrió un error al descomprimir:", e)
else:
    print("El archivo no está comprimido.")
    try:
        archivo_salida = rle_imagen.comprimir_a_rlebits(ruta_archivo)
        print("")
        print("Archivo comprimido correctamente.")
        print("Ruta del nuevo archivo:", archivo_salida)
    except Exception as e:
        print("Ocurrió un error al comprimir:", e)

print("")
print("Fin del programa.")
input("Presiona Enter para salir...")
