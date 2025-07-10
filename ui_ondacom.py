
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def aplicar_estilo_ondacom():
    style = ttk.Style()
    style.configure("Treeview.Heading", background="#004080", foreground="white", font=("Segoe UI", 10, "bold"))
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=25, background="#FFFFFF", fieldbackground="#FFFFFF")
    style.map("Treeview", background=[("selected", "#CCE4F6")])

def carregar_logo(widget_pai, imagem_path="ONDACOM-1.png", largura=200, altura=60):
    try:
        imagem = Image.open(imagem_path).resize((largura, altura))
        logo = ImageTk.PhotoImage(imagem)
        lbl = tk.Label(widget_pai, image=logo, bg="white")
        lbl.image = logo
        lbl.pack(anchor="nw", pady=(5, 0), padx=5)
        lbl_footer = tk.Label(widget_pai, text="by DFSoluções", font=("Arial", 9), fg="gray")
        lbl_footer.pack(side="bottom", anchor="sw", padx=10, pady=5)
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")

def aplicar_listras_treeview(tree):
    tree.tag_configure("par", background="#F0F4F8")
    tree.tag_configure("impar", background="#FFFFFF")
    for idx, iid in enumerate(tree.get_children()):
        tag = "par" if idx % 2 == 0 else "impar"
        tree.item(iid, tags=(tag,))
