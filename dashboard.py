import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import conversorCompleto  # Importa o módulo do conversor
import os

def abrir_conversor():
    """Abre a janela do conversor em uma nova janela."""
    conversorCompleto.janela_conversor()

def renomear_arquivos_janela():
    """Cria uma janela para renomear arquivos RAW."""
    janela_renomear = tk.Toplevel()
    janela_renomear.title("Renomear Arquivos RAW")
    janela_renomear.geometry("400x300")

    # Campo para o nome base
    tk.Label(janela_renomear, text="Nome base para renomear (opcional):").pack(pady=5)
    nome_base_entry = tk.Entry(janela_renomear, width=40)
    nome_base_entry.pack(pady=5)

    # Checkbox para usar o nome da pasta
    usar_nome_pasta = tk.BooleanVar()  # Variável para controlar o estado do checkbox
    checkbox = tk.Checkbutton(
        janela_renomear, 
        text="Usar o nome da pasta como nome base", 
        variable=usar_nome_pasta
    )
    checkbox.pack(pady=5)

    # Campo para selecionar a pasta
    tk.Label(janela_renomear, text="Pasta com os arquivos .NEF ou .CR2:").pack(pady=5)
    entry_pasta = tk.Entry(janela_renomear, width=40)
    entry_pasta.pack(pady=5)
    tk.Button(janela_renomear, text="Selecionar Pasta", command=lambda: selecionar_pasta(entry_pasta)).pack(pady=5)

    # Label de status
    status_label = tk.Label(janela_renomear, text="Pronto para iniciar", wraplength=350)
    status_label.pack(pady=10)

    # Função para determinar o nome base antes de chamar a renomeação
    def iniciar_renomeacao():
        pasta = entry_pasta.get()
        nome_base = nome_base_entry.get().strip()
        if usar_nome_pasta.get() and pasta:  # Se o checkbox está marcado e há uma pasta selecionada
            nome_base = os.path.basename(pasta)  # Usa o nome da pasta como nome base
        conversorCompleto.renomear_arquivos_raw(pasta, nome_base, status_label, janela_renomear)

    # Botão para iniciar a renomeação
    tk.Button(janela_renomear, text="Renomear", command=iniciar_renomeacao).pack(pady=10)

def selecionar_pasta(entry):
    """Função auxiliar para selecionar uma pasta e preencher o campo de entrada."""
    pasta = filedialog.askdirectory(title="Selecione a pasta com os arquivos .NEF ou .CR2")
    if pasta:
        entry.delete(0, tk.END)
        entry.insert(0, pasta)

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

# Botão para renomear arquivos
botao_renomear = ttk.Button(frame_principal, text="Renomear Arquivos", command=renomear_arquivos_janela)
botao_renomear.pack(pady=10)

# Iniciar o dashboard
janela_dashboard.mainloop()