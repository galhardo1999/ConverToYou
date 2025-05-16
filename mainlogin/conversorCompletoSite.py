import rawpy
from PIL import Image, ImageOps
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import os
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from datetime import datetime

API_URL = "http://localhost:5000"

cancelar = False
FORMATOS_SUPORTADOS = {
    'RAW': ['.nef', '.cr2', '.cr3', '.arw', '.raw', '.dng'],
    'JPEG': ['.jpg', '.jpeg'],
    'PNG': ['.png'],
    'TIFF': ['.tif', '.tiff'],
    'WebP': ['.webp'],
    'BMP': ['.bmp'],
    'GIF': ['.gif']
}

def selecionar_pasta_origem(entry_origem):
    pasta = filedialog.askdirectory(title="Selecione a pasta com os arquivos de origem")
    if pasta:
        entry_origem.delete(0, tk.END)
        entry_origem.insert(0, pasta)

def selecionar_pasta_destino(entry_destino):
    pasta = filedialog.askdirectory(title="Selecione a pasta de destino para as imagens convertidas")
    if pasta:
        entry_destino.delete(0, tk.END)
        entry_destino.insert(0, pasta)

def processar_arquivo(args):
    caminho_arquivo, pasta_origem, pasta_destino, manter_estrutura, baixa_resolucao, formato_destino, qualidade = args
    if cancelar:
        return None, caminho_arquivo
    
    try:
        extensao = os.path.splitext(caminho_arquivo)[1].lower()
        
        if extensao in FORMATOS_SUPORTADOS['RAW']:
            with rawpy.imread(caminho_arquivo) as raw:
                thumb = raw.extract_thumb()
                if thumb.format == rawpy.ThumbFormat.JPEG:
                    imagem = Image.open(io.BytesIO(thumb.data))
                    imagem = ImageOps.exif_transpose(imagem)
                else:
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        use_auto_wb=False,
                        no_auto_bright=False,
                        output_color=rawpy.ColorSpace.sRGB,
                        highlight_mode=rawpy.HighlightMode.Clip,
                    )
                    imagem = Image.fromarray(rgb)
        else:
            imagem = Image.open(caminho_arquivo)
            imagem = ImageOps.exif_transpose(imagem)
        
        if baixa_resolucao:
            largura, altura = imagem.size
            if largura > altura:
                nova_largura = 1920
                nova_altura = int((1920 / largura) * altura)
            else:
                nova_altura = 1920
                nova_largura = int((1920 / altura) * largura)
            imagem = imagem.resize((nova_largura, nova_altura), Image.Resampling.BICUBIC)
        
        extensao_destino = '.' + formato_destino.lower()
        nome_saida = os.path.splitext(os.path.basename(caminho_arquivo))[0] + extensao_destino
        
        if manter_estrutura:
            subpasta_relativa = os.path.relpath(os.path.dirname(caminho_arquivo), pasta_origem)
            pasta_saida = os.path.join(pasta_destino, subpasta_relativa)
            os.makedirs(pasta_saida, exist_ok=True)
            caminho_saida = os.path.join(pasta_saida, nome_saida)
        else:
            caminho_saida = os.path.join(pasta_destino, nome_saida)
        
        if formato_destino.upper() == 'JPEG':
            imagem.save(caminho_saida, 'JPEG', quality=qualidade)
        elif formato_destino.upper() == 'PNG':
            imagem.save(caminho_saida, 'PNG', compress_level=int(qualidade/10))
        elif formato_destino.upper() == 'TIFF':
            imagem.save(caminho_saida, 'TIFF', compression='tiff_deflate')
        elif formato_destino.upper() == 'WEBP':
            imagem.save(caminho_saida, 'WEBP', quality=qualidade)
        elif formato_destino.upper() == 'BMP':
            imagem.save(caminho_saida, 'BMP')
        elif formato_destino.upper() == 'GIF':
            imagem.save(caminho_saida, 'GIF')
        else:
            imagem.save(caminho_saida, formato_destino.upper())
            
        return True, caminho_arquivo
    except Exception as e:
        return f"Erro ao processar {os.path.basename(caminho_arquivo)}: {e}", caminho_arquivo

