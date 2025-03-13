import tkinter as tk
from tkinter import ttk
import conversorCompleto  # Importa o módulo do conversor

def abrir_conversor():
    """Abre a janela do conversor em uma nova janela."""
    conversorCompleto.janela_conversor()

# Criar a janela principal do dashboard
janela_dashboard = tk.Tk()
janela_dashboard.title("ConverToou - Ferramentas de Imagem  by Alexandre G.")
janela_dashboard.geometry("600x400")

# Frame principal
frame_principal = ttk.Frame(janela_dashboard, padding="10")
frame_principal.pack(fill="both", expand=True)

# Título do Dashboard
titulo = ttk.Label(frame_principal, text="Bem-vindo ao ConverToou", font=("Helvetica", 16, "bold"))
titulo.pack(pady=20)

# Botão para abrir o conversor
botao_conversor = ttk.Button(frame_principal, text="Conversor RAW para JPEG", command=abrir_conversor)
botao_conversor.pack(pady=10)

# Iniciar o dashboard
janela_dashboard.mainloop()