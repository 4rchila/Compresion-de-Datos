#Proyecto III Estructura de datos II
## Integrantes 
### Edgar Eduardo Rodas Lopez - 
### Andrés Alejandro Mazariegos Lopez 
### German Archila Batz
### Rodrigo Gabriel Perez 
### Cristian Antonio
### Pablo Jose Lorenzo

## Descripición 
### El proyecto tiene como objetivo la implementacion de los diversos algoritmos de compresion vistos en clase:	
* Texto plano de Huffman
* Compresión de Imagenes RLE
* Compresión de Audio de Huffman 

## Especificaciones tecnicas
### Compresión de Texto
Cuando se ingresa a la parte de compresión Huffman, se le pide ingresar un archivo existente al usuario.
Se ingresa un texto y tiene un botón de previsualización del texto con la cantidad de letras (incluyendo espacios).
Al comprimir en Huffman se muestra un registro en pantalla con toda la información de la compresión.
Este genera un archivo .bin con la compresión Huffman.
Ahora, para generar la descompresión se necesita tener un archivo .txt vacío.
Se selecciona el .bin que se desea descomprimir y el .txt vacío al cual se copiará la información.
Luego, se presiona en el botón de descomprimir Huffman y el resultante es el archivo previamente creado pero con la información del texto original.
### Compresión de Imágenes
La compresión de imágenes utiliza el algoritmo RLE (Run-Length Encoding) para reducir el tamaño de los archivos.
Este algoritmo trabaja directamente sobre los bytes del archivo de imagen, sin importar su formato original (por ejemplo, .png o .bmp), por lo que puede aplicarse a cualquier imagen almacenada en forma binaria.
Para este proyecto se utilizaron las siguientes librerías:
  1. OS
  Manejo de rutas, nombres y ubicaciones de los archivos de imagen tanto en compresión como en descompresión.
  2. Struct
  Empaquetado y desempaquetado de los datos binarios, necesarios para guardar la información de la imagen comprimida en un formato propio .rle.
  3. Typing (Optional)
  Uso de anotaciones de tipo opcional para mejorar la claridad y control de las funciones que reciben o devuelven rutas de archivo.
A grandes rasgos, el programa utiliza el algoritmo RLE para recorrer todos los bytes del archivo original y detectar secuencias consecutivas de valores iguales, reemplazándolas por un par (cantidad, valor).
Este método resulta muy eficiente en imágenes con pocos colores o grandes áreas uniformes, ya que reduce considerablemente el tamaño del archivo.

Durante la compresión, el programa genera un archivo con extensión .rle que contiene:
+ Una cabecera identificadora del formato (RLEIMG1),
+ El nombre original del archivo,
+ Su tamaño original en bytes,
+ Y la secuencia de datos comprimidos.

En la descompresión, el proceso se invierte: se leen los pares (cantidad, valor) y se reconstruye el flujo binario original, devolviendo una copia idéntica de la imagen inicial, la cual puede visualizarse o manipularse sin pérdida alguna de información.
De esta forma, el programa logra una compresión sin pérdida, manteniendo la calidad original de la imagen y permitiendo su restauración completa a partir del archivo comprimido .rle.

### Compresión de Audio
La compresion de audio utiliza el algoritmo de Huffman de compresión de audio.
Este algoritmo unicamente trabaja con archivos de audio ".wav", al ser el unico formato comercial que no se encuentra comprimido o reducido.
Para este se utilizo las librerias:
+ Pickle 
	Creación de un archivo ".flac" que comprimen en texto plano el audio para su descompresión luego.
+ Regular Expresions
	Comprobación del uso correcto de los formatos establecidos para la subida de archivos, por medio de expresiones regulares.
+ Heap
	Creación de monticulos o heaps, para ordenar el arbol binario necesario para el uso del algoritmo de Huffman.
+ Wave
	Reproducción de los archivos de audio, tanto antes como despues de ser comprimidos.

Groso modo el programa usa el algoritmo de Huffman para convertir el archivo a .wav a uno de texto plano .flac, usando la libreria pickle.
Una vez codificado y comprimido como un .flac, el archivo puede ser manejado como texto plano para luego en caso de querer ser reproducido tener que descomprimirse.
Este al ser reproducido se maneja como un .wav normal, ya que la descodificación y descompresion del archivo lo convierte nuevamente en un archivo .wav el cual el programa podra reproducir sin problemas.
Ademas la pestaña de compresión de audio puede ser utilizada como un reproudctor de auido (siempre y cuando sean .wav) normal.