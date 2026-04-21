"""
Programa de Cadastro de Tipos de Ativo
Tela Inicial 
JC Jan/2026
Ver 1
Banco de Dados inv.db
Tabela inv00
Módulo: inv11_01.py
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import inv00_0      # módulo de banco de dados
import inv11_02     # módulo de inclusão
import inv11_03     # módulo de alteração


def abrir_lista(root):

    # Evita abrir várias janelas iguais
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and widget.title() == "Consulta de Tipos de Ativos":
            widget.lift()
            return

    # Criar janela
    janela = tk.Toplevel(root)
    janela.title("Consulta de Tipos de Ativos")
    janela.geometry("750x450")
    janela.grab_set()

    # Atalho ESC para fechar
    janela.bind("<Escape>", lambda e: janela.destroy())

    # -----------------------------
    #       BOTÕES SUPERIORES
    # -----------------------------
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack(fill="x")

    # Os callbacks serão adicionados depois da criação do grid
    # (por isso usamos lambda vazio aqui temporariamente)
    btn_incluir = ttk.Button(frame_botoes, text="INCLUIR", width=12)
    btn_incluir.pack(side="left", padx=5)

    btn_alterar = ttk.Button(frame_botoes, text="ALTERAR", width=12)
    btn_alterar.pack(side="left", padx=5)

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

    colunas = ("INV00_01", "INV00_02", "INV00_03", "INV00_20")

    tree = ttk.Treeview(frame_grid, columns=colunas, show="headings", height=15)

    tree.heading("INV00_01", text="Código")
    tree.heading("INV00_02", text="Descrição")
    tree.heading("INV00_03", text="Requer Segmento")
    tree.heading("INV00_20", text="Limite Perc.Invest.")

    tree.column("INV00_01", width=80)
    tree.column("INV00_02", width=250)
    tree.column("INV00_03", width=100)
    tree.column("INV00_20", width=150)

    tree.pack(fill="both", expand=True)

    # -----------------------------
    #   FUNÇÃO PARA ATUALIZAR GRID
    # -----------------------------
    def atualizar_grid():
        # Limpa o grid
        for i in tree.get_children():
            tree.delete(i)

        # Recarrega os dados
        conn = inv00_0.conectar()
        registros = inv00_0.listar_registros(conn)
        for reg in registros:
            tree.insert("", tk.END, values=reg)

        # Atualiza aviso da soma dos percentuais
        total_perc = inv00_0.soma_perc(conn)
        if total_perc != 100:
            label_aviso.config(text=f"Soma dos Percentuais é {total_perc:.2f}%, o Limite é 100%!")
        else:
            label_aviso.config(text="")

        conn.close()

    # -----------------------------
    #   CARREGAR DADOS INICIAIS
    # -----------------------------
    atualizar_grid()

    # -----------------------------
    #   CONECTAR CALLBACKS
    # -----------------------------
    btn_incluir.config(
        command=lambda: inv11_02.abrir_janela(janela, atualizar_grid)
    )

    btn_alterar.config(
        command=lambda: inv11_03.alterar_registro(tree, atualizar_grid)
    )


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
        inv00_0.excluir_registro(conn, codigo)
        conn.close()

        # Limpa o grid
        for i in tree.get_children():
            tree.delete(i)

        # Recarrega os dados do banco
        conn = inv00_0.conectar()
        registros = inv00_0.listar_registros(conn)
        for reg in registros:
            if len(reg) == 4:
                tree.insert("", tk.END, values=reg)

        # Atualiza aviso da soma dos percentuais
        total_perc = inv00_0.soma_perc(conn)
        conn.close()

        if total_perc != 100:
            tree.master.children['!frame2'].children['!label'].config(
                text=f"Soma dos Percentuais é {total_perc:.2f}%, o Limite é 100%!")
        else:
            tree.master.children['!frame2'].children['!label'].config(text="")

        messagebox.showinfo("Sucesso", "Registro excluído com sucesso!", parent=janela)

    janela.lift()
    janela.focus_force()
