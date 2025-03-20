import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time

# Variável global para controlar o cancelamento
cancelar = False

class SeparadorRaw:
    def __init__(self, root):
        self.root = root
        self.root.title("Copiar Fotos RAW - Escola")
        self.root.geometry("740x650")
        self.root.configure(bg="#f5f6f5")

        self.pasta_raw = tk.StringVar()
        self.pasta_alunos = tk.StringVar()
        self.pasta_destino = tk.StringVar()
        self.cancelar = False

        # Estilo ttk
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 11), padding=10)
        style.configure("TLabel", background="#f5f6f5", font=("Helvetica", 11))
        style.configure("Accent.TButton", background="#ADD8E6", foreground="black", font=("Helvetica", 11), padding=(10, 2))
        style.configure("Transparent.TFrame", background="#f5f6f5")
        style.configure("TProgressbar", thickness=20)

        # Frame principal
        frame_principal = ttk.Frame(self.root, padding="20", style="Transparent.TFrame")
        frame_principal.grid(row=0, column=0, sticky="nsew")

        # Título e subtítulo
        ttk.Label(frame_principal, text="Copiar Fotos RAW", font=("Helvetica", 20, "bold"), foreground="#0288D1").grid(row=0, column=0, columnspan=3, pady=(0, 2))
        ttk.Label(frame_principal, text="Version Alpha 1.0", font=("Helvetica", 10, "italic"), foreground="#666").grid(row=1, column=0, columnspan=3, pady=(0, 8))

        # Interface
        ttk.Label(frame_principal, text="Pasta com arquivos:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_principal, textvariable=self.pasta_raw, width=50).grid(row=2, column=1, padx=5, pady=3)
        ttk.Button(frame_principal, text="Selecionar", command=lambda: self.selecionar_pasta(self.pasta_raw), style="Accent.TButton").grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(frame_principal, text="Pasta com fotos dos alunos (JPEG):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_principal, textvariable=self.pasta_alunos, width=50).grid(row=3, column=1, padx=5, pady=3)
        ttk.Button(frame_principal, text="Selecionar", command=lambda: self.selecionar_pasta(self.pasta_alunos), style="Accent.TButton").grid(row=3, column=2, padx=5, pady=5)

        ttk.Label(frame_principal, text="Pasta de destino para os RAW:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_principal, textvariable=self.pasta_destino, width=50).grid(row=4, column=1, padx=5, pady=3)
        ttk.Button(frame_principal, text="Selecionar", command=lambda: self.selecionar_pasta(self.pasta_destino), style="Accent.TButton").grid(row=4, column=2, padx=5, pady=5)

        # Frame para o texto com barra de rolagem
        texto_frame = ttk.Frame(frame_principal)
        texto_frame.grid(row=5, column=0, columnspan=3, padx=5, pady=10, sticky="nsew")

        # Área de texto para o log com barra de rolagem
        self.log_texto = tk.Text(texto_frame, height=15, width=97, font=("Helvetica", 10))
        self.log_texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Adicionar barra de rolagem vertical
        scrollbar = ttk.Scrollbar(texto_frame, orient="vertical", command=self.log_texto.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_texto.configure(yscrollcommand=scrollbar.set)

        self.progresso = ttk.Progressbar(frame_principal, length=650, mode='determinate')
        self.progresso.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

        self.label_progresso = ttk.Label(frame_principal, text="Progresso: 0% | Tempo estimado: --")
        self.label_progresso.grid(row=7, column=0, columnspan=3, pady=8)

        # Frame para centralizar os botões
        frame_botoes = ttk.Frame(frame_principal, style="Transparent.TFrame")
        frame_botoes.grid(row=8, column=0, columnspan=3, pady=10)

        self.botao_iniciar = ttk.Button(frame_botoes, text="Iniciar Processamento", command=self.processar, style="Accent.TButton", width=25)
        self.botao_iniciar.grid(row=0, column=0, padx=5, pady=8)

        self.botao_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=self.cancelar_processo, style="Accent.TButton", width=25, state=tk.DISABLED)
        self.botao_cancelar.grid(row=0, column=1, padx=5, pady=8)

        # Rodapé
        ttk.Label(frame_principal, text="© 2025 - Desenvolvido por Alexandre Galhardo", font=("Helvetica", 8), foreground="#999").grid(row=9, column=0, columnspan=3, pady=10)

        # Centralizar janela
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)  # Alterado para destroy

    def selecionar_pasta(self, var):
        """Seleciona uma pasta e atualiza a variável correspondente."""
        pasta = filedialog.askdirectory()
        if pasta:
            var.set(pasta)

    def log(self, mensagem):
        self.log_texto.insert(tk.END, mensagem + "\n")
        self.log_texto.see(tk.END)
        self.root.update()

    def cancelar_processo(self):
        """Cancela o processamento em andamento."""
        self.cancelar = True
        self.log("Cancelamento solicitado...")

    def contar_jpegs(self, pasta_alunos):
        total = 0
        for aluno in os.listdir(pasta_alunos):
            caminho_aluno = os.path.join(pasta_alunos, aluno)
            if os.path.isdir(caminho_aluno):
                total += len([f for f in os.listdir(caminho_aluno) if f.lower().endswith(('.jpeg', '.jpg'))])
        return total

    def formatar_tempo(self, segundos):
        if segundos < 60:
            return f"{int(segundos)}s"
        minutos = segundos // 60
        segundos_restantes = int(segundos % 60)
        return f"{minutos}m {segundos_restantes}s"

    def processar(self):
        """Processa os arquivos RAW e os copia para as pastas de destino."""
        pasta_raw = self.pasta_raw.get()
        pasta_alunos = self.pasta_alunos.get()
        pasta_destino = self.pasta_destino.get()

        if not (pasta_raw and pasta_alunos and pasta_destino):
            messagebox.showerror("Erro", "Por favor, selecione todas as pastas!")
            return

        self.cancelar = False
        self.botao_iniciar.config(state=tk.DISABLED)
        self.botao_cancelar.config(state=tk.NORMAL)

        # Criar a pasta de destino, se não existir
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)

        # Indexar arquivos RAW
        raw_files = {}
        self.log("Indexando arquivos RAW...")
        for root_dir, dirs, files in os.walk(pasta_raw):
            if self.cancelar:
                break
            for file in files:
                if file.lower().endswith(('.cr2', '.nef')):
                    nome_base = os.path.splitext(file)[0]
                    raw_files[nome_base] = os.path.join(root_dir, file)

        if self.cancelar:
            self.log("Processo cancelado durante indexação.")
            self.finalizar_processo()
            return

        self.log(f"Encontrados {len(raw_files)} arquivos RAW.\n")

        # Contar total de JPEGs para a barra de progresso
        total_jpegs = self.contar_jpegs(pasta_alunos)
        if total_jpegs == 0:
            messagebox.showerror("Erro", "Nenhum arquivo JPEG encontrado nas pastas dos alunos!")
            self.finalizar_processo()
            return

        self.progresso["maximum"] = total_jpegs
        self.progresso["value"] = 0
        processed = 0
        total_copiados = 0
        total_nao_encontrados = 0
        tempo_inicio = time.time()

        # Processar pastas dos alunos
        for aluno in os.listdir(pasta_alunos):
            if self.cancelar:
                break
            caminho_aluno = os.path.join(pasta_alunos, aluno)
            if os.path.isdir(caminho_aluno):
                destino_aluno = os.path.join(pasta_destino, aluno)
                if not os.path.exists(destino_aluno):
                    os.makedirs(destino_aluno)

                for foto in os.listdir(caminho_aluno):
                    if self.cancelar:
                        break
                    if foto.lower().endswith(('.jpeg', '.jpg')):
                        nome_base = os.path.splitext(foto)[0]
                        processed += 1
                        self.progresso["value"] = processed

                        # Calcular progresso e tempo restante
                        percentual = (processed / total_jpegs) * 100
                        tempo_decorrido = time.time() - tempo_inicio
                        if processed > 0:
                            tempo_por_arquivo = tempo_decorrido / processed
                            arquivos_restantes = total_jpegs - processed
                            tempo_restante = tempo_por_arquivo * arquivos_restantes
                            tempo_str = self.formatar_tempo(tempo_restante)
                        else:
                            tempo_str = "--"
                        self.label_progresso.config(text=f"Progresso: {percentual:.1f}% | Tempo estimado: {tempo_str}")

                        if nome_base in raw_files:
                            raw_path = raw_files[nome_base]
                            destino_raw = os.path.join(destino_aluno, os.path.basename(raw_path))
                            try:
                                shutil.copy2(raw_path, destino_raw)
                                self.log(f"Copiado: {os.path.basename(raw_path)} -> {destino_aluno}")
                                total_copiados += 1
                            except Exception as e:
                                self.log(f"Erro ao copiar {raw_path}: {e}")
                        else:
                            self.log(f"RAW não encontrado para: {foto}")
                            total_nao_encontrados += 1

        if self.cancelar:
            self.log("\nProcesso cancelado pelo usuário.")
        else:
            self.log(f"\nProcesso concluído!")
        self.log(f"Total de arquivos RAW copiados: {total_copiados}")
        self.log(f"Total de arquivos não encontrados: {total_nao_encontrados}")
        self.finalizar_processo()

    def finalizar_processo(self):
        """Finaliza o processamento, exibindo mensagem e restaurando botões."""
        if self.cancelar:
            messagebox.showinfo("Cancelado", "O processamento foi interrompido.")
        else:
            messagebox.showinfo("Concluído", "Processamento finalizado!")
        self.botao_iniciar.config(state=tk.NORMAL)
        self.botao_cancelar.config(state=tk.DISABLED)
        self.progresso["value"] = 0
        self.label_progresso.config(text="Progresso: 0% | Tempo estimado: --")

def janela_separador(master=None):
    """Abre a janela para copiar fotos RAW como uma janela secundária."""
    root = tk.Toplevel(master)  # Usar Toplevel em vez de Tk
    app = SeparadorRaw(root)
    return root

if __name__ == "__main__":
    root = tk.Tk()
    app = SeparadorRaw(root)
    root.mainloop()