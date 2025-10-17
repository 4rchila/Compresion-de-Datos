import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from compresion_imagen import rle_imagen

def create_imagen_frame(parent, show_frame_callback):
    frame = ctk.CTkFrame(parent)

    # Variables
    ruta_archivo = ctk.StringVar()
    tamaño_original = ctk.StringVar(value="Tamaño original: ---")
    tamaño_comprimido = ctk.StringVar(value="Tamaño comprimido: ---")
    estado = ctk.StringVar(value="Seleccione una imagen PNG, JPG o un archivo RLEBITS para comenzar.")

    # Encabezado
    header_frame = ctk.CTkFrame(frame, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=20)
    
    btn_volver_inicio = ctk.CTkButton(
        header_frame,
        text="← Volver al Inicio",
        fg_color="#172b54",
        border_color="#6de0ff",
        border_width=1,
        hover_color="#6de0ff",
        text_color="white",
        width=120,
        command=lambda: show_frame_callback("Home")  # Cambia al frame principal
    )
    btn_volver_inicio.pack(side="left")
    
    # Título de la pestaña (puedes personalizar el texto)
    ctk.CTkLabel(
        header_frame,
        text="NOMBRE DE LA PESTAÑA 💾",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color="#6de0ff"
    ).pack(side="left", padx=20)

    titulo = ctk.CTkLabel(frame, text="Compresión de Imágenes con RLE",
                          font=ctk.CTkFont(size=20, weight="bold"),
                          text_color="#A8D0E6")
    titulo.pack(pady=20)

    # Botones principales
    frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
    frame_botones.pack(pady=10)

    btn_cargar = ctk.CTkButton(frame_botones, text="📂 Cargar Archivo", width=160,
                               command=lambda: cargar_archivo())
    btn_cargar.grid(row=0, column=0, padx=10)

    btn_comprimir = ctk.CTkButton(frame_botones, text="🗜️ Comprimir", width=160,
                                  command=lambda: comprimir())
    btn_comprimir.grid(row=0, column=1, padx=10)

    btn_descomprimir = ctk.CTkButton(frame_botones, text="💾 Descomprimir", width=160,
                                     command=lambda: descomprimir())
    btn_descomprimir.grid(row=0, column=2, padx=10)

    # Información del archivo
    label_ruta = ctk.CTkLabel(frame, text="Archivo seleccionado: ---", wraplength=550,
                              text_color="#C9D6E3", font=ctk.CTkFont(size=13))
    label_ruta.pack(pady=10)

    # Tamaños
    frame_tamaños = ctk.CTkFrame(frame, fg_color="#1B2A41", corner_radius=12)
    frame_tamaños.pack(pady=15, padx=20, fill="x")

    lbl_original = ctk.CTkLabel(frame_tamaños, textvariable=tamaño_original,
                                text_color="#A8D0E6", font=ctk.CTkFont(size=14))
    lbl_original.pack(pady=5)

    lbl_comprimido = ctk.CTkLabel(frame_tamaños, textvariable=tamaño_comprimido,
                                  text_color="#A8D0E6", font=ctk.CTkFont(size=14))
    lbl_comprimido.pack(pady=5)

    # Estado
    estado_label = ctk.CTkLabel(frame, textvariable=estado, wraplength=550,
                                text_color="#98C1D9", font=ctk.CTkFont(size=13))
    estado_label.pack(pady=15)

    # ==== Funciones internas ====
    def cargar_archivo():
        ruta = filedialog.askopenfilename(
            title="Selecciona una imagen o archivo comprimido",
            filetypes=[("Imágenes PNG y JPG o Archivos RLEBITS", "*.png;*.jpg;*.rlebits"),
                       ("Imágenes", "*.png;*.jpg"),
                       ("Archivos RLE", "*.rlebits")]
        )
        if ruta:
            ruta_archivo.set(ruta)
            nombre = os.path.basename(ruta)
            ext = os.path.splitext(nombre)[1].lower()
            label_ruta.configure(text=f"Archivo seleccionado: {nombre}")
            tamaño_original.set("Tamaño original: ---")
            tamaño_comprimido.set("Tamaño comprimido: ---")
            if ext in [".png", ".jpg"]:
                estado.set("Imagen cargada correctamente. Lista para comprimir.")
            elif ext == ".rlebits":
                estado.set("Archivo RLE cargado correctamente. Listo para descomprimir.")
            else:
                estado.set("Formato no compatible.")
        else:
            estado.set("No se seleccionó ningún archivo.")

    def comprimir():
        if not ruta_archivo.get():
            messagebox.showwarning("Atención", "Primero selecciona una imagen PNG o JPG.")
            return
        if not ruta_archivo.get().lower().endswith((".png", ".jpg")):
            messagebox.showwarning("Atención", "Solo se pueden comprimir imágenes PNG o JPG.")
            return
        try:
            archivo_salida = rle_imagen.comprimir_a_rlebits(ruta_archivo.get())
            tamaño_o = os.path.getsize(ruta_archivo.get())
            tamaño_c = os.path.getsize(archivo_salida)
            tamaño_original.set(f"Tamaño original: {tamaño_o} bytes ({tamaño_o*8} bits)")
            tamaño_comprimido.set(f"Tamaño comprimido: {tamaño_c} bytes ({tamaño_c*8} bits)")
            estado.set(f"Ahorro: {tamaño_o - tamaño_c} bytes ({(tamaño_o - tamaño_c)*8} bits)")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al comprimir:\n{e}")

    def descomprimir():
        if not ruta_archivo.get():
            messagebox.showwarning("Atención", "Primero selecciona un archivo .rlebits.")
            return
        if not ruta_archivo.get().lower().endswith(".rlebits"):
            messagebox.showwarning("Atención", "Solo se pueden descomprimir archivos .rlebits.")
            return
        try:
            archivo_salida = rle_imagen.descomprimir_rlebits(ruta_archivo.get())
            estado.set(f"✅ Archivo descomprimido correctamente.\nGuardado en:\n{archivo_salida}")
            tamaño_original.set("Tamaño original: ---")
            tamaño_comprimido.set("Tamaño comprimido: ---")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al descomprimir:\n{e}")

    return frame
