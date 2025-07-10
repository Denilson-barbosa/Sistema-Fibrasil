from datetime import datetime
import pandas as pd
import tkinter as tk

def formatar_datas_para_exibicao(val):
    if pd.isna(val):
        return ""
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.strftime("%d/%m/%Y %H:%M:%S")
    return val

from datetime import datetime

def converter_datas_para_salvar(coluna, valor):
    if not valor or not isinstance(valor, str):
        return valor

    if "DATA" in coluna.upper() or "PREVISAO" in coluna.upper():
        try:
            for fmt in ("%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    data = datetime.strptime(valor.strip(), fmt)
                    return data.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
        except Exception:
            pass

    return valor


def aplicar_mascara_data(entry):
    def formatar(event):
        texto = entry.get().replace("/", "").replace(":", "").replace(" ", "")
        novo = ""
        for i, c in enumerate(texto):
            if i == 2 or i == 4:
                novo += "/"
            elif i == 8:
                novo += " "
            elif i == 10 or i == 12:
                novo += ":"
            novo += c
        entry.delete(0, tk.END)
        entry.insert(0, novo[:19])
    entry.bind("<KeyRelease>", formatar)
