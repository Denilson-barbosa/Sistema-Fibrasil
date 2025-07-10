import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import pandas as pd
from core.database import executar_consulta
from datetime import datetime

# Estilo visual OndaCom
from ui_ondacom import aplicar_estilo_ondacom, carregar_logo, aplicar_listras_treeview

def criar_aba_mysql(notebook):
    aba = tk.Frame(notebook, bg="white")
    notebook.add(aba, text="MySQL")

    aplicar_estilo_ondacom()
    carregar_logo(aba)

    # Frame com barras de rolagem
    frame_tree = tk.Frame(aba, bg="white")
    frame_tree.pack(fill="both", expand=True)

    scroll_y = ttk.Scrollbar(frame_tree, orient="vertical")
    scroll_y.pack(side="right", fill="y")

    scroll_x = ttk.Scrollbar(frame_tree, orient="horizontal")
    scroll_x.pack(side="bottom", fill="x")

    tree = ttk.Treeview(frame_tree, show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    tree.pack(side="left", fill="both", expand=True)

    scroll_y.config(command=tree.yview)
    scroll_x.config(command=tree.xview)

    def carregar_dados():
        query = "SELECT * FROM Fibrasil_TTK LIMIT 100"
        dados = executar_consulta(query, fetch=True, dictionary=True)
        if not dados:
            return
        colunas = list(dados[0].keys())
        tree["columns"] = colunas
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        for row in tree.get_children():
            tree.delete(row)
        for linha in dados:
            valores = [linha[c] for c in colunas]
            tree.insert("", "end", values=valores)

        aplicar_listras_treeview(tree)

    # Edição com dois cliques
    def editar_celula(event):
        item = tree.identify_row(event.y)
        coluna = tree.identify_column(event.x)
        if not item or not coluna:
            return
        col_index = int(coluna.replace("#", "")) - 1
        col_nome = tree["columns"][col_index]

        x, y, w, h = tree.bbox(item, column=coluna)
        valor_antigo = tree.item(item)["values"][col_index]

        entry = tk.Entry(tree)
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, valor_antigo)
        entry.focus()

        def salvar(event):
            novo_valor = entry.get()
            entry.destroy()

            # Conversão se for data
            if "DATA" in col_nome:
                try:
                    novo_valor = datetime.strptime(novo_valor, "%d/%m/%Y %H:%M:%S")
                except ValueError:
                    messagebox.showerror("Erro", f"Formato inválido para campo {col_nome}. Use dd/mm/yyyy HH:MM:SS.")
                    return

            # Atualizar visual
            valores = list(tree.item(item)["values"])
            valores[col_index] = novo_valor
            tree.item(item, values=valores)

            ocorrencia = valores[0]
            query = f"UPDATE Fibrasil_TTK SET {col_nome} = %s WHERE OCORRENCIA = %s"
            executar_consulta(query, (novo_valor, ocorrencia))

        entry.bind("<Return>", salvar)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    tree.bind("<Double-1>", editar_celula)

    # Exportação
    frame_export = tk.LabelFrame(aba, text="Exportar por intervalo de Data Início", bg="white")
    frame_export.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_export, text="Data Início (dd/mm/yyyy):", bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_data_inicio = tk.Entry(frame_export)
    entry_data_inicio.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_export, text="Data Fim (dd/mm/yyyy):", bg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_data_fim = tk.Entry(frame_export)
    entry_data_fim.grid(row=1, column=1, padx=5, pady=5)

    def buscar_dados():
        inicio = entry_data_inicio.get().strip()
        fim = entry_data_fim.get().strip()
        try:
            data_inicio_sql = datetime.strptime(inicio, "%d/%m/%Y").strftime("%Y-%m-%d")
            data_fim_sql = datetime.strptime(fim, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use dd/mm/yyyy.")
            return None
        query = "SELECT * FROM Fibrasil_TTK WHERE DATA_INICIO BETWEEN %s AND %s"
        dados = executar_consulta(query, (data_inicio_sql, data_fim_sql), fetch=True, dictionary=True)
        if not dados:
            messagebox.showinfo("Aviso", "Nenhum dado encontrado no intervalo informado.")
        return pd.DataFrame(dados)

    def exportar_para_excel():
        df = buscar_dados()
        if df is not None and not df.empty:
            caminho = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
            if caminho:
                df.to_excel(caminho, index=False)
                messagebox.showinfo("Exportado", f"Arquivo salvo em:\n{caminho}")

    def exportar_para_csv():
        df = buscar_dados()
        if df is not None and not df.empty:
            caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
            if caminho:
                df.to_csv(caminho, index=False, sep=";")
                messagebox.showinfo("Exportado", f"Arquivo salvo em:\n{caminho}")

    tk.Button(frame_tree, text="Recarregar Tabela", command=carregar_dados).pack(pady=5)
    tk.Button(frame_export, text="Exportar para Excel", command=exportar_para_excel).grid(row=2, column=0, columnspan=2, pady=5)
    tk.Button(frame_export, text="Exportar para CSV", command=exportar_para_csv).grid(row=3, column=0, columnspan=2, pady=5)

    carregar_dados()
