import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import conversorCompleto  # Importa o módulo do conversorRAWtoJPG
import renomearArquivo    # Importa o módulo do renomearArquivos
import separarRAW         # Importa o módulo do separaRAW

def abrir_renomeador():
    """Abre a janela do conversor em uma nova janela."""
    renomearArquivo.janela_renomear_arquivos()

def abrir_conversor():
    """Abre a janela do conversor em uma nova janela."""
    conversorCompleto.janela_conversor()

def abrir_separador_raw():
    """Abre a janela do conversor em uma nova janela."""
    separarRAW.janela_separador()

def abrir_separador_alunos():
    """Abre a janela do conversor em uma nova janela."""
    separarRAW.janela_separador()

# Configuração da janela principal
janela_dashboard = tk.Tk()
janela_dashboard.title("ConverToou - Ferramentas de Imagem")
janela_dashboard.geometry("500x500")  # Aumentei um pouco para melhor proporção
janela_dashboard.configure(bg="#f5f6f5")  # Fundo cinza claro suave
janela_dashboard.resizable(False, False)  # Janela não redimensionável para manter o layout

# Estilo ttk
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 11), padding=10)
style.configure("TLabel", background="#f5f6f5", font=("Helvetica", 11))  # Fundo igual ao da janela
style.configure("Accent.TButton", background="#ADD8E6", foreground="black")  # Azul-claro para botões

# Frame principal
frame_principal = ttk.Frame(janela_dashboard, padding="20")
frame_principal.pack(fill="both", expand=True)
frame_principal.configure(style="Transparent.TFrame")  # Frame sem fundo destacado

# Estilo para o frame (remover fundo padrão)
style.configure("Transparent.TFrame", background="#f5f6f5")

# Título estilizado
titulo = ttk.Label(frame_principal, text="ConverToou", font=("Helvetica", 20, "bold"), foreground="#0288D1", background="#f5f6f5")
titulo.pack(pady=(20, 30))

# Subtítulo
subtitulo = ttk.Label(frame_principal, text="Ferramenta desenvolvida por Alexandre Galhardo", font=("Helvetica", 10, "italic"), foreground="#666", background="#f5f6f5")
subtitulo.pack(pady=(0, 20))

# Frame para botões
frame_botoes = ttk.Frame(frame_principal, style="Transparent.TFrame")
frame_botoes.pack()

# Botões com estilo
botao_renomear = ttk.Button(frame_botoes, text="Renomear Arquivos", command=abrir_renomeador, style="Accent.TButton", width=25)
botao_renomear.pack(pady=10)

botao_conversor = ttk.Button(frame_botoes, text="Conversor RAW para JPEG", command=abrir_conversor, style="Accent.TButton", width=25)
botao_conversor.pack(pady=10)

botao_separar = ttk.Button(frame_botoes, text="Separar Fotos em RAW", command=abrir_separador_raw, style="Accent.TButton", width=25)
botao_separar.pack(pady=10)

botao_separar = ttk.Button(frame_botoes, text="Separar Fotos dos Alunos", command=abrir_separador_raw, style="Accent.TButton", width=25)
botao_separar.pack(pady=10)

# Estilização adicional para hover e clique (efeito ao passar o mouse e clicar)
#style.map("Accent.TButton",
          #background=[("active", "#87CEEB"), ("!active", "#ADD8E6")],  # Escurece um pouco ao passar o mouse/clicar
          #foreground=[("active", "black"), ("!active", "black"), ("pressed", "black")])  # Mantém texto preto em todos os estados

# Rodapé (opcional)
rodape = ttk.Label(frame_principal, text="© 2025 - Desenvolvido por Alexandre Galhardo", font=("Helvetica", 8), foreground="#999", background="#f5f6f5")
rodape.pack(side="bottom", pady=10)

# Centralizar a janela na tela
janela_dashboard.update_idletasks()
width = janela_dashboard.winfo_width()
height = janela_dashboard.winfo_height()
x = (janela_dashboard.winfo_screenwidth() // 2) - (width // 2)
y = (janela_dashboard.winfo_screenheight() // 2) - (height // 2)
janela_dashboard.geometry(f"{width}x{height}+{x}+{y}")

# Iniciar o dashboard
janela_dashboard.mainloop()