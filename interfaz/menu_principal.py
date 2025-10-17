import customtkinter as ctk
from PIL import Image

from ventana_texto import create_text_compression_frame
from ventana_audio import create_audio_frame
from ventan_imagen import create_imagen_frame


def on_enter(event):
    event.widget.master.configure(
        fg_color="#6de0ff",
        text_color="#172b54",
        border_color="#6de0ff",
        border_width=1
    )

def on_leave(event):
    event.widget.master.configure(
        fg_color="#172b54",
        text_color="white",
        border_color="#6de0ff",
        border_width=1
    )

def create_home_frame(main_container, show_frame_callback):
    frame = ctk.CTkFrame(main_container, fg_color="#172b54")

    frame.grid_rowconfigure((0, 2), weight=1)
    frame.grid_rowconfigure(1, weight=0)
    frame.grid_columnconfigure((0, 1), weight=1)

    # === PANEL IZQUIERDO DECORATIVO ===
    side_panel = ctk.CTkFrame(frame, fg_color="#122448", corner_radius=15)
    side_panel.grid(row=1, column=0, padx=(0, 30), pady=40, sticky="nsew")
    side_panel.grid_rowconfigure((0, 1, 2), weight=1)
    side_panel.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(side_panel, text="📦 DATAZIP PANEL", text_color="#6de0ff",
                 font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(25, 10))
    ctk.CTkLabel(side_panel, text="Estado general del sistema\nCompresión de datos optimizada.",
                 text_color="white", justify="center").pack(pady=(0, 30))
    
    # Tarjetas decorativas de "info"
    info_card = ctk.CTkFrame(side_panel, fg_color="#172b54", corner_radius=10, border_color="#6de0ff", border_width=1)
    info_card.pack(pady=15, padx=20, fill="x")
    ctk.CTkLabel(info_card, text="Archivos procesados: 0", text_color="white").pack(pady=10)
    
    info_card2 = ctk.CTkFrame(side_panel, fg_color="#172b54", corner_radius=10, border_color="#6de0ff", border_width=1)
    info_card2.pack(pady=10, padx=20, fill="x")
    ctk.CTkLabel(info_card2, text="Última compresión: --/--/----", text_color="white").pack(pady=10)

    # === PANEL CENTRAL PRINCIPAL ===
    button_container = ctk.CTkFrame(frame, fg_color="#122448", corner_radius=15)
    button_container.grid(row=1, column=1, pady=80, sticky="n")
    button_container.grid_rowconfigure(0, weight=1)
    button_container.grid_columnconfigure((0, 1, 2), weight=1)

    # Cargar íconos (deja espacio aunque no los tengas todavía)
    imagen_archivo = Image.open("../utils/archivo.png")
    imagen_foto = Image.open("../utils/imagen.png")
    imagen_audio = Image.open("../utils/auriculares.png")
    icon_size = (50, 50)
    
    file_ctk = ctk.CTkImage(dark_image=imagen_archivo, light_image=imagen_archivo, size=icon_size)
    img_ctk = ctk.CTkImage(dark_image=imagen_foto, light_image=imagen_foto, size=icon_size)
    audio_ctk = ctk.CTkImage(dark_image=imagen_audio, light_image=imagen_audio, size=icon_size)
    
    btn1 = ctk.CTkButton(button_container, text="Compresión de Texto", image=file_ctk, compound="top",
                         width=160, height=130, fg_color="#172b54", border_color="#6de0ff",
                         hover=False, border_width=1, font=ctk.CTkFont(size=14, weight="bold"),
                         command=lambda: show_frame_callback("Texto"))

    btn2 = ctk.CTkButton(button_container, text="Compresión de Imágenes", image=img_ctk, compound="top",
                         width=160, height=130, fg_color="#172b54", border_color="#6de0ff",
                         hover=False, border_width=1, font=ctk.CTkFont(size=14, weight="bold"),
                         command=lambda: show_frame_callback("Imagen"))

    btn3 = ctk.CTkButton(button_container, text="Compresión de Audio", image=audio_ctk, compound="top",
                         width=160, height=130, fg_color="#172b54", border_color="#6de0ff",
                         hover=False, border_width=1, font=ctk.CTkFont(size=14, weight="bold"),
                         command=lambda: show_frame_callback("Audio"))

    # Colocar botones
    btn1.grid(row=0, column=0, padx=25, pady=25)
    btn2.grid(row=0, column=1, padx=25, pady=25)
    btn3.grid(row=0, column=2, padx=25, pady=25)

    for btn in [btn1, btn2, btn3]:
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    return frame


def create_view_frame(main_container, title, show_frame_callback):
    frame = ctk.CTkFrame(main_container, fg_color="#122448")

    ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=24, weight="bold"), text_color="#6de0ff").pack(pady=40)
    ctk.CTkButton(frame, text="← Volver al Inicio", fg_color="#172b54", border_color="#6de0ff",
                  border_width=1, hover_color="#6de0ff", text_color="white",
                  command=lambda: show_frame_callback("Home")).pack(pady=20)
    ctk.CTkLabel(frame, text="Zona de vista previa / configuración", 
                 text_color="white", font=ctk.CTkFont(size=16)).pack(pady=20)

    return frame


def show_frame(frame_name, views_dict):
    frame_to_show = views_dict.get(frame_name)
    if frame_to_show:
        frame_to_show.tkraise()


# === APP ===
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("DataZip - Compresión de Archivos")
app.geometry("1000x600")
app.configure(fg_color="#0e1e3a")

# Header
header_frame = ctk.CTkFrame(app, fg_color="#122448", corner_radius=0)
header_frame.grid(row=0, column=0, sticky="ew")
ctk.CTkLabel(header_frame, text="DATAZIP", text_color="#6de0ff",
             font=ctk.CTkFont(size=22, weight="bold")).pack(padx=30, pady=15, anchor="w")

# Contenedor principal
main_container = ctk.CTkFrame(app, fg_color="transparent")
main_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=30)
app.grid_rowconfigure(1, weight=1)
app.grid_columnconfigure(0, weight=1)

views = {}
show_frame_callback = lambda name: show_frame(name, views)

views["Home"] = create_home_frame(main_container, show_frame_callback)
views["Texto"] = create_text_compression_frame(main_container, show_frame_callback)
views["Imagen"] = create_imagen_frame(main_container, show_frame_callback)
views["Audio"] = create_audio_frame(main_container, show_frame_callback)

for frame in views.values():
    frame.grid(row=0, column=0, sticky="nsew")

show_frame("Home", views)

app.mainloop()

##marco = ctk.CTkFrame(app)
##marco.pack(pady=20, padx=20)

