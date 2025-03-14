import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import hashlib
from datetime import datetime, timedelta
import json
import sys

# Caminho para o arquivo de licença
LICENCA_ARQUIVO = os.path.join(os.path.dirname(__file__), "licenca.json")

# Senha secreta (deve ser igual ao gerador)
SENHA_SECRETA = "sua_senha_secreta"  # Substitua por algo único

# Função para obter o identificador único da máquina
def get_machine_id():
    return hashlib.md5(os.environ.get("COMPUTERNAME", "default").encode()).hexdigest()

# Função para gerar uma chave válida
def gerar_chave_licenca(machine_id, codigo_renovacao=""):
    return hashlib.sha256((machine_id + SENHA_SECRETA + codigo_renovacao).encode()).hexdigest()[:16]

# Função para salvar a licença
def salvar_licenca(chave, codigo_renovacao):
    data_ativacao = datetime.now().strftime("%Y-%m-%d")
    licenca = {"chave": chave, "data_ativacao": data_ativacao, "codigo_renovacao": codigo_renovacao}
    with open(LICENCA_ARQUIVO, "w") as f:
        json.dump(licenca, f)

# Função para verificar a licença
def verificar_licenca():
    machine_id = get_machine_id()
    if not os.path.exists(LICENCA_ARQUIVO):
        return False, "Nenhuma licença encontrada. Insira uma chave válida."
    
    try:
        with open(LICENCA_ARQUIVO, "r") as f:
            licenca = json.load(f)
        chave = licenca.get("chave")
        data_ativacao = datetime.strptime(licenca.get("data_ativacao"), "%Y-%m-%d")
        codigo_renovacao = licenca.get("codigo_renovacao", "")
        
        chave_correta = gerar_chave_licenca(machine_id, codigo_renovacao)
        if chave != chave_correta:
            return False, "Chave de licença inválida."
        
        if datetime.now() > data_ativacao + timedelta(days=30):
            os.remove(LICENCA_ARQUIVO)
            return False, "Licença expirada. Solicite uma nova chave."
        
        return True, "Licença válida."
    except Exception as e:
        if os.path.exists(LICENCA_ARQUIVO):
            os.remove(LICENCA_ARQUIVO)
        return False, f"Erro ao verificar licença: {e}"

# Função para solicitar a chave com mensagem do machine_id
def solicitar_chave():
    machine_id = get_machine_id()
    messagebox.showinfo("Machine ID", f"Por favor, forneça este Machine ID ao suporte para obter sua chave: {machine_id}")
    
    def ativar():
        chave_inserida = entry_chave.get()
        codigo_renovacao = entry_codigo.get()
        if not codigo_renovacao:
            messagebox.showerror("Erro", "O código de renovação é obrigatório!")
            return
        if chave_inserida == gerar_chave_licenca(machine_id, codigo_renovacao):
            salvar_licenca(chave_inserida, codigo_renovacao)
            messagebox.showinfo("Sucesso", "Licença ativada com sucesso! O programa será reiniciado.")
            janela.destroy()
            root.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            messagebox.showerror("Erro", "Chave ou código de renovação inválido!")
    
    janela = tk.Toplevel(root)
    janela.title("Ativação de Licença")
    janela.geometry("300x200")
    
    tk.Label(janela, text="Insira a chave de licença:").pack(pady=10)
    entry_chave = tk.Entry(janela, width=30)
    entry_chave.pack(pady=5)
    
    tk.Label(janela, text="Insira o código de renovação:").pack(pady=10)
    entry_codigo = tk.Entry(janela, width=30)
    entry_codigo.pack(pady=5)
    
    tk.Button(janela, text="Ativar", command=ativar).pack(pady=10)

# Variável global para controlar o cancelamento
cancelar = False

def selecionar_pasta(entry):
    pasta = filedialog.askdirectory()
    if pasta:
        entry.delete(0, tk.END)
        entry.insert(0, pasta)

def cancelar_processo():
    global cancelar
    cancelar = True
    text_output.insert(tk.END, "\nCancelamento solicitado...\n")
    root.update()

def contar_jpegs(pasta_alunos):
    total = 0
    for aluno in os.listdir(pasta_alunos):
        caminho_aluno = os.path.join(pasta_alunos, aluno)
        if os.path.isdir(caminho_aluno):
            total += len([f for f in os.listdir(caminho_aluno) if f.lower().endswith(('.jpeg', '.jpg'))])
    return total

def formatar_tempo(segundos):
    if segundos < 60:
        return f"{int(segundos)}s"
    minutos = segundos // 60
    segundos_restantes = int(segundos % 60)
    return f"{minutos}m {segundos_restantes}s"

def processar():
    global cancelar
    cancelar = False

    pasta_raw = entry_raw.get()
    pasta_alunos = entry_alunos.get()
    pasta_destino = entry_destino.get()

    if not (pasta_raw and pasta_alunos and pasta_destino):
        messagebox.showerror("Erro", "Por favor, selecione todas as pastas!")
        return

    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    raw_files = {}
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, "Indexando arquivos RAW...\n")
    root.update()
    
    for root_dir, dirs, files in os.walk(pasta_raw):
        if cancelar:
            break
        for file in files:
            if file.lower().endswith(('.cr2', '.nef')):
                nome_base = os.path.splitext(file)[0]
                raw_files[nome_base] = os.path.join(root_dir, file)
    
    if cancelar:
        text_output.insert(tk.END, "Processo cancelado durante indexação.\n")
        return
    
    text_output.insert(tk.END, f"Encontrados {len(raw_files)} arquivos RAW.\n\n")
    root.update()

    total_jpegs = contar_jpegs(pasta_alunos)
    if total_jpegs == 0:
        messagebox.showerror("Erro", "Nenhum arquivo JPEG encontrado nas pastas dos alunos!")
        return
    
    progress_bar["maximum"] = total_jpegs
    progress_bar["value"] = 0
    processed = 0
    total_copiados = 0
    total_nao_encontrados = 0
    tempo_inicio = time.time()

    for aluno in os.listdir(pasta_alunos):
        if cancelar:
            break
        caminho_aluno = os.path.join(pasta_alunos, aluno)
        if os.path.isdir(caminho_aluno):
            destino_aluno = os.path.join(pasta_destino, aluno)
            if not os.path.exists(destino_aluno):
                os.makedirs(destino_aluno)
            
            for foto in os.listdir(caminho_aluno):
                if cancelar:
                    break
                if foto.lower().endswith(('.jpeg', '.jpg')):
                    nome_base = os.path.splitext(foto)[0]
                    processed += 1
                    progress_bar["value"] = processed
                    
                    porcentagem = (processed / total_jpegs) * 100
                    tempo_decorrido = time.time() - tempo_inicio
                    if processed > 0:
                        tempo_por_arquivo = tempo_decorrido / processed
                        arquivos_restantes = total_jpegs - processed
                        tempo_restante = tempo_por_arquivo * arquivos_restantes
                        label_progress.config(text=f"Progresso: {processed}/{total_jpegs} ({porcentagem:.1f}%) - Restante: {formatar_tempo(tempo_restante)}")
                    else:
                        label_progress.config(text=f"Progresso: {processed}/{total_jpegs} ({porcentagem:.1f}%)")
                    
                    if nome_base in raw_files:
                        raw_path = raw_files[nome_base]
                        destino_raw = os.path.join(destino_aluno, os.path.basename(raw_path))
                        try:
                            shutil.copy2(raw_path, destino_raw)
                            text_output.insert(tk.END, f"Copiado: {os.path.basename(raw_path)} -> {destino_aluno}\n")
                            total_copiados += 1
                        except Exception as e:
                            text_output.insert(tk.END, f"Erro ao copiar {raw_path}: {e}\n")
                    else:
                        text_output.insert(tk.END, f"RAW não encontrado para: {foto}\n")
                        total_nao_encontrados += 1
                    text_output.see(tk.END)
                    root.update()

    if cancelar:
        text_output.insert(tk.END, "\nProcesso cancelado pelo usuário.\n")
    else:
        text_output.insert(tk.END, f"\nProcesso concluído!\n")
    text_output.insert(tk.END, f"Total de arquivos RAW copiados: {total_copiados}\n")
    text_output.insert(tk.END, f"Total de arquivos não encontrados: {total_nao_encontrados}\n")
    label_progress.config(text=f"Progresso: {processed}/{total_jpegs} (100%)" if not cancelar else "Cancelado")
    messagebox.showinfo("Concluído", "Processamento finalizado ou cancelado!")

# Configuração da interface gráfica
root = tk.Tk()
root.title("Copiar Fotos RAW - Escola")
root.geometry("600x450")

# Verificar licença ao iniciar
valida, mensagem = verificar_licenca()
if not valida:
    messagebox.showwarning("Licença", mensagem)
    solicitar_chave()
    root.mainloop()
    sys.exit()

# Labels e Entradas
tk.Label(root, text="Pasta com arquivos RAW:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_raw = tk.Entry(root, width=50)
entry_raw.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Selecionar", command=lambda: selecionar_pasta(entry_raw)).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Pasta com fotos dos alunos (JPEG):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_alunos = tk.Entry(root, width=50)
entry_alunos.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Selecionar", command=lambda: selecionar_pasta(entry_alunos)).grid(row=1, column=2, padx=5, pady=5)

tk.Label(root, text="Pasta de destino para os RAW:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_destino = tk.Entry(root, width=50)
entry_destino.grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="Selecionar", command=lambda: selecionar_pasta(entry_destino)).grid(row=2, column=2, padx=5, pady=5)

tk.Button(root, text="Processar", command=processar, bg="green", fg="white").grid(row=3, column=1, pady=5)
tk.Button(root, text="Cancelar", command=cancelar_processo, bg="red", fg="white").grid(row=3, column=2, pady=5)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=4, column=0, columnspan=3, padx=5, pady=5)
label_progress = tk.Label(root, text="Progresso: 0/0 (0%)")
label_progress.grid(row=5, column=0, columnspan=3)

text_output = tk.Text(root, height=15, width=70)
text_output.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()