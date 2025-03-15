import rawpy
from PIL import Image 
import numpy as np 
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import os

# Variável global para controlar o cancelamento
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
        
def converter_raw_para_jpeg(pasta_origem, pasta_destino, status_label, janela, manter_estrutura=True, botao_converter=None, botao_cancelar=None, baixa_resolucao_var=None):
    global cancelar
    cancelar = False
    
    if not pasta_origem or not pasta_destino:
        messagebox.showerror("Erro", "Por favor, selecione as pastas de origem e destino!")
        return
    
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    total_arquivos = 0
    arquivos_convertidos = 0
    tempo_inicio = time.time()
    
    for raiz, _, arquivos in os.walk(pasta_origem):
        for arquivo in arquivos:
            if arquivo.lower().endswith(('.nef', '.cr2')):
                total_arquivos += 1
    
    if total_arquivos == 0:
        messagebox.showinfo("Aviso", "Nenhum arquivo .NEF ou .CR2 encontrado nas pastas!")
        return
    
    botao_converter.config(state="disabled")
    botao_cancelar.config(state="normal")
    
    baixa_resolucao = baixa_resolucao_var.get()
    
    for raiz, _, arquivos in os.walk(pasta_origem):
        for arquivo in arquivos:
            if cancelar:
                break
            if arquivo.lower().endswith(('.nef', '.cr2')):
                caminho_arquivo = os.path.join(raiz, arquivo)
                try:
                    with rawpy.imread(caminho_arquivo) as raw:
                        rgb = raw.postprocess(use_camera_wb=True, use_auto_wb=False, no_auto_bright=False)
                    imagem = Image.fromarray(rgb)
                    
                    if baixa_resolucao:
                        largura, altura = imagem.size
                        if largura > altura:
                            nova_largura = 1920
                            nova_altura = int((1920 / largura) * altura)
                        else:
                            nova_altura = 1920
                            nova_largura = int((1920 / altura) * largura)
                        imagem = imagem.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)
                    
                    nome_saida = os.path.splitext(arquivo)[0] + '.jpg'
                    if manter_estrutura:
                        subpasta_relativa = os.path.relpath(raiz, pasta_origem)
                        pasta_saida = os.path.join(pasta_destino, subpasta_relativa)
                        if not os.path.exists(pasta_saida):
                            os.makedirs(pasta_saida)
                        caminho_saida = os.path.join(pasta_saida, nome_saida)
                    else:
                        caminho_saida = os.path.join(pasta_destino, nome_saida)
                    
                    imagem.save(caminho_saida, 'JPEG', quality=95)
                    arquivos_convertidos += 1
                
                except Exception as e:
                    messagebox.showwarning("Aviso", f"Erro ao processar {arquivo}: {e}")
                
                progresso = (arquivos_convertidos / total_arquivos) * 100
                tempo_decorrido = time.time() - tempo_inicio
                if arquivos_convertidos > 0:
                    tempo_medio_por_arquivo = tempo_decorrido / arquivos_convertidos
                    arquivos_restantes = total_arquivos - arquivos_convertidos
                    tempo_restante = tempo_medio_por_arquivo * arquivos_restantes
                    tempo_restante_min = int(tempo_restante // 60)
                    tempo_restante_seg = int(tempo_restante % 60)
                    estimativa = f" (~{tempo_restante_min}m {tempo_restante_seg}s)"
                else:
                    estimativa = ""
                
                status_label.config(text=f"Processando: {arquivo} ({progresso:.1f}%){estimativa}")
                janela.update()
    
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

def janela_conversor():
    """Cria a janela do conversor como uma janela secundária."""
    janela = tk.Toplevel()
    janela.title("ConverToou - Conversor RAW para JPEG")
    janela.geometry("600x600")
    janela.configure(bg="#f5f6f5")  # Fundo cinza claro suave
    janela.resizable(False, False)  # Janela não redimensionável

    # Estilo ttk
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 11), padding=10)
    style.configure("TLabel", background="#f5f6f5", font=("Helvetica", 11))  # Fundo igual ao da janela
    style.configure("Accent.TButton", background="#0288D1", foreground="white")  # Azul elegante
    style.map("Accent.TButton",
              background=[("active", "#0277BD"), ("!active", "#0288D1")],
              foreground=[("active", "white"), ("!active", "white")])

    # Frame principal
    frame_principal = ttk.Frame(janela, padding="20", style="Transparent.TFrame")
    frame_principal.pack(fill="both", expand=True)

    # Estilo para frame transparente
    style.configure("Transparent.TFrame", background="#f5f6f5")

    # Título
    titulo = ttk.Label(frame_principal, text="Conversor RAW para JPEG", font=("Helvetica", 18, "bold"), foreground="#0288D1", background="#f5f6f5")
    titulo.pack(pady=(10, 20))

    # Entrada Origem
    ttk.Label(frame_principal, text="Pasta de Origem (.NEF ou .CR2):", background="#f5f6f5").pack(pady=5)
    entry_origem = ttk.Entry(frame_principal, width=50)
    entry_origem.pack(pady=5)
    ttk.Button(frame_principal, text="Selecionar", command=lambda: selecionar_pasta_origem(entry_origem), width=12).pack(pady=5)

    # Entrada Destino
    ttk.Label(frame_principal, text="Pasta de Destino (JPEG):", background="#f5f6f5").pack(pady=5)
    entry_destino = ttk.Entry(frame_principal, width=50)
    entry_destino.pack(pady=5)
    ttk.Button(frame_principal, text="Selecionar", command=lambda: selecionar_pasta_destino(entry_destino), width=12).pack(pady=5)

    # Checkbox
    baixa_resolucao_var = tk.BooleanVar()
    checkbox_baixa_resolucao = ttk.Checkbutton(frame_principal, text="Converter em baixa resolução (1920px)", variable=baixa_resolucao_var)
    checkbox_baixa_resolucao.pack(pady=10)

    # Status
    status_label = ttk.Label(frame_principal, text="Pronto para iniciar", wraplength=500, justify="center", background="#f5f6f5")
    status_label.pack(pady=10)

    # Frame para botões
    frame_botoes = ttk.Frame(frame_principal, style="Transparent.TFrame")
    frame_botoes.pack(pady=20)

    botao_converter = ttk.Button(frame_botoes, text="Converter", style="Accent.TButton", command=lambda: converter_raw_para_jpeg(
        entry_origem.get(), entry_destino.get(), status_label, janela, manter_estrutura=True, 
        botao_converter=botao_converter, botao_cancelar=botao_cancelar, baixa_resolucao_var=baixa_resolucao_var))
    botao_converter.pack(side="left", padx=10)

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

# Para testar standalone (remova se for usar no dashboard)
if __name__ == "__main__":
    janela_conversor()
    tk.mainloop()