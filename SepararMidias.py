import rawpy
from PIL import Image 
import numpy as np 
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

def janela_renomear_arquivos(master=None):
    """Cria uma janela para renomear arquivos RAW."""
    janela_renomear = tk.Toplevel(master)
    janela_renomear.title("ConverToou - Separa Midias")
    janela_renomear.geometry("600x600")
    janela_renomear.configure(bg="#f5f6f5")
    janela_renomear.resizable(False, False)

    # Estilo ttk
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 11), padding=6)
    style.configure("TLabel", background="#f5f6f5", font=("Helvetica", 11))
    style.configure("Accent.TButton", background="#0288D1", foreground="white")
    style.map("Accent.TButton",
              background=[("active", "#0277BD"), ("!active", "#0288D1")],
              foreground=[("active", "black"), ("!active", "black")])

    # Frame principal com borda sutil
    frame_principal = ttk.Frame(janela_renomear, padding="20", style="Transparent.TFrame", relief="groove", borderwidth=1)
    frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

    style.configure("Transparent.TFrame", background="#f5f6f5")

    # Título
    titulo = ttk.Label(frame_principal, text="Renomear Arquivos", font=("Helvetica", 18, "bold"), foreground="#0288D1", background="#f5f6f5")
    titulo.pack(pady=(0, 25))

    # Frame para entrada de pasta com borda
    frame_pasta = ttk.Frame(frame_principal, style="Transparent.TFrame", relief="groove", borderwidth=1)
    frame_pasta.pack(pady=10, padx=10, fill="x")
    ttk.Label(frame_pasta, text="Pasta com os arquivos:", background="#f5f6f5").pack(pady=(5, 5))
    frame_input_pasta = ttk.Frame(frame_pasta, style="Transparent.TFrame")
    frame_input_pasta.pack(anchor="center", pady=(0, 5))
    entry_pasta = ttk.Entry(frame_input_pasta, width=40)
    entry_pasta.pack(side="left", padx=(0, 10))
    ttk.Button(frame_input_pasta, text="Selecionar", command=lambda: selecionar_pasta(entry_pasta), style="TButton").pack(side="left")
    # Tooltip para pasta
    tk.Label(frame_pasta, text="Selecione a pasta contendo os arquivos a renomear", font=("Helvetica", 8), fg="#999", bg="#f5f6f5").pack(pady=(5, 0))

    # Frame para entrada de nome base com borda
    frame_nome_base = ttk.Frame(frame_principal, style="Transparent.TFrame", relief="groove", borderwidth=1)
    frame_nome_base.pack(pady=10, padx=10, fill="x")
    ttk.Label(frame_nome_base, text="Nome base (opcional):", background="#f5f6f5").pack(pady=(5, 5))
    nome_base_entry = ttk.Entry(frame_nome_base, width=40)
    nome_base_entry.pack(anchor="center", pady=(0, 5))
    # Tooltip para nome base
    tk.Label(frame_nome_base, text="Digite um nome base ou deixe em branco", font=("Helvetica", 8), fg="#999", bg="#f5f6f5").pack(pady=(5, 0))

    # Checkbox
    usar_nome_pasta = tk.BooleanVar()
    checkbox = ttk.Checkbutton(frame_principal, text="Usar nome da pasta como base", variable=usar_nome_pasta)
    checkbox.pack(pady=15)

    # Status com borda sutil
    status_frame = ttk.Frame(frame_principal, style="Transparent.TFrame", relief="groove", borderwidth=1)
    status_frame.pack(pady=10, padx=10, fill="x")
    status_label = ttk.Label(status_frame, text="Pronto para iniciar", wraplength=500, justify="center", background="#f5f6f5")
    status_label.pack(pady=10)

    # Botão Renomear
    botao_renomear = ttk.Button(frame_principal, text="Renomear", style="Accent.TButton", command=lambda: renomear_arquivos(
        entry_pasta.get(), nome_base_entry.get().strip() if not usar_nome_pasta.get() else None, status_label, janela_renomear, usar_nome_pasta.get()))
    botao_renomear.pack(pady=25)

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