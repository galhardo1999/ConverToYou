import rawpy
from PIL import Image 
import numpy as np 
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os


def renomear_arquivos(pasta_origem, nome_base, status_label, janela, usar_nome_pasta=False):
    """Renomeia os arquivos na pasta de origem."""
    total_arquivos = 0
    arquivos_renomeados = 0
    
    # Contar total de arquivos RAW
    for raiz, _, arquivos in os.walk(pasta_origem):
        for arquivo in arquivos:
            if arquivo.lower().endswith(('.nef', '.cr2', '.jpeg','.jpg')):
                total_arquivos += 1
    
    if total_arquivos == 0:
        status_label.config(text="Nenhum arquivo encontrado!")
        janela.update()
        return 0
    
    # Renomear os arquivos
    for raiz, _, arquivos in os.walk(pasta_origem):
        contador_local = 1  # Contador reinicia para cada subpasta quando usar_nome_pasta é True
        for arquivo in arquivos:
            if arquivo.lower().endswith(('.nef', '.cr2', '.jpeg','.jpg')):
                caminho_antigo = os.path.join(raiz, arquivo)
                extensao = os.path.splitext(arquivo)[1]
                if usar_nome_pasta:  # Usa o nome da pasta atual como base
                    nome_base_pasta = os.path.basename(raiz) or "SemNome"  # Evita nome vazio
                    novo_nome = f"{nome_base_pasta}_{contador_local:03d}{extensao}"
                    contador_local += 1
                elif nome_base:  # Usa o nome base fornecido pelo usuário
                    novo_nome = f"{nome_base}_{arquivos_renomeados + 1:03d}{extensao}"
                else:  # Se não houver nome base e checkbox desmarcado, mantém o nome original
                    arquivos_renomeados += 1
                    continue
                
                caminho_novo = os.path.join(raiz, novo_nome)
                try:
                    os.rename(caminho_antigo, caminho_novo)
                    arquivos_renomeados += 1
                    status_label.config(text=f"Renomeando: {arquivo} -> {novo_nome}")
                    janela.update()
                except Exception as e:
                    messagebox.showwarning("Aviso", f"Erro ao renomear {arquivo}: {e}")
    
    status_label.config(text=f"Renomeação concluída! {arquivos_renomeados}/{total_arquivos} arquivos renomeados.")
    janela.update()
    return arquivos_renomeados


def janela_renomear_arquivos():
    """Cria uma janela para renomear arquivos RAW."""
    janela_renomear = tk.Toplevel()
    janela_renomear.title("Renomear Arquivos RAW")
    janela_renomear.geometry("400x300")

    

    # Campo para selecionar a pasta
    tk.Label(janela_renomear, text="Pasta com os arquivos").pack(pady=5)
    entry_pasta = tk.Entry(janela_renomear, width=40)
    entry_pasta.pack(pady=5)
    tk.Button(janela_renomear, text="Selecionar Pasta", command=lambda: selecionar_pasta(entry_pasta)).pack(pady=5)
    
    # Campo para o nome base
    tk.Label(janela_renomear, text="Nome base para renomear (opcional):").pack(pady=5)
    nome_base_entry = tk.Entry(janela_renomear, width=40)
    nome_base_entry.pack(pady=5)

    # Checkbox para usar o nome da pasta
    usar_nome_pasta = tk.BooleanVar()
    checkbox = tk.Checkbutton(
        janela_renomear, 
        text="Usar o nome da pasta de cada arquivo como nome base", 
        variable=usar_nome_pasta
    )
    checkbox.pack(pady=5)

    # Label de status
    status_label = tk.Label(janela_renomear, text="Pronto para iniciar", wraplength=350)
    status_label.pack(pady=10)

    # Função para iniciar a renomeação
    def iniciar_renomeacao():
        pasta = entry_pasta.get()
        nome_base = nome_base_entry.get().strip() if not usar_nome_pasta.get() else None
        renomear_arquivos(pasta, nome_base, status_label, janela_renomear, usar_nome_pasta.get())

    # Botão para iniciar a renomeação
    tk.Button(janela_renomear, text="Renomear", command=iniciar_renomeacao).pack(pady=10)

    def selecionar_pasta(entry):
        """Função auxiliar para selecionar uma pasta e preencher o campo de entrada."""
        pasta = filedialog.askdirectory(title="Selecione a pasta com os arquivos .NEF ou .CR2")
        if pasta:
            entry.delete(0, tk.END)
            entry.insert(0, pasta)
