import tkinter as tk
from tkinter import ttk, messagebox
from core.database import executar_consulta
from .planilha import criar_aba_planilha
from .mysql import criar_aba_mysql
from .usuarios import criar_aba_usuarios

# Estilo visual OndaCom
from ui_ondacom import aplicar_estilo_ondacom, carregar_logo

def iniciar_interface():
    root = tk.Tk()
    root.title("Sistema Fibrasil TTK")
    root.geometry("1200x700")
    aplicar_estilo_ondacom()

    # Fundo branco
    root.configure(bg="white")

    # Logomarca no topo
    carregar_logo(root)

    login_frame = tk.Frame(root, bg="white")
    login_frame.pack(pady=40)

    tk.Label(login_frame, text="Usuário:", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5, pady=5)
    usuario_entry = tk.Entry(login_frame, font=("Segoe UI", 10))
    usuario_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(login_frame, text="Senha:", bg="white", font=("Segoe UI", 10)).grid(row=1, column=0, padx=5, pady=5)
    senha_entry = tk.Entry(login_frame, show="*", font=("Segoe UI", 10))
    senha_entry.grid(row=1, column=1, padx=5, pady=5)

    notebook = ttk.Notebook(root)

    def tentar_login():
        usuario = usuario_entry.get()
        senha = senha_entry.get()

        if not usuario or not senha:
            messagebox.showwarning("Atenção", "Preencha usuário e senha.")
            return

        query = "SELECT * FROM usuarios WHERE usuario = %s"
        resultados = executar_consulta(query, (usuario,), fetch=True, dictionary=True)

        if not resultados:
            messagebox.showerror("Erro", "Usuário não encontrado.")
            return

        dados = resultados[0]
        senha_armazenada = dados["senha"]

        import bcrypt
        senha_ok = False
        try:
            senha_ok = bcrypt.checkpw(senha.encode(), senha_armazenada.encode())
        except Exception:
            senha_ok = (senha == senha_armazenada)

        if senha_ok:
            login_frame.pack_forget()
            notebook.pack(fill="both", expand=True)
            messagebox.showinfo("Login", f"Bem-vindo, {dados['usuario']}")
            criar_aba_planilha(notebook)
            criar_aba_mysql(notebook)
            if dados["nivel_acesso"] == "supervisor":
                criar_aba_usuarios(notebook)
        else:
            messagebox.showerror("Erro", "Senha incorreta.")

    tk.Button(login_frame, text="Login", command=tentar_login, font=("Segoe UI", 10, "bold")).grid(row=2, columnspan=2, pady=10)

    root.mainloop()
