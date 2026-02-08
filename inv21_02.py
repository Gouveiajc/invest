"""
Tela de Inclusão de Movimentação
Tabela INV03
Módulo: inv21_02.py
Fev/2026
"""

import tkinter as tk
from tkinter import ttk, messagebox
import inv00_0
import inv00_1


def abrir_janela_inv03(root, tree):

    janela = tk.Toplevel(root)
    janela.title("Inclusão de Movimento")
    janela.geometry("600x550")
    janela.grab_set()
    janela.bind("<Escape>", lambda e: janela.destroy())

    frame = ttk.Frame(janela, padding=10)
    frame.pack(fill="both", expand=True)

    campos = {}

    ttk.Label(frame, text="Código Ativo:").grid(row=0, column=0, sticky="w", pady=5)

    try:
        conn = inv00_0.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT INV02_06, INV02_02, INV02_17 FROM INV02 ORDER BY INV02_06")
        tipos = cursor.fetchall()
        lista_tipos = [t[0] for t in tipos]
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar tipos: {e}")
        lista_tipos = []
    finally:
        conn.close()

    combo_codigo = ttk.Combobox(frame, values=lista_tipos, state="readonly", width=20)
    combo_codigo.grid(row=0, column=1, sticky="w", pady=5)
    campos["INV03_06"] = combo_codigo

    ttk.Label(frame, text="Descrição Ativo:").grid(row=1, column=0, sticky="w", pady=5)

    descricao_var = tk.StringVar()
    entry_descricao = ttk.Entry(frame, textvariable=descricao_var, width=40, state="readonly")
    entry_descricao.grid(row=1, column=1, sticky="w", pady=5)
    campos["INV03_02"] = entry_descricao

    def converter_virgula(event):
        widget = event.widget
        texto = widget.get()
        novo = texto.replace(",", ".")
        if texto != novo:
            widget.delete(0, tk.END)
            widget.insert(0, novo)

    def calcular_total_rs(*args):
        qtd = campos["INV03_07"].get().replace(",", ".")
        vlr = campos["INV03_13"].get().replace(",", ".")
        try:
            total = float(qtd) * float(vlr)
            campos["INV03_14"].config(state="normal")
            campos["INV03_14"].delete(0, tk.END)
            campos["INV03_14"].insert(0, f"{total:.2f}")
            campos["INV03_14"].config(state="readonly")
        except:
            campos["INV03_14"].config(state="normal")
            campos["INV03_14"].delete(0, tk.END)
            campos["INV03_14"].config(state="readonly")

    def calcular_total_us(*args):
        if campos["INV03_16"].cget("state") == "disabled":
            return

        qtd = campos["INV03_07"].get().replace(",", ".")
        vlr = campos["INV03_22"].get().replace(",", ".")

        try:
            total = float(qtd) * float(vlr)
            campos["INV03_16"].config(state="normal")
            campos["INV03_16"].delete(0, tk.END)
            campos["INV03_16"].insert(0, f"{total:.2f}")
            campos["INV03_16"].config(state="readonly")
        except:
            campos["INV03_16"].config(state="normal")
            campos["INV03_16"].delete(0, tk.END)
            campos["INV03_16"].config(state="readonly")

    def atualizar_descricao(event=None):
        codigo = combo_codigo.get()

        if not codigo:
            descricao_var.set("")
            return

        conn = inv00_0.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT INV02_02, INV02_17 FROM INV02 WHERE INV02_06 = ?", (codigo,))
        dado = cursor.fetchone()
        conn.close()

        if not dado:
            descricao_var.set("")
            return

        descricao, usa_dolar_flag = dado
        descricao_var.set(descricao)

        usa_dolar = (usa_dolar_flag == "S")
        janela.usa_dolar = "S" if usa_dolar else "N"

        if usa_dolar:
            campos["INV03_15"].config(state="normal")
            campos["INV03_22"].config(state="normal")

            campos["INV03_15"].bind("<KeyRelease>", converter_virgula)
            campos["INV03_22"].bind("<KeyRelease>", converter_virgula)

            campos["INV03_15"].bind("<KeyRelease>", calcular_total_us)
            campos["INV03_22"].bind("<KeyRelease>", calcular_total_us)
            campos["INV03_07"].bind("<KeyRelease>", calcular_total_us)

            campos["INV03_16"].config(state="readonly")
            campos["INV03_16"].delete(0, tk.END)

        else:
            for campo in ["INV03_15", "INV03_22"]:
                campos[campo].config(state="disabled")
                campos[campo].delete(0, tk.END)

            campos["INV03_16"].config(state="readonly")
            campos["INV03_16"].delete(0, tk.END)

    combo_codigo.bind("<<ComboboxSelected>>", atualizar_descricao)

    labels = {
        "INV03_12": "Tp Mov. (C/D/V):",
        "INV03_07": "Quantidade:",
        "INV03_13": "Valor Unitário:",
        "INV03_14": "Valor Total R$:",
        "INV03_15": "Cotação US$:",
        "INV03_22": "Valor Unitário US$:",
        "INV03_16": "Valor Total US$:",
        "INV03_18": "Data Inclusão:",
        "INV03_19": "Nota Corretagem:"
    }

    row = 2
    for campo, texto in labels.items():
        ttk.Label(frame, text=texto).grid(row=row, column=0, sticky="w", pady=5)

        if campo == "INV03_12":
            entrada = ttk.Combobox(frame, values=["C", "D", "V"], width=10, state="readonly")
        elif campo in ["INV03_14", "INV03_16"]:
            entrada = ttk.Entry(frame, width=30, state="readonly")
        else:
            entrada = ttk.Entry(frame, width=30)

        entrada.grid(row=row, column=1, sticky="w", pady=5)
        campos[campo] = entrada
        row += 1

    campos["INV03_07"].bind("<KeyRelease>", converter_virgula)
    campos["INV03_13"].bind("<KeyRelease>", converter_virgula)
    campos["INV03_07"].bind("<KeyRelease>", calcular_total_rs)
    campos["INV03_13"].bind("<KeyRelease>", calcular_total_rs)

    campos["INV03_15"].config(state="disabled")
    campos["INV03_22"].config(state="disabled")
    campos["INV03_16"].config(state="readonly")

    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack()

    ttk.Button(frame_botoes, text="Salvar", width=15,
               command=lambda: gravar_registro(janela, campos, tree)).grid(row=0, column=0, padx=10)

    ttk.Button(frame_botoes, text="Retornar", width=15,
               command=janela.destroy).grid(row=0, column=1, padx=10)


def gravar_registro(janela, campos, tree):

    registro = {}

    campos_numericos = [
        "INV03_07",
        "INV03_13",
        "INV03_14",
        "INV03_15",
        "INV03_22",
        "INV03_16"
    ]

    # COPIA DOS CAMPOS
    for campo in campos:
        widget = campos[campo]
        valor = widget.get().strip()

        if campo in campos_numericos:
            valor = valor.replace(",", ".")

        registro[campo] = valor

    registro["usa_dolar"] = getattr(janela, "usa_dolar", "N")

    erro = inv00_1.validar_campos_inv03(registro)
    if erro:
        messagebox.showwarning("Atenção", erro, parent=janela)
        return

    conn = inv00_0.conectar()
    inv00_0.inserir_registro_inv03(conn, registro)
    conn.close()

    quantidade = float(registro["INV03_07"])
    total_rs = float(registro["INV03_14"])
    total_us = float(registro["INV03_16"]) if registro["usa_dolar"] == "S" else 0.0

    conn = inv00_0.conectar()
    inv00_0.atualizar_posicao_inv02(
        conn,
        codigo_ativo=registro["INV03_06"],
        tipo_mov=registro["INV03_12"],
        quantidade=quantidade,
        total_rs=total_rs,
        total_us=total_us,
        usa_dolar=registro["usa_dolar"]
    )
    conn.close()

    for i in tree.get_children():
        tree.delete(i)

    conn = inv00_0.conectar()
    registros = inv00_0.listar_registros_inv03(conn)
    conn.close()

    for reg in registros:
        tree.insert("", tk.END, values=reg)

    messagebox.showinfo("Sucesso", "Registro incluído com sucesso!", parent=janela)
    janela.destroy()
