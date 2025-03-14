import tkinter as tk
from tkinter import ttk, messagebox
import hashlib

# Senha secreta (deve ser igual ao programa principal)
SENHA_SECRETA = "sua_senha_secreta"  # Substitua por algo único

# Função para gerar a chave de licença
def gerar_chave_licenca(machine_id, codigo_renovacao=""):
    return hashlib.sha256((machine_id + SENHA_SECRETA + codigo_renovacao).encode()).hexdigest()[:16]

# Função para gerar e exibir a chave
def gerar():
    machine_id = entry_machine_id.get().strip()
    codigo_renovacao = entry_codigo.get().strip()
    if not machine_id or not codigo_renovacao:
        messagebox.showerror("Erro", "Por favor, insira o Machine ID e o código de renovação!")
        return
    
    chave = gerar_chave_licenca(machine_id, codigo_renovacao)
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, f"Chave gerada para Machine ID '{machine_id}' e Código '{codigo_renovacao}':\n\n{chave}\n\n")
    text_output.insert(tk.END, "Copie esta chave e o código de renovação e forneça ao cliente. Válido por 30 dias a partir da ativação.")

# Configuração da interface gráfica
root = tk.Tk()
root.title("Gerador de Chaves - Copiar Fotos RAW")
root.geometry("400x350")

tk.Label(root, text="Insira o Machine ID do cliente:").pack(pady=10)
entry_machine_id = tk.Entry(root, width=40)
entry_machine_id.pack(pady=5)

tk.Label(root, text="Insira um código de renovação único:").pack(pady=10)
entry_codigo = tk.Entry(root, width=40)
entry_codigo.pack(pady=5)

tk.Button(root, text="Gerar Chave", command=gerar, bg="blue", fg="white").pack(pady=10)

text_output = tk.Text(root, height=10, width=50)
text_output.pack(pady=10)

root.mainloop()