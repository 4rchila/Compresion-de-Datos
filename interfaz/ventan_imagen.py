import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import customtkinter as ctk
from tkinter import filedialog, messagebox
from compresion_imagen import rle_imagen


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VentanaImagen(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Ventana principal
        self.title("Compresión de Imágenes (RLE)")
        self.geometry("600x400")
        self.resizable(False, False)

        # Variables
        self.ruta_archivo = None
        self.tamaño_original = ctk.StringVar(value="Tamaño original: ---")
        self.tamaño_comprimido = ctk.StringVar(value="Tamaño comprimido: ---")
        self.estado = ctk.StringVar(value="Seleccione una imagen PNG, JPG o un archivo RLEBITS para comenzar.")

        # Encabezado
        titulo = ctk.CTkLabel(self, text="Compresión de Imágenes con RLE",
                              font=ctk.CTkFont(size=20, weight="bold"),
                              text_color="#A8D0E6")
        titulo.pack(pady=20)

        # Botones principales
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(pady=10)

        self.btn_cargar = ctk.CTkButton(frame_botones, text="📂 Cargar Archivo", width=160, command=self.cargar_archivo)
        self.btn_cargar.grid(row=0, column=0, padx=10)

        self.btn_comprimir = ctk.CTkButton(frame_botones, text="🗜️ Comprimir", width=160, command=self.comprimir)
        self.btn_comprimir.grid(row=0, column=1, padx=10)

        self.btn_descomprimir = ctk.CTkButton(frame_botones, text="💾 Descomprimir", width=160, command=self.descomprimir)
        self.btn_descomprimir.grid(row=0, column=2, padx=10)

        # Información del archivo 
        self.label_ruta = ctk.CTkLabel(self, text="Archivo seleccionado: ---", wraplength=550,
                                       text_color="#C9D6E3", font=ctk.CTkFont(size=13))
        self.label_ruta.pack(pady=10)

        # Tamaños
        frame_tamaños = ctk.CTkFrame(self, fg_color="#1B2A41", corner_radius=12)
        frame_tamaños.pack(pady=15, padx=20, fill="x")

        lbl_original = ctk.CTkLabel(frame_tamaños, textvariable=self.tamaño_original,
                                    text_color="#A8D0E6", font=ctk.CTkFont(size=14))
        lbl_original.pack(pady=5)

        lbl_comprimido = ctk.CTkLabel(frame_tamaños, textvariable=self.tamaño_comprimido,
                                      text_color="#A8D0E6", font=ctk.CTkFont(size=14))
        lbl_comprimido.pack(pady=5)

        # Estado
        estado_label = ctk.CTkLabel(self, textvariable=self.estado, wraplength=550,
                                    text_color="#98C1D9", font=ctk.CTkFont(size=13))
        estado_label.pack(pady=15)

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona una imagen o archivo comprimido",
            filetypes=[
                ("Imágenes PNG y JPG o Archivos RLEBITS", "*.png;*.jpg;*.rlebits"),
                ("Imágenes", "*.png;*.jpg"),
                ("Archivos RLE", "*.rlebits")
            ]
        )
        if ruta:
            self.ruta_archivo = ruta
            nombre = os.path.basename(ruta)
            ext = os.path.splitext(nombre)[1].lower()

            self.label_ruta.configure(text=f"Archivo seleccionado: {nombre}")
            self.tamaño_original.set("Tamaño original: ---")
            self.tamaño_comprimido.set("Tamaño comprimido: ---")

            if ext in [".png", ".jpg"]:
                self.estado.set("Imagen cargada correctamente. Lista para comprimir.")
            elif ext == ".rlebits":
                self.estado.set("Archivo RLE cargado correctamente. Listo para descomprimir.")
            else:
                self.estado.set("Formato no compatible.")
        else:
            self.estado.set("No se seleccionó ningún archivo.")

    def comprimir(self):
        if not self.ruta_archivo:
            messagebox.showwarning("Atención", "Primero selecciona una imagen PNG o JPG.")
            return

        if not self.ruta_archivo.lower().endswith((".png", ".jpg")):
            messagebox.showwarning("Atención", "Solo se pueden comprimir imágenes PNG o JPG.")
            return

        try:
            archivo_salida = rle_imagen.comprimir_a_rlebits(self.ruta_archivo)

            tamaño_original = os.path.getsize(self.ruta_archivo)
            tamaño_comprimido = os.path.getsize(archivo_salida)

            # Conversión a bits
            original_bits = tamaño_original * 8
            comprimido_bits = tamaño_comprimido * 8

            # Ahorro
            ahorro_bytes = tamaño_original - tamaño_comprimido
            ahorro_bits = ahorro_bytes * 8

            self.tamaño_original.set(f"Tamaño original: {tamaño_original} bytes ({original_bits} bits)")
            self.tamaño_comprimido.set(f"Tamaño comprimido: {tamaño_comprimido} bytes ({comprimido_bits} bits)")
            self.estado.set(f"Ahorro: {ahorro_bytes} bytes ({ahorro_bits} bits)")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al comprimir:\n{e}")




    def descomprimir(self):
        if not self.ruta_archivo:
            messagebox.showwarning("Atención", "Primero selecciona un archivo .rlebits.")
            return

        if not self.ruta_archivo.lower().endswith(".rlebits"):
            messagebox.showwarning("Atención", "Solo se pueden descomprimir archivos .rlebits.")
            return

        try:
            archivo_salida = rle_imagen.descomprimir_rlebits(self.ruta_archivo)
            self.estado.set(f"✅ Archivo descomprimido correctamente.\nGuardado en:\n{archivo_salida}")
            self.tamaño_original.set("Tamaño original: ---")
            self.tamaño_comprimido.set("Tamaño comprimido: ---")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al descomprimir:\n{e}")


if __name__ == "__main__":
    app = VentanaImagen()
    app.mainloop()
