# app_interfaz.py
# Interfaz Tkinter para compresión Huffman: WAV ↔ .huff ↔ WAV
import os
import platform
import tempfile
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

try:
    # Lógica Huffman (este archivo debe existir)
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

# ===== Reproductor simple (WAV) =====
try:
    import simpleaudio as sa  # pip install simpleaudio
except Exception:
    sa = None

USE_WINSOUND = sa is None and platform.system().lower().startswith("win")
if USE_WINSOUND:
    try:
        import winsound
    except Exception:
        winsound = None


class ReproductorAudio:
    def __init__(self):
        self.play_obj = None
        self._aviso_pausa = False

    def reproducir_wav(self, ruta: str):
        if not os.path.exists(ruta):
            raise FileNotFoundError("No se encontró el archivo WAV.")
        if os.path.splitext(ruta)[1].lower() != ".wav":
            raise ValueError("Solo se puede reproducir .wav.")
        self.detener()
        if sa is not None:
            wave_obj = sa.WaveObject.from_wave_file(ruta)
            self.play_obj = wave_obj.play()
        elif USE_WINSOUND and winsound is not None:
            winsound.PlaySound(ruta, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            raise RuntimeError("Para reproducir instala simpleaudio: pip install simpleaudio")

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
        self.root.title("Compresor de Audio (Huffman): WAV ↔ .huff (sin pérdida)")
        self.root.geometry("760x360")
        self.root.minsize(680, 320)
        self.root.configure(bg=self.APP_BG)

        self.rep = ReproductorAudio()
        self._ruta_wav = ""
        self._ruta_huff = None
        self._tmp_convert_wav = None  # no lo usamos aquí, pero lo dejamos para consistencia

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
        ttk.Label(hdr, text="WAV ↔ .huff (Huffman sin pérdida)", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            hdr,
            text="• Comprimir: genera '<original>.huff' y '<original> (comprimido).wav'  • Descomprimir: '<archivo>.huff' → '<archivo>_descomprimido.wav'",
            style="Hint.TLabel", wraplength=720
        ).pack(anchor="w", pady=(2, 0))

        body = ttk.Frame(self.root, padding=12)
        body.pack(fill="both", expand=True, padx=12, pady=6)

        fila1 = ttk.Frame(body)
        fila1.grid(row=0, column=0, sticky="w", pady=(4, 8))
        ttk.Label(fila1, text="Archivo WAV:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.ent_ruta = ttk.Entry(fila1, width=60)
        self.ent_ruta.grid(row=0, column=1, sticky="w")
        ttk.Button(fila1, text="Buscar…", command=self._buscar_wav).grid(row=0, column=2, padx=(8, 0))

        fila2 = ttk.Frame(body)
        fila2.grid(row=1, column=0, sticky="w", pady=(0, 6))
        ttk.Label(fila2, text="Reproduce el WAV original, el WAV (comprimido) o el WAV descomprimido.",
                  style="Hint.TLabel").grid(row=0, column=0, sticky="w")

        bot = ttk.Frame(body)
        bot.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        for i in range(7):
            bot.columnconfigure(i, weight=1)

        self.btn_comp = ttk.Button(bot, text="Comprimir → .huff", style="Accent.TButton",
                                   command=self._accion_comprimir, state="disabled")
        self.btn_comp.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.btn_desc = ttk.Button(bot, text="Descomprimir .huff → WAV", command=self._accion_descomprimir)
        self.btn_desc.grid(row=0, column=1, sticky="ew", padx=6)

        self.btn_play_orig = ttk.Button(bot, text="Reproducir WAV original",
                                        command=self._accion_play_original, state="disabled")
        self.btn_play_orig.grid(row=0, column=2, sticky="ew", padx=6)

        self.btn_play_comp = ttk.Button(bot, text="Reproducir WAV (comprimido)",
                                        command=self._accion_play_comprimido, state="disabled")
        self.btn_play_comp.grid(row=0, column=3, sticky="ew", padx=6)

        self.btn_play_desc = ttk.Button(bot, text="Reproducir WAV descomprimido",
                                        command=self._accion_play_descomp, state="disabled")
        self.btn_play_desc.grid(row=0, column=4, sticky="ew", padx=6)

        self.btn_pause = ttk.Button(bot, text="Pausar", command=self._accion_pausar)
        self.btn_pause.grid(row=0, column=5, sticky="ew", padx=6)

        self.btn_resume = ttk.Button(bot, text="Reanudar", command=self._accion_reanudar)
        self.btn_resume.grid(row=0, column=6, sticky="ew", padx=(6, 0))

    # ====================== Acciones ======================
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

        # Habilitar botones de reproducción si existen archivos generados
        base = os.path.splitext(self._ruta_wav)[0]
        wav_comp = f"{base} (comprimido).wav"
        self.btn_play_comp.configure(state="normal" if os.path.exists(wav_comp) else "disabled")

        wav_desc = f"{base}_descomprimido.wav"
        self.btn_play_desc.configure(state="normal" if os.path.exists(wav_desc) else "disabled")

    def _accion_play_original(self):
        if not self._ruta_wav:
            mb.showwarning("Sin archivo", "Selecciona un WAV primero.")
            return
        try:
            self.rep.reproducir_wav(self._ruta_wav)
        except Exception as e:
            mb.showerror("Reproducir WAV", str(e))

    def _accion_play_comprimido(self):
        if not self._ruta_wav:
            mb.showwarning("Sin archivo", "Selecciona un WAV primero.")
            return
        base = os.path.splitext(self._ruta_wav)[0]
        wav_comp = f"{base} (comprimido).wav"
        if not os.path.exists(wav_comp):
            mb.showwarning("No existe", "Aún no hay WAV (comprimido). Pulsa Comprimir primero.")
            return
        try:
            self.rep.reproducir_wav(wav_comp)
        except Exception as e:
            mb.showerror("Reproducir WAV (comprimido)", str(e))

    def _accion_play_descomp(self):
        if not self._ruta_wav:
            mb.showwarning("Sin archivo", "Selecciona un WAV primero (para ubicar la base).")
            return
        base = os.path.splitext(self._ruta_wav)[0]
        wav_desc = f"{base}_descomprimido.wav"
        if not os.path.exists(wav_desc):
            # si no existe, intenta deducir desde .huff
            ruta_huff = base + ".huff"
            if os.path.exists(ruta_huff):
                comp = CompresionAudio(self._ruta_wav)
                try:
                    wav_out = comp.extraerArchivo(ruta_huff)
                    wav_desc = wav_out
                except Exception as e:
                    mb.showerror("Descomprimir para reproducir", str(e))
                    return
            else:
                mb.showwarning("No existe", "No encuentro el WAV descomprimido.")
                return
        try:
            self.rep.reproducir_wav(wav_desc)
        except Exception as e:
            mb.showerror("Reproducir WAV descomprimido", str(e))

    def _accion_pausar(self):
        try:
            self.rep.pausar()
        except Exception as e:
            mb.showerror("Pausar", str(e))

    def _accion_reanudar(self):
        # Reanuda sobre el WAV original
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
            ruta_huff, wav_ver = comp.comprimir()  # crea <base>.huff y "<base> (comprimido).wav"
            self._ruta_huff = ruta_huff
            self.btn_play_comp.configure(state="normal" if os.path.exists(wav_ver) else "disabled")
            mb.showinfo("Listo", f"Generados:\n- {os.path.basename(ruta_huff)}\n- {os.path.basename(wav_ver)}")
        except Exception as e:
            mb.showerror("Comprimir (Huffman)", str(e))

    def _accion_descomprimir(self):
        # Si hay WAV cargado, intenta su <base>.huff; si no, pide uno
        ruta_huff = ""
        if self._ruta_wav:
            ruta_huff = os.path.splitext(self._ruta_wav)[0] + ".huff"
        if not ruta_huff or not os.path.exists(ruta_huff):
            ruta_huff = fd.askopenfilename(title="Selecciona .huff",
                                           filetypes=[("HUFFMAN", "*.huff"), ("Todos", "*.*")])
            if not ruta_huff:
                return
        try:
            # Para extraer no importa que self._ruta_wav exista; se usa solo para base
            comp = CompresionAudio(self._ruta_wav or "salida.wav")
            wav_out = comp.extraerArchivo(ruta_huff)  # <base>_descomprimido.wav
            self.btn_play_desc.configure(state="normal" if os.path.exists(wav_out) else "disabled")
            mb.showinfo("Listo", f"Descomprimido en:\n{wav_out}")
        except Exception as e:
            mb.showerror("Descomprimir (Huffman)", str(e))

    def _al_cerrar(self):
        try:
            self.rep.detener()
        except Exception:
            pass
        # (No hay temporales que limpiar acá)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
