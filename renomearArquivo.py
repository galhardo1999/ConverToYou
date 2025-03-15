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
    
    # Contar total de arquivos RAW e JPEG
    for raiz, _, arquivos in os.walk(pasta_origem):
        for arquivo in arquivos:
            if arquivo.lower().endswith(('.nef', '.cr2', '.jpeg', '.jpg')):
                total_arquivos += 1
    
    if total_arquivos == 0:
        status_label.config(text="Nenhum arquivo encontrado!")
        janela.update()
        return 0
    
    # Renomear os arquivos
    for raiz, _, arquivos in os.walk(pasta_origem):
        contador_local = 1  # Contador reinicia para cada subpasta quando usar_nome_pasta é True
        for arquivo in arquivos:
            if arquivo.lower().endswith(('.nef', '.cr2', '.jpeg', '.jpg')):
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
    
    status_label.config(text=f"Concluído! {arquivos_renomeados}/{total_arquivos} arquivos renomeados.")
    janela.update()
    return arquivos_renomeados

def selecionar_pasta(entry):
    """Função auxiliar para selecionar uma pasta e preencher o campo de entrada."""
    pasta = filedialog.askdirectory(title="Selecione a pasta com os arquivos")
    if pasta:
        entry.delete(0, tk.END)
        entry.insert(0, pasta)

def janela_renomear_arquivos():
    """Cria uma janela para renomear arquivos RAW."""
    janela_renomear = tk.Toplevel()
    janela_renomear.title("ConverToou - Renomear Arquivos")
    janela_renomear.geometry("600x600")
    janela_renomear.configure(bg="#f5f6f5")  # Fundo cinza claro suave
    janela_renomear.resizable(False, False)  # Janela não redimensionável

    # Estilo ttk
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 11), padding=10)
    style.configure("TLabel", background="#f5f6f5", font=("Helvetica", 11))  # Fundo igual ao da janela
    style.configure("Accent.TButton", background="#0288D1", foreground="white")  # Azul elegante
    style.map("Accent.TButton",
              background=[("active", "#0277BD"), ("!active", "#0288D1")],
              foreground=[("active", "white"), ("!active", "white")])

    # Frame principal
    frame_principal = ttk.Frame(janela_renomear, padding="20", style="Transparent.TFrame")
    frame_principal.pack(fill="both", expand=True)

    # Estilo para frame transparente
    style.configure("Transparent.TFrame", background="#f5f6f5")

    # Título
    titulo = ttk.Label(frame_principal, text="Renomear Arquivos", font=("Helvetica", 18, "bold"), foreground="#0288D1", background="#f5f6f5")
    titulo.pack(pady=(10, 20))

    # Entrada Pasta
    ttk.Label(frame_principal, text="Pasta com os arquivos:", background="#f5f6f5").pack(pady=5)
    entry_pasta = ttk.Entry(frame_principal, width=50)
    entry_pasta.pack(pady=5)
    ttk.Button(frame_principal, text="Selecionar", command=lambda: selecionar_pasta(entry_pasta), width=12).pack(pady=5)

    # Entrada Nome Base
    ttk.Label(frame_principal, text="Nome base (opcional):", background="#f5f6f5").pack(pady=5)
    nome_base_entry = ttk.Entry(frame_principal, width=50)
    nome_base_entry.pack(pady=5)

    # Checkbox
    usar_nome_pasta = tk.BooleanVar()
    checkbox = ttk.Checkbutton(frame_principal, text="Usar nome da pasta como base", variable=usar_nome_pasta)
    checkbox.pack(pady=10)

    # Status
    status_label = ttk.Label(frame_principal, text="Pronto para iniciar", wraplength=500, justify="center", background="#f5f6f5")
    status_label.pack(pady=10)

    # Botão Renomear
    botao_renomear = ttk.Button(frame_principal, text="Renomear", style="Accent.TButton", command=lambda: renomear_arquivos(
        entry_pasta.get(), nome_base_entry.get().strip() if not usar_nome_pasta.get() else None, status_label, janela_renomear, usar_nome_pasta.get()))
    botao_renomear.pack(pady=20)

    # Rodapé
    rodape = ttk.Label(frame_principal, text="© 2025 - Desenvolvido por Alexandre Galhardo", font=("Helvetica", 8), foreground="#999", background="#f5f6f5")
    rodape.pack(side="bottom", pady=10)

    # Centralizar a janela
    janela_renomear.update_idletasks()
    width = janela_renomear.winfo_width()
    height = janela_renomear.winfo_height()
    x = (janela_renomear.winfo_screenwidth() // 2) - (width // 2)
    y = (janela_renomear.winfo_screenheight() // 2) - (height // 2)
    janela_renomear.geometry(f"{width}x{height}+{x}+{y}")

# Para testar standalone (remova se for usar no dashboard)
if __name__ == "__main__":
    janela_renomear_arquivos()
    tk.mainloop()