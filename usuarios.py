import tkinter as tk
from tkinter import messagebox, ttk
import bcrypt
from core.database import executar_consulta
from ui_ondacom import aplicar_estilo_ondacom, carregar_logo, aplicar_listras_treeview


def criar_aba_usuarios(notebook):
    aba = tk.Frame(notebook)
    notebook.add(aba, text="Usuários")

    tk.Label(aba, text="Cadastro de novo usuário").grid(row=0, column=0, columnspan=2, pady=10)

    tk.Label(aba, text="Usuário:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    entry_usuario = tk.Entry(aba)
    entry_usuario.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(aba, text="Senha:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    entry_senha = tk.Entry(aba, show="*")
    entry_senha.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(aba, text="Nível de acesso:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    combo_nivel = ttk.Combobox(aba, values=["supervisor", "operador"], state="readonly")
    combo_nivel.grid(row=3, column=1, padx=5, pady=5)
    combo_nivel.set("operador")

    def cadastrar_usuario():
        usuario = entry_usuario.get().strip()
        senha = entry_senha.get().strip()
        nivel = combo_nivel.get().strip()

        if not usuario or not senha or not nivel:
            messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos.")
            return

        hash_senha = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

        try:
            executar_consulta(
                "INSERT INTO usuarios (usuario, senha, nivel_acesso) VALUES (%s, %s, %s)",
                (usuario, hash_senha, nivel)
            )
            messagebox.showinfo("Sucesso", f"Usuário '{usuario}' cadastrado com sucesso!")
            entry_usuario.delete(0, tk.END)
            entry_senha.delete(0, tk.END)
            combo_nivel.set("operador")
            carregar_usuarios()
        except Exception as e:
            messagebox.showerror("Erro ao cadastrar", str(e))

    tk.Button(aba, text="Cadastrar Usuário", command=cadastrar_usuario).grid(row=4, column=0, columnspan=2, pady=15)

    # Listagem de usuários
    frame_lista = tk.Frame(aba)
    frame_lista.grid(row=5, column=0, columnspan=2, pady=10)

    tree = ttk.Treeview(frame_lista, columns=("id", "usuario", "nivel"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("usuario", text="Usuário")
    tree.heading("nivel", text="Nível de Acesso")
    tree.column("id", width=50)
    tree.column("usuario", width=150)
    tree.column("nivel", width=100)
    tree.pack()

    def carregar_usuarios():
        for row in tree.get_children():
            tree.delete(row)
        dados = executar_consulta("SELECT id, usuario, nivel_acesso FROM usuarios", fetch=True, dictionary=True)
        for row in dados:
            tree.insert("", "end", values=(row["id"], row["usuario"], row["nivel_acesso"]))

    def excluir_usuario():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Seleção", "Selecione um usuário para excluir.")
            return
        item = tree.item(selecionado[0])
        usuario_id = item["values"][0]
        usuario_nome = item["values"][1]

        confirm = messagebox.askyesno("Confirmar", f"Deseja excluir o usuário '{usuario_nome}'?")
        if confirm:
            try:
                executar_consulta("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
                tree.delete(selecionado[0])
                messagebox.showinfo("Excluído", f"Usuário '{usuario_nome}' foi removido.")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    tk.Button(aba, text="Excluir Usuário Selecionado", command=excluir_usuario).grid(row=6, column=0, columnspan=2)

    carregar_usuarios()
