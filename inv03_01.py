"""
Tela de Consulta dos Ativos
Tabela INV01
Módulo: inv03_01.py
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import inv00_0      # módulo de banco de dados
import inv03_02     # módulo de inclusão

def abrir_lista(root):

    # Evita abrir várias janelas iguais
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and widget.title() == "Consulta de Ativos":
            widget.lift()
            return

    # Criar janela
    janela = tk.Toplevel(root)
    janela.title("Consulta de Ativos")
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
               command=lambda: inv03_02.abrir_janela_inv02(janela, tree) ).pack(side="left", padx=5)

    ttk.Button(frame_botoes, text="ALTERAR", width=12,
               command=lambda: inv03_03.alterar_registro(tree)).pack(side="left", padx=5)

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

    colunas = ("INV02_06", "INV02_02", "INV02_01", "INV02_05", "INV02_07", "INV02_08", "INV02_09", "INV02_10", "INV02_17", "INV02_18", "INV02_20", "INV02_21")

    tree = ttk.Treeview(frame_grid, columns=colunas, show="headings", height=15)

    tree.heading("INV02_06", text="Código")
    tree.heading("INV02_02", text="Descrição")
    tree.heading("INV02_01", text="Tipo Ativo")
    tree.heading("INV02_05", text="Segmento")
    tree.heading("INV02_07", text="Quantidade")
    tree.heading("INV02_08", text="Custo Médio")
    tree.heading("INV02_09", text="Custo Aquisição")
    tree.heading("INV02_17", text="Ativo Exterior")
    tree.heading("INV02_10", text="Custo Aquisição US$")
    tree.heading("INV02_18", text="Data da Compra")
    tree.heading("INV02_20", text="% Investir")
    tree.heading("INV02_21", text="Obs.:")
  
    tree.column("INV02_06", width=80)
    tree.column("INV02_02", width=250)
    tree.column("INV02_01", width=80)
    tree.column("INV02_05", width=100)
    tree.column("INV02_07", width=80)
    tree.column("INV02_08", width=150)
    tree.column("INV02_09", width=150)
    tree.column("INV02_17", width=80)
    tree.column("INV02_10", width=100)
    tree.column("INV02_18", width=100)
    tree.column("INV02_20", width=100)
    tree.column("INV02_21", width=250)

    tree.pack(fill="both", expand=True)

    # -----------------------------
    #       CARREGAR DADOS
    # -----------------------------
    conn = inv00_0.conectar()
    registros = inv00_0.listar_registros_inv02(conn)

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
        inv00_0.excluir_registro_inv02(conn, codigo)
        conn.close()

        # Limpa o grid
        for i in tree.get_children():
            tree.delete(i)

        # Recarrega os dados do banco
        conn = inv00_0.conectar()
        registros = inv00_0.listar_registros_inv02(conn)
        conn.close()
        for reg in registros:
            tree.insert("", tk.END, values=reg)

        messagebox.showinfo("Sucesso", "Registro excluído com sucesso!", parent=janela)

    # Devolve o foco para a janela do grid
    janela.lift()
    janela.focus_force()
