import tkinter as _tkinter
from tkinter import ttk as _ttk

# colores
APP_BG   = "#f0f4f8"
PRI      = "#219ebc"

PRI_DARK = "#023047"

# vetnana 
ventana = _tkinter.Tk()
ventana.title("Reproductor de Audio")

ventana.geometry("640x360")

ventana.minsize(560, 320)
ventana.configure(bg=APP_BG)

ventana.resizable(1, 1)

# estilos
style = _ttk.Style()
try:
    style.theme_use("clam")

except _tkinter.TclError:
    pass

style.configure("TFrame", background=APP_BG)
style.configure("TLabel", background=APP_BG, foreground=PRI_DARK, font=("Segoe UI", 10))
style.configure("Header.TLabel", font=("Segoe UI Semibold", 18))

style.configure("Hint.TLabel", foreground="#499ac5")

style.configure("TButton", padding=8)
style.configure(" Accent.TButton", foreground="white", padding=10)
style.map(" Accent.TButton",
          background=[("!disabled", PRI), ("active", "#1f93ad"), ("pressed", PRI_DARK)])

# encabezado 
_encabezado = _ttk.Frame(ventana, padding=16, style="TFrame")
_encabezado. pack(fill="x")
_tt1 = _ttk.Label(_encabezado, text="Compresión de Audio", style="Header.TLabel")
_tt1.pack(anchor="w")
_tt2 = _ttk.Label(_encabezado,
                  text="Selecciona un audio y elige formato",
                  style="Hint.TLabel", wraplength=600)
_tt2.pack(anchor="w", pady=(2, 0))

# 
_cuerpo = _ttk.Frame(ventana, padding=16, style="TFrame")
_cuerpo.pack(fill="both", expand=True, padx=16, pady=8)

#  Busca
fila1 = _ttk.Frame(_cuerpo, style="TFrame")
fila1.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(6, 10))
fila1.columnconfigure(1, weight=1)

_lbl_audio = _ttk.Label(fila1, text="Archivo de audio:")
_lbl_audio.grid(row=0, column=0, sticky="w", padx=(0, 8))

_ent_audio = _ttk.Entry(fila1)
_ent_audio.grid(row=0, column=1, sticky="ew")
_btn_buscar = _ttk.Button(fila1, text="Buscar…", command=lambda: None)
_btn_buscar.grid(row=0, column=2, padx=(8, 0))

# ´ti´po de audio  
fila2 = _ttk.Frame(_cuerpo, style="TFrame")
fila2.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 8))
fila2.columnconfigure(1, weight=1)

_lbl_codec = _ttk.Label(fila2, text="Tipo de audio :")
_lbl_codec.grid(row=0, column=0, sticky="w", padx=(0, 8))

_cb_codec = _ttk.Combobox(fila2, state="readonly",
                          values=["MP3", "  "], width=12)
_cb_codec.set("MP3")
_cb_codec.grid(row=0, column=1, sticky="w")


# acciones comprimir y comparar 
fila4 = _ttk.Frame(_cuerpo, style="TFrame")

fila4.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(6, 0))
fila4.columnconfigure(0, weight=1)
fila4.columnconfigure(1, weight=1)

_btn_comprimir = _ttk.Button(fila4, text="Comprimir", style="Accent.TButton", command=lambda: None)
_btn_comprimir.grid(row=0, column=0, sticky="ew", padx=(0, 6))

_btn_comparar = _ttk.Button(fila4, text="Comparar versiones", command=lambda: None)
_btn_comparar.grid(row=0, column=1, sticky="ew", padx=(6, 0))


## loop de v4entana
ventana.mainloop()



## REPRODUCIR AUDIOS 
import os
try:
    import simpleaudio as sa
except ImportError:
    sa = None

class ReproductorAudio:
    def __init__(self):
        self.play_obj = None
        self.wave_obj = None

    def reproducir(self, ruta_wav):
        if sa is None:
            raise RuntimeError("Instala simpleaudio: pip install simpleaudio")
        if self.play_obj is not None:
            try:
                self.play_obj.stop()
            except Exception:
                pass
        self.wave_obj = sa.WaveObject.from_wave_file(ruta_wav)
        self.play_obj = self.wave_obj.play()

    

def on_archivo_insertado(ruta_entrada):
    rep = ReproductorAudio()

    ruta = ruta_entrada
    
    ext = os.path.splitext(ruta_entrada)[1].lower()
    if ext != ".wav":
        salida = os.path.splitext(ruta_entrada)[0] + "_dec.wav"
        
        HuffmanAudio().descompresion_archivo(ruta_entrada, salida)
        
        ruta = salida
    rep.reproducir(ruta)
    return rep
