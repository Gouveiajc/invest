"""Conciliação de Movimentação
Tabela INV02
Módulo: inv22_01.py
Fev/2026
"""

import tkinter as tk
from tkinter import ttk, messagebox
import inv00_0


def conciliar_ativos():

 # Confirmação antes de iniciar 
    if not messagebox.askyesno( 
        "Conciliação",
          "Deseja iniciar a conciliação de todos os ativos?"
    ):
        return  # usuário cancelou
     
    conn = inv00_0.conectar()
    ativos = inv00_0.listar_registros_inv02(conn)
    #conn.close()

    for linha in ativos:
        codigo = linha[0]
        inv00_0.conciliar_ativo_inv02(codigo)

    messagebox.showinfo(
        "Conciliação",
        "Processo concluído.\nTodos os ativos foram conciliados."
    )
