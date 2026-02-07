"""
Tela de Consulta de Movimentação
Tabela INV03
Módulo: inv21_01.py
Fev/2026
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import inv00_0      # módulo de banco de dados
import inv21_02

def abrir_lista(root):

    # Evita abrir várias janelas iguais
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and widget.title() == "Cadastro Movimento":
            widget.lift()
            return

    # Criar janela
    janela = tk.Toplevel(root)
    janela.title("Cadastro Movimento")
    janela.geometry("1600x450")
    janela.grab_set()

    # Atalho ESC para fechar
    janela.bind("<Escape>", lambda e: janela.destroy())

    # -----------------------------
    #       BOTÕES SUPERIORES
    # -----------------------------
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack(fill="x")

    ttk.Button(frame_botoes, text="INCLUIR", width=12,
               command=lambda: inv21_02.abrir_janela_inv03(janela, tree) ).pack(side="left", padx=5)

    ttk.Button(frame_botoes, text="ALTERAR", width=12,
               command=lambda: inv21_03.alterar_registro(tree)).pack(side="left", padx=5)

    ttk.Button(frame_botoes, text="DELETAR", width=12,
               command=lambda: deletar_registro(tree)).pack(side="left", padx=5)

    ttk.Button(frame_botoes, text="RETORNAR", width=12,
               command=janela.destroy).pack(side="right", padx=5)

    # -----------------------------
    #       GRID (TREEVIEW)
    # -----------------------------
    frame_grid = ttk.Frame(janela, padding=10)
    frame_grid.pack(fill="both", expand=True)


    # Label para mensagens
    label_aviso = ttk.Label(frame_grid, text="", foreground="red", font=("Arial", 10, "bold"))
    label_aviso.pack(anchor="w", pady=(0, 5))

    colunas = ("INV03_06", "INV03_02", "INV03_12", "INV03_07", "INV03_13", "INV03_14", "INV03_15",  "INV03_22", "INV03_16", "INV03_18", "INV03_19")

    tree = ttk.Treeview(frame_grid, columns=colunas, show="headings", height=15)

    tree.heading("INV03_06", text="Código")
    tree.heading("INV03_02", text="Descrição")
    tree.heading("INV03_12", text="Tp Mov.")
    tree.heading("INV03_07", text="Quantidade")
    tree.heading("INV03_13", text="Valor Unitário")
    tree.heading("INV03_14", text="Valor Total R$")
    tree.heading("INV03_15", text="Cotação US$")
    tree.heading("INV03_22", text="Valor Unitário US$")
    tree.heading("INV03_16", text="Valor Total US$")
    tree.heading("INV03_18", text="Data Inclusão")
    tree.heading("INV03_19", text="Nota Corretagem")
    
  
    tree.column("INV03_06", width=80)
    tree.column("INV03_02", width=250)
    tree.column("INV03_12", width=50)
    tree.column("INV03_07", width=80)
    tree.column("INV03_13", width=150)
    tree.column("INV03_14", width=150)
    tree.column("INV03_15", width=150)
    tree.column("INV03_22", width=150)
    tree.column("INV03_16", width=150)
    tree.column("INV03_18", width=100)
    tree.column("INV03_19", width=250)
        
    tree.pack(fill="both", expand=True)

    # -----------------------------
    #       CARREGAR DADOS
    # -----------------------------
    conn = inv00_0.conectar()
    registros = inv00_0.listar_registros_inv03(conn)

    for reg in registros:
        tree.insert("", tk.END, values=reg)

    conn.close()

# -----------------------------
#       FUNÇÕES AUXILIARES
# -----------------------------

def deletar_registro(tree):
    item = tree.selection()
    janela = tree.master  # janela do grid

    if not item:
        messagebox.showwarning("Atenção", "Selecione um registro para deletar.", parent=janela)
        return

    valores = tree.item(item, "values")
    codigo = valores[0]
    desc   = valores[1]

    if messagebox.askyesno("Confirmar", f"Excluir o registro: \nCódigo: {codigo} \nDescrição: {desc}?", parent=janela):
        conn = inv00_0.conectar()
        inv00_0.excluir_registro_inv01(conn, codigo)
        conn.close()

        # Limpa o grid
        for i in tree.get_children():
            tree.delete(i)

        # Recarrega os dados do banco
        conn = inv00_0.conectar()
        registros = inv00_0.listar_registros_inv01(conn)
        conn.close()
        for reg in registros:
            tree.insert("", tk.END, values=reg)

        messagebox.showinfo("Sucesso", "Registro excluído com sucesso!", parent=janela)

    # Devolve o foco para a janela do grid
    janela.lift()
    janela.focus_force()