def check_usage(email, num_files):
    try:
        response = requests.post(f"{API_URL}/api/usage", json={"email": email}, timeout=5)
        response.raise_for_status()
        usage = response.json()
        if not usage.get("success"):
            return False, usage.get("message", "Erro ao verificar uso")
        
        remaining = usage.get("remaining", 0)
        if remaining == "ilimitadas":
            return True, None
        if remaining < num_files:
            return False, f"Você atingiu o limite de conversões este mês. Restam {remaining} de {usage['limit']} fotos."
        return True, None
    except requests.Timeout:
        return False, "Tempo limite excedido ao verificar uso. Verifique se o servidor está ativo."
    except requests.RequestException as e:
        return False, f"Erro ao conectar ao servidor: {str(e)}"

def update_usage(email, count):
    try:
        response = requests.post(f"{API_URL}/api/increment_usage", json={"email": email, "count": count}, timeout=5)
        response.raise_for_status()
        result = response.json()
        if not result.get("success"):
            return False, result.get("message", "Erro ao atualizar uso")
        return True, result.get("message", "Uso atualizado com sucesso")
    except requests.Timeout:
        return False, "Tempo limite excedido ao atualizar uso. Verifique se o servidor está ativo."
    except requests.RequestException as e:
        return False, f"Erro ao conectar ao servidor: {str(e)}"

def converter_imagens(email, pasta_origem, pasta_destino, status_label, janela, formato_origem, formato_destino, 
                     manter_estrutura=True, botao_converter=None, botao_cancelar=None, 
                     baixa_resolucao_var=None, qualidade_var=None, on_update=None):
    global cancelar
    cancelar = False
    
    if not pasta_origem or not pasta_destino:
        messagebox.showerror("Erro", "Por favor, selecione as pastas de origem e destino!")
        return
    
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    extensoes_origem = []
    if formato_origem == "Todos":
        for formato in FORMATOS_SUPORTADOS.values():
            extensoes_origem.extend(formato)
    else:
        extensoes_origem = FORMATOS_SUPORTADOS.get(formato_origem, [])
    
    arquivos_para_converter = []
    for raiz, _, arquivos in os.walk(pasta_origem):
        for arquivo in arquivos:
            if any(arquivo.lower().endswith(ext) for ext in extensoes_origem):
                arquivos_para_converter.append(os.path.join(raiz, arquivo))
    
    total_arquivos = len(arquivos_para_converter)
    if total_arquivos == 0:
        messagebox.showinfo("Aviso", f"Nenhum arquivo {formato_origem} encontrado nas pastas!")
        return
    
    can_convert, error_message = check_usage(email, total_arquivos)
    if not can_convert:
        messagebox.showerror("Erro", error_message)
        return
    
    botao_converter.config(state="disabled")
    botao_cancelar.config(state="normal")
    
    baixa_resolucao = baixa_resolucao_var.get()
    qualidade = qualidade_var.get()
    arquivos_convertidos = 0
    tempo_inicio = time.time()
    ultima_atualizacao = tempo_inicio
    
    num_nucleos = os.cpu_count()
    max_workers = max(1, int(num_nucleos * 0.8))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(processar_arquivo, 
                                 (arquivo, pasta_origem, pasta_destino, manter_estrutura, 
                                  baixa_resolucao, formato_destino, qualidade)) 
                  for arquivo in arquivos_para_converter]
        
        for future in as_completed(futures):
            if cancelar:
                executor.shutdown(wait=False)
                break
            resultado, arquivo = future.result()
            if resultado is True:
                arquivos_convertidos += 1
            
            agora = time.time()
            if agora - ultima_atualizacao >= 1.0:
                progresso = (arquivos_convertidos / total_arquivos) * 100
                tempo_decorrido = agora - tempo_inicio
                tempo_medio_por_arquivo = tempo_decorrido / arquivos_convertidos if arquivos_convertidos > 0 else 0
                arquivos_restantes = total_arquivos - arquivos_convertidos
                tempo_restante = tempo_medio_por_arquivo * arquivos_restantes
                tempo_restante_min = int(tempo_restante // 60)
                tempo_restante_seg = int(tempo_restante % 60)
                estimativa = f" (~{tempo_restante_min}m {tempo_restante_seg}s)"
                status_label.config(text=f"Processando: {os.path.basename(arquivo)} ({progresso:.1f}%){estimativa}")
                janela.update()
                ultima_atualizacao = agora
    
    # Atualizar o contador de uso se houver imagens convertidas
    if arquivos_convertidos > 0:
        success, error_message = update_usage(email, arquivos_convertidos)
        if not success:
            status_label.config(text=f"Erro: {arquivos_convertidos}/{total_arquivos} convertidos.")
            messagebox.showerror("Erro", error_message)
            botao_converter.config(state="normal")
            botao_cancelar.config(state="disabled")
            return
    
    if cancelar:
        status_label.config(text=f"Cancelado! {arquivos_convertidos}/{total_arquivos} convertidos.")
        messagebox.showinfo("Cancelado", "A conversão foi interrompida pelo usuário.")
    else:
        status_label.config(text=f"Concluído! {arquivos_convertidos}/{total_arquivos} convertidos (100%).")
        messagebox.showinfo("Sucesso", "Conversão concluída!")
    
    # Atualizar a interface do dashboard, se fornecido
    if on_update:
        on_update()
    
    botao_converter.config(state="normal")
    botao_cancelar.config(state="disabled")

    
def cancelar_conversao():
    global cancelar
    cancelar = True

def janela_conversor(master=None, email=None, on_update=None):
    if not email:
        messagebox.showerror("Erro", "E-mail do usuário não fornecido!")
        return
    
    janela = tk.Toplevel(master)
    janela.title("ConverTool - Conversor de Imagens")
    janela.geometry("650x800")
    janela.configure(bg="#f5f6f5")
    janela.resizable(False, False)

    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 11), padding=6)
    style.configure("TLabel", background="#f5f6f5", font=("Helvetica", 11))
    style.configure("Accent.TButton", background="#0288D1", foreground="white")
    style.map("Accent.TButton",
              background=[("active", "#0277BD"), ("!active", "#0288D1")],
              foreground=[("active", "black"), ("!active", "black")])

    frame_principal = ttk.Frame(janela, padding="20", style="Transparent.TFrame", relief="groove", borderwidth=1)
    frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

    style.configure("Transparent.TFrame", background="#f5f6f5")

    titulo = ttk.Label(frame_principal, text="Conversor de Imagens", font=("Helvetica", 18, "bold"), foreground="#0288D1", background="#f5f6f5")
    titulo.pack(pady=(0, 25))

    frame_pasta_origem = ttk.Frame(frame_principal, style="Transparent.TFrame", relief="groove", borderwidth=1)
    frame_pasta_origem.pack(pady=10, padx=10, fill="x")
    ttk.Label(frame_pasta_origem, text="Pasta de Origem:", background="#f5f6f5").pack(pady=(5, 5))
    frame_input_origem = ttk.Frame(frame_pasta_origem, style="Transparent.TFrame")
    frame_input_origem.pack(anchor="center", pady=(0, 5))
    entry_origem = ttk.Entry(frame_input_origem, width=40)
    entry_origem.pack(side="left", padx=(0, 10))
    ttk.Button(frame_input_origem, text="Selecionar", command=lambda: selecionar_pasta_origem(entry_origem), style="TButton").pack(side="left")
    tk.Label(frame_pasta_origem, text="Selecione a pasta com as imagens de origem", font=("Helvetica", 8), fg="#999", bg="#f5f6f5").pack(pady=(5, 0))

    frame_pasta_destino = ttk.Frame(frame_principal, style="Transparent.TFrame", relief="groove", borderwidth=1)
    frame_pasta_destino.pack(pady=10, padx=10, fill="x")
    ttk.Label(frame_pasta_destino, text="Pasta de Destino:", background="#f5f6f5").pack(pady=(5, 5))
    frame_input_destino = ttk.Frame(frame_pasta_destino, style="Transparent.TFrame")
    frame_input_destino.pack(anchor="center", pady=(0, 5))
    entry_destino = ttk.Entry(frame_input_destino, width=40)
    entry_destino.pack(side="left", padx=(0, 10))
    ttk.Button(frame_input_destino, text="Selecionar", command=lambda: selecionar_pasta_destino(entry_destino), style="TButton").pack(side="left")
    tk.Label(frame_pasta_destino, text="Selecione a pasta para salvar as imagens convertidas", font=("Helvetica", 8), fg="#999", bg="#f5f6f5").pack(pady=(5, 0))

    frame_formatos = ttk.Frame(frame_principal, style="Transparent.TFrame", relief="groove", borderwidth=1)
    frame_formatos.pack(pady=10, padx=10, fill="x")
    
    frame_formato_origem = ttk.Frame(frame_formatos, style="Transparent.TFrame")
    frame_formato_origem.pack(pady=10, fill="x")
    ttk.Label(frame_formato_origem, text="Formato de Origem:", background="#f5f6f5").pack(side="left", padx=(10, 5))
    
    formatos_origem = ["Todos", "RAW", "JPEG", "PNG", "TIFF", "WebP", "BMP", "GIF"]
    formato_origem_var = tk.StringVar(value=formatos_origem[0])
    combobox_origem = ttk.Combobox(frame_formato_origem, textvariable=formato_origem_var, values=formatos_origem, width=15, state="readonly")
    combobox_origem.pack(side="left", padx=5)
    
    frame_formato_destino = ttk.Frame(frame_formatos, style="Transparent.TFrame")
    frame_formato_destino.pack(pady=10, fill="x")
    ttk.Label(frame_formato_destino, text="Formato de Destino:", background="#f5f6f5").pack(side="left", padx=(10, 5))
    
    formatos_destino = ["JPEG", "PNG", "TIFF", "WebP", "BMP", "GIF"]
    formato_destino_var = tk.StringVar(value=formatos_destino[0])
    combobox_destino = ttk.Combobox(frame_formato_destino, textvariable=formato_destino_var, values=formatos_destino, width=15, state="readonly")
    combobox_destino.pack(side="left", padx=5)

    frame_configuracoes = ttk.Frame(frame_principal, style="Transparent.TFrame", relief="groove", borderwidth=1)
    frame_configuracoes.pack(pady=10, padx=10, fill="x")
    ttk.Label(frame_configuracoes, text="Configurações:", background="#f5f6f5", font=("Helvetica", 12, "bold")).pack(pady=(10, 5))

    frame_qualidade = ttk.Frame(frame_configuracoes, style="Transparent.TFrame")
    frame_qualidade.pack(pady=5, fill="x")
    ttk.Label(frame_qualidade, text="Qualidade:", background="#f5f6f5").pack(side="left", padx=(10, 5))
    qualidade_var = tk.IntVar(value=100)
    escala_qualidade = ttk.Scale(frame_qualidade, from_=1, to=100, variable=qualidade_var, orient="horizontal", length=200)
    escala_qualidade.pack(side="left", padx=5)
    label_qualidade = ttk.Label(frame_qualidade, textvariable=qualidade_var, background="#f5f6f5", width=3)
    label_qualidade.pack(side="left", padx=5)
    
    baixa_resolucao_var = tk.BooleanVar()
    checkbox_baixa_resolucao = ttk.Checkbutton(frame_configuracoes, text="Converter em baixa resolução", variable=baixa_resolucao_var)
    checkbox_baixa_resolucao.pack(pady=10)
    
    manter_estrutura_var = tk.BooleanVar(value=True)
    checkbox_estrutura = ttk.Checkbutton(frame_configuracoes, text="Manter estrutura de pastas", variable=manter_estrutura_var)
    checkbox_estrutura.pack(pady=5)

    status_frame = ttk.Frame(frame_principal, style="Transparent.TFrame", relief="groove", borderwidth=1)
    status_frame.pack(pady=10, padx=10, fill="x")
    status_label = ttk.Label(status_frame, text="Pronto para iniciar", wraplength=500, justify="center", background="#f5f6f5")
    status_label.pack(pady=10)

    frame_botoes = ttk.Frame(frame_principal, style="Transparent.TFrame")
    frame_botoes.pack(pady=25)

    botao_converter = ttk.Button(frame_botoes, text="Converter", style="Accent.TButton", 
                               command=lambda: converter_imagens(
                                   email,
                                   entry_origem.get(), entry_destino.get(), status_label, janela,
                                   formato_origem_var.get(), formato_destino_var.get(),
                                   manter_estrutura=manter_estrutura_var.get(), 
                                   botao_converter=botao_converter, botao_cancelar=botao_cancelar, 
                                   baixa_resolucao_var=baixa_resolucao_var, qualidade_var=qualidade_var,
                                   on_update=on_update))
    botao_converter.pack(side="left", padx=10)

    botao_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=cancelar_conversao, state="disabled")
    botao_cancelar.pack(side="left", padx=10)

    rodape = ttk.Label(frame_principal, text="© 2025 - Desenvolvido por Alexandre Galhardo", font=("Helvetica", 8), foreground="#999")
    rodape.pack(pady=(20, 0))

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    janela_conversor(root, email="admin@example.com")
    root.mainloop()