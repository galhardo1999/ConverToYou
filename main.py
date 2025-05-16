import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import conversorCompleto  # Certifique-se de que o arquivo está no mesmo diretório
import renomearArquivo    # Certifique-se de que o arquivo está no mesmo diretório
import separarRAW
import SepararMidias

def abrir_renomeador():
    try:
        renomearArquivo.janela_renomear_arquivos(janela_dashboard)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao abrir renomeador: {str(e)}")

def abrir_conversor():
    try:
        conversorCompleto.janela_conversor(janela_dashboard)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao abrir conversor: {str(e)}")

def abrir_separador_raw():
    try:
        separarRAW.janela_separador(janela_dashboard)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao abrir separador RAW: {str(e)}")

def abrir_separador_midias():
    try:
        separarMidias.janela_separador(janela_dashboard)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao abrir separador RAW: {str(e)}")

# Configuração da janela principal
janela_dashboard = tk.Tk()
janela_dashboard.title("ConverToYou - Ferramentas de Imagem")
janela_dashboard.geometry("500x425")
janela_dashboard.configure(bg="#f5f6f5")
janela_dashboard.resizable(False, False)

# Estilo ttk
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 11), padding=10)
style.configure("TLabel", background="#f5f6f5", font=("Helvetica", 11))
style.configure("Accent.TButton", background="#ADD8E6", foreground="black")
style.configure("Transparent.TFrame", background="#f5f6f5")

# Frame principal
frame_principal = ttk.Frame(janela_dashboard, padding="20", style="Transparent.TFrame")
frame_principal.pack(fill="both", expand=True)

# Título e subtítulo
titulo = ttk.Label(frame_principal, text="ConverToYou", font=("Helvetica", 20, "bold"), foreground="#0288D1")
titulo.pack(pady=(20, 0))
subtitulo = ttk.Label(frame_principal, text="Version Alpha 1.0.1", font=("Helvetica", 10, "italic"), foreground="#666")
subtitulo.pack(pady=(2, 50))

# Frame para botões
frame_botoes = ttk.Frame(frame_principal, style="Transparent.TFrame")
frame_botoes.pack()

# Botões
botao_renomear = ttk.Button(frame_botoes, text="Renomear Arquivos", command=abrir_renomeador, style="Accent.TButton", width=30)
botao_renomear.pack(pady=10)

botao_conversor = ttk.Button(frame_botoes, text="Conversor de Imagens", command=abrir_conversor, style="Accent.TButton", width=30)
botao_conversor.pack(pady=10)

botao_separar = ttk.Button(frame_botoes, text="Fotos escolhidas JPG para Raw", command=abrir_separador_raw, style="Accent.TButton", width=30)
botao_separar.pack(pady=10)

botao_separar = ttk.Button(frame_botoes, text="Separar Midias", command=abrir_separador_midias, style="Accent.TButton", width=30)
botao_separar.pack(pady=10)

# Rodapé
rodape = ttk.Label(frame_principal, text="© 2025 - Desenvolvido por Alexandre Galhardo", font=("Helvetica", 8), foreground="#999")
rodape.pack(side="bottom", pady=10)

# Centralizar janela
janela_dashboard.update_idletasks()
width = janela_dashboard.winfo_width()
height = janela_dashboard.winfo_height()
x = (janela_dashboard.winfo_screenwidth() // 2) - (width // 2)
y = (janela_dashboard.winfo_screenheight() // 2) - (height // 2)
janela_dashboard.geometry(f"{width}x{height}+{x}+{y}")

# Protocolo de fechamento
janela_dashboard.protocol("WM_DELETE_WINDOW", janela_dashboard.quit)

# Iniciar o dashboard
janela_dashboard.mainloop()