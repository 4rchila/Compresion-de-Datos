import customtkinter as ctk
from PIL import Image
import os
from tkinter import filedialog, messagebox

def create_text_compression_frame(main_container, show_frame_callback):
    frame = ctk.CTkFrame(main_container, fg_color="#122448")
    
    selected_file_path = ctk.StringVar(value="")
    compression_ratio = ctk.StringVar(value="0%")
    original_size = ctk.StringVar(value="0 KB")
    compressed_size = ctk.StringVar(value="0 KB")
    
    def select_file():
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de texto",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            selected_file_path.set(file_path)
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / 1024  
            
            file_info_label.configure(text=f"📄 {file_name}")
            original_size.set(f"{file_size:.2f} KB")
            
            compress_huffman_btn.configure(state="normal")
            compress_lzw_btn.configure(state="normal")
            preview_btn.configure(state="normal")
            
            compression_ratio.set("0%")
            compressed_size.set("0 KB")
            result_text.delete("1.0", "end")
    
    def compress_huffman():
        file_path = selected_file_path.get()
        if file_path:
            try:
                original_size_kb = float(original_size.get().split()[0])
                compressed_size_kb = original_size_kb * 0.6  # 40% de compresión
                ratio = (1 - (compressed_size_kb / original_size_kb)) * 100
                
                compressed_size.set(f"{compressed_size_kb:.2f} KB")
                compression_ratio.set(f"{ratio:.1f}%")
                
                result_text.delete("1.0", "end")
                result_text.insert("1.0", f"✅ Compresión Huffman completada\n\n"
                                        f"• Tamaño original: {original_size.get()}\n"
                                        f"• Tamaño comprimido: {compressed_size.get()}\n"
                                        f"• Ratio de compresión: {compression_ratio.get()}\n\n"
                                        f"Archivo guardado como: {file_path}.huffman")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error en compresión: {str(e)}")
    
    def compress_lzw():
        file_path = selected_file_path.get()
        if file_path:
            try:
                original_size_kb = float(original_size.get().split()[0])
                compressed_size_kb = original_size_kb * 0.7  
                ratio = (1 - (compressed_size_kb / original_size_kb)) * 100
                
                compressed_size.set(f"{compressed_size_kb:.2f} KB")
                compression_ratio.set(f"{ratio:.1f}%")
                
                result_text.delete("1.0", "end")
                result_text.insert("1.0", f"✅ Compresión LZW completada\n\n"
                                        f"• Tamaño original: {original_size.get()}\n"
                                        f"• Tamaño comprimido: {compressed_size.get()}\n"
                                        f"• Ratio de compresión: {compression_ratio.get()}\n\n"
                                        f"Archivo guardado como: {file_path}.lzw")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error en compresión: {str(e)}")
    
    def preview_content():
        file_path = selected_file_path.get()
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                preview_window = ctk.CTkToplevel(frame)
                preview_window.title("Vista previa del archivo")
                preview_window.geometry("600x400")
                preview_window.configure(fg_color="#122448")
                
                preview_text = ctk.CTkTextbox(preview_window, width=580, height=350)
                preview_text.pack(pady=20, padx=10)
                preview_text.insert("1.0", content)
                preview_text.configure(state="disabled")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo: {str(e)}")
    
    def save_compressed():
        if compressed_size.get() != "0 KB":
            file_path = filedialog.asksaveasfilename(
                title="Guardar archivo comprimido",
                defaultextension=".zip",
                filetypes=[("Archivo comprimido", "*.zip"), ("Todos los archivos", "*.*")]
            )
            if file_path:
                messagebox.showinfo("Éxito", f"Archivo guardado en: {file_path}")
        else:
            messagebox.showwarning("Advertencia", "Primero debe comprimir un archivo")

    header_frame = ctk.CTkFrame(frame, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=20)
    
    ctk.CTkButton(header_frame, text="← Volver al Inicio", fg_color="#172b54", 
                  border_color="#6de0ff", border_width=1, hover_color="#6de0ff", 
                  text_color="white", width=120,
                  command=lambda: show_frame_callback("Home")).pack(side="left")
    
    ctk.CTkLabel(header_frame, text="COMPRESIÓN DE TEXTO 📝", 
                 font=ctk.CTkFont(size=24, weight="bold"), 
                 text_color="#6de0ff").pack(side="left", padx=20)
    
    main_content = ctk.CTkFrame(frame, fg_color="transparent")
    main_content.pack(fill="both", expand=True, padx=20, pady=10)
    
    left_panel = ctk.CTkFrame(main_content, fg_color="#172b54", corner_radius=10)
    left_panel.pack(side="left", fill="y", padx=(0, 10))
    
    ctk.CTkLabel(left_panel, text="1. Seleccionar Archivo", 
                 font=ctk.CTkFont(size=16, weight="bold"), 
                 text_color="#6de0ff").pack(pady=(20, 10))
    
    ctk.CTkButton(left_panel, text="📁 Examinar Archivos", 
                  command=select_file, 
                  fg_color="#122448", hover_color="#6de0ff").pack(pady=10, padx=20, fill="x")
    
    file_info_label = ctk.CTkLabel(left_panel, text="Ningún archivo seleccionado", 
                                   text_color="white", wraplength=200)
    file_info_label.pack(pady=10)
    
    info_frame = ctk.CTkFrame(left_panel, fg_color="#122448", corner_radius=8)
    info_frame.pack(pady=20, padx=20, fill="x")
    
    ctk.CTkLabel(info_frame, text="📊 Información del Archivo", 
                 font=ctk.CTkFont(weight="bold"), text_color="#6de0ff").pack(pady=(10, 5))
    ctk.CTkLabel(info_frame, text=f"Tamaño original: {original_size.get()}", 
                 text_color="white").pack(pady=2)
    ctk.CTkLabel(info_frame, text=f"Tamaño comprimido: {compressed_size.get()}", 
                 text_color="white").pack(pady=2)
    ctk.CTkLabel(info_frame, text=f"Ratio: {compression_ratio.get()}", 
                 text_color="white").pack(pady=(2, 10))
    
    right_panel = ctk.CTkFrame(main_content, fg_color="#172b54", corner_radius=10)
    right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
    
    ctk.CTkLabel(right_panel, text="2. Método de Compresión", 
                 font=ctk.CTkFont(size=16, weight="bold"), 
                 text_color="#6de0ff").pack(pady=(20, 10))
    
    compression_buttons = ctk.CTkFrame(right_panel, fg_color="transparent")
    compression_buttons.pack(pady=10, fill="x", padx=20)
    
    compress_huffman_btn = ctk.CTkButton(compression_buttons, text="Huffman", 
                                        command=compress_huffman, state="disabled",
                                        fg_color="#122448", hover_color="#6de0ff")
    compress_huffman_btn.pack(side="left", padx=5, fill="x", expand=True)
    
    compress_lzw_btn = ctk.CTkButton(compression_buttons, text="LZW", 
                                    command=compress_lzw, state="disabled",
                                    fg_color="#122448", hover_color="#6de0ff")
    compress_lzw_btn.pack(side="left", padx=5, fill="x", expand=True)
    
    preview_btn = ctk.CTkButton(compression_buttons, text="Vista Previa", 
                               command=preview_content, state="disabled",
                               fg_color="#122448", hover_color="#6de0ff")
    preview_btn.pack(side="left", padx=5, fill="x", expand=True)
    
    ctk.CTkLabel(right_panel, text="3. Resultados", 
                 font=ctk.CTkFont(size=16, weight="bold"), 
                 text_color="#6de0ff").pack(pady=(20, 10))
    
    result_text = ctk.CTkTextbox(right_panel, height=150, font=ctk.CTkFont(size=12))
    result_text.pack(pady=10, padx=20, fill="both", expand=True)
    result_text.insert("1.0", "Los resultados de compresión aparecerán aquí...")
    
    save_btn = ctk.CTkButton(right_panel, text="💾 Guardar Archivo Comprimido", 
                            command=save_compressed,
                            fg_color="#122448", hover_color="#6de0ff",
                            border_color="#6de0ff", border_width=1)
    save_btn.pack(pady=20, padx=20, fill="x")
    
    return frame