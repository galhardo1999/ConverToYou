import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time

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

    # Criar a pasta de destino, se não existir
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    # Indexar arquivos RAW
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

    # Contar total de JPEGs para a barra de progresso
    total_jpegs = contar_jpegs(pasta_alunos)
    if total_jpegs == 0:
        messagebox.showerror("Erro", "Nenhum arquivo JPEG encontrado nas pastas dos alunos!")
        return
    
    progress_bar["maximum"] = total_jpegs
    progress_bar["value"] = 0
    processed = 0
    total_copiados = 0
    total_nao_encontrados = 0
    tempo_inicio = time.time()  # Início do processamento

    # Processar pastas dos alunos
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
                    
                    # Calcular progresso e tempo restante
                    porcentagem = (processed / total_jpegs) * 100
                    tempo_decorrido = time.time() - tempo_inicio
                    if processed > 0:  # Evitar divisão por zero
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
                    text_output.see(tk.END)  # Rolagem automática
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

# Botões de ação
tk.Button(root, text="Processar", command=processar, bg="green", fg="white").grid(row=3, column=1, pady=5)
tk.Button(root, text="Cancelar", command=cancelar_processo, bg="red", fg="white").grid(row=3, column=2, pady=5)

# Barra de progresso
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=4, column=0, columnspan=3, padx=5, pady=5)
label_progress = tk.Label(root, text="Progresso: 0/0 (0%)")
label_progress.grid(row=5, column=0, columnspan=3)

# Área de texto para saída
text_output = tk.Text(root, height=15, width=70)
text_output.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

# Iniciar a interface
root.mainloop()