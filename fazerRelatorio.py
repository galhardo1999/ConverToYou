import face_recognition
import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time
from PIL import Image, ImageEnhance
from datetime import datetime
import pandas as pd

class GeradorRelatorioComparativo:
    def __init__(self, root, pasta_fotos_geral=None, pasta_saida=None):
        self.root = root
        self.root.title("Relatório de Fotos por Aluno")
        self.root.geometry("690x650")
        self.root.configure(bg="#f5f6f5")

        self.pasta_fotos_geral = tk.StringVar(value=pasta_fotos_geral or "")
        self.pasta_saida = tk.StringVar(value=pasta_saida or "")

        # Estilo ttk
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 11), padding=10)
        style.configure("TLabel", background="#f5f6f5", font=("Helvetica", 11))
        style.configure("Accent.TButton", background="#ADD8E6", foreground="black", font=("Helvetica", 11), padding=(10, 2))

        # Frame principal
        frame_principal = ttk.Frame(self.root, padding="20")
        frame_principal.grid(row=0, column=0, sticky="nsew")

        # Título
        ttk.Label(frame_principal, text="Relatório de Fotos por Aluno", font=("Helvetica", 16, "bold"), foreground="#0288D1").grid(row=0, column=0, columnspan=3, pady=10)

        # Seleção da pasta geral
        ttk.Label(frame_principal, text="Pasta com Todas as Fotos:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_principal, textvariable=self.pasta_fotos_geral, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame_principal, text="Selecionar", command=self.selecionar_pasta_geral, style="Accent.TButton").grid(row=1, column=2, padx=5, pady=5)

        # Seleção da pasta de saída
        ttk.Label(frame_principal, text="Pasta de Saída:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_principal, textvariable=self.pasta_saida, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame_principal, text="Selecionar", command=self.selecionar_pasta_saida, style="Accent.TButton").grid(row=2, column=2, padx=5, pady=5)

        # Frame para o texto com barra de rolagem
        texto_frame = ttk.Frame(frame_principal)
        texto_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=10, sticky="nsew")

        # Área de texto para o relatório com barra de rolagem
        self.relatorio_texto = tk.Text(texto_frame, height=25, width=80, font=("Helvetica", 10))
        self.relatorio_texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Adicionar barra de rolagem vertical
        scrollbar = ttk.Scrollbar(texto_frame, orient="vertical", command=self.relatorio_texto.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.relatorio_texto.configure(yscrollcommand=scrollbar.set)

        # Botões
        ttk.Button(frame_principal, text="Gerar e Salvar Relatório em Excel", command=self.gerar_e_salvar_relatorio_excel, style="Accent.TButton").grid(row=4, column=0, columnspan=3, pady=10)

        # Centralizar janela
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def selecionar_pasta_geral(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_fotos_geral.set(pasta)

    def selecionar_pasta_saida(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_saida.set(pasta)

    def listar_subpastas_geral(self, pasta):
        subpastas = {}
        for item in os.listdir(pasta):
            caminho = os.path.join(pasta, item)
            if os.path.isdir(caminho):
                fotos = [f for f in os.listdir(caminho) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                subpastas[item] = fotos
        return subpastas

    def contar_fotos_por_aluno(self, pasta, subpastas_geral):
        contagem_alunos = {}
        
        for aluno in os.listdir(pasta):
            caminho = os.path.join(pasta, aluno)
            if os.path.isdir(caminho):
                fotos_aluno = [f for f in os.listdir(caminho) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                contagem_alunos[aluno] = {
                    "total": len(fotos_aluno),
                    "origem": {subpasta: 0 for subpasta in subpastas_geral.keys()}
                }
                
                for foto_aluno in fotos_aluno:
                    for subpasta, fotos_subpasta in subpastas_geral.items():
                        if foto_aluno in fotos_subpasta:
                            contagem_alunos[aluno]["origem"][subpasta] += 1
                            break
        
        return contagem_alunos

    def gerar_e_salvar_relatorio_excel(self):
        pasta_geral = self.pasta_fotos_geral.get()
        pasta_saida = self.pasta_saida.get()

        if not (pasta_geral and pasta_saida):
            messagebox.showerror("Erro", "Por favor, selecione ambas as pastas!")
            return

        if not (os.path.exists(pasta_geral) and os.path.exists(pasta_saida)):
            messagebox.showerror("Erro", "Uma das pastas selecionadas não existe!")
            return

        self.relatorio_texto.delete(1.0, tk.END)

        subpastas_geral = self.listar_subpastas_geral(pasta_geral)
        contagem_alunos = self.contar_fotos_por_aluno(pasta_saida, subpastas_geral)

        dados_excel = []
        for aluno, info in contagem_alunos.items():
            linha = {"Nome do Aluno": aluno, "Quantidade Total de Fotos": info["total"]}
            for subpasta, qtd in info["origem"].items():
                linha[f"{subpasta}"] = f"{qtd} foto(s)"
            dados_excel.append(linha)

        df = pd.DataFrame(dados_excel)

        relatorio_texto = ""
        for _, row in df.iterrows():
            relatorio_texto += f"Nome do Aluno: {row['Nome do Aluno']}\n"
            relatorio_texto += f"Quantidade Total de Fotos: {row['Quantidade Total de Fotos']}\n"
            for col in df.columns[2:]:
                relatorio_texto += f"{col}: {row[col]}\n"
            relatorio_texto += "\n"
        self.relatorio_texto.insert(tk.END, relatorio_texto)

        arquivo_excel = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Arquivos Excel", "*.xlsx")],
            title="Salvar Relatório em Excel",
            initialfile=f"relatorio_fotos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        if arquivo_excel:
            df.to_excel(arquivo_excel, index=False, engine='openpyxl')
            messagebox.showinfo("Sucesso", f"Relatório salvo em Excel com sucesso em:\n{arquivo_excel}")