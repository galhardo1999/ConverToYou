import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, ttk
import rawpy
from PIL import Image, ImageOps
import numpy as np
import io

class PhotoProcessorApp:
    def __init__(self, master):
        self.master = master
        self.root = Toplevel(master)
        self.root.title("Photo Processor")
        self.root.geometry("400x200")

        # Interface principal
        tk.Label(self.root, text="Photo Processor", font=("Arial", 16)).pack(pady=20)
        tk.Label(self.root, text="Selecione uma opção no menu acima").pack(pady=10)

        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opções", menu=file_menu)
        file_menu.add_command(label="Criar JSON", command=self.open_create_json_window)
        file_menu.add_command(label="Converter RAW para JPEG", command=self.open_convert_raw_window)

    def open_create_json_window(self):
        # Janela para criar JSON
        json_window = Toplevel(self.root)
        json_window.title("Criar Arquivo JSON")
        json_window.geometry("600x300")

        # Variáveis
        jpeg_folder = tk.StringVar()
        json_file = tk.StringVar()

        # Interface
        tk.Label(json_window, text="Criar Arquivo JSON", font=("Arial", 14)).pack(pady=10)

        tk.Label(json_window, text="Pasta com arquivos JPEG:").pack()
        tk.Entry(json_window, textvariable=jpeg_folder, width=50).pack()
        tk.Button(json_window, text="Selecionar Pasta JPEG", command=lambda: self.select_jpeg_folder(jpeg_folder)).pack(pady=5)

        tk.Label(json_window, text="Arquivo JSON de saída:").pack()
        tk.Entry(json_window, textvariable=json_file, width=50).pack()
        tk.Button(json_window, text="Selecionar Local para Salvar JSON", command=lambda: self.select_json_save_file(json_file)).pack(pady=5)

        tk.Button(json_window, text="Escanear JPEGs e Salvar JSON", command=lambda: self.scan_jpeg_folder(jpeg_folder, json_file)).pack(pady=10)

    def open_convert_raw_window(self):
        # Janela para converter RAW
        convert_window = Toplevel(self.root)
        convert_window.title("Converter RAW para JPEG")
        convert_window.geometry("600x500")

        # Variáveis
        json_file = tk.StringVar()
        raw_folder = tk.StringVar()
        output_folder = tk.StringVar()

        # Interface
        tk.Label(convert_window, text="Converter RAW para JPEG", font=("Arial", 14)).pack(pady=10)

        tk.Label(convert_window, text="Arquivo JSON com lista de JPEGs:").pack()
        tk.Entry(convert_window, textvariable=json_file, width=50).pack()
        tk.Button(convert_window, text="Selecionar Arquivo JSON", command=lambda: self.select_json_file(json_file)).pack(pady=5)

        tk.Label(convert_window, text="Pasta com arquivos RAW:").pack()
        tk.Entry(convert_window, textvariable=raw_folder, width=50).pack()
        tk.Button(convert_window, text="Selecionar Pasta RAW", command=lambda: self.select_raw_folder(raw_folder)).pack(pady=5)

        tk.Label(convert_window, text="Pasta de destino para JPEGs convertidos:").pack()
        tk.Entry(convert_window, textvariable=output_folder, width=50).pack()
        tk.Button(convert_window, text="Selecionar Pasta de Destino", command=lambda: self.select_output_folder(output_folder)).pack(pady=5)

        # Barra de progresso
        tk.Label(convert_window, text="Progresso:").pack(pady=5)
        progress = ttk.Progressbar(convert_window, orient="horizontal", length=400, mode="determinate")
        progress.pack(pady=5)

        tk.Button(convert_window, text="Converter RAWs para JPEG", command=lambda: self.convert_raw_to_jpeg(json_file, raw_folder, output_folder, progress, convert_window)).pack(pady=10)

    def select_jpeg_folder(self, jpeg_folder_var):
        folder = filedialog.askdirectory(title="Selecione a pasta com arquivos JPEG")
        if folder:
            jpeg_folder_var.set(folder)

    def select_json_save_file(self, json_file_var):
        file = filedialog.asksaveasfilename(
            title="Salvar arquivo JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if file:
            json_file_var.set(file)

    def select_json_file(self, json_file_var):
        file = filedialog.askopenfilename(title="Selecione o arquivo JSON", filetypes=[("JSON files", "*.json")])
        if file:
            json_file_var.set(file)

    def select_raw_folder(self, raw_folder_var):
        folder = filedialog.askdirectory(title="Selecione a pasta com arquivos RAW")
        if folder:
            raw_folder_var.set(folder)

    def select_output_folder(self, output_folder_var):
        folder = filedialog.askdirectory(title="Selecione a pasta de destino para JPEGs")
        if folder:
            output_folder_var.set(folder)

    def scan_jpeg_folder(self, jpeg_folder_var, json_file_var):
        folder = jpeg_folder_var.get()
        json_file = json_file_var.get()
        if not folder:
            messagebox.showerror("Erro", "Selecione uma pasta com arquivos JPEG!")
            return
        if not json_file:
            messagebox.showerror("Erro", "Selecione um local para salvar o arquivo JSON!")
            return

        jpeg_files = []
        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg')):
                    relative_path = os.path.relpath(os.path.join(root, file), folder)
                    # Normalizar caminhos para usar separadores consistentes
                    relative_path = relative_path.replace('\\', '/')
                    jpeg_files.append(relative_path)

        if not jpeg_files:
            messagebox.showinfo("Aviso", "Nenhum arquivo JPEG encontrado!")
            return

        # Salvar em JSON
        try:
            with open(json_file, 'w') as f:
                json.dump({"jpeg_files": jpeg_files}, f, indent=4)
            messagebox.showinfo("Sucesso", f"Encontrados {len(jpeg_files)} arquivos JPEG. Lista salva em {json_file}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar o JSON: {e}")

    def convert_raw_to_jpeg(self, json_file_var, raw_folder_var, output_folder_var, progress, window):
        json_file = json_file_var.get()
        raw_folder = raw_folder_var.get()
        output_folder = output_folder_var.get()
        if not json_file or not os.path.exists(json_file):
            messagebox.showerror("Erro", "Selecione um arquivo JSON válido!")
            return
        if not raw_folder:
            messagebox.showerror("Erro", "Selecione uma pasta com arquivos RAW!")
            return
        if not output_folder:
            messagebox.showerror("Erro", "Selecione uma pasta de destino para os JPEGs!")
            return

        # Carregar lista de JPEGs
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                jpeg_files = data["jpeg_files"]
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar o JSON: {e}")
            return

        # Configurar barra de progresso
        total_files = len(jpeg_files)
        progress['maximum'] = total_files
        progress['value'] = 0
        window.update_idletasks()

        raw_extensions = ('.nef', '.cr2', '.arw', '.dng')  # Extensões RAW comuns
        converted = 0
        for idx, jpeg_path in enumerate(jpeg_files):
            # Normalizar caminho do JSON
            jpeg_path = os.path.normpath(jpeg_path.replace('\\', '/'))
            # Extrair nome do arquivo sem extensão
            jpeg_filename = os.path.splitext(os.path.basename(jpeg_path))[0]
            # Flag para indicar se o arquivo RAW foi encontrado
            found = False
            # Procurar arquivo RAW correspondente na pasta RAW (incluindo subpastas)
            for root, _, files in os.walk(raw_folder):
                for file in files:
                    if file.lower().startswith(jpeg_filename.lower()) and file.lower().endswith(raw_extensions):
                        raw_file_path = os.path.join(root, file)
                        try:
                            # Processar arquivo RAW (lógica adaptada do conversorCompleto.py)
                            with rawpy.imread(raw_file_path) as raw:
                                # Tentar extrair a miniatura embutida
                                thumb = raw.extract_thumb()
                                if thumb.format == rawpy.ThumbFormat.JPEG:
                                    imagem = Image.open(io.BytesIO(thumb.data))
                                    imagem = ImageOps.exif_transpose(imagem)  # Preservar orientação
                                else:
                                    # Pós-processamento com configurações para manter características
                                    rgb = raw.postprocess(
                                        use_camera_wb=True,  # Usar balanço de branco da câmera
                                        use_auto_wb=False,  # Desativar balanço de branco automático
                                        no_auto_bright=False,  # Permitir ajuste automático de brilho
                                        output_color=rawpy.ColorSpace.sRGB,  # Espaço de cor sRGB
                                        highlight_mode=rawpy.HighlightMode.Clip  # Gerenciar realces
                                    )
                                    imagem = Image.fromarray(rgb)
                                    imagem = ImageOps.exif_transpose(imagem)  # Preservar orientação

                            # Criar caminho de saída mantendo a estrutura do JSON
                            output_path = os.path.join(output_folder, jpeg_path)
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            # Salvar como JPEG com qualidade 95
                            imagem.save(output_path, 'JPEG', quality=95)
                            converted += 1
                            print(f"Convertido: {raw_file_path} -> {output_path}")
                            found = True
                        except Exception as e:
                            print(f"Erro ao processar {raw_file_path}: {e}")
                        break  # Encontrou o arquivo RAW correspondente, sai do loop de arquivos
                if found:
                    break  # Sai do loop de subpastas apenas se o arquivo foi encontrado e convertido
            
            # Atualizar barra de progresso
            progress['value'] = idx + 1
            window.update_idletasks()

            if converted > 0 and converted % 10 == 0:  # Atualizar status a cada 10 conversões
                print(f"Progresso: {converted} arquivos convertidos")

        messagebox.showinfo("Sucesso", f"Convertidos {converted} arquivos RAW para JPEG na pasta {output_folder}!")

def janela_photo_processor(master=None):
    """Função para abrir a interface do PhotoProcessorApp como uma janela filha."""
    app = PhotoProcessorApp(master)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal
    janela_photo_processor(root)
    root.mainloop()