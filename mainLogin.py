import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import conversorCompletoSite
import renomearArquivo
import separarRAW

API_URL = "http://localhost:5000/api/login"
API_USAGE_URL = "http://localhost:5000/api/usage"

def update_usage_label():
    """Atualiza o label_plano com o uso mais recente do usuário."""
    try:
        response = requests.post(API_USAGE_URL, json={"email": session_info["user_email"]}, timeout=1)
        result = response.json()
        if result.get("success"):
            session_info["photo_count"] = result.get("photo_count", 0)
            session_info["limit"] = result.get("limit", 300)
            limit_display = session_info["limit"] if session_info["limit"] != float('inf') else 'ilimitadas'
            label_plano.config(text=f"Plano: {session_info['plan_name']} ({session_info['photo_count']}/{limit_display})")
        else:
            messagebox.showerror("Erro", "Falha ao atualizar uso: " + result.get("message", "Erro desconhecido"))
    except requests.Timeout:
        messagebox.showerror("Erro", "Tempo limite excedido ao atualizar uso. Verifique se o servidor está ativo.")
    except requests.RequestException as e:
        messagebox.showerror("Erro", f"Falha ao atualizar uso: {str(e)}")

def abrir_renomeador():
    try:
        renomearArquivo.janela_renomear_arquivos(janela_dashboard)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao abrir renomeador: {str(e)}")

def abrir_conversor():
    try:
        conversorCompletoSite.janela_conversor(janela_dashboard, email=session_info["user_email"], on_update=update_usage_label)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao abrir conversor: {str(e)}")


def login():
    email = entry_email.get()
    password = entry_password.get()
    if not email or not password:
        messagebox.showerror("Erro", "Por favor, preencha e-mail e senha.")
        return
    
    try:
        response = requests.post(API_URL, json={"email": email, "password": password}, timeout=5)
        result = response.json()
        if result.get("success"):
            if result.get("plan_status") == "active" or result.get("email") == "admin@example.com":
                session_info["user_email"] = email
                session_info["plan_name"] = result.get("plan_name")
                session_info["plan_status"] = result.get("plan_status")
                usage = result.get("usage", {})
                session_info["photo_count"] = usage.get("photo_count", 0)
                session_info["limit"] = usage.get("limit", 300)
                limit_display = session_info["limit"] if session_info["limit"] != float('inf') else 'ilimitadas'
                janela_login.pack_forget()
                label_plano.config(text=f"Plano: {session_info['plan_name']} ({session_info['photo_count']}/{limit_display})")
                janela_dashboard.pack(fill="both", expand=True)
                root.update()
            else:
                messagebox.showwarning("Aviso", "Você não possui um plano ativo. Assine um plano no site.")
        else:
            messagebox.showerror("Erro", result.get("message", "Falha ao autenticar"))
    except requests.Timeout:
        messagebox.showerror("Erro", "Tempo limite excedido ao conectar ao servidor. Verifique sua conexão ou se o servidor está ativo.")
    except requests.RequestException as e:
        messagebox.showerror("Erro", f"Falha na conexão com o servidor: {str(e)}")

root = tk.Tk()
root.title("ConverToYou - Ferramentas de Imagem")
root.geometry("500x425")
root.configure(bg="#f5f6f5")
root.resizable(False, False)

session_info = {}

style = ttk.Style()
style.configure("TButton", font=("Helvetica", 11), padding=10)
style.configure("TLabel", background="#f5f6f5", font=("Helvetica", 11))
style.configure("Accent.TButton", background="#ADD8E6", foreground="black")
style.configure("Transparent.TFrame", background="#f5f6f5")

janela_login = ttk.Frame(root, padding="20", style="Transparent.TFrame")
janela_login.pack(fill="both", expand=True)

titulo_login = ttk.Label(janela_login, text="ConverToYou", font=("Helvetica", 20, "bold"), foreground="#0288D1")
titulo_login.pack(pady=(20, 20))

frame_form = ttk.Frame(janela_login, style="Transparent.TFrame")
frame_form.pack()

ttk.Label(frame_form, text="E-mail:", background="#f5f6f5").pack(pady=(10, 5))
entry_email = ttk.Entry(frame_form, width=30)
entry_email.pack()

ttk.Label(frame_form, text="Senha:", background="#f5f6f5").pack(pady=(10, 5))
entry_password = ttk.Entry(frame_form, width=30, show="*")
entry_password.pack()

botao_login = ttk.Button(frame_form, text="Entrar", command=login, style="Accent.TButton")
botao_login.pack(pady=20)

janela_dashboard = ttk.Frame(root, padding="20", style="Transparent.TFrame")

titulo = ttk.Label(janela_dashboard, text="ConverToYou", font=("Helvetica", 20, "bold"), foreground="#0288D1")
titulo.pack(pady=(20, 0))
subtitulo = ttk.Label(janela_dashboard, text="Version Alpha 1.0.1", font=("Helvetica", 10, "italic"), foreground="#666")
subtitulo.pack(pady=(2, 10))

label_plano = ttk.Label(janela_dashboard, text="Plano: Nenhum", font=("Helvetica", 12), foreground="#0288D1")
label_plano.pack(pady=(0, 40))

frame_botoes = ttk.Frame(janela_dashboard, style="Transparent.TFrame")
frame_botoes.pack()

botao_renomear = ttk.Button(frame_botoes, text="Renomear Arquivos", command=abrir_renomeador, style="Accent.TButton", width=30)
botao_renomear.pack(pady=10)

botao_conversor = ttk.Button(frame_botoes, text="Conversor de Imagens", command=abrir_conversor, style="Accent.TButton", width=30)
botao_conversor.pack(pady=10)

rodape = ttk.Label(janela_dashboard, text="© 2025 - Desenvolvido por Alexandre Galhardo", font=("Helvetica", 8), foreground="#999")
rodape.pack(side="bottom", pady=10)

root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")

root.protocol("WM_DELETE_WINDOW", root.quit)

root.mainloop()