import rawpy
from PIL import Image
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import os
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

cancelar = False

def selecionar_pasta_origem(entry_origem):
    pasta = filedialog.askdirectory(title="Selecione a pasta com os arquivos .NEF ou .CR2")
    if pasta:
        entry_origem.delete(0, tk.END)
        entry_origem.insert(0, pasta)

def selecionar_pasta_destino(entry_destino):
    pasta = filedialog.askdirectory(title="Selecione a pasta de destino para os JPEGs")
    if pasta:
        entry_destino.delete(0, tk.END)
        entry_destino.insert(0, pasta)

def processar_arquivo(args):
    """Função para extrair a prévia JPEG embutida no arquivo RAW."""
    caminho_arquivo, pasta_destino, manter_estrutura, baixa_resolucao = args
    if cancelar:
        return None, caminho_arquivo
    
    try:
        with rawpy.imread(caminho_arquivo) as raw:
            # Extrai a prévia embutida (geralmente um JPEG criado pela câmera)
            thumb = raw.extract_thumb()
            if thumb.format == rawpy.ThumbFormat.JPEG:
                # Converte os dados da prévia JPEG em uma imagem PIL
                imagem = Image.open(io.BytesIO(thumb.data))
            else:
                # Caso a prévia não seja JPEG (raramente acontece), converte para RGB
                rgb = raw.postprocess(
                    use_camera_wb=True,
                    use_auto_wb=False,
                    no_auto_bright=False,
                    output_color=rawpy.ColorSpace.sRGB,
                    highlight_mode=rawpy.HighlightMode.Clip,
                )
                imagem = Image.fromarray(rgb)

        # Aplica redimensionamento se baixa resolução estiver ativada
        if baixa_resolucao:
            largura, altura = imagem.size
            if largura > altura:
                nova_largura = 1920
                nova_altura = int((1920 / largura) * altura)
            else:
                nova_altura = 1920
                nova_largura = int((1920 / altura) * largura)
            imagem = imagem.resize((nova_largura, nova_altura), Image.Resampling.BICUBIC)
        
        # Define o caminho de saída
        nome_saida = os.path.splitext(os.path.basename(caminho_arquivo))[0] + '.jpg'
        if manter_estrutura:
            subpasta_relativa = os.path.relpath(os.path.dirname(caminho_arquivo), os.path.dirname(caminho_arquivo))
            pasta_saida = os.path.join(pasta_destino, subpasta_relativa)
            os.makedirs(pasta_saida, exist_ok=True)
            caminho_saida = os.path.join(pasta_saida, nome_saida)
        else:
            caminho_saida = os.path.join(pasta_destino, nome_saida)
        
        # Salva a imagem como JPEG
        imagem.save(caminho_saida, 'JPEG', quality=85)
        return True, caminho_arquivo
    except Exception as e:
        return f"Erro ao processar {os.path.basename(caminho_arquivo)}: {e}", caminho_arquivo

def converter_raw_para_jpeg(pasta_origem, pasta_destino, status_label, janela, manter_estrutura=True, botao_converter=None, botao_cancelar=None, baixa_resolucao_var=None):
    global cancelar
    cancelar = False
    
    if not pasta_origem or not pasta_destino:
        messagebox.showerror("Erro", "Por favor, selecione as pastas de origem e destino!")
        return
    
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    arquivos_raw = [os.path.join(raiz, arquivo) for raiz, _, arquivos in os.walk(pasta_origem) 
                    for arquivo in arquivos if arquivo.lower().endswith(('.nef', '.cr2', '.cr3'))]
    
    total_arquivos = len(arquivos_raw)
    if total_arquivos == 0:
        messagebox.showinfo("Aviso", "Nenhum arquivo RAW encontrado nas pastas!")
        return
    
    botao_converter.config(state="disabled")
    botao_cancelar.config(state="normal")
    
    baixa_resolucao = baixa_resolucao_var.get()
    arquivos_convertidos = 0
    tempo_inicio = time.time()
    ultima_atualizacao = tempo_inicio
    
    num_nucleos = os.cpu_count()
    max_workers = max(1, int(num_nucleos * 0.8))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(processar_arquivo, (arquivo, pasta_destino, manter_estrutura, baixa_resolucao)) for arquivo in arquivos_raw]
        
        for future in as_completed(futures):
            if cancelar:
                executor.shutdown(wait=False)
                break
            resultado, arquivo = future.result()
            arquivos_convertidos += 1 if resultado is True else 0
            
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
    
    if cancelar:
        status_label.config(text=f"Cancelado! {arquivos_convertidos}/{total_arquivos} convertidos.")
        messagebox.showinfo("Cancelado", "A conversão foi interrompida pelo usuário.")
    else:
        status_label.config(text=f"Concluído! {arquivos_convertidos}/{total_arquivos} convertidos (100%).")
        messagebox.showinfo("Sucesso", "Conversão concluída!")
    
    botao_converter.config(state="normal")
    botao_cancelar.config(state="disabled")

def cancelar_conversao():
    global cancelar
    cancelar = True

def janela_conversor(master=None):
    janela = tk.Toplevel(master)
    janela.title("ConverToou - Conversor RAW para JPEG")
    janela.geometry("600x600")
    janela.configure(bg="#f5f6f5")
    janela.resizable(False, False)

    # Estilo ttk
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 11), padding=6)
    style.configure("TLabel", background="#f5f6f5", font=("Helvetica", 11))
    style.configure("Accent.TButton", background="#0288D1", foreground="white")
    style.map("Accent.TButton",
              background=[("active", "#0277BD"), ("!active", "#0288D1")],
              foreground=[("active", "black"), ("!active", "black")])

    # Frame principal com borda sutil
    frame_principal = ttk.Frame(janela, padding="20", style="Transparent.TFrame", relief="groove", borderwidth=1)
    frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

    style.configure("Transparent.TFrame", background="#f5f6f5")

    # Título
    titulo = ttk.Label(frame_principal, text="Conversor RAW para JPEG", font=("Helvetica", 18, "bold"), foreground="#0288D1", background="#f5f6f5")
    titulo.pack(pady=(0, 25))

    # Frame para entrada de pasta origem com borda
    frame_pasta_origem = ttk.Frame(frame_principal, style="Transparent.TFrame", relief="groove", borderwidth=1)
    frame_pasta_origem.pack(pady=10, padx=10, fill="x")
    ttk.Label(frame_pasta_origem, text="Pasta de Origem:", background="#f5f6f5").pack(pady=(5, 5))
    frame_input_origem = ttk.Frame(frame_pasta_origem, style="Transparent.TFrame")
    frame_input_origem.pack(anchor="center", pady=(0, 5))
    entry_origem = ttk.Entry(frame_input_origem, width=40)
    entry_origem.pack(side="left", padx=(0, 10))
    ttk.Button(frame_input_origem, text="Selecionar", command=lambda: selecionar_pasta_origem(entry_origem), style="TButton").pack(side="left")
    # Tooltip para pasta origem
    tk.Label(frame_pasta_origem, text="Selecione a pasta com os arquivos RAW", font=("Helvetica", 8), fg="#999", bg="#f5f6f5").pack(pady=(5, 0))

    # Frame para entrada de pasta destino com borda
    frame_pasta_destino = ttk.Frame(frame_principal, style="Transparent.TFrame", relief="groove", borderwidth=1)
    frame_pasta_destino.pack(pady=10, padx=10, fill="x")
    ttk.Label(frame_pasta_destino, text="Pasta de Destino (JPEG):", background="#f5f6f5").pack(pady=(5, 5))
    frame_input_destino = ttk.Frame(frame_pasta_destino, style="Transparent.TFrame")
    frame_input_destino.pack(anchor="center", pady=(0, 5))
    entry_destino = ttk.Entry(frame_input_destino, width=40)
    entry_destino.pack(side="left", padx=(0, 10))
    ttk.Button(frame_input_destino, text="Selecionar", command=lambda: selecionar_pasta_destino(entry_destino), style="TButton").pack(side="left")
    # Tooltip para pasta destino
    tk.Label(frame_pasta_destino, text="Selecione a pasta para salvar os JPEGs", font=("Helvetica", 8), fg="#999", bg="#f5f6f5").pack(pady=(5, 0))

    # Checkbox
    baixa_resolucao_var = tk.BooleanVar()
    checkbox_baixa_resolucao = ttk.Checkbutton(frame_principal, text="Converter em baixa resolução (1920px)", variable=baixa_resolucao_var)
    checkbox_baixa_resolucao.pack(pady=15)

    # Status com borda sutil
    status_frame = ttk.Frame(frame_principal, style="Transparent.TFrame", relief="groove", borderwidth=1)
    status_frame.pack(pady=10, padx=10, fill="x")
    status_label = ttk.Label(status_frame, text="Pronto para iniciar", wraplength=500, justify="center", background="#f5f6f5")
    status_label.pack(pady=10)

    # Frame para botões
    frame_botoes = ttk.Frame(frame_principal, style="Transparent.TFrame")
    frame_botoes.pack(pady=25)

    # Botão Converter
    botao_converter = ttk.Button(frame_botoes, text="Converter", style="Accent.TButton", command=lambda: converter_raw_para_jpeg(
        entry_origem.get(), entry_destino.get(), status_label, janela, manter_estrutura=True, 
        botao_converter=botao_converter, botao_cancelar=botao_cancelar, baixa_resolucao_var=baixa_resolucao_var))
    botao_converter.pack(side="left", padx=10)

    # Botão Cancelar
    botao_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=cancelar_conversao, state="disabled")
    botao_cancelar.pack(side="left", padx=10)

    # Rodapé
    rodape = ttk.Label(frame_principal, text="© 2025 - Desenvolvido por Alexandre Galhardo", font=("Helvetica", 8), foreground="#999", background="#f5f6f5")
    rodape.pack(side="bottom", pady=10)

    # Centralizar a janela
    janela.update_idletasks()
    width = janela.winfo_width()
    height = janela.winfo_height()
    x = (janela.winfo_screenwidth() // 2) - (width // 2)
    y = (janela.winfo_screenheight() // 2) - (height // 2)
    janela.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    janela_conversor(root)
    root.mainloop()