import face_recognition 
import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time
from PIL import Image, ImageEnhance

class SeparadorFotos:
    def __init__(self, root):
        self.root = root
        self.root.title("Separador de Fotos por Reconhecimento Facial")
        self.root.geometry("720x650")
        self.root.configure(bg="#f5f6f5")
        #self.root.resizable(False, False)

        self.pasta_fotos = tk.StringVar()
        self.pasta_identificacao = tk.StringVar()
        self.pasta_saida = tk.StringVar()
        self.cancelar = False

        # Estilo ttk
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 11), padding=10)
        style.configure("TLabel", background="#f5f6f5", font=("Helvetica", 11))
        # Ajuste do padding vertical para igualar a altura das labels
        style.configure("Accent.TButton", background="#ADD8E6", foreground="black", font=("Helvetica", 11), padding=(10, 2))
        style.configure("Transparent.TFrame", background="#f5f6f5")
        style.configure("TProgressbar", thickness=20)

        # Frame principal
        frame_principal = ttk.Frame(self.root, padding="20", style="Transparent.TFrame")
        frame_principal.grid(row=0, column=0, sticky="nsew")

        # Título e subtítulo
        ttk.Label(frame_principal, text="Separador de Fotos", font=("Helvetica", 20, "bold"), foreground="#0288D1").grid(row=0, column=0, columnspan=3, pady=(0, 2))
        ttk.Label(frame_principal, text="Version Alpha 1.0.1", font=("Helvetica", 10, "italic"), foreground="#666").grid(row=1, column=0, columnspan=3, pady=(0, 8))

        # Interface
        ttk.Label(frame_principal, text="Pasta com Todas as Fotos:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_principal, textvariable=self.pasta_fotos, width=50).grid(row=2, column=1, padx=5, pady=3)
        ttk.Button(frame_principal, text="Selecionar", command=self.selecionar_pasta_fotos, style="Accent.TButton").grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(frame_principal, text="Pasta de Identificação dos Alunos:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_principal, textvariable=self.pasta_identificacao, width=50).grid(row=3, column=1, padx=5, pady=3)
        ttk.Button(frame_principal, text="Selecionar", command=self.selecionar_pasta_identificacao, style="Accent.TButton").grid(row=3, column=2, padx=5, pady=5)

        ttk.Label(frame_principal, text="Pasta de Saída:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_principal, textvariable=self.pasta_saida, width=50).grid(row=4, column=1, padx=5, pady=3)
        ttk.Button(frame_principal, text="Selecionar", command=self.selecionar_pasta_saida, style="Accent.TButton").grid(row=4, column=2, padx=5, pady=5)

        self.log_texto = tk.Text(frame_principal, height=15, width=97, font=("Helvetica", 10))
        self.log_texto.grid(row=5, column=0, columnspan=3, padx=5, pady=10)

        self.progresso = ttk.Progressbar(frame_principal, length=650, mode='determinate')
        self.progresso.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

        self.label_progresso = ttk.Label(frame_principal, text="Progresso: 0% | Tempo estimado: --")
        self.label_progresso.grid(row=7, column=0, columnspan=3, pady=8)

        # Frame para centralizar os botões
        frame_botoes = ttk.Frame(frame_principal, style="Transparent.TFrame")
        frame_botoes.grid(row=8, column=0, columnspan=3, pady=10)

        self.botao_iniciar = ttk.Button(frame_botoes, text="Iniciar Processamento", command=self.processar_fotos, style="Accent.TButton", width=25)
        self.botao_iniciar.grid(row=0, column=0, padx=5, pady=8)

        self.botao_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=self.cancelar_processamento, style="Accent.TButton", width=25, state=tk.DISABLED)
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
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)

    def selecionar_pasta_fotos(self):
        """Seleciona a pasta contendo todas as fotos."""
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_fotos.set(pasta)

    def selecionar_pasta_identificacao(self):
        """Seleciona a pasta com fotos de identificação dos alunos."""
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_identificacao.set(pasta)

    def selecionar_pasta_saida(self):
        """Seleciona a pasta de saída para as fotos separadas."""
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_saida.set(pasta)

    def log(self, mensagem):
        self.log_texto.insert(tk.END, mensagem + "\n")
        self.log_texto.see(tk.END)
        self.root.update()

    def cancelar_processamento(self):
        """Cancela o processamento em andamento."""
        self.cancelar = True
        self.log("Cancelamento solicitado...")

    def preprocessar_imagem(self, caminho):
        """Pré-processa a imagem para melhorar contraste e brilho."""
        try:
            imagem = Image.open(caminho).convert('RGB')
            enhancer = ImageEnhance.Contrast(imagem)
            imagem = enhancer.enhance(1.5)
            enhancer = ImageEnhance.Brightness(imagem)
            imagem = enhancer.enhance(1.2)
            caminho_temp = caminho + "_temp.jpg"
            imagem.save(caminho_temp)
            imagem_processada = face_recognition.load_image_file(caminho_temp)
            os.remove(caminho_temp)
            return imagem_processada
        except Exception as e:
            self.log(f"Erro ao pré-processar {caminho}: {str(e)}")
            return face_recognition.load_image_file(caminho)

    def processar_fotos(self):
        """Processa as fotos e separa por reconhecimento facial."""
        pasta_fotos = self.pasta_fotos.get()
        pasta_identificacao = self.pasta_identificacao.get()
        pasta_saida = self.pasta_saida.get()

        if not (pasta_fotos and pasta_identificacao and pasta_saida):
            messagebox.showerror("Erro", "Por favor, selecione todas as pastas!")
            return

        self.cancelar = False
        self.botao_iniciar.config(state=tk.DISABLED)
        self.botao_cancelar.config(state=tk.NORMAL)
        Path(pasta_saida).mkdir(parents=True, exist_ok=True)
        
        pasta_nao_identificadas = os.path.join(pasta_saida, "Fotos Não Identificadas")
        Path(pasta_nao_identificadas).mkdir(parents=True, exist_ok=True)
        
        self.log("Iniciando processamento (primeira análise)...")

        identificacoes = {}
        for arquivo in os.listdir(pasta_identificacao):
            if self.cancelar:
                break
            caminho = os.path.join(pasta_identificacao, arquivo)
            if not os.path.isfile(caminho) or not arquivo.lower().endswith(('.jpg', '.jpeg', '.png')):
                self.log(f"Ignorando {arquivo} (não é uma imagem)")
                continue
            try:
                Image.open(caminho).verify()
                imagem = self.preprocessar_imagem(caminho)
                codificacoes = face_recognition.face_encodings(imagem)
                if not codificacoes:
                    self.log(f"Nenhum rosto encontrado em {arquivo}")
                    continue
                codificacao = codificacoes[0]
                nome_aluno = os.path.splitext(arquivo)[0]
                identificacoes[nome_aluno] = codificacao
                self.log(f"Carregada identificação de {nome_aluno}")
            except Exception as e:
                self.log(f"Erro ao carregar {arquivo}: {str(e)}")

        fotos = []
        for raiz, _, arquivos in os.walk(pasta_fotos):
            for arquivo in arquivos:
                if arquivo.lower().endswith(('.jpg', '.jpeg', '.png')):
                    fotos.append(os.path.join(raiz, arquivo))
        total_fotos = len(fotos)
        fotos_processadas = 0
        tempo_inicio = time.time()

        for foto in fotos:
            if self.cancelar:
                break
            caminho_foto = foto
            try:
                Image.open(caminho_foto).verify()
                imagem_desconhecida = self.preprocessar_imagem(caminho_foto)
                codificacoes_desconhecidas = face_recognition.face_encodings(imagem_desconhecida)

                if len(codificacoes_desconhecidas) == 0:
                    self.log(f"Nenhum rosto encontrado em {foto}")
                    destino = os.path.join(pasta_nao_identificadas, os.path.basename(foto))
                    shutil.copy(caminho_foto, destino)
                    self.log(f"Foto {foto} movida para 'Fotos Não Identificadas' (sem rosto detectado)")
                else:
                    identificados = False
                    for i, codificacao_desconhecida in enumerate(codificacoes_desconhecidas):
                        distancias = face_recognition.face_distance(list(identificacoes.values()), codificacao_desconhecida)
                        tolerancia = 0.50
                        menor_distancia = min(distancias) if distancias.size > 0 else float('inf')

                        if menor_distancia <= tolerancia:
                            identificados = True
                            indice_melhor = distancias.argmin()
                            nome_aluno = list(identificacoes.keys())[indice_melhor]
                            pasta_aluno = os.path.join(pasta_saida, nome_aluno)
                            Path(pasta_aluno).mkdir(parents=True, exist_ok=True)
                            destino = os.path.join(pasta_aluno, os.path.basename(foto))
                            shutil.copy(caminho_foto, destino)
                            self.log(f"Rosto {i+1} em {foto} identificado como {nome_aluno} (distância: {menor_distancia:.2f})")
                        else:
                            self.log(f"Rosto {i+1} em {foto} não identificado (menor distância: {menor_distancia:.2f} > tolerância {tolerancia})")

                    if not identificados:
                        destino = os.path.join(pasta_nao_identificadas, os.path.basename(foto))
                        shutil.copy(caminho_foto, destino)
                        self.log(f"Foto {foto} movida para 'Fotos Não Identificadas' (nenhum rosto identificado)")

                fotos_processadas += 1
                percentual = (fotos_processadas / total_fotos) * 100
                self.progresso['value'] = percentual

                tempo_decorrido = time.time() - tempo_inicio
                if fotos_processadas > 0:
                    tempo_medio_por_foto = tempo_decorrido / fotos_processadas
                    fotos_restantes = total_fotos - fotos_processadas
                    tempo_estimado = tempo_medio_por_foto * fotos_restantes
                    minutos = int(tempo_estimado // 60)
                    segundos = int(tempo_estimado % 60)
                    tempo_str = f"{minutos}m {segundos}s"
                else:
                    tempo_str = "--"
                self.label_progresso.config(text=f"Progresso: {percentual:.1f}% | Tempo estimado: {tempo_str}")

            except Exception as e:
                self.log(f"Imagem corrompida ou erro ao processar {foto}: {str(e)}")
                destino = os.path.join(pasta_nao_identificadas, os.path.basename(foto))
                shutil.copy(caminho_foto, destino)
                self.log(f"Foto {foto} movida para 'Fotos Não Identificadas' devido a erro")

        if not self.cancelar:
            self.log("\nIniciando segunda análise nas fotos não identificadas (tolerância mais flexível)...")
            fotos_nao_identificadas = [f for f in os.listdir(pasta_nao_identificadas) if os.path.isfile(os.path.join(pasta_nao_identificadas, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            total_fotos_segunda = len(fotos_nao_identificadas)
            fotos_processadas_segunda = 0
            tempo_inicio_segunda = time.time()

            for foto in fotos_nao_identificadas:
                if self.cancelar:
                    break
                caminho_foto = os.path.join(pasta_nao_identificadas, foto)
                try:
                    Image.open(caminho_foto).verify()
                    imagem_desconhecida = self.preprocessar_imagem(caminho_foto)
                    codificacoes_desconhecidas = face_recognition.face_encodings(imagem_desconhecida)

                    if len(codificacoes_desconhecidas) == 0:
                        self.log(f"Segunda análise: Nenhum rosto encontrado em {foto} (permanece não identificado)")
                    else:
                        identificados = False
                        for i, codificacao_desconhecida in enumerate(codificacoes_desconhecidas):
                            distancias = face_recognition.face_distance(list(identificacoes.values()), codificacao_desconhecida)
                            tolerancia_segunda = 0.5
                            menor_distancia = min(distancias) if distancias.size > 0 else float('inf')

                            if menor_distancia <= tolerancia_segunda:
                                identificados = True
                                indice_melhor = distancias.argmin()
                                nome_aluno = list(identificacoes.keys())[indice_melhor]
                                pasta_aluno = os.path.join(pasta_saida, nome_aluno)
                                Path(pasta_aluno).mkdir(parents=True, exist_ok=True)
                                destino = os.path.join(pasta_aluno, foto)
                                shutil.move(caminho_foto, destino)
                                self.log(f"Segunda análise: Rosto {i+1} em {foto} identificado como {nome_aluno} (distância: {menor_distancia:.2f})")
                                break
                            else:
                                self.log(f"Segunda análise: Rosto {i+1} em {foto} não identificado (menor distância: {menor_distancia:.2f} > tolerância {tolerancia_segunda})")

                        if not identificados:
                            self.log(f"Segunda análise: Foto {foto} ainda não identificada (nenhum rosto reconhecido)")

                    fotos_processadas_segunda += 1
                    percentual = (fotos_processadas_segunda / total_fotos_segunda) * 100 if total_fotos_segunda > 0 else 100
                    self.progresso['value'] = percentual

                    tempo_decorrido_segunda = time.time() - tempo_inicio_segunda
                    if fotos_processadas_segunda > 0 and total_fotos_segunda > 0:
                        tempo_medio_por_foto = tempo_decorrido_segunda / fotos_processadas_segunda
                        fotos_restantes = total_fotos_segunda - fotos_processadas_segunda
                        tempo_estimado = tempo_medio_por_foto * fotos_restantes
                        minutos = int(tempo_estimado // 60)
                        segundos = int(tempo_estimado % 60)
                        tempo_str = f"{minutos}m {segundos}s"
                    else:
                        tempo_str = "--"
                    self.label_progresso.config(text=f"Progresso (2ª análise): {percentual:.1f}% | Tempo estimado: {tempo_str}")

                except Exception as e:
                    self.log(f"Imagem corrompida ou erro na segunda análise de {foto}: {str(e)}")

        if self.cancelar:
            self.log("Processamento cancelado pelo usuário.")
            messagebox.showinfo("Cancelado", "O processamento foi interrompido.")
        else:
            self.log("Processamento concluído (incluindo segunda análise)!")
            messagebox.showinfo("Concluído", "O processamento das fotos foi finalizado.")

        self.botao_iniciar.config(state=tk.NORMAL)
        self.botao_cancelar.config(state=tk.DISABLED)
        self.progresso['value'] = 0
        self.label_progresso.config(text="Progresso: 0% | Tempo estimado: --")

def janela_separador_fotos():
    """Abre a janela para separar fotos por reconhecimento facial."""
    try:
        root = tk.Toplevel()
        app = SeparadorFotos(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao abrir separador de fotos: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SeparadorFotos(root)
    root.mainloop()