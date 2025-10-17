# app_interfaz.py
import os
import platform
import tempfile
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

# ===== Importa tu lógica Huffman =====
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
        self.root.title("Compresión de Audio (WAV ↔ FLAC por Huffman)")
        self.root.geometry("760x360")
        self.root.minsize(680, 320)
        self.root.configure(bg=self.APP_BG)

        self.rep = ReproductorAudio()
        self._ruta_wav = ""
        self._ruta_flac = None
        self._ultima_descomp = None   # última ruta WAV creada al descomprimir
        self._temp_wavs = []          # temporales para reproducción desde FLAC

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
        ttk.Label(hdr, text="Compresión de Audio (WAV ↔ FLAC por Huffman)", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            hdr,
            text="Genera copia WAV, archivo .flac (contenedor Huffman) y WAV descomprimido.",
            style="Hint.TLabel", wraplength=700
        ).pack(anchor="w", pady=(2, 0))

        body = ttk.Frame(self.root, padding=12)
        body.pack(fill="both", expand=True, padx=12, pady=6)

        # Selección de archivo WAV
        fila1 = ttk.Frame(body)
        fila1.grid(row=0, column=0, sticky="w", pady=(4, 8))
        ttk.Label(fila1, text="Archivo WAV:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.ent_ruta = ttk.Entry(fila1, width=60)
        self.ent_ruta.grid(row=0, column=1, sticky="w")
        ttk.Button(fila1, text="Buscar…", command=self._buscar_wav).grid(row=0, column=2, padx=(8, 0))

        # Selección de archivo FLAC
        fila3 = ttk.Frame(body)
        fila3.grid(row=1, column=0, sticky="w", pady=(0, 8))
        ttk.Label(fila3, text="Archivo FLAC:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.ent_ruta_flac = ttk.Entry(fila3, width=60)
        self.ent_ruta_flac.grid(row=0, column=1, sticky="w")
        ttk.Button(fila3, text="Buscar FLAC…", command=self._buscar_flac).grid(row=0, column=2, padx=(8, 0))

        # Info
        fila2 = ttk.Frame(body)
        fila2.grid(row=2, column=0, sticky="w", pady=(0, 6))
        ttk.Label(fila2, text="Reproduce WAV .",
                  style="Hint.TLabel").grid(row=0, column=0, sticky="w")

        # Botones principales
        bot = ttk.Frame(body)
        bot.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        for i in range(7):
            bot.columnconfigure(i, weight=1)

        self.btn_comp = ttk.Button(bot, text="Comprimir WAV → FLAC", style="Accent.TButton",
                                   command=self._accion_comprimir, state="disabled")
        self.btn_comp.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.btn_desc = ttk.Button(bot, text="Descomprimir FLAC → WAV",
                                   command=self._accion_descomprimir)
        self.btn_desc.grid(row=0, column=1, sticky="ew", padx=6)

        self.btn_play_orig = ttk.Button(bot, text="Reproducir WAV ",
                                        command=self._accion_play_original, state="disabled")
        self.btn_play_orig.grid(row=0, column=2, sticky="ew", padx=6)

        self.btn_play_seg = ttk.Button(bot, text="Reproducir FLAC (temporal)",
                                       command=self._accion_play_desde_flac, state="disabled")
        self.btn_play_seg.grid(row=0, column=3, sticky="ew", padx=6)

        self.btn_pause = ttk.Button(bot, text="Pausar", command=self._accion_pausar)
        self.btn_pause.grid(row=0, column=4, sticky="ew", padx=6)

        self.btn_resume = ttk.Button(bot, text="Reanudar", command=self._accion_reanudar)
        self.btn_resume.grid(row=0, column=5, sticky="ew", padx=6)

        self.btn_comp_ver = ttk.Button(bot, text="Comparar versiones",
                                       command=self._accion_comparar)
        self.btn_comp_ver.grid(row=0, column=6, sticky="ew", padx=(6, 0))

        # Estado inferior
        self.lbl_estado = ttk.Label(self.root, text="Listo.", style="Hint.TLabel")
        self.lbl_estado.pack(anchor="w", padx=16, pady=(8, 12))

    # ===== Util =====
    def _set_estado(self, msg: str):
        self.lbl_estado.config(text=msg)
        self.root.update_idletasks()

    def _temp_wav_path(self) -> str:
        fd_tmp = tempfile.NamedTemporaryFile(prefix="flac_tmp_", suffix=".wav", delete=False)
        ruta = fd_tmp.name
        fd_tmp.close()
        self._temp_wavs.append(ruta)
        return ruta

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
        # ¿Existe su FLAC correspondiente?
        cand = os.path.splitext(self._ruta_wav)[0] + ".flac"
        if os.path.exists(cand):
            self._ruta_flac = cand
            self.ent_ruta_flac.delete(0, tk.END)
            self.ent_ruta_flac.insert(0, cand)
            self.btn_play_seg.configure(state="normal")
        else:
            self._ruta_flac = None
            self.btn_play_seg.configure(state="disabled")

    def _buscar_flac(self):
        p = fd.askopenfilename(title="Selecciona FLAC", filetypes=[("FLAC", "*.flac")])
        if not p:
            return
        if os.path.splitext(p)[1].lower() != ".flac":
            mb.showwarning("Formato", "Selecciona un archivo .flac")
            return
        self.ent_ruta_flac.delete(0, tk.END)
        self.ent_ruta_flac.insert(0, p)
        self._ruta_flac = p
        self.btn_play_seg.configure(state="normal")

    def _accion_play_original(self):
        if not self._ruta_wav:
            mb.showwarning("Sin archivo", "Selecciona un WAV primero.")
            return
        try:
            self.rep.reproducir_wav(self._ruta_wav)
            self._set_estado(f"Reproduciendo: {os.path.basename(self._ruta_wav)}")
        except Exception as e:
            mb.showerror("Reproducir", str(e))

    def _accion_play_desde_flac(self):
        ruta_flac = self._ruta_flac or self.ent_ruta_flac.get().strip()
        if not ruta_flac:
            mb.showwarning("Sin FLAC", "Selecciona o genera un archivo FLAC primero.")
            return
        if not os.path.exists(ruta_flac):
            mb.showwarning("No existe", f"No se encontró el archivo FLAC: {ruta_flac}")
            return
        try:
            temp_wav = self._temp_wav_path()
            comp = CompresionAudio("dummy.wav")
            wav_descomprimido = comp.extraerArchivo(ruta_flac, temp_wav)
            self.rep.reproducir_wav(wav_descomprimido)
            self._set_estado(f"Reproduciendo (temporal): {os.path.basename(wav_descomprimido)}")
        except NotImplementedError as e:
            mb.showerror("Formato WAV", str(e))
        except Exception as e:
            mb.showerror("Reproducir FLAC", f"Error al descomprimir FLAC: {str(e)}")

    def _accion_pausar(self):
        try:
            self.rep.pausar()
            self._set_estado("Pausado.")
        except Exception as e:
            mb.showerror("Pausar", str(e))

    def _accion_reanudar(self):
        if not self._ruta_wav:
            mb.showwarning("Sin archivo", "Selecciona un WAV primero.")
            return
        try:
            self.rep.reanudar(self._ruta_wav)
            self._set_estado("Reanudando desde el inicio.")
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
            self._set_estado("Comprimiendo...")
            comp = CompresionAudio(self._ruta_wav)
            res = comp.comprimir()  # dict: {"wav_copia": ..., "flac": ...}
            self._ruta_flac = res["flac"]
            self.ent_ruta_flac.delete(0, tk.END)
            self.ent_ruta_flac.insert(0, self._ruta_flac)
            self.btn_play_seg.configure(state="normal")
            msg = "WAV comprimido a FLAC.\n"
            if res.get("wav_copia"):
                msg += f"Copia WAV: {os.path.basename(res['wav_copia'])}\n"
            msg += f"FLAC: {os.path.basename(self._ruta_flac)}"
            mb.showinfo("Listo", msg)
            self._set_estado("Compresión finalizada.")
        except NotImplementedError as e:
            mb.showerror("Formato WAV", str(e))
            self._set_estado("Error de formato WAV.")
        except Exception as e:
            mb.showerror("Comprimir", str(e))
            self._set_estado("Error al comprimir.")

    def _accion_descomprimir(self):
        ruta_flac = self.ent_ruta_flac.get().strip() or self._ruta_flac
        if not ruta_flac:
            if self._ruta_wav:
                ruta_flac = os.path.splitext(self._ruta_wav)[0] + ".flac"
            else:
                mb.showwarning("Sin archivo", "Selecciona un archivo FLAC para descomprimir.")
                return

        if not os.path.exists(ruta_flac):
            mb.showwarning("No existe", f"No se encontró el archivo FLAC: {ruta_flac}")
            return

        try:
            self._set_estado("Descomprimiendo...")
            comp = CompresionAudio("dummy.wav")
            wav_out = comp.extraerArchivo(ruta_flac)  # crea la tercera copia WAV
            self._ultima_descomp = wav_out
            self.btn_play_seg.configure(state="normal")
            mb.showinfo("Listo", f"FLAC descomprimido a WAV:\n{os.path.basename(wav_out)}")
            self._set_estado("Descompresión finalizada.")
        except NotImplementedError as e:
            mb.showerror("Formato WAV", str(e))
            self._set_estado("Error de formato WAV.")
        except Exception as e:
            mb.showerror("Descomprimir", str(e))
            self._set_estado("Error al descomprimir.")

    def _accion_comparar(self):
        if not self._ruta_wav:
            mb.showwarning("Sin WAV", "Selecciona un WAV para comparar.")
            return

        # FLAC asociado
        ruta_flac = self.ent_ruta_flac.get().strip() or self._ruta_flac
        if not ruta_flac or not os.path.exists(ruta_flac):
            mb.showwarning("Sin FLAC", "Genera o selecciona un FLAC primero.")
            return

        # Asegurar WAV descomprimido (si no existe, crear temporal)
        wav_desc = self._ultima_descomp
        temp_creado = False
        try:
            if not wav_desc or not os.path.exists(wav_desc):
                temp_creado = True
                wav_desc = self._temp_wav_path()
                comp = CompresionAudio("dummy.wav")
                wav_desc = comp.extraerArchivo(ruta_flac, wav_desc)

            # Ratio de compresión
            try:
                size_wav = os.path.getsize(self._ruta_wav)
                size_flac = os.path.getsize(ruta_flac)
                ratio = (size_flac / size_wav * 100.0) if size_wav > 0 else float("inf")
            except Exception:
                ratio = float("nan")

            # Comparación binaria
            iguales = False
            try:
                with open(self._ruta_wav, "rb") as f1, open(wav_desc, "rb") as f2:
                    iguales = f1.read() == f2.read()
            except Exception:
                iguales = False

            texto = [
                f"Tamaño WAV original: {size_wav if 'size_wav' in locals() else 'N/D'} bytes",
                f"Tamaño FLAC: {size_flac if 'size_flac' in locals() else 'N/D'} bytes",
                f"Ratio (FLAC / WAV): {ratio:.2f}%",
                f"¿WAV descomprimido idéntico al original?: {'SÍ' if iguales else 'NO'}",
            ]
            mb.showinfo("Comparación", "\n".join(texto))
        finally:
            if temp_creado and wav_desc and os.path.exists(wav_desc):
                try:
                    os.remove(wav_desc)
                    if wav_desc in self._temp_wavs:
                        self._temp_wavs.remove(wav_desc)
                except Exception:
                    pass

    def _al_cerrar(self):
        try:
            self.rep.detener()
            for p in self._temp_wavs:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass
            if os.path.exists("temp_flac_decompressed.wav"):
                try:
                    os.remove("temp_flac_decompressed.wav")
                except Exception:
                    pass
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
