"""
Tela de Inclusão de Movimentação
Tabela INV03
Módulo: inv21_02.py
Fev/2026
"""

import tkinter as tk
from tkinter import ttk, messagebox
import inv00_0      # módulo de banco de dados
import inv00_1      # validações

# ---------------------------------------------------------
#   ABRIR JANELA DE INCLUSÃO
# ---------------------------------------------------------
def abrir_janela_inv03(root, tree):

    janela = tk.Toplevel(root)
    janela.title("Inclusão de Movimento")
    janela.geometry("600x550")
    janela.grab_set()
    janela.bind("<Escape>", lambda e: janela.destroy())

    frame = ttk.Frame(janela, padding=10)
    frame.pack(fill="both", expand=True)

    campos = {}   # dicionário para armazenar widgets

    # ---------------------------------------------------------
    #   CÓDIGO DO ATIVO (COMBOBOX)
    # ---------------------------------------------------------
    ttk.Label(frame, text="Código Ativo:").grid(row=0, column=0, sticky="w", pady=5)

    try:
        conn = inv00_0.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT INV02_06, INV02_02, INV02_17 FROM INV02 ORDER BY INV02_06")
        tipos = cursor.fetchall()
        lista_tipos = [t[0] for t in tipos]   # SOMENTE O CÓDIGO
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar tipos: {e}")
        lista_tipos = []
    finally:
        conn.close()

    combo_codigo = ttk.Combobox(frame, values=lista_tipos, state="readonly", width=20)
    combo_codigo.grid(row=0, column=1, sticky="w", pady=5)
    campos["INV03_06"] = combo_codigo

    # ---------------------------------------------------------
    #   DESCRIÇÃO DO ATIVO (ENTRY SOMENTE LEITURA)
    # ---------------------------------------------------------
    ttk.Label(frame, text="Descrição Ativo:").grid(row=1, column=0, sticky="w", pady=5)

    descricao_var = tk.StringVar()
    entry_descricao = ttk.Entry(frame, textvariable=descricao_var, width=40, state="readonly")
    entry_descricao.grid(row=1, column=1, sticky="w", pady=5)
    campos["INV03_02"] = entry_descricao

    # ---------------------------------------------------------
    #   FUNÇÃO PARA ATUALIZAR DESCRIÇÃO E CAMPOS EM DÓLAR
    # ---------------------------------------------------------
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

        # Habilitar ou desabilitar campos em dólar
        for campo in ["INV03_15", "INV03_22", "INV03_16"]:
            if usa_dolar:
                campos[campo].config(state="normal")
            else:
                campos[campo].delete(0, tk.END)
                campos[campo].config(state="disabled")

    combo_codigo.bind("<<ComboboxSelected>>", atualizar_descricao)

    # ---------------------------------------------------------
    #   OUTROS CAMPOS DA TABELA INV03
    # ---------------------------------------------------------
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

        # Tp Mov. (C/D/V)
        if campo == "INV03_12":
            entrada = ttk.Combobox(frame, values=["C", "D", "V"], width=10, state="readonly")

        # Valor Total R$ (somente leitura)
        elif campo == "INV03_14":
            entrada = ttk.Entry(frame, width=30, state="readonly")

        else:
            entrada = ttk.Entry(frame, width=30)

        entrada.grid(row=row, column=1, sticky="w", pady=5)
        campos[campo] = entrada
        row += 1

    # ---------------------------------------------------------
    #   CÁLCULO AUTOMÁTICO DO VALOR TOTAL R$
    # ---------------------------------------------------------
    def calcular_total_rs(*args):
        # Converte vírgula para ponto automaticamente
        qtd_txt = campos["INV03_07"].get().replace(",", ".")
        vlr_txt = campos["INV03_13"].get().replace(",", ".")

        try:
            qtd = float(qtd_txt)
            vlr = float(vlr_txt)
            total = qtd * vlr

            campos["INV03_14"].config(state="normal")
            campos["INV03_14"].delete(0, tk.END)
            campos["INV03_14"].insert(0, f"{total:.2f}")
            campos["INV03_14"].config(state="readonly")

        except:
            campos["INV03_14"].config(state="normal")
            campos["INV03_14"].delete(0, tk.END)
            campos["INV03_14"].config(state="readonly")

    # ---------------------------------------------------------
    #   CONVERTER VÍRGULA PARA PONTO NOS CAMPOS NUMÉRICOS
    # ---------------------------------------------------------
    def converter_virgula(event):
        widget = event.widget
        texto = widget.get()
        novo_texto = texto.replace(",", ".")
        if texto != novo_texto:
            widget.delete(0, tk.END)
            widget.insert(0, novo_texto)

    campos["INV03_07"].bind("<KeyRelease>", converter_virgula)
    campos["INV03_13"].bind("<KeyRelease>", converter_virgula)
    campos["INV03_07"].bind("<KeyRelease>", calcular_total_rs)
    campos["INV03_13"].bind("<KeyRelease>", calcular_total_rs)
 


    # ---------------------------------------------------------
    #   CAMPOS EM DÓLAR COMEÇAM DESABILITADOS
    # ---------------------------------------------------------
    for campo in ["INV03_15", "INV03_22", "INV03_16"]:
        campos[campo].config(state="disabled")

    # ---------------------------------------------------------
    #   BOTÕES
    # ---------------------------------------------------------
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack()

    ttk.Button(frame_botoes, text="Salvar", width=15,
            command=lambda: gravar_registro(janela, campos, tree)).grid(row=0, column=0, padx=10)

    ttk.Button(frame_botoes, text="Retornar", width=15,
            command=janela.destroy).grid(row=0, column=1, padx=10)

# ---------------------------------------------------------
#   GRAVAR REGISTRO
# ---------------------------------------------------------
def gravar_registro(janela, campos, tree):

    # ---------------------------------------------------------
    #   MONTAR DICIONÁRIO REGISTRO (COM CONVERSÃO , → .)
    # ---------------------------------------------------------
    registro = {}

    # Campos numéricos que devem usar ponto
    campos_numericos = [
        "INV03_07",  # Quantidade
        "INV03_13",  # Valor Unitário
        "INV03_14",  # Valor Total R$
        "INV03_15",  # Cotação US$
        "INV03_22",  # Valor Unitário US$
        "INV03_16"   # Valor Total US$
    ]

    for campo in campos:
        valor = campos[campo].get().strip()

        # Converte vírgula para ponto nos campos numéricos
        if campo in campos_numericos:
            valor = valor.replace(",", ".")

        registro[campo] = valor

    # ---------------------------------------------------------
    #   VALIDAÇÃO CENTRALIZADA
    # ---------------------------------------------------------
    erro = inv00_1.validar_campos_inv03(registro)

    if erro:
        messagebox.showwarning("Atenção", erro, parent=janela)
        return

    # ---------------------------------------------------------
    #   GRAVAR NO BANCO
    # ---------------------------------------------------------
    conn = inv00_0.conectar()
    inv00_0.inserir_registro_inv03(conn, registro)
    conn.close()

    # ---------------------------------------------------------
    #   ATUALIZAR GRID
    # ---------------------------------------------------------
    for i in tree.get_children():
        tree.delete(i)

    conn = inv00_0.conectar()
    registros = inv00_0.listar_registros_inv03(conn)
    conn.close()

    for reg in registros:
        tree.insert("", tk.END, values=reg)

    messagebox.showinfo("Sucesso", "Registro incluído com sucesso!", parent=janela)
    janela.destroy()

