Organizacion de las ramas 
main                # Rama estable (versión final del proyecto)
│
└── develop         # Rama de integración de módulos
    ├── texto-huffman-german
    ├── texto-huffman-rodrigo
    ├── imagen-rle-tonny
    ├── imagen-rle-pablito
    ├── audio-huffman-andres
    ├── audio-huffman-eduardo

  !!!Todo lo del gui y documentos se va a trabajar en develop!!!


# Proyecto III Estructura de datos II
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
### Interfaz grafica

### Compresión de Texto

### Compresión de Imagenes

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
