import os
import platform
import tempfile
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, filedialog as fd, messagebox as mb

try:
    from compresion_audio.huffman_audio import CompresionAudio
except ModuleNotFoundError:
    import importlib.util
    _AQUI = os.path.dirname(os.path.abspath(__file__))
    _BASES = [_AQUI, os.path.abspath(os.path.join(_AQUI, "..")), os.path.abspath(os.path.join(_AQUI, "../.."))]
    _CAND = []
    for b in _BASES:
        _pkg = os.path.join(b, "compresion_audio")
        _CAND += [os.path.join(_pkg, "huffman_audio.py"), os.path.join(b, "huffman_audio.py")]
    CompresionAudio = None
    for ruta_py in _CAND:
        if os.path.exists(ruta_py):
            spec = importlib.util.spec_from_file_location("huffman_audio_fallback", ruta_py)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            CompresionAudio = getattr(mod, "CompresionAudio", None)
            if CompresionAudio:
                break
    if CompresionAudio is None:
        raise ModuleNotFoundError("No se encontró compresion_audio/huffman_audio.py")

try:
    import simpleaudio as sa
except Exception:
    sa = None

USE_WINSOUND = sa is None and platform.system().lower().startswith("win")
if USE_WINSOUND:
    try:
        import winsound
    except Exception:
        winsound = None
        USE_WINSOUND = False


class ReproductorAudio:
    def __init__(self):
        self.play_obj = None
        self._aviso_pausa = False

    def reproducir_wav(self, ruta: str):
        if not os.path.exists(ruta):
            raise FileNotFoundError("No se encontró el archivo")
        if os.path.splitext(ruta)[1].lower() != ".wav":
            raise ValueError("Solo se permiten archivos WAV")
        self.detener()
        if sa is not None:
            wave_obj = sa.WaveObject.from_wave_file(ruta)
            self.play_obj = wave_obj.play()
        elif USE_WINSOUND and winsound is not None:
            winsound.PlaySound(ruta, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            raise RuntimeError("Instala simpleaudio para reproducir audio")

    def pausar(self):
        if not self._aviso_pausa:
            mb.showinfo("Pausa", "Pausar reinicia el audio al reanudar.")
            self._aviso_pausa = True
        self.detener()

    def reanudar(self, ruta: str):
        self.reproducir_wav(ruta)

    def detener(self):
        if sa is not None and self.play_obj is not None:
            try:
                self.play_obj.stop()
            except Exception:
                pass
            self.play_obj = None
        if USE_WINSOUND and winsound is not None:
            try:
                winsound.PlaySound(None, 0)
            except Exception:
                pass

def create_audio_frame(parent, show_frame_callback):
    frame = ttk.Frame(parent)
    
    rep = ReproductorAudio()
    ruta_wav = tk.StringVar()
    ruta_flac = tk.StringVar()

    # --- Título ---
    ttk.Label(
        frame,
        text="Compresión de Audio (WAV ↔ FLAC por Huffman)",
        font=("Segoe UI Semibold", 16)
    ).pack(anchor="w", pady=(10, 4), padx=20)

    ttk.Label(
        frame,
        text="Selecciona un archivo WAV para comprimir o un FLAC para descomprimir.",
        foreground="#499ac5"
    ).pack(anchor="w", padx=20)

    # --- Cuerpo ---
    body = ttk.Frame(frame, padding=20)
    body.pack(fill="both", expand=True)

    # Campo WAV
    fila1 = ttk.Frame(body)
    fila1.pack(fill="x", pady=4)
    ttk.Label(fila1, text="Archivo WAV:").pack(side="left")
    wav_entry = ttk.Entry(fila1, textvariable=ruta_wav, width=50)
    wav_entry.pack(side="left", padx=8, fill="x", expand=True)
    ttk.Button(fila1, text="Buscar...", command=lambda: buscar_wav()).pack(side="left")

    # Campo FLAC
    fila2 = ttk.Frame(body)
    fila2.pack(fill="x", pady=4)
    ttk.Label(fila2, text="Archivo FLAC:").pack(side="left")
    flac_entry = ttk.Entry(fila2, textvariable=ruta_flac, width=50)
    flac_entry.pack(side="left", padx=8, fill="x", expand=True)
    ttk.Button(fila2, text="Buscar FLAC...", command=lambda: buscar_flac()).pack(side="left")

    # --- Botones principales ---
    botones = ttk.Frame(body)
    botones.pack(fill="x", pady=10)

    ttk.Button(botones, text="Comprimir WAV → FLAC", command=lambda: comprimir()).pack(side="left", padx=6)
    ttk.Button(botones, text="Descomprimir FLAC → WAV", command=lambda: descomprimir()).pack(side="left", padx=6)
    ttk.Button(botones, text="▶ Reproducir WAV", command=lambda: reproducir_wav()).pack(side="left", padx=6)
    ttk.Button(botones, text="⏸ Pausar", command=lambda: rep.pausar()).pack(side="left", padx=6)
    ttk.Button(botones, text="🔁 Reanudar", command=lambda: rep.reanudar(ruta_wav.get())).pack(side="left", padx=6)

    # --- Botón de regreso ---
    ttk.Button(
        frame,
        text="🔙 Regresar al menú principal",
        command=lambda: show_frame_callback("Menú")
    ).pack(anchor="e", padx=20, pady=(0, 10))

    # --- Estado ---
    estado = ttk.Label(frame, text="Listo.", foreground="#499ac5")
    estado.pack(anchor="w", padx=20, pady=(0, 10))

    # === Funciones internas ===
    def set_estado(msg):
        estado.config(text=msg)
        frame.update_idletasks()

    def buscar_wav():
        p = fd.askopenfilename(title="Selecciona WAV", filetypes=[("WAV", "*.wav")])
        if not p:
            return
        if not p.lower().endswith(".wav"):
            mb.showwarning("Formato", "Selecciona un archivo WAV válido.")
            return
        ruta_wav.set(p)
        set_estado(f"Archivo seleccionado: {os.path.basename(p)}")

    def buscar_flac():
        p = fd.askopenfilename(title="Selecciona FLAC", filetypes=[("FLAC", "*.flac")])
        if not p:
            return
        if not p.lower().endswith(".flac"):
            mb.showwarning("Formato", "Selecciona un archivo FLAC válido.")
            return
        ruta_flac.set(p)
        set_estado(f"Archivo seleccionado: {os.path.basename(p)}")

    def reproducir_wav():
        if not ruta_wav.get():
            mb.showwarning("Sin archivo", "Selecciona un archivo WAV primero.")
            return
        try:
            rep.reproducir_wav(ruta_wav.get())
            set_estado(f"Reproduciendo: {os.path.basename(ruta_wav.get())}")
        except Exception as e:
            mb.showerror("Error", str(e))

    def comprimir():
        if not ruta_wav.get():
            mb.showwarning("Sin archivo", "Selecciona un WAV para comprimir.")
            return
        try:
            comp = CompresionAudio(ruta_wav.get())
            res = comp.comprimir()
            ruta_flac.set(res["flac"])
            mb.showinfo("Éxito", "Archivo comprimido correctamente.")
            set_estado("Compresión completada.")
        except Exception as e:
            mb.showerror("Error", str(e))
            set_estado("Error durante compresión.")

    def descomprimir():
        if not ruta_flac.get():
            mb.showwarning("Sin archivo", "Selecciona un FLAC para descomprimir.")
            return
        try:
            comp = CompresionAudio("dummy.wav")
            comp.extraerArchivo(ruta_flac.get())
            mb.showinfo("Éxito", "Archivo descomprimido correctamente.")
            set_estado("Descompresión completada.")
        except Exception as e:
            mb.showerror("Error", str(e))
            set_estado("Error durante descompresión.")

    return frame


