import os
import rawpy
from PIL import Image
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import time

# Variável global para controlar o cancelamento
cancelar = False

def converter_nef_para_jpeg(pasta_origem, pasta_destino, status_label, manter_estrutura=True, botao_converter=None, botao_cancelar=None, baixa_resolucao_var=None):
    global cancelar
    cancelar = False  # Resetar o estado de cancelamento
    
    if not pasta_origem or not pasta_destino:
        messagebox.showerror("Erro", "Por favor, selecione as pastas de origem e destino!")
        return
    
    # Criar a pasta de destino se ela não existir
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    total_arquivos = 0
    arquivos_convertidos = 0
    tempo_inicio = time.time()
    
    # Contar todos os arquivos .NEF em subpastas
    for raiz, _, arquivos in os.walk(pasta_origem):
        for arquivo in arquivos:
            if arquivo.lower().endswith('.nef'):
                total_arquivos += 1
    
    if total_arquivos == 0:
        messagebox.showinfo("Aviso", "Nenhum arquivo .NEF encontrado nas pastas!")
        return
    
    # Desativar o botão "Converter" e ativar o "Cancelar" durante o processo
    botao_converter.config(state="disabled")
    botao_cancelar.config(state="normal")
    
    # Verificar se o checkbox de baixa resolução está marcado
    baixa_resolucao = baixa_resolucao_var.get()
    
    # Processar os arquivos em todas as subpastas
    for raiz, _, arquivos in os.walk(pasta_origem):
        for arquivo in arquivos:
            if cancelar:  # Verificar se o usuário cancelou
                break
                
            if arquivo.lower().endswith('.nef'):
                caminho_arquivo = os.path.join(raiz, arquivo)
                
                inicio_arquivo = time.time()
                try:
                    with rawpy.imread(caminho_arquivo) as raw:
                        rgb = raw.postprocess()
                    
                    imagem = Image.fromarray(rgb)
                    
                    # Redimensionar apenas se o checkbox de baixa resolução estiver marcado
                    if baixa_resolucao:
                        largura, altura = imagem.size
                        if largura > altura:
                            nova_largura = 1920
                            nova_altura = int((1920 / largura) * altura)
                        else:
                            nova_altura = 1920
                            nova_largura = int((1920 / altura) * largura)
                        imagem = imagem.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)
                    # Se não estiver marcado, mantém a resolução original
                    
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
                
                # Calcular progresso e estimativa de tempo
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
    
    # Finalizar (seja por conclusão ou cancelamento)
    if cancelar:
        status_label.config(text=f"Cancelado! {arquivos_convertidos}/{total_arquivos} arquivos convertidos.")
        messagebox.showinfo("Cancelado", "A conversão foi interrompida pelo usuário.")
    else:
        status_label.config(text=f"Concluído! {arquivos_convertidos}/{total_arquivos} arquivos convertidos (100%).")
        messagebox.showinfo("Sucesso", "Conversão concluída!")
    
    # Reativar o botão "Converter" e desativar o "Cancelar"
    botao_converter.config(state="normal")
    botao_cancelar.config(state="disabled")

def cancelar_conversao():
    global cancelar
    cancelar = True

def selecionar_pasta_origem(entry_origem):
    pasta = filedialog.askdirectory(title="Selecione a pasta com os arquivos .NEF")
    if pasta:
        entry_origem.delete(0, tk.END)
        entry_origem.insert(0, pasta)

def selecionar_pasta_destino(entry_destino):
    pasta = filedialog.askdirectory(title="Selecione a pasta de destino para os JPEGs")
    if pasta:
        entry_destino.delete(0, tk.END)
        entry_destino.insert(0, pasta)

# Criar a janela principal
janela = tk.Tk()
janela.title("Conversor de .NEF para JPEG")
janela.geometry("600x300")  # Aumentei a altura para caber o checkbox

# Label e campo para pasta de origem
tk.Label(janela, text="Pasta de Origem (.NEF):").pack(pady=5)
entry_origem = tk.Entry(janela, width=50)
entry_origem.pack(pady=5)
tk.Button(janela, text="Selecionar", command=lambda: selecionar_pasta_origem(entry_origem)).pack()

# Label e campo para pasta de destino
tk.Label(janela, text="Pasta de Destino (JPEG):").pack(pady=5)
entry_destino = tk.Entry(janela, width=50)
entry_destino.pack(pady=5)
tk.Button(janela, text="Selecionar", command=lambda: selecionar_pasta_destino(entry_destino)).pack()

# Checkbox para baixa resolução
baixa_resolucao_var = tk.BooleanVar()
checkbox_baixa_resolucao = tk.Checkbutton(janela, text="Converter em baixa resolução.", variable=baixa_resolucao_var)
checkbox_baixa_resolucao.pack(pady=10)

# Label para status
status_label = tk.Label(janela, text="Pronto para iniciar", wraplength=400)
status_label.pack(pady=10)

# Frame para os botões
frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=20)

# Botão para iniciar a conversão
botao_converter = tk.Button(frame_botoes, text="Converter", command=lambda: converter_nef_para_jpeg(
    entry_origem.get(), entry_destino.get(), status_label, manter_estrutura=True, 
    botao_converter=botao_converter, botao_cancelar=botao_cancelar, baixa_resolucao_var=baixa_resolucao_var))
botao_converter.pack(side=tk.LEFT, padx=10)

# Botão para cancelar
botao_cancelar = tk.Button(frame_botoes, text="Cancelar", command=cancelar_conversao, state="disabled")
botao_cancelar.pack(side=tk.LEFT, padx=10)

# Iniciar a interface
janela.mainloop()