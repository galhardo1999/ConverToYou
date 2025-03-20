import tkinter as tk
from tkinter import ttk, messagebox
import conversorCompleto
import renomearArquivo
import separarRAW
import separaFotos
import fazerRelatorio
import json
import os
from datetime import datetime, timedelta
import stripe

# Configurar a chave secreta do Stripe (substitua pela sua chave)
stripe.api_key = "sk_test_51R4oUMKtdJBavtk3tqtQUgagXZeDwuUsb58Yy9DYrq1Ult6Yufvh8LHP38FvtBqCY9sES4i94xi6EeVQRS0iEsaB008R5dMyBw"  # Substitua por sua chave secreta real

# Simulação de um arquivo de usuário para armazenar o plano e expiração
USER_FILE = "user_data.json"

# Função para carregar ou criar dados do usuário
def load_user_data():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            user_data = json.load(f)
            # Garantir que 'expiration' esteja presente
            if "expiration" not in user_data:
                user_data["expiration"] = None
            return user_data
    else:
        # Plano padrão: Gratuito
        default_data = {"subscription": "Free", "username": "guest", "expiration": None}
        with open(USER_FILE, 'w') as f:
            json.dump(default_data, f)
        return default_data

# Função para verificar se a licença está ativa e calcular dias restantes
def is_subscription_active():
    user_data = load_user_data()
    if user_data["subscription"] == "Premium" and user_data["expiration"] is not None:
        expiration_date = datetime.strptime(user_data["expiration"], "%Y-%m-%d")
        if datetime.now() <= expiration_date:
            return True, expiration_date
    return False, None

# Função para calcular os dias restantes até a expiração
def get_days_remaining(expiration_date):
    if expiration_date:
        delta = expiration_date - datetime.now()
        return max(0, delta.days)  # Retorna 0 se já expirou
    return None

# Função para verificar o plano do usuário
def check_subscription(feature):
    is_active, _ = is_subscription_active()
    user_data = load_user_data()
    subscription = user_data["subscription"] if is_active else "Free"
    
    plans = {
        "Free": ["Renomear Arquivos"],
        "Basic": ["Renomear Arquivos", "Conversor RAW para JPEG"],
        "Premium": ["Renomear Arquivos", "Conversor RAW para JPEG", "Fotos escolhidas JPG para Raw", 
                    "Separar Fotos de Alunos", "Relatório de Alunos"]
    }
    return feature in plans[subscription]

# Funções de abertura com verificação de plano
def abrir_renomeador():
    if check_subscription("Renomear Arquivos"):
        try:
            renomearArquivo.janela_renomear_arquivos(janela_dashboard)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir renomeador: {str(e)}")

def abrir_conversor():
    if check_subscription("Conversor RAW para JPEG"):
        try:
            conversorCompleto.janela_conversor(janela_dashboard)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir conversor: {str(e)}")

def abrir_separador_raw():
    if check_subscription("Fotos escolhidas JPG para Raw"):
        try:
            separarRAW.janela_separador(janela_dashboard)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir separador RAW: {str(e)}")

def abrir_fazer_relatorio():
    if check_subscription("Relatório de Alunos"):
        try:
            janela_relatorio = tk.Toplevel(janela_dashboard)
            app = fazerRelatorio.GeradorRelatorioComparativo(janela_relatorio)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir o gerador de relatórios: {str(e)}")

def abrir_separar_fotos():
    if check_subscription("Separar Fotos de Alunos"):
        try:
            separaFotos.janela_separador_fotos(janela_dashboard)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir separador de fotos: {str(e)}")

# Função para atualizar o estado dos botões com base no plano
def update_button_states():
    user_data = load_user_data()
    is_active, expiration_date = is_subscription_active()
    subscription = user_data["subscription"] if is_active else "Free"
    
    # Calcular dias restantes
    days_remaining = get_days_remaining(expiration_date)
    
    # Atualizar subtítulo com "Expira em" se for Premium e ativo
    if subscription == "Premium" and is_active and days_remaining is not None:
        subtitulo.config(text=f"Plano: {subscription} (Expira em: {days_remaining} dias)")
    else:
        subtitulo.config(text=f"Plano: {subscription}")
    
    plans = {
        "Free": ["Renomear Arquivos"],
        "Basic": ["Renomear Arquivos", "Conversor RAW para JPEG"],
        "Premium": ["Renomear Arquivos", "Conversor RAW para JPEG", "Fotos escolhidas JPG para Raw", 
                    "Separar Fotos de Alunos", "Relatório de Alunos"]
    }
    
    buttons = {
        "Renomear Arquivos": botao_renomear,
        "Conversor RAW para JPEG": botao_conversor,
        "Fotos escolhidas JPG para Raw": botao_separar,
        "Separar Fotos de Alunos": botao_separar_fotos,
        "Relatório de Alunos": botao_relatorio
    }
    
    for feature, button in buttons.items():
        if feature in plans[subscription]:
            button.config(state="normal")
        else:
            button.config(state="disabled")

# Função para criar uma sessão de checkout no Stripe e abrir no browser
def become_premium():
    try:
        # Criar uma sessão de checkout no Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': 'Plano Premium - 30 Dias',
                    },
                    'unit_amount': 1,  # R$50,00 (em centavos)
                    'recurring': {
                        'interval': 'month',
                        'interval_count': 1,
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url='http://localhost:8000/success',
            cancel_url='http://localhost:8000/cancel',
        )
        
        # Abrir o link de checkout no navegador padrão
        import webbrowser
        webbrowser.open(session.url)
        
        # Simulação de pagamento bem-sucedido (em produção, use webhooks)
        messagebox.showinfo("Pagamento", "Após o pagamento, seu plano será atualizado para Premium.")
        user_data = load_user_data()
        user_data["subscription"] = "Premium"
        user_data["expiration"] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        with open(USER_FILE, 'w') as f:
            json.dump(user_data, f)
        update_button_states()

    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao processar pagamento: {str(e)}")

# Configuração da janela principal
janela_dashboard = tk.Tk()
janela_dashboard.title("ConverToYou - Ferramentas de Imagem")
janela_dashboard.geometry("500x600")
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
subtitulo = ttk.Label(frame_principal, text="", font=("Helvetica", 10, "italic"), foreground="#666")
subtitulo.pack(pady=(2, 50))

# Frame para botões
frame_botoes = ttk.Frame(frame_principal, style="Transparent.TFrame")
frame_botoes.pack()

# Botões
botao_renomear = ttk.Button(frame_botoes, text="Renomear Arquivos", command=abrir_renomeador, style="Accent.TButton", width=30)
botao_renomear.pack(pady=10)

botao_conversor = ttk.Button(frame_botoes, text="Conversor RAW para JPEG", command=abrir_conversor, style="Accent.TButton", width=30)
botao_conversor.pack(pady=10)

botao_separar = ttk.Button(frame_botoes, text="Fotos escolhidas JPG para Raw", command=abrir_separador_raw, style="Accent.TButton", width=30)
botao_separar.pack(pady=10)

botao_separar_fotos = ttk.Button(frame_botoes, text="Separar Fotos de Alunos", command=abrir_separar_fotos, style="Accent.TButton", width=30)
botao_separar_fotos.pack(pady=10)

botao_relatorio = ttk.Button(frame_botoes, text="Relatório de Alunos", command=abrir_fazer_relatorio, style="Accent.TButton", width=30)
botao_relatorio.pack(pady=10)

botao_premium = ttk.Button(frame_botoes, text="Seja Premium", command=become_premium, style="Accent.TButton", width=30)
botao_premium.pack(pady=10)

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

# Atualizar estado dos botões ao iniciar
update_button_states()

# Protocolo de fechamento
janela_dashboard.protocol("WM_DELETE_WINDOW", janela_dashboard.quit)

# Iniciar o dashboard
janela_dashboard.mainloop()
