import customtkinter as ctk
from PIL import Image
import os
from tkinter import filedialog, messagebox
import time
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

print(f"📂 Directorio actual: {current_dir}")
print(f"📂 Directorio padre: {parent_dir}")
print("📦 Paths configurados:")

try:
    from compresion_texto import gestor_archivos_texto
    from compresion_texto import hyffman
    LOGICA_DISPONIBLE = True
    print("✅ Módulos importados correctamente")
    
except ImportError as e:
    print(f"❌ Error importando: {e}")
    print("🔍 Buscando módulos...")
    compression_path = os.path.join(parent_dir, "compression_texto")
    if os.path.exists(compression_path):
        print(f"✅ Carpeta compression_texto encontrada en: {compression_path}")
        archivos = os.listdir(compression_path)
        print(f"📄 Archivos en compression_texto: {archivos}")
    else:
        print("❌ No se encuentra compression_texto")
    LOGICA_DISPONIBLE = False


def create_text_compression_frame(main_container, show_frame_callback):
    frame = ctk.CTkFrame(main_container, fg_color="#122448")
    
    selected_file_path = ctk.StringVar(value="")
    compression_ratio = ctk.StringVar(value="0%")
    original_size = ctk.StringVar(value="0 KB")
    compressed_size = ctk.StringVar(value="0 KB")
    compressed_file_path = ctk.StringVar(value="")

    estaComprimido = ctk.BooleanVar(value=False)
    
    def select_file():
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[
                ("Archivos de texto", "*.txt"),
                ("Archivos comprimidos", "*.bin"),
                ("Todos los archivos", "*.*")
            ]
        )
        if file_path:
            selected_file_path.set(file_path)
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / 1024  # Tamaño en KB
            
            file_info_label.configure(text=f"📄 {file_name}")
            
            # Determinar si es archivo comprimido o texto
            if file_path.lower().endswith('.bin'):
                estaComprimido.set(True)
                original_size.set("N/A")
                compressed_size.set(f"{file_size:.2f} KB")
                compression_ratio.set("N/A")
                
                # Configurar interfaz para descompresión
                file_info_label.configure(text=f"📦 {file_name} (comprimido)")
                compress_huffman_btn.configure(state="disabled")
                preview_btn.configure(state="disabled")
                decompress_btn.configure(state="normal")
                
                result_text.delete("1.0", "end")
                result_text.insert("1.0", 
                    f"📦 Archivo comprimido detectado\n"
                    f"• Archivo: {file_name}\n"
                    f"• Tamaño: {file_size:.2f} KB\n"
                    f"• Listo para descomprimir\n\n"
                    f"💡 Haz clic en 'Descomprimir' para extraer el contenido"
                )
                
            else:
                # Es archivo de texto normal
                estaComprimido.set(False)
                original_size.set(f"{file_size:.2f} KB")
                compressed_size.set("0 KB")
                compression_ratio.set("0%")
                
                # Configurar interfaz para compresión
                file_info_label.configure(text=f"📄 {file_name}")
                compress_huffman_btn.configure(state="normal")
                preview_btn.configure(state="normal")
                decompress_btn.configure(state="disabled")
                
                # Limpiar resultados anteriores
                compressed_file_path.set("")
                result_text.delete("1.0", "end")
                result_text.insert("1.0", "Archivo de texto listo para compresión...")

    def select_file_for_compression():
        """Seleccionar específicamente para compresión"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de texto para comprimir",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            selected_file_path.set(file_path)
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / 1024
            
            file_info_label.configure(text=f"📄 {file_name}")
            original_size.set(f"{file_size:.2f} KB")
            compressed_size.set("0 KB")
            compression_ratio.set("0%")
            
            compress_huffman_btn.configure(state="normal")
            preview_btn.configure(state="normal")
            decompress_btn.configure(state="disabled")
            
            compressed_file_path.set("")
            result_text.delete("1.0", "end")
            result_text.insert("1.0", "Archivo de texto listo para compresión...")

    def select_file_for_decompression():
        """Seleccionar específicamente para descompresión"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo comprimido para descomprimir",
            filetypes=[("Archivos comprimidos", "*.bin"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            selected_file_path.set(file_path)
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / 1024
            
            file_info_label.configure(text=f"📦 {file_name} (comprimido)")
            original_size.set("N/A")
            compressed_size.set(f"{file_size:.2f} KB")
            compression_ratio.set("N/A")
            
            compress_huffman_btn.configure(state="disabled")
            preview_btn.configure(state="disabled")
            decompress_btn.configure(state="normal")
            
            result_text.delete("1.0", "end")
            result_text.insert("1.0", 
                f"📦 Archivo comprimido detectado\n"
                f"• Listo para descomprimir\n"
                f"• Tamaño: {file_size:.2f} KB"
            )

    def decompress_file():
        file_path = selected_file_path.get()
        if file_path and os.path.exists(file_path):
            try:
                # Verificar que sea un archivo .bin
                if not file_path.lower().endswith('.bin'):
                    messagebox.showwarning("Advertencia", "Por favor seleccione un archivo .bin comprimido")
                    return

                # Seleccionar donde guardar el archivo descomprimido
                output_path = filedialog.asksaveasfilename(
                    title="Guardar archivo descomprimido como...",
                    defaultextension=".txt",
                    filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
                )

                if output_path:
                    # Mostrar progreso
                    result_text.delete("1.0", "end")
                    result_text.insert("1.0", "⏳ Descomprimiendo archivo...\n")
                    frame.update()

                    start_time = time.time()

                    # Usar tu lógica real de descompresión
                    gestor_archivos_texto.descomprimir_archivo_txt(file_path, output_path)

                    end_time = time.time()
                    decompression_time = end_time - start_time

                    # Calcular información del archivo resultante
                    if os.path.exists(output_path):
                        decompressed_size = os.path.getsize(output_path) / 1024
                        compressed_size_bytes = os.path.getsize(file_path)
                        decompressed_size_bytes = os.path.getsize(output_path)

                        result_text.delete("1.0", "end")
                        result_text.insert("1.0", 
                            f"✅ Descompresión completada\n\n"
                            f"• Archivo comprimido: {os.path.basename(file_path)}\n"
                            f"• Tamaño comprimido: {compressed_size_bytes / 1024:.2f} KB\n"
                            f"• Archivo descomprimido: {os.path.basename(output_path)}\n"
                            f"• Tamaño descomprimido: {decompressed_size:.2f} KB\n"
                            f"• Tiempo de descompresión: {decompression_time:.2f} segundos\n\n"
                            f"💡 Archivo guardado en:\n{output_path}"
                        )
                    else:
                        result_text.insert("1.0", 
                            f"✅ Descompresión completada\n"
                            f"• Tiempo: {decompression_time:.2f} segundos\n"
                            f"• Archivo guardado en: {output_path}"
                        )

            except Exception as e:
                messagebox.showerror("Error", f"Error en descompresión: {str(e)}")
                result_text.delete("1.0", "end")
                result_text.insert("1.0", f"❌ Error en descompresión: {str(e)}")
        else:
            messagebox.showwarning("Advertencia", "Primero debe seleccionar un archivo comprimido")
    
    def compress_huffman():
        file_path = selected_file_path.get()
        if file_path:
            try:
                result_text.delete("1.0", "end")
                result_text.insert("1.0", "⏳ Comprimiendo archivo...\n")
                frame.update()
                
                file_dir = os.path.dirname(file_path)
                file_name = os.path.basename(file_path)
                compressed_path = os.path.join(file_dir, f"comprimido_{file_name}.bin")
                
                start_time = time.time()
                
                gestor_archivos_texto.comprimir_archivo_txt(file_path, compressed_path)
                
                end_time = time.time()
                compression_time = end_time - start_time
                
                original_size_bytes = os.path.getsize(file_path)
                compressed_size_bytes = os.path.getsize(compressed_path)
                ratio = (1 - (compressed_size_bytes / original_size_bytes)) * 100
                
                original_size.set(f"{original_size_bytes / 1024:.2f} KB")
                compressed_size.set(f"{compressed_size_bytes / 1024:.2f} KB")
                compression_ratio.set(f"{ratio:.1f}%")
                compressed_file_path.set(compressed_path)
                
                result_text.delete("1.0", "end")
                result_text.insert("1.0", 
                    f"✅ Compresión Huffman completada\n\n"
                    f"• Archivo original: {os.path.basename(file_path)}\n"
                    f"• Tamaño original: {original_size.get()}\n"
                    f"• Tamaño comprimido: {compressed_size.get()}\n"
                    f"• Ratio de compresión: {compression_ratio.get()}\n"
                    f"• Tiempo de compresión: {compression_time:.2f} segundos\n"
                    f"• Archivo comprimido: {os.path.basename(compressed_path)}\n\n"
                    f"💡 Espacio ahorrado: {original_size_bytes - compressed_size_bytes} bytes"
                )
                
                save_btn.configure(state="normal")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error en compresión Huffman: {str(e)}")
                result_text.delete("1.0", "end")
                result_text.insert("1.0", f"❌ Error en compresión: {str(e)}")
    
    def decompress_file():
        if compressed_file_path.get() and os.path.exists(compressed_file_path.get()):
            try:
                output_path = filedialog.asksaveasfilename(
                    title="Guardar archivo descomprimido",
                    defaultextension=".txt",
                    filetypes=[("Archivos de texto", "*.txt")]
                )
                
                if output_path:
                    result_text.insert("end", f"\n\n⏳ Descomprimiendo archivo...")
                    frame.update()
                    
                    start_time = time.time()
                    
                    gestor_archivos_texto.descomprimir_archivo_txt(compressed_file_path.get(), output_path)
                    
                    end_time = time.time()
                    decompression_time = end_time - start_time
                    
                    result_text.insert("end", 
                        f"\n✅ Descompresión completada\n"
                        f"• Archivo guardado: {os.path.basename(output_path)}\n"
                        f"• Tiempo de descompresión: {decompression_time:.2f} segundos"
                    )
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error en descompresión: {str(e)}")
        else:
            messagebox.showwarning("Advertencia", "Primero debe comprimir un archivo")
    
    def preview_content():
        file_path = selected_file_path.get()
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                if len(content) > 10000:
                    content = content[:10000] + "\n\n... (contenido truncado)"
                
                preview_window = ctk.CTkToplevel(frame)
                preview_window.title("Vista previa del archivo")
                preview_window.geometry("700x500")
                preview_window.configure(fg_color="#122448")
                
                header_frame = ctk.CTkFrame(preview_window, fg_color="transparent")
                header_frame.pack(fill="x", padx=20, pady=10)
                
                ctk.CTkLabel(header_frame, text="Vista previa del archivo", 
                            font=ctk.CTkFont(size=16, weight="bold"),
                            text_color="#6de0ff").pack(side="left")
                
                ctk.CTkLabel(header_frame, text=f"Caracteres: {len(content)}", 
                            text_color="white").pack(side="right")
                
                preview_text = ctk.CTkTextbox(preview_window, width=660, height=400)
                preview_text.pack(pady=10, padx=20, fill="both", expand=True)
                preview_text.insert("1.0", content)
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo: {str(e)}")
    
    def save_compressed():
        if compressed_file_path.get() and os.path.exists(compressed_file_path.get()):
            save_path = filedialog.asksaveasfilename(
                title="Guardar archivo comprimido como...",
                defaultextension=".bin",
                filetypes=[("Archivo comprimido", "*.bin"), ("Todos los archivos", "*.*")]
            )
            
            if save_path:
                try:
                    import shutil
                    shutil.copy2(compressed_file_path.get(), save_path)
                    messagebox.showinfo("Éxito", f"Archivo guardado en:\n{save_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")
        else:
            messagebox.showwarning("Advertencia", "Primero debe comprimir un archivo")

    # === INTERFAZ DE COMPRESIÓN DE TEXTO ===
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
    
    # ctk.CTkLabel(info_frame, text="📊 Información del Archivo", 
    #              font=ctk.CTkFont(weight="bold"), text_color="#6de0ff").pack(pady=(10, 5))
    # ctk.CTkLabel(info_frame, text=f"Tamaño original: {original_size.get()}", 
    #              text_color="white").pack(pady=2)
    # ctk.CTkLabel(info_frame, text=f"Tamaño comprimido: {compressed_size.get()}", 
    #              text_color="white").pack(pady=2)
    # ctk.CTkLabel(info_frame, text=f"Ratio: {compression_ratio.get()}", 
    #              text_color="white").pack(pady=(2, 10))
    
    right_panel = ctk.CTkFrame(main_content, fg_color="#172b54", corner_radius=10)
    right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
    
    ctk.CTkLabel(right_panel, text="2. Compresión Huffman", 
                 font=ctk.CTkFont(size=16, weight="bold"), 
                 text_color="#6de0ff").pack(pady=(20, 10))
    
    compression_buttons = ctk.CTkFrame(right_panel, fg_color="transparent")
    compression_buttons.pack(pady=10, fill="x", padx=20)
    
    compress_huffman_btn = ctk.CTkButton(compression_buttons, text="Comprimir con Huffman", 
                                        command=compress_huffman, state="disabled",
                                        fg_color="#122448", hover_color="#6de0ff")
    compress_huffman_btn.pack(side="left", padx=5, fill="x", expand=True)
    
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
    
    action_buttons = ctk.CTkFrame(right_panel, fg_color="transparent")
    action_buttons.pack(pady=20, padx=20, fill="x")
    
    save_btn = ctk.CTkButton(action_buttons, text="💾 Guardar Comprimido", 
                            command=save_compressed, state="disabled",
                            fg_color="#122448", hover_color="#6de0ff",
                            border_color="#6de0ff", border_width=1)
    save_btn.pack(side="left", padx=5, fill="x", expand=True)
    
    decompress_btn = ctk.CTkButton(action_buttons, text="📤 Descomprimir", 
                                  command=decompress_file,
                                  fg_color="#122448", hover_color="#6de0ff",
                                  border_color="#6de0ff", border_width=1)
    decompress_btn.pack(side="left", padx=5, fill="x", expand=True)
    
    return frame