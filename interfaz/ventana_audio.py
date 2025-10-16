# ventana_audio.py
# Interfaz Tkinter para compresión/descompresión WAV con Huffman + reproducción.
# Sin diálogos para guardar .huff: todo se genera junto al WAV original.

import os
import sys
import platform
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

# ===== Bootstrap de import (carga el módulo de lógica aunque no sea paquete) =====
try:
    from compresion_audio.huffman_audio import CompresionAudio
except ModuleNotFoundError:
    _AQUI = os.path.dirname(os.path.abspath(__file__))
    _BASES = [_AQUI, os.path.abspath(os.path.join(_AQUI, "..")), os.path.abspath(os.path.join(_AQUI, "../.."))]
    _CAND = []
    for b in _BASES:
        _pkg = os.path.join(b, "compresion_audio")
        _CAND += [os.path.join(_pkg, "huffman_audio.py"), os.path.join(b, "huffman_audio.py")]
    CompresionAudio = None
    import importlib.util
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

# ===== Reproductor =====
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
            raise FileNotFoundError("No se encontró el archivo WAV.")
        if os.path.splitext(ruta)[1].lower() != ".wav":
            raise ValueError("Solo se permite reproducir archivos .wav")
        self.detener()
        if sa is not None:
            wave_obj = sa.WaveObject.from_wave_file(ruta)
            self.play_obj = wave_obj.play()
        elif USE_WINSOUND and winsound is not None:
            winsound.PlaySound(ruta, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            raise RuntimeError("Instala simpleaudio: pip install simpleaudio")

    def pausar(self):
        if not self._aviso_pausa:
            mb.showinfo("Pausa", "Pausar detiene. Reanudar inicia desde el principio.")
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


# ===== UI =====
class App:
    APP_BG = "#f0f4f8"
    PRI = "#219ebc"
    PRI_DARK = "#023047"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Compresión de Audio (Huffman)")
        self.root.geometry("680x300")
        self.root.minsize(620, 260)
        self.root.configure(bg=self.APP_BG)

        self.rep = ReproductorAudio()
        self._ruta_wav = ""
        self._ruta_segunda = None  # "<base> (comprimido).wav"

        self._config_estilos()
        self._layout()
        self.root.protocol("WM_DELETE_WINDOW", self._al_cerrar)

    def _config_estilos(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("TFrame", background=self.APP_BG)
        s.configure("TLabel", background=self.APP_BG, foreground=self.PRI_DARK, font=("Segoe UI", 10))
        s.configure("Header.TLabel", font=("Segoe UI Semibold", 16))
        s.configure("Hint.TLabel", foreground="#499ac5")
        s.configure("TButton", padding=6)
        s.configure("Accent.TButton", foreground="white", padding=8)
        s.map("Accent.TButton",
              background=[("!disabled", self.PRI), ("active", "#1f93ad"), ("pressed", self.PRI_DARK)])

    def _layout(self):
        hdr = ttk.Frame(self.root, padding=12)
        hdr.pack(fill="x")
        ttk.Label(hdr, text="Compresión de Audio (Huffman)", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            hdr,
            text="Genera automáticamente '<base>.huff', '<base> (comprimido).wav' y '<base>_descomprimido.wav'.",
            style="Hint.TLabel", wraplength=600
        ).pack(anchor="w", pady=(2, 0))

        body = ttk.Frame(self.root, padding=12)
        body.pack(fill="both", expand=True, padx=12, pady=6)

        fila1 = ttk.Frame(body)
        fila1.grid(row=0, column=0, sticky="w", pady=(4, 8))
        ttk.Label(fila1, text="Archivo WAV:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.ent_ruta = ttk.Entry(fila1, width=50)
        self.ent_ruta.grid(row=0, column=1, sticky="w")
        ttk.Button(fila1, text="Buscar…", command=self._buscar_wav).grid(row=0, column=2, padx=(8, 0))

        fila2 = ttk.Frame(body)
        fila2.grid(row=1, column=0, sticky="w", pady=(0, 6))
        ttk.Label(fila2, text="Reproduce WAV original o la segunda versión (comprimido).",
                  style="Hint.TLabel").grid(row=0, column=0, sticky="w")

        bot = ttk.Frame(body)
        bot.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        for i in range(6):
            bot.columnconfigure(i, weight=1)

        self.btn_comp = ttk.Button(bot, text="Comprimir", style="Accent.TButton",
                                   command=self._accion_comprimir, state="disabled")
        self.btn_comp.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.btn_desc = ttk.Button(bot, text="Descomprimir", command=self._accion_descomprimir)
        self.btn_desc.grid(row=0, column=1, sticky="ew", padx=6)

        self.btn_play_orig = ttk.Button(bot, text="Reproducir original",
                                        command=self._accion_play_original, state="disabled")
        self.btn_play_orig.grid(row=0, column=2, sticky="ew", padx=6)

        self.btn_play_seg = ttk.Button(bot, text="Reproducir segunda versión",
                                       command=self._accion_play_segunda, state="disabled")
        self.btn_play_seg.grid(row=0, column=3, sticky="ew", padx=6)

        self.btn_pause = ttk.Button(bot, text="Pausar", command=self._accion_pausar)
        self.btn_pause.grid(row=0, column=4, sticky="ew", padx=6)

        self.btn_resume = ttk.Button(bot, text="Reanudar", command=self._accion_reanudar)
        self.btn_resume.grid(row=0, column=5, sticky="ew", padx=(6, 0))

    # ===== Acciones =====
    def _buscar_wav(self):
        p = fd.askopenfilename(title="Selecciona WAV", filetypes=[("WAV", "*.wav")])
        if not p:
            return
        if os.path.splitext(p)[1].lower() != ".wav":
            mb.showwarning("Formato", "Selecciona un archivo .wav")
            return
        self._ruta_wav = p
        self.ent_ruta.delete(0, tk.END)
        self.ent_ruta.insert(0, p)
        self.btn_play_orig.configure(state="normal")
        self.btn_comp.configure(state="normal")
        cand = self._ruta_wav.replace(".wav", " (comprimido).wav")
        if os.path.exists(cand):
            self._ruta_segunda = cand
            self.btn_play_seg.configure(state="normal")
        else:
            self._ruta_segunda = None
            self.btn_play_seg.configure(state="disabled")

    def _accion_play_original(self):
        if not self._ruta_wav:
            mb.showwarning("Sin archivo", "Selecciona un WAV primero.")
            return
        try:
            self.rep.reproducir_wav(self._ruta_wav)
        except Exception as e:
            mb.showerror("Reproducir", str(e))

    def _accion_play_segunda(self):
        if not self._ruta_segunda or not os.path.exists(self._ruta_segunda):
            mb.showwarning("No existe", "Primero comprime para generar la segunda versión.")
            return
        try:
            self.rep.reproducir_wav(self._ruta_segunda)
        except Exception as e:
            mb.showerror("Reproducir segunda", str(e))

    def _accion_pausar(self):
        try:
            self.rep.pausar()
        except Exception as e:
            mb.showerror("Pausar", str(e))

    def _accion_reanudar(self):
        if not self._ruta_wav:
            mb.showwarning("Sin archivo", "Selecciona un WAV primero.")
            return
        try:
            self.rep.reanudar(self._ruta_wav)
        except Exception as e:
            mb.showerror("Reanudar", str(e))

    def _accion_comprimir(self):
        if not self._ruta_wav:
            mb.showwarning("Sin archivo", "Selecciona un WAV primero.")
            return
        if os.path.splitext(self._ruta_wav)[1].lower() != ".wav":
            mb.showwarning("Formato", "Selecciona un archivo .wav")
            return
        try:
            comp = CompresionAudio(self._ruta_wav)
            ruta_huff, wav_ver = comp.comprimir()  # crea <base>.huff y <base> (comprimido).wav
            # Guardar también una copia con nombre alterno (opcional)
            # Si no quieres copia, comenta el siguiente bloque:
            base_dir = os.path.dirname(self._ruta_wav)
            base_name = os.path.splitext(os.path.basename(self._ruta_wav))[0]
            sugerido_seg = os.path.join(base_dir, f"{base_name} (segunda versión).wav")
            # Si no existe la copia “(segunda versión)” y quieres duplicar:
            if not os.path.exists(sugerido_seg) and os.path.exists(wav_ver):
                try:
                    shutil.copyfile(wav_ver, sugerido_seg)
                    self._ruta_segunda = sugerido_seg
                except Exception:
                    # Si falla, usa el “(comprimido).wav”
                    self._ruta_segunda = wav_ver
            else:
                self._ruta_segunda = wav_ver

            self.btn_play_seg.configure(state="normal")
            mb.showinfo("Listo",
                        f"Generado:\n- {os.path.basename(ruta_huff)} (interno)\n- {os.path.basename(self._ruta_segunda)}")
        except Exception as e:
            mb.showerror("Comprimir", str(e))

    def _accion_descomprimir(self):
        # Intenta automáticamente <base>.huff del WAV seleccionado
        if self._ruta_wav:
            huff_auto = os.path.splitext(self._ruta_wav)[0] + ".huff"
        else:
            huff_auto = ""

        if huff_auto and os.path.exists(huff_auto):
            ruta_huff = huff_auto
        else:
            # Si no hay WAV o no existe su .huff, deja elegir uno
            ruta_huff = fd.askopenfilename(title="Selecciona .huff",
                                           filetypes=[("Huffman (.huff)", "*.huff"), ("Todos", "*.*")])
            if not ruta_huff:
                return

        try:
            comp = CompresionAudio(self._ruta_wav or "dummy.wav")
            wav_out = comp.extraerArchivo(ruta_huff)  # crea <base>_descomprimido.wav
            mb.showinfo("Listo", f"Descomprimido en:\n{wav_out}")
        except Exception as e:
            mb.showerror("Descomprimir", str(e))

    def _al_cerrar(self):
        try:
            self.rep.detener()
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
