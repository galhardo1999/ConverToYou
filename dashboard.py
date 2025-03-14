import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import conversorCompleto  # Importa o módulo do conversor
import renomearArquivo  # Importa o módulo do conversor
import os

def abrir_conversor():
    """Abre a janela do conversor em uma nova janela."""
    conversorCompleto.janela_conversor()

def abrir_renomeador():
    """Abre a janela do conversor em uma nova janela."""
    renomearArquivo.janela_renomear_arquivos()

# Criar a janela principal do dashboard
janela_dashboard = tk.Tk()
janela_dashboard.title("ConverToou - Ferramentas de Imagem  by Alexandre G.")
janela_dashboard.geometry("500x200")

# Frame principal
frame_principal = ttk.Frame(janela_dashboard, padding="10")
frame_principal.pack(fill="both", expand=True)

# Título do Dashboard
titulo = ttk.Label(frame_principal, text="Bem-vindo ao ConverToou", font=("Helvetica", 16, "bold"))
titulo.pack(pady=20)

# Botão para abrir o conversor
botao_conversor = ttk.Button(frame_principal, text="Conversor RAW para JPEG", command=abrir_conversor)
botao_conversor.pack(pady=10)

# Botão para renomear arquivos
botao_renomear = ttk.Button(frame_principal, text="    Renomear Arquivos    ", command=abrir_renomeador)
botao_renomear.pack(pady=10)

# Iniciar o dashboard
janela_dashboard.mainloop()