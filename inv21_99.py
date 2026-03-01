"""
Tela de Inclusão de Movimentação
Tabela INV03
Módulo: inv21_02.py
Fev/2026
"""

import tkinter as tk
from tkinter import ttk, messagebox
import inv00_0      # módulo de banco de dados


# ---------------------------------------------------------
#   ABRIR JANELA DE INCLUSÃO
# ---------------------------------------------------------
def abrir_janela_inv03(root, tree):

    janela = tk.Toplevel(root)
    janela.title("Inclusão de Movimento")
    janela.geometry("900x550")
    janela.grab_set()
    janela.bind("<Escape>", lambda e: janela.destroy())

    frame = ttk.Frame(janela, padding=10)
    frame.pack(fill="both", expand=True)

    # ---------------------------------------------------------
    #   CAMPOS
    # ---------------------------------------------------------
    labels = {
        "INV03_06": "Código",
        "INV03_02": "Descrição",
        "INV03_12": "Tp Mov.",
        "INV03_07": "Quantidade",
        "INV03_13": "Valor Unitário",
        "INV03_14": "Valor Total R$",
        "INV03_15": "Cotação US$",
        "INV03_22": "Valor Unitário US$",
        "INV03_16": "Valor Total US$",
        "INV03_18": "Data Inclusão",
        "INV03_19": "Nota Corretagem"
    }

    campos = {}

    row = 0
    for campo, texto in labels.items():
        ttk.Label(frame, text=texto).grid(row=row, column=0, sticky="w", pady=5)
        entrada = ttk.Entry(frame, width=30)
        entrada.grid(row=row, column=1, sticky="w", pady=5)
        campos[campo] = entrada
        row += 1

    # ---------------------------------------------------------
    #   COMBO DO CÓDIGO (INV02)
    # ---------------------------------------------------------
    conn = inv00_0.conectar()
    lista_codigos = inv00_0.listar_registros_inv02(conn)
    conn.close()

    campos["INV03_06"].destroy()
    campos["INV03_06"] = ttk.Combobox(frame, values=lista_codigos, width=28)
    campos["INV03_06"].grid(row=0, column=1, sticky="w", pady=5)

    # ---------------------------------------------------------
    #   TIPO DE MOVIMENTO
    # ---------------------------------------------------------
    campos["INV03_12"].destroy()
    campos["INV03_12"] = ttk.Combobox(frame, values=["C", "D", "V"], width=10)
    campos["INV03_12"].grid(row=2, column=1, sticky="w", pady=5)

    # ---------------------------------------------------------
    #   CAMPOS EM DÓLAR (dependem do INV02_17)
    # ---------------------------------------------------------
    def atualizar_campos_dolar(event=None):
        codigo = campos["INV03_06"].get()
        if not codigo:
            return

        conn = inv00_0.conectar()
        dados = inv00_0.buscar_inv02_por_codigo(conn, codigo)
        conn.close()

        usa_dolar = (dados[0][0] == "S") if dados else False

        for campo in ["INV03_15", "INV03_22", "INV03_16"]:
            if usa_dolar:
                campos[campo].config(state="normal")
            else:
                campos[campo].delete(0, tk.END)
                campos[campo].config(state="disabled")

        # Atualiza descrição automaticamente
        if dados:
            campos["INV03_02"].delete(0, tk.END)
            campos["INV03_02"].insert(0, dados[0][1])

    campos["INV03_06"].bind("<<ComboboxSelected>>", atualizar_campos_dolar)

# --- BOTÕES ---
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack()

    ttk.Button(frame_botoes, text="Salvar", width=12, command=salvar).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botoes, text="Retornar", width=12, command=janela.destroy).grid(row=0, column=1, padx=10)

    entry_codigo.focus()


# ---------------------------------------------------------
#   GRAVAR REGISTRO
# ---------------------------------------------------------
def gravar_registro(janela, campos, tree):

    # -----------------------------
    #   VALIDAÇÕES
    # -----------------------------
    codigo = campos["INV03_06"].get().strip()
    descricao = campos["INV03_02"].get().strip()
    tp_mov = campos["INV03_12"].get().strip()
    quantidade = campos["INV03_07"].get().strip()

    if not codigo:
        messagebox.showwarning("Atenção", "Código não pode ser vazio.", parent=janela)
        return

    if not descricao:
        messagebox.showwarning("Atenção", "Descrição não pode ser vazia.", parent=janela)
        return

    if tp_mov not in ["C", "D", "V"]:
        messagebox.showwarning("Atenção", "Tp Mov. deve ser C, D ou V.", parent=janela)
        return

    try:
        if float(quantidade) <= 0:
            raise ValueError
    except:
        messagebox.showwarning("Atenção", "Quantidade deve ser maior que zero.", parent=janela)
        return

    # -----------------------------
    #   MONTAR REGISTRO
    # -----------------------------
    registro = {campo: campos[campo].get().strip() for campo in campos}

    # -----------------------------
    #   GRAVAR NO BANCO
    # -----------------------------
    conn = inv00_0.conectar()
    inv00_0.inserir_registro_inv03(conn, registro)
    conn.close()

    # -----------------------------
    #   ATUALIZAR GRID
    # -----------------------------
    for i in tree.get_children():
        tree.delete(i)

    conn = inv00_0.conectar()
    registros = inv00_0.listar_registros_inv03(conn)
    conn.close()

    for reg in registros:
        tree.insert("", tk.END, values=reg)

    messagebox.showinfo("Sucesso", "Registro incluído com sucesso!", parent=janela)
    janela.destroy()
