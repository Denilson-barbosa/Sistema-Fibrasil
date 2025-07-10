import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from core.database import inserir_dados
from core.util import formatar_datas_para_exibicao, converter_datas_para_salvar
from ui_ondacom import aplicar_estilo_ondacom, carregar_logo, aplicar_listras_treeview


colunas = ["OCORRENCIA", "UF", "MUNICIPIO", "DATA_INICIO", "PREVISAO", "SLA", "SLA_RESTANTE", "AFETACAO", "TAG", "ARMARIO",
           "SPLITTER", "CTO_GP", "DATA_ULTIMA_OBS", "PRAZO", "DATA_ATRIBUICAO", "EQUIPE_EXECUTANTE", "STATUS", "OBS",
           "TECNICO_ANTERIOR", "UNIC_TOKEN", "DATA_ENCERRAMENTO", "REFERENCIA_CLIENTE", "TIPO_FALHA", "MOTIVO_ABERTURA"]

CAMINHO_FIXO = r"C:\Users\denilson.barbosa\OneDrive - ONDACOM\Área de Trabalho\PYTHON\Fibrasil TTK.xlsx"

def aplicar_mascara_data_hora(entry_widget):
    def formatar(event):
        # Captura apenas os dígitos
        texto = ''.join(c for c in entry_widget.get() if c.isdigit())
        nova = ""

        if len(texto) > 0:
            nova += texto[:2]
        if len(texto) > 2:
            nova += "/" + texto[2:4]
        if len(texto) > 4:
            nova += "/" + texto[4:8]
        if len(texto) > 8:
            nova += " " + texto[8:10]
        if len(texto) > 10:
            nova += ":" + texto[10:12]
        if len(texto) > 12:
            nova += ":" + texto[12:14]

        # Evita loop do evento: só atualiza se diferente
        if entry_widget.get() != nova:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, nova)

        # Validação final
        if len(nova) == 19:
            try:
                datetime.strptime(nova, "%d/%m/%Y %H:%M:%S")
                entry_widget.config(fg="black")
            except ValueError:
                entry_widget.config(fg="red")
        else:
            entry_widget.config(fg="black")

    entry_widget.bind("<KeyRelease>", formatar)


def criar_aba_planilha(notebook):
    aba = tk.Frame(notebook)
    notebook.add(aba, text="Importar Planilha")

    frame_tree = tk.Frame(aba)
    frame_tree.pack(fill="both", expand=True)

    scroll_y = ttk.Scrollbar(frame_tree, orient="vertical")
    scroll_y.pack(side="right", fill="y")

    scroll_x = ttk.Scrollbar(frame_tree, orient="horizontal")
    scroll_x.pack(side="bottom", fill="x")

    tree = ttk.Treeview(frame_tree, show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    tree["columns"] = colunas
    tree.pack(side="left", fill="both", expand=True)

    scroll_y.config(command=tree.yview)
    scroll_x.config(command=tree.xview)

    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=200, minwidth=150, stretch=True)

    def editar_celula(event):
        item = tree.identify_row(event.y)
        coluna = tree.identify_column(event.x)
        if not item or not coluna:
            return

        col_index = int(coluna.replace("#", "")) - 1
        col_nome = colunas[col_index]

        colunas_nao_editaveis = ["OCORRENCIA", "UF", "DATA_INICIO", "PREVISAO", "SLA", "SLA_RESTANTE"]

        if col_nome in colunas_nao_editaveis:
            return  # impede edição manual

        # Preencher automaticamente a coluna DATA_ENCERRAMENTO com data e hora atual
        if col_nome == "DATA_ENCERRAMENTO":
            data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            valores = list(tree.item(item)["values"])
            valores[col_index] = data_hora_atual
            tree.item(item, values=valores)
            return

        # Para outras colunas, abrir Entry para edição manual
        x, y, w, h = tree.bbox(item, column=coluna)
        valor_antigo = tree.item(item)["values"][col_index]

        entry = tk.Entry(tree)
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, valor_antigo)
        entry.focus()

        # Aplicar máscara se for DATA_ATRIBUICAO
        if col_nome == "DATA_ATRIBUICAO":
            aplicar_mascara_data_hora(entry)

        def salvar(event):
            novo_valor = entry.get()
            entry.destroy()

            valores = list(tree.item(item)["values"])
            valores[col_index] = novo_valor
            tree.item(item, values=valores)

        entry.bind("<Return>", salvar)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    tree.bind("<Double-1>", editar_celula)

    tk.Button(aba, text="Atualizar Planilha", command=lambda: importar_planilha(tree, CAMINHO_FIXO)).pack(pady=5)
    tk.Button(aba, text="Salvar Linha", command=lambda: salvar_linha(tree)).pack(pady=5)

    agendar_atualizacao(tree)
    return tree

def importar_planilha(tree, file_path):
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df.columns = colunas
        referencias = set(tree.item(i)["values"][0] for i in tree.get_children())
        novos = df[~df["OCORRENCIA"].isin(referencias)]
        for _, row in novos.iterrows():
            valores = [formatar_datas_para_exibicao(row.get(col, "")) for col in colunas]
            tree.insert("", "end", values=valores)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao importar planilha:\n{e}")

def salvar_linha(tree):
    item = tree.selection()
    if not item:
        messagebox.showwarning("Aviso", "Selecione uma linha para salvar.")
        return

    valores = list(tree.item(item[0])["values"])

    # Verificar campos obrigatórios
    colunas_obrigatorias = [
        "MUNICIPIO", "TAG", "ARMARIO", "SPLITTER", "CTO_GP",
        "DATA_ATRIBUICAO", "EQUIPE_EXECUTANTE", "STATUS",
        "TECNICO_ANTERIOR", "UNIC_TOKEN", "DATA_ENCERRAMENTO", "MOTIVO_ABERTURA"
    ]
    
    for nome_coluna in colunas_obrigatorias:
        idx = colunas.index(nome_coluna)
        if not str(valores[idx]).strip():
            messagebox.showerror("Erro", f'O campo obrigatório "{nome_coluna}" está vazio.')
            return

    # Converter datas antes de salvar
    for i, col in enumerate(colunas):
        valores[i] = converter_datas_para_salvar(col, valores[i])

    try:
        inserir_dados(colunas, valores)
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def agendar_atualizacao(tree):
    importar_planilha(tree, CAMINHO_FIXO)
    tree.after(900000, lambda: agendar_atualizacao(tree))  # 15 min
