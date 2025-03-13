import rawpy
from PIL import Image
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time
import os  # Já adicionado anteriormente

# Variável global para controlar o cancelamento
cancelar = False

def renomear_arquivos_raw(pasta_origem, nome_base, status_label, janela):
    """Renomeia os arquivos .NEF e .CR2 na pasta de origem."""
    total_arquivos = 0
    arquivos_renomeados = 0
    
    for raiz, _, arquivos in os.walk(pasta_origem):
        for arquivo in arquivos:
            if arquivo.lower().endswith(('.nef', '.cr2')):
                total_arquivos += 1
    
    if total_arquivos == 0:
        status_label.config(text="Nenhum arquivo .NEF ou .CR2 encontrado!")
        janela.update()
        return 0
    
    for raiz, _, arquivos in os.walk(pasta_origem):
        for arquivo in arquivos:
            if arquivo.lower().endswith(('.nef', '.cr2')):
                caminho_antigo = os.path.join(raiz, arquivo)
                if nome_base:
                    extensao = os.path.splitext(arquivo)[1]
                    novo_nome = f"{nome_base}_{arquivos_renomeados + 1:03d}{extensao}"
                    caminho_novo = os.path.join(raiz, novo_nome)
                    try:
                        os.rename(caminho_antigo, caminho_novo)
                        arquivos_renomeados += 1
                        status_label.config(text=f"Renomeando: {arquivo} -> {novo_nome}")
                        janela.update()
                    except Exception as e:
                        messagebox.showwarning("Aviso", f"Erro ao renomear {arquivo}: {e}")
                else:
                    arquivos_renomeados += 1
    
    status_label.config(text=f"Renomeação concluída! {arquivos_renomeados}/{total_arquivos} arquivos renomeados.")
    janela.update()
    return arquivos_renomeados

def converter_raw_para_jpeg(pasta_origem, pasta_destino, status_label, janela, manter_estrutura=True, botao_converter=None, botao_cancelar=None, baixa_resolucao_var=None, nome_base_entry=None):
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
                inicio_arquivo = time.time()
                try:
                    with rawpy.imread(caminho_arquivo) as raw:
                        rgb = raw.postprocess()
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
                    estimativa = f" (~{tempo_restante_min}m {tempo_restante_seg}s restantes)"
                else:
                    estimativa = ""
                
                status_label.config(text=f"Processando: {arquivo} ({progresso:.1f}%){estimativa}")
                janela.update()
    
    if cancelar:
        status_label.config(text=f"Cancelado! {arquivos_convertidos}/{total_arquivos} arquivos convertidos.")
        messagebox.showinfo("Cancelado", "A conversão foi interrompida pelo usuário.")
    else:
        status_label.config(text=f"Concluído! {arquivos_convertidos}/{total_arquivos} arquivos convertidos (100%).")
        messagebox.showinfo("Sucesso", "Conversão concluída!")
    
    botao_converter.config(state="normal")
    botao_cancelar.config(state="disabled")

def cancelar_conversao():
    global cancelar
    cancelar = True

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

def janela_conversor():
    """Cria a janela do conversor como uma janela secundária."""
    janela = tk.Toplevel()
    janela.title("Conversor de .NEF/.CR2 para JPEG")
    janela.geometry("500x500")

    tk.Label(janela, text="Nome base para renomear (opcional):").pack(pady=5)
    nome_base_entry = tk.Entry(janela, width=50)
    nome_base_entry.pack(pady=5)

    tk.Label(janela, text="Pasta de Origem (.NEF ou .CR2):").pack(pady=5)
    entry_origem = tk.Entry(janela, width=50)
    entry_origem.pack(pady=5)
    tk.Button(janela, text="Selecionar", command=lambda: selecionar_pasta_origem(entry_origem)).pack()

    tk.Label(janela, text="Pasta de Destino (JPEG):").pack(pady=5)
    entry_destino = tk.Entry(janela, width=50)
    entry_destino.pack(pady=5)
    tk.Button(janela, text="Selecionar", command=lambda: selecionar_pasta_destino(entry_destino)).pack()

    baixa_resolucao_var = tk.BooleanVar()
    checkbox_baixa_resolucao = tk.Checkbutton(janela, text="Converter em baixa resolução", variable=baixa_resolucao_var)
    checkbox_baixa_resolucao.pack(pady=10)

    status_label = tk.Label(janela, text="Pronto para iniciar", wraplength=400)
    status_label.pack(pady=10)

    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=20)

    botao_converter = tk.Button(frame_botoes, text="Converter", command=lambda: converter_raw_para_jpeg(
        entry_origem.get(), entry_destino.get(), status_label, janela, manter_estrutura=True, 
        botao_converter=botao_converter, botao_cancelar=botao_cancelar, baixa_resolucao_var=baixa_resolucao_var, nome_base_entry=nome_base_entry))
    botao_converter.pack(side=tk.LEFT, padx=10)

    botao_cancelar = tk.Button(frame_botoes, text="Cancelar", command=cancelar_conversao, state="disabled")
    botao_cancelar.pack(side=tk.LEFT, padx=10)

if __name__ == "__main__":
    janela_conversor()